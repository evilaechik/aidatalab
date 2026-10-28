#!/usr/bin/env python3
"""Tune and explain the local Fortune-100 XGBoost diagnostic safely.

Optuna chooses XGBoost parameters inside each outer training fold.  The outer
fold stays untouched until final scoring, and SHAP values are calculated only
for those held-out predictions.  This prevents tuning and explanation results
from being presented as in-sample performance.

The input outcome is a Data Axle-derived *candidate location* proxy, not a
source-verified Fortune office score.  Results must stay local and must not be
interpreted as causal policy effects.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
import optuna
import pandas as pd
import shap
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

from run_fortune100_candidate_xgboost import (
    DEFAULT_FACTORS,
    DEFAULT_ROSTER,
    DEFAULT_TARGET,
    FEATURES,
    RANDOM_SEED,
    load_data,
    new_model,
    reject_repo_output,
    standardized_msa,
)


RIDGE_ALPHAS = np.logspace(-3, 5, 33)


def tuned_model(params: dict[str, float | int]) -> XGBRegressor:
    """Keep the tuned search intentionally small for roughly 100 MSAs."""
    return XGBRegressor(
        objective="reg:squarederror",
        tree_method="hist",
        random_state=RANDOM_SEED,
        n_jobs=1,
        **params,
    )


def trial_parameters(trial: optuna.Trial) -> dict[str, float | int]:
    """A conservative search space; deep trees would overfit this sample."""
    return {
        "n_estimators": trial.suggest_int("n_estimators", 75, 300, step=25),
        "max_depth": trial.suggest_int("max_depth", 1, 3),
        "min_child_weight": trial.suggest_int("min_child_weight", 2, 10),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.08, log=True),
        "subsample": trial.suggest_float("subsample", 0.65, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.65, 1.0),
        "reg_alpha": trial.suggest_float("reg_alpha", 0.001, 5.0, log=True),
        "reg_lambda": trial.suggest_float("reg_lambda", 1.0, 100.0, log=True),
    }


def fit_and_predict(
    train: pd.DataFrame,
    test: pd.DataFrame,
    target_column: str,
    model: XGBRegressor,
    feature_columns: list[str],
) -> tuple[np.ndarray, SimpleImputer, np.ndarray]:
    """Fit one model, returning raw-scale predictions and its held-out matrix."""
    imputer = SimpleImputer(strategy="median", keep_empty_features=True)
    x_train = imputer.fit_transform(train[feature_columns])
    x_test = imputer.transform(test[feature_columns])
    model.fit(x_train, np.log1p(train[target_column].astype(float).to_numpy()))
    prediction = np.maximum(np.expm1(model.predict(x_test)), 0)
    return prediction, imputer, x_test


def fit_linear_and_predict(
    train: pd.DataFrame,
    test: pd.DataFrame,
    target_column: str,
    feature_columns: list[str],
    *,
    ridge_alpha: float | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Fit OLS or Ridge using training-fold scaling and return raw predictions."""
    imputer = SimpleImputer(strategy="median", keep_empty_features=True)
    scaler = StandardScaler()
    x_train = scaler.fit_transform(imputer.fit_transform(train[feature_columns]))
    x_test = scaler.transform(imputer.transform(test[feature_columns]))
    model = (
        LinearRegression()
        if ridge_alpha is None
        else Ridge(alpha=ridge_alpha)
    )
    model.fit(x_train, np.log1p(train[target_column].astype(float).to_numpy()))
    prediction = np.maximum(np.expm1(model.predict(x_test)), 0)
    return prediction, np.asarray(model.coef_, dtype=float)


def tune_outer_fold(
    train: pd.DataFrame,
    target_column: str,
    fold: int,
    trials: int,
    feature_columns: list[str],
) -> tuple[dict[str, float | int], pd.DataFrame]:
    """Find parameters using only inner splits of the outer training MSAs."""
    inner = KFold(n_splits=3, shuffle=True, random_state=RANDOM_SEED + fold)

    def objective(trial: optuna.Trial) -> float:
        params = trial_parameters(trial)
        fold_maes = []
        for inner_train, inner_test in inner.split(train):
            training = train.iloc[inner_train]
            validation = train.iloc[inner_test]
            prediction, _, _ = fit_and_predict(
                training, validation, target_column, tuned_model(params), feature_columns
            )
            fold_maes.append(
                mean_absolute_error(validation[target_column].astype(float), prediction)
            )
        return float(np.mean(fold_maes))

    study = optuna.create_study(
        direction="minimize",
        sampler=optuna.samplers.TPESampler(seed=RANDOM_SEED + fold),
    )
    study.optimize(objective, n_trials=trials, show_progress_bar=False)
    trials_frame = pd.DataFrame(
        [
            {
                "outer_fold": fold,
                "trial": trial.number,
                "inner_cv_mae": trial.value,
                "state": trial.state.name,
                **trial.params,
            }
            for trial in study.trials
        ]
    )
    return study.best_params, trials_frame


