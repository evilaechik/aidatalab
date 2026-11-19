#!/usr/bin/env python3
"""Evaluate a regularized XGBoost model of a supplied Fortune location outcome.

The default target is Fortune's listed *global* headquarters count by MSA,
which has a complete zero-or-count universe.  A caller may instead supply a
clearly named sensitivity outcome, such as documented regional/divisional HQ
evidence.  The outcome definition travels into every result file so an
incomplete regional component cannot be misrepresented as a full office census.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import StratifiedKFold
from xgboost import XGBRegressor


SCRIPT = Path(__file__).resolve()
ARTEM = SCRIPT.parents[1]
DEFAULT_OUTCOME = ARTEM / "data" / "big_business_presence" / "fortune500_global_hq_msa_outcome_2025.csv"
DEFAULT_ROSTER = ARTEM / "data" / "business_entry_models" / "top100_xgboost" / "top_100_msa_roster.csv"
DEFAULT_FACTORS = ARTEM / "data" / "business_entry_models" / "external_qcew_factors" / "external_factor_model_panel.csv"

FEATURES = [
    "log_qcew_employment",
    "qcew_employment_growth",
    "avg_weekly_wage",
    "establishments_per_100_jobs",
    "share_manufacturing",
    "share_information",
    "share_finance",
    "share_professional",
    "share_health",
    "share_hospitality",
    "employment_weighted_corporate_tax_rate",
    "employment_share_in_gross_receipts_tax_states",
    "regional_price_parity",
    "fhfa_hpi_yoy_growth",
]
SEED = 20261106


def msa_code(value: object) -> str:
    return str(value).replace(".0", "").zfill(5)


def prepare_output(path: Path) -> Path:
    """Create the requested output directory, including a repository data folder."""
    resolved = path.expanduser().resolve()
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def load_panel(
    outcome_path: Path, roster_path: Path, factors_path: Path, year: int, target_column: str, features: list[str]
) -> pd.DataFrame:
    outcome = pd.read_csv(outcome_path, dtype={"msa_cbsa": str})
    if target_column not in outcome.columns:
        raise ValueError(f"Outcome file must include {target_column!r}.")
    outcome["msa"] = outcome["msa_cbsa"].map(msa_code)
    if outcome["msa"].duplicated().any():
        raise ValueError("HQ outcome has duplicate MSAs.")

    roster = pd.read_csv(roster_path, dtype={"msa": str})
    roster["msa"] = roster["msa"].map(msa_code)
    if roster["msa"].duplicated().any():
        raise ValueError("Model roster has duplicate MSAs.")

    factors = pd.read_csv(factors_path, dtype={"msa": str})
    factors["msa"] = factors["msa"].map(msa_code)
    factors = factors[pd.to_numeric(factors["year"], errors="coerce").eq(year)].copy()
    if factors["msa"].duplicated().any():
        raise ValueError(f"Factor data has duplicate MSA rows for {year}.")
    missing_features = set(features) - set(factors.columns)
    if missing_features:
        raise ValueError(f"Factor data missing features: {sorted(missing_features)}")

    panel = roster.merge(
        outcome[["msa", target_column]], on="msa", how="left", validate="one_to_one"
    ).merge(
        factors[["msa", *features]], on="msa", how="left", validate="one_to_one"
    )
    panel[target_column] = pd.to_numeric(panel[target_column], errors="coerce")
    panel["outcome_row_available"] = panel[target_column].notna()
    panel["factor_row_available"] = panel[features].notna().any(axis=1)
    panel["included_in_model"] = panel["factor_row_available"] & panel["outcome_row_available"]
    return panel


def fixed_model(objective: str) -> XGBRegressor:
    """A shallow, strongly regularized model suitable for fewer than 100 MSAs."""
    return XGBRegressor(
        objective=objective,
        eval_metric="poisson-nloglik" if objective == "count:poisson" else "rmse",
        n_estimators=180,
        max_depth=2,
        min_child_weight=6,
        learning_rate=0.03,
        subsample=0.80,
        colsample_bytree=0.80,
        reg_alpha=0.35,
        reg_lambda=35.0,
        max_delta_step=1.0,
        random_state=SEED,
        n_jobs=1,
    )


def trial_params(trial) -> dict[str, float | int]:
    return {
        "n_estimators": trial.suggest_int("n_estimators", 75, 300, step=25),
        "max_depth": trial.suggest_int("max_depth", 1, 3),
        "min_child_weight": trial.suggest_int("min_child_weight", 3, 12),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.08, log=True),
        "subsample": trial.suggest_float("subsample", 0.65, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.65, 1.0),
        "reg_alpha": trial.suggest_float("reg_alpha", 0.01, 5.0, log=True),
        "reg_lambda": trial.suggest_float("reg_lambda", 5.0, 100.0, log=True),
    }


def model_with_params(params: dict[str, float | int], objective: str) -> XGBRegressor:
    return XGBRegressor(
        objective=objective,
        eval_metric="poisson-nloglik" if objective == "count:poisson" else "rmse",
        max_delta_step=1.0,
        random_state=SEED,
        n_jobs=1,
        **params,
    )


def fit_predict(
    train: pd.DataFrame,
    test: pd.DataFrame,
    target_column: str,
    features: list[str],
    target_transform: str,
    model: XGBRegressor,
) -> tuple[np.ndarray, np.ndarray]:
    imputer = SimpleImputer(strategy="median", keep_empty_features=True)
    x_train = imputer.fit_transform(train[features])
    x_test = imputer.transform(test[features])
    y_train = train[target_column].to_numpy()
    if target_transform == "log1p":
        y_train = np.log1p(y_train)
    model.fit(x_train, y_train)
    prediction = model.predict(x_test)
    if target_transform == "log1p":
        prediction = np.expm1(prediction)
    return np.maximum(prediction, 0), x_test


def tune_outer_fold(
    train: pd.DataFrame,
    target_column: str,
    features: list[str],
    objective_name: str,
    target_transform: str,
    fold: int,
    trials: int,
) -> tuple[dict[str, float | int], pd.DataFrame]:
    import optuna

    y = train[target_column].to_numpy()
    inner = StratifiedKFold(n_splits=3, shuffle=True, random_state=SEED + fold)

    def objective(trial) -> float:
        params = trial_params(trial)
        errors = []
        for train_index, validation_index in inner.split(train, y > 0):
            prediction, _ = fit_predict(
                train.iloc[train_index], train.iloc[validation_index], target_column, features,
                target_transform, model_with_params(params, objective_name)
            )
            errors.append(
                mean_absolute_error(y[validation_index], prediction)
            )
        return float(np.mean(errors))

    study = optuna.create_study(
        direction="minimize",
        sampler=optuna.samplers.TPESampler(seed=SEED + fold),
    )
    study.optimize(objective, n_trials=trials, show_progress_bar=False)
    trial_frame = pd.DataFrame(
        [
            {"outer_fold": fold, "trial": trial.number, "inner_cv_mae": trial.value, **trial.params}
            for trial in study.trials
            if trial.value is not None
        ]
    )
    return study.best_params, trial_frame


def metrics(predictions: pd.DataFrame, outcome_definition: str) -> pd.DataFrame:
    rows = []
    for model_name, group in predictions.groupby("model", sort=False):
        actual = group["actual_outcome_count"].to_numpy()
        predicted = group["predicted_outcome_count"].to_numpy()
        rows.append(
            {
                "model": model_name,
                "held_out_msas": len(group),
                "mae_outcome": mean_absolute_error(actual, predicted),
                "rmse_outcome": mean_squared_error(actual, predicted) ** 0.5,
                "held_out_r2": r2_score(actual, predicted),
                "outcome_definition": outcome_definition,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--outcome-csv", type=Path, default=DEFAULT_OUTCOME)
    parser.add_argument("--roster-csv", type=Path, default=DEFAULT_ROSTER)
    parser.add_argument("--factors-csv", type=Path, default=DEFAULT_FACTORS)
    parser.add_argument("--factor-year", type=int, default=2022)
    parser.add_argument("--optuna-trials", type=int, default=25)
    parser.add_argument("--target-column", default="fortune500_global_hq_count")
    parser.add_argument("--model-objective", choices=["count:poisson", "reg:squarederror"], default="count:poisson")
    parser.add_argument("--target-transform", choices=["identity", "log1p"], default="identity")
    parser.add_argument(
        "--exclude-features", default="",
        help="Comma-separated predictors to omit, for example log_qcew_employment.",
    )
    parser.add_argument(
        "--outcome-description",
        default="Fortune 2025 listed global headquarters count by MSA; not regional HQs.",
    )
    parser.add_argument("--output-prefix", default="fortune500_global_hq_xgb")
    args = parser.parse_args()
    if args.optuna_trials < 10:
        raise ValueError("Use at least 10 Optuna trials for the nested comparison.")
    for path in [args.outcome_csv, args.roster_csv, args.factors_csv]:
        if not path.expanduser().is_file():
            raise FileNotFoundError(path)
    output = prepare_output(args.output_dir)

    excluded_features = {item.strip() for item in args.exclude_features.split(",") if item.strip()}
    unknown_exclusions = excluded_features - set(FEATURES)
    if unknown_exclusions:
        raise ValueError(f"Unknown excluded feature(s): {sorted(unknown_exclusions)}")
    features = [feature for feature in FEATURES if feature not in excluded_features]
    if not features:
        raise ValueError("At least one feature must remain after --exclude-features.")
    panel = load_panel(
        args.outcome_csv, args.roster_csv, args.factors_csv, args.factor_year, args.target_column, features
    )
    panel.to_csv(output / f"{args.output_prefix}_model_input_audit.csv", index=False, quoting=csv.QUOTE_MINIMAL)
    usable = panel[panel["included_in_model"]].copy().reset_index(drop=True)
    if len(usable) < 50:
        raise ValueError(f"Need at least 50 MSAs with factors; found {len(usable)}.")

    import optuna

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    target = usable[args.target_column].to_numpy()
    model_label = "poisson" if args.model_objective == "count:poisson" else "squared_error"
    outer = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    prediction_rows: list[dict[str, object]] = []
    parameter_rows: list[dict[str, object]] = []
    trial_rows: list[pd.DataFrame] = []
    importance_rows: list[dict[str, object]] = []

    for fold, (train_index, test_index) in enumerate(outer.split(usable, target > 0), start=1):
        train, test = usable.iloc[train_index], usable.iloc[test_index]
        best_params, trial_frame = tune_outer_fold(
            train, args.target_column, features, args.model_objective, args.target_transform, fold, args.optuna_trials
        )
        parameter_rows.append({"outer_fold": fold, **best_params})
        trial_rows.append(trial_frame)

        fixed_prediction, fixed_x_test = fit_predict(
            train, test, args.target_column, features, args.target_transform, fixed_model(args.model_objective)
        )
        tuned_prediction, _ = fit_predict(
            train, test, args.target_column, features, args.target_transform,
            model_with_params(best_params, args.model_objective)
        )
        mean_prediction = np.full(len(test), train[args.target_column].mean())
        for row_number, (_, row) in enumerate(test.iterrows()):
            for model_name, prediction in [
                (f"fixed_regularized_{model_label}_xgboost", fixed_prediction[row_number]),
                (f"nested_optuna_{model_label}_xgboost", tuned_prediction[row_number]),
                ("training_mean_baseline", mean_prediction[row_number]),
            ]:
                prediction_rows.append(
                    {
                        "outer_fold": fold,
                        "model": model_name,
                        "msa": row["msa"],
                        "msa_title": row["msa_title"],
                        "actual_outcome_count": row[args.target_column],
                        "predicted_outcome_count": float(prediction),
                    }
                )

        base_mae = mean_absolute_error(test[args.target_column], fixed_prediction)
        rng = np.random.default_rng(SEED + fold)
        for feature_index, feature in enumerate(features):
            for repeat in range(30):
                shuffled = fixed_x_test.copy()
                shuffled[:, feature_index] = rng.permutation(shuffled[:, feature_index])
                permuted_model = fixed_model(args.model_objective)
                x_train = SimpleImputer(strategy="median", keep_empty_features=True).fit_transform(train[features])
                y_train = train[args.target_column].to_numpy()
                if args.target_transform == "log1p":
                    y_train = np.log1p(y_train)
                permuted = permuted_model.fit(x_train, y_train).predict(shuffled)
                if args.target_transform == "log1p":
                    permuted = np.expm1(permuted)
                permuted = np.maximum(permuted, 0)
                importance_rows.append(
                    {
                        "outer_fold": fold,
                        "feature": feature,
                        "repeat": repeat + 1,
                        "held_out_mae_increase": mean_absolute_error(test[args.target_column], permuted) - base_mae,
                    }
                )

    predictions = pd.DataFrame(prediction_rows)
    metric_frame = metrics(predictions, args.outcome_description)
    importance = (
        pd.DataFrame(importance_rows)
        .groupby("feature", as_index=False)
        .agg(
            held_out_mae_increase=("held_out_mae_increase", "mean"),
            permutation_std=("held_out_mae_increase", "std"),
            folds=("outer_fold", "nunique"),
            permutations=("repeat", "size"),
        )
        .sort_values("held_out_mae_increase", ascending=False)
    )
    importance["interpretation"] = (
        "Held-out association with the supplied Fortune location outcome; not causal. "
        + args.outcome_description
    )

    predictions.to_csv(output / f"{args.output_prefix}_outer_fold_predictions.csv", index=False)
    metric_frame.to_csv(output / f"{args.output_prefix}_metrics.csv", index=False)
    importance.to_csv(output / f"{args.output_prefix}_permutation_importance.csv", index=False)
    pd.DataFrame(parameter_rows).to_csv(output / f"{args.output_prefix}_optuna_parameters.csv", index=False)
    pd.concat(trial_rows, ignore_index=True).to_csv(output / f"{args.output_prefix}_optuna_trials.csv", index=False)
    print(f"Usable top-100 MSAs: {len(usable):,}")
    print(metric_frame.to_string(index=False))
    print("\nTop held-out permutation associations:")
    print(importance.head(8).to_string(index=False))
    print(f"\nOutput: {output}")


if __name__ == "__main__":
    main()
