#!/usr/bin/env python3
"""Evaluate a regularized XGBoost model of public Fortune 500 global-HQ counts.

This is the project's defensible first corporate-location model.  The outcome
is Fortune's listed *global* headquarters count by MSA, so every top-100 MSA
has a true zero or a count—not an unobserved office footprint.  It deliberately
does not label offices or branches as regional HQs.  Those require separate
company-source verification before they can augment this outcome.
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
REPO_ROOT = ARTEM.parent
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


def external_output(path: Path) -> Path:
    """Keep model outputs outside the repository so data artifacts stay deliberate."""
    resolved = path.expanduser().resolve()
    try:
        resolved.relative_to(REPO_ROOT)
    except ValueError:
        resolved.mkdir(parents=True, exist_ok=True)
        return resolved
    raise ValueError("Use an output directory outside the repository.")


def load_panel(outcome_path: Path, roster_path: Path, factors_path: Path, year: int) -> pd.DataFrame:
    outcome = pd.read_csv(outcome_path, dtype={"msa_cbsa": str})
    if "fortune500_global_hq_count" not in outcome.columns:
        raise ValueError("Outcome file must include fortune500_global_hq_count.")
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
    missing_features = set(FEATURES) - set(factors.columns)
    if missing_features:
        raise ValueError(f"Factor data missing features: {sorted(missing_features)}")

    panel = roster.merge(
        outcome[["msa", "fortune500_global_hq_count"]], on="msa", how="left", validate="one_to_one"
    ).merge(
        factors[["msa", *FEATURES]], on="msa", how="left", validate="one_to_one"
    )
    panel["fortune500_global_hq_count"] = pd.to_numeric(panel["fortune500_global_hq_count"], errors="coerce")
    if panel["fortune500_global_hq_count"].isna().any():
        raise ValueError("A roster MSA lacks a global-HQ count; this should be a complete zero-or-count outcome.")
    panel["factor_row_available"] = panel[FEATURES].notna().any(axis=1)
    panel["included_in_model"] = panel["factor_row_available"]
    return panel


def fixed_model() -> XGBRegressor:
    """A shallow, strongly regularized count model suitable for <100 MSAs."""
    return XGBRegressor(
        objective="count:poisson",
        eval_metric="poisson-nloglik",
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


def poisson_model(params: dict[str, float | int]) -> XGBRegressor:
    return XGBRegressor(
        objective="count:poisson",
        eval_metric="poisson-nloglik",
        max_delta_step=1.0,
        random_state=SEED,
        n_jobs=1,
        **params,
    )


def fit_predict(train: pd.DataFrame, test: pd.DataFrame, model: XGBRegressor) -> tuple[np.ndarray, np.ndarray]:
    imputer = SimpleImputer(strategy="median", keep_empty_features=True)
    x_train = imputer.fit_transform(train[FEATURES])
    x_test = imputer.transform(test[FEATURES])
    model.fit(x_train, train["fortune500_global_hq_count"].to_numpy())
    return np.maximum(model.predict(x_test), 0), x_test


def tune_outer_fold(train: pd.DataFrame, fold: int, trials: int) -> tuple[dict[str, float | int], pd.DataFrame]:
    import optuna

    y = train["fortune500_global_hq_count"].to_numpy()
    inner = StratifiedKFold(n_splits=3, shuffle=True, random_state=SEED + fold)

    def objective(trial) -> float:
        params = trial_params(trial)
        errors = []
        for train_index, validation_index in inner.split(train, y > 0):
            prediction, _ = fit_predict(
                train.iloc[train_index], train.iloc[validation_index], poisson_model(params)
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


def metrics(predictions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for model_name, group in predictions.groupby("model", sort=False):
        actual = group["actual_global_hq_count"].to_numpy()
        predicted = group["predicted_global_hq_count"].to_numpy()
        rows.append(
            {
                "model": model_name,
                "held_out_msas": len(group),
                "mae_global_hq_count": mean_absolute_error(actual, predicted),
                "rmse_global_hq_count": mean_squared_error(actual, predicted) ** 0.5,
                "held_out_r2": r2_score(actual, predicted),
                "outcome_definition": "Fortune 2025 listed global headquarters count by MSA; not regional HQs.",
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
    args = parser.parse_args()
    if args.optuna_trials < 10:
        raise ValueError("Use at least 10 Optuna trials for the nested comparison.")
    for path in [args.outcome_csv, args.roster_csv, args.factors_csv]:
        if not path.expanduser().is_file():
            raise FileNotFoundError(path)
    output = external_output(args.output_dir)

    panel = load_panel(args.outcome_csv, args.roster_csv, args.factors_csv, args.factor_year)
    panel.to_csv(output / "fortune500_global_hq_model_input_audit.csv", index=False, quoting=csv.QUOTE_MINIMAL)
    usable = panel[panel["included_in_model"]].copy().reset_index(drop=True)
    if len(usable) < 50:
        raise ValueError(f"Need at least 50 MSAs with factors; found {len(usable)}.")

    import optuna

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    target = usable["fortune500_global_hq_count"].to_numpy()
    outer = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    prediction_rows: list[dict[str, object]] = []
    parameter_rows: list[dict[str, object]] = []
    trial_rows: list[pd.DataFrame] = []
    importance_rows: list[dict[str, object]] = []

    for fold, (train_index, test_index) in enumerate(outer.split(usable, target > 0), start=1):
        train, test = usable.iloc[train_index], usable.iloc[test_index]
        best_params, trial_frame = tune_outer_fold(train, fold, args.optuna_trials)
        parameter_rows.append({"outer_fold": fold, **best_params})
        trial_rows.append(trial_frame)

        fixed_prediction, fixed_x_test = fit_predict(train, test, fixed_model())
        tuned_prediction, _ = fit_predict(train, test, poisson_model(best_params))
        mean_prediction = np.full(len(test), train["fortune500_global_hq_count"].mean())
        for row_number, (_, row) in enumerate(test.iterrows()):
            for model_name, prediction in [
                ("fixed_regularized_poisson_xgboost", fixed_prediction[row_number]),
                ("nested_optuna_poisson_xgboost", tuned_prediction[row_number]),
                ("training_mean_baseline", mean_prediction[row_number]),
            ]:
                prediction_rows.append(
                    {
                        "outer_fold": fold,
                        "model": model_name,
                        "msa": row["msa"],
                        "msa_title": row["msa_title"],
                        "actual_global_hq_count": row["fortune500_global_hq_count"],
                        "predicted_global_hq_count": float(prediction),
                    }
                )

        base_mae = mean_absolute_error(test["fortune500_global_hq_count"], fixed_prediction)
        rng = np.random.default_rng(SEED + fold)
        for feature_index, feature in enumerate(FEATURES):
            for repeat in range(30):
                shuffled = fixed_x_test.copy()
                shuffled[:, feature_index] = rng.permutation(shuffled[:, feature_index])
                permuted = np.maximum(fixed_model().fit(
                    SimpleImputer(strategy="median", keep_empty_features=True).fit_transform(train[FEATURES]),
                    train["fortune500_global_hq_count"].to_numpy(),
                ).predict(shuffled), 0)
                importance_rows.append(
                    {
                        "outer_fold": fold,
                        "feature": feature,
                        "repeat": repeat + 1,
                        "held_out_mae_increase": mean_absolute_error(test["fortune500_global_hq_count"], permuted) - base_mae,
                    }
                )

    predictions = pd.DataFrame(prediction_rows)
    metric_frame = metrics(predictions)
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
    importance["interpretation"] = "Held-out association with Fortune 500 global-HQ count; not causal and not a regional-HQ result."

    predictions.to_csv(output / "fortune500_global_hq_xgb_outer_fold_predictions.csv", index=False)
    metric_frame.to_csv(output / "fortune500_global_hq_xgb_metrics.csv", index=False)
    importance.to_csv(output / "fortune500_global_hq_xgb_permutation_importance.csv", index=False)
    pd.DataFrame(parameter_rows).to_csv(output / "fortune500_global_hq_xgb_optuna_parameters.csv", index=False)
    pd.concat(trial_rows, ignore_index=True).to_csv(output / "fortune500_global_hq_xgb_optuna_trials.csv", index=False)
    print(f"Usable top-100 MSAs: {len(usable):,}")
    print(metric_frame.to_string(index=False))
    print("\nTop held-out permutation associations:")
    print(importance.head(8).to_string(index=False))
    print(f"\nOutput: {output}")


if __name__ == "__main__":
    main()