def tune_ridge_outer_fold(
    train: pd.DataFrame,
    target_column: str,
    fold: int,
    feature_columns: list[str],
) -> tuple[float, pd.DataFrame]:
    """Tune Ridge penalty on raw-count MAE using only the outer training fold."""
    inner = KFold(n_splits=3, shuffle=True, random_state=RANDOM_SEED + fold)
    result_rows: list[dict[str, float | int]] = []
    for alpha in RIDGE_ALPHAS:
        fold_maes = []
        for inner_train, inner_test in inner.split(train):
            training = train.iloc[inner_train]
            validation = train.iloc[inner_test]
            prediction, _ = fit_linear_and_predict(
                training,
                validation,
                target_column,
                feature_columns,
                ridge_alpha=float(alpha),
            )
            fold_maes.append(
                mean_absolute_error(validation[target_column].astype(float), prediction)
            )
        result_rows.append(
            {
                "outer_fold": fold,
                "ridge_alpha": float(alpha),
                "inner_cv_mae": float(np.mean(fold_maes)),
            }
        )
    trials = pd.DataFrame(result_rows)
    best = trials.loc[trials["inner_cv_mae"].idxmin(), "ridge_alpha"]
    return float(best), trials


def metric_rows(predictions: pd.DataFrame, target_column: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for model_name, group in predictions.groupby("model", sort=False):
        actual = group["actual_candidate_count"].to_numpy()
        predicted = group["predicted_candidate_count"].to_numpy()
        rows.append(
            {
                "model": model_name,
                "held_out_msas": len(group),
                "mae_candidate_companies": mean_absolute_error(actual, predicted),
                "rmse_candidate_companies": mean_squared_error(actual, predicted) ** 0.5,
                "held_out_r2": r2_score(actual, predicted),
                "target_definition": f"{target_column}; Data Axle candidate evidence, not verified office presence",
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-scores-csv", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--roster-csv", type=Path, default=DEFAULT_ROSTER)
    parser.add_argument("--factors-csv", type=Path, default=DEFAULT_FACTORS)
    parser.add_argument("--factor-year", type=int, default=2022)
    parser.add_argument("--target-column", default=DEFAULT_TARGET)
    parser.add_argument("--optuna-trials", type=int, default=40)
    parser.add_argument(
        "--extra-features-csv",
        type=Path,
        action="append",
        help="Optional public MSA feature file. Must contain one row per msa.",
    )
    parser.add_argument(
        "--extra-feature-columns",
        action="append",
        help="Comma-separated numeric columns from --extra-features-csv to add to the model.",
    )
    args = parser.parse_args()
    if args.optuna_trials < 10:
        raise ValueError("Use at least 10 Optuna trials")
    for path in [args.candidate_scores_csv, args.roster_csv, args.factors_csv]:
        if not path.expanduser().is_file():
            raise FileNotFoundError(path)
    extra_files = args.extra_features_csv or []
    extra_column_groups = args.extra_feature_columns or []
    if bool(extra_files) != bool(extra_column_groups) or len(extra_files) != len(extra_column_groups):
        raise ValueError("Supply one --extra-feature-columns value for every --extra-features-csv")
    for path in extra_files:
        if not path.expanduser().is_file():
            raise FileNotFoundError(path)

    output_dir = reject_repo_output(args.output_dir)
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    data = load_data(
        args.candidate_scores_csv,
        args.roster_csv,
        args.factors_csv,
        args.factor_year,
        args.target_column,
    )
    feature_columns = FEATURES.copy()
    for extra_path, column_group in zip(extra_files, extra_column_groups):
        extra_columns = [
            column.strip() for column in column_group.split(",") if column.strip()
        ]
        if not extra_columns:
            raise ValueError("--extra-feature-columns must name at least one column")
        duplicate_columns = set(extra_columns) & set(feature_columns)
        if duplicate_columns:
            raise ValueError(f"Duplicate model feature names: {sorted(duplicate_columns)}")
        extra = pd.read_csv(extra_path, dtype={"msa": str})
        if "msa" not in extra.columns:
            raise ValueError("Extra features file must include an 'msa' column")
        missing_columns = set(extra_columns) - set(extra.columns)
        if missing_columns:
            raise ValueError(f"Extra features file is missing: {sorted(missing_columns)}")
        extra["msa"] = standardized_msa(extra["msa"])
        if extra["msa"].duplicated().any():
            raise ValueError("Extra features file has duplicate MSA codes")
        for column in extra_columns:
            extra[column] = pd.to_numeric(extra[column], errors="coerce")
        data = data.merge(
            extra[["msa", *extra_columns]], on="msa", how="left", validate="one_to_one"
        )
        feature_columns.extend(extra_columns)
    data.to_csv(output_dir / "optuna_shap_input_audit.csv", index=False, quoting=csv.QUOTE_MINIMAL)
    usable = data.loc[data["included_in_xgboost"]].copy().reset_index(drop=True)
    if len(usable) < 50:
        raise ValueError(f"Need at least 50 usable MSAs; found {len(usable)}")

    outer = KFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
    prediction_rows: list[dict[str, object]] = []
    parameter_rows: list[dict[str, object]] = []
    trial_rows: list[pd.DataFrame] = []
    shap_rows: list[dict[str, object]] = []
    ridge_trials: list[pd.DataFrame] = []
    ridge_parameters: list[dict[str, float | int]] = []
    linear_coefficient_rows: list[dict[str, object]] = []

    for fold, (train_index, test_index) in enumerate(outer.split(usable), start=1):
        train, test = usable.iloc[train_index], usable.iloc[test_index]
        best_params, trials_frame = tune_outer_fold(
            train, args.target_column, fold, args.optuna_trials, feature_columns
        )
        trial_rows.append(trials_frame)
        parameter_rows.append({"outer_fold": fold, **best_params})
        ridge_alpha, ridge_trials_frame = tune_ridge_outer_fold(
            train, args.target_column, fold, feature_columns
        )
        ridge_trials.append(ridge_trials_frame)
        ridge_parameters.append({"outer_fold": fold, "ridge_alpha": ridge_alpha})

        tuned = tuned_model(best_params)
        tuned_prediction, tuned_imputer, tuned_x_test = fit_and_predict(
            train, test, args.target_column, tuned, feature_columns
        )
        fixed_prediction, _, _ = fit_and_predict(
            train, test, args.target_column, new_model(), feature_columns
        )
        ols_prediction, ols_coefficients = fit_linear_and_predict(
            train, test, args.target_column, feature_columns
        )
        ridge_prediction, ridge_coefficients = fit_linear_and_predict(
            train,
            test,
            args.target_column,
            feature_columns,
            ridge_alpha=ridge_alpha,
        )
        mean_prediction = np.full(
            len(test), train[args.target_column].astype(float).mean()
        )
        for row_number, (_, row) in enumerate(test.iterrows()):
            for model_name, prediction in [
                ("optuna_tuned_xgboost", tuned_prediction[row_number]),
                ("fixed_parameter_xgboost", fixed_prediction[row_number]),
                ("ordinary_linear_regression", ols_prediction[row_number]),
                ("nested_ridge_regression", ridge_prediction[row_number]),
                ("training_mean_baseline", mean_prediction[row_number]),
            ]:
                prediction_rows.append(
                    {
                        "outer_fold": fold,
                        "model": model_name,
                        "msa": row["msa"],
                        "msa_title": row["msa_title"],
                        "actual_candidate_count": float(row[args.target_column]),
                        "predicted_candidate_count": float(prediction),
                    }
                )
        for feature_number, feature in enumerate(feature_columns):
            linear_coefficient_rows.extend(
                [
                    {
                        "outer_fold": fold,
                        "model": "ordinary_linear_regression",
                        "feature": feature,
                        "standardized_log_count_coefficient": float(ols_coefficients[feature_number]),
                    },
                    {
                        "outer_fold": fold,
                        "model": "nested_ridge_regression",
                        "feature": feature,
                        "standardized_log_count_coefficient": float(ridge_coefficients[feature_number]),
                    },
                ]
            )

        explanation_input = pd.DataFrame(tuned_x_test, columns=feature_columns)
        explainer = shap.TreeExplainer(tuned)
        shap_values = np.asarray(explainer.shap_values(explanation_input))
        for row_number, (_, row) in enumerate(test.iterrows()):
            for feature_number, feature in enumerate(feature_columns):
                shap_rows.append(
                    {
                        "outer_fold": fold,
                        "msa": row["msa"],
                        "msa_title": row["msa_title"],
                        "actual_candidate_count": float(row[args.target_column]),
                        "held_out_prediction": float(tuned_prediction[row_number]),
                        "feature": feature,
                        "imputed_feature_value": float(tuned_x_test[row_number, feature_number]),
                        "shap_value_log_count": float(shap_values[row_number, feature_number]),
                    }
                )

    predictions = pd.DataFrame(prediction_rows)
    metrics = metric_rows(predictions, args.target_column)
    optuna_trials = pd.concat(trial_rows, ignore_index=True)
    selected_parameters = pd.DataFrame(parameter_rows)
    ridge_trial_frame = pd.concat(ridge_trials, ignore_index=True)
    ridge_parameter_frame = pd.DataFrame(ridge_parameters)
    linear_coefficients = pd.DataFrame(linear_coefficient_rows)
    linear_coefficient_summary = (
        linear_coefficients.assign(
            abs_standardized_coefficient=lambda frame: frame[
                "standardized_log_count_coefficient"
            ].abs()
        )
        .groupby(["model", "feature"], as_index=False)
        .agg(
            mean_standardized_log_count_coefficient=(
                "standardized_log_count_coefficient", "mean"
            ),
            mean_abs_standardized_log_count_coefficient=(
                "abs_standardized_coefficient", "mean"
            ),
            coefficient_std=("standardized_log_count_coefficient", "std"),
            held_out_folds=("outer_fold", "nunique"),
        )
        .sort_values(["model", "mean_abs_standardized_log_count_coefficient"], ascending=[True, False])
    )
    linear_coefficient_summary["interpretation"] = (
        "Training-fold standardized coefficient on log1p(candidate count); predictive association, not a causal policy effect."
    )
    shap_values = pd.DataFrame(shap_rows)
    shap_importance = (
        shap_values.assign(abs_shap_value=lambda frame: frame["shap_value_log_count"].abs())
        .groupby("feature", as_index=False)
        .agg(
            mean_abs_shap_value=("abs_shap_value", "mean"),
            mean_shap_value=("shap_value_log_count", "mean"),
            shap_std=("shap_value_log_count", "std"),
            held_out_msas=("msa", "nunique"),
        )
        .sort_values("mean_abs_shap_value", ascending=False)
    )
    shap_importance["interpretation"] = (
        "Out-of-fold contribution to an XGBoost candidate-location prediction; predictive, not causal."
    )

    predictions.to_csv(output_dir / "optuna_shap_outer_fold_predictions.csv", index=False)
    metrics.to_csv(output_dir / "optuna_shap_model_comparison.csv", index=False)
    optuna_trials.to_csv(output_dir / "optuna_inner_cv_trials.csv", index=False)
    selected_parameters.to_csv(output_dir / "optuna_selected_parameters_by_outer_fold.csv", index=False)
    ridge_trial_frame.to_csv(output_dir / "ridge_inner_cv_alpha_trials.csv", index=False)
    ridge_parameter_frame.to_csv(output_dir / "ridge_selected_alpha_by_outer_fold.csv", index=False)
    linear_coefficients.to_csv(
        output_dir / "linear_standardized_coefficients_by_outer_fold.csv", index=False
    )
    linear_coefficient_summary.to_csv(
        output_dir / "linear_standardized_coefficient_summary.csv", index=False
    )
    shap_values.to_csv(output_dir / "shap_out_of_fold_values.csv", index=False)
    shap_importance.to_csv(output_dir / "shap_out_of_fold_global_importance.csv", index=False)
    (output_dir / "README.txt").write_text(
        "EXPLORATORY ONLY. Optuna hyperparameters were selected using inner cross-validation within each outer training fold. "
        "Ridge penalties were selected using the same outer-training-only approach. SHAP values explain only outer-fold held-out predictions. "
        "The outcome is a screened Data Axle candidate-location proxy, not source-verified office presence. Do not interpret model contributions "
        "or linear coefficients as causal policy effects.\n",
        encoding="utf-8",
    )
    pd.DataFrame({"feature": feature_columns}).to_csv(
        output_dir / "model_feature_columns.csv", index=False
    )

    print(f"Usable MSAs: {len(usable)}")
    print(metrics.to_string(index=False))
    print("\nOut-of-fold SHAP importance:")
    print(shap_importance.head(10).to_string(index=False))
    print(f"\nOutput: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
