#!/usr/bin/env python3
"""Run an explicitly exploratory XGBoost diagnostic for Fortune 100 exports.

The outcome is the number of distinct Fortune 100 firms with at least one
*Data Axle commercial-location candidate* assigned to an MSA.  It is not the
project's verified-office score: retail stores, kiosks, warehouses, branches,
and offices can all be represented in the export.

This script deliberately refuses to run unless ``--allow-incomplete-proxy`` is
provided.  That safeguard matters because a missing MSA in an export is
unknown coverage, not zero company presence.  Its results are useful only for
data-quality exploration; do not present feature importances as causal or as
the drivers of corporate office location.

Inputs and outputs containing licensed Data Axle-derived values must remain
outside the repository.  The script enforces that output guardrail.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold
from xgboost import XGBRegressor


SCRIPT_PATH = Path(__file__).resolve()
ARTEM_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = ARTEM_ROOT.parent
DEFAULT_ROSTER = ARTEM_ROOT / "data" / "business_entry_models" / "top100_xgboost" / "top_100_msa_roster.csv"
DEFAULT_FACTORS = ARTEM_ROOT / "data" / "business_entry_models" / "external_qcew_factors" / "external_factor_model_panel.csv"

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
DEFAULT_TARGET = "distinct_matched_current_f100_nonexcluded_candidate_companies"
RANDOM_SEED = 20261022


def reject_repo_output(path: Path) -> Path:
    """Keep Data Axle-derived outputs out of version control."""
    resolved = path.expanduser().resolve()
    try:
        resolved.relative_to(REPO_ROOT)
    except ValueError:
        resolved.mkdir(parents=True, exist_ok=True)
        return resolved
    raise ValueError(f"Output directory must be outside the repository: {resolved}")


def standardized_msa(series: pd.Series) -> pd.Series:
    return series.astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5)


def parse_study_states(value: str) -> set[str]:
    states = {item.strip() for item in value.split(",") if item.strip()}
    if not states:
        raise ValueError("--study-states must contain at least one state")
    return states


def msa_is_within_states(member_states: object, study_states: set[str]) -> bool:
    """Keep only MSAs whose full multi-state geography is in the study area."""
    states = {item.strip() for item in str(member_states).split(";") if item.strip()}
    return bool(states) and states.issubset(study_states)


def load_data(
    scores_path: Path,
    roster_path: Path,
    factors_path: Path,
    factor_year: int,
    target_column: str,
) -> pd.DataFrame:
    scores = pd.read_csv(scores_path, dtype={"msa_cbsa": str})
    if target_column not in scores.columns:
        raise ValueError(f"Scores file is missing {target_column!r}")
    scores["msa"] = standardized_msa(scores["msa_cbsa"])
    scores = scores.drop_duplicates("msa", keep="last")

    roster = pd.read_csv(roster_path, dtype={"msa": str})
    roster["msa"] = standardized_msa(roster["msa"])
    if roster["msa"].duplicated().any():
        raise ValueError("Top-100 roster has duplicate MSA codes")

    factors = pd.read_csv(factors_path, dtype={"msa": str})
    factors["msa"] = standardized_msa(factors["msa"])
    factors["year"] = pd.to_numeric(factors["year"], errors="coerce")
    factors = factors[factors["year"].eq(factor_year)].copy()
    if factors["msa"].duplicated().any():
        raise ValueError(f"Factor data has duplicate MSA rows for {factor_year}")
    missing_features = set(FEATURES) - set(factors.columns)
    if missing_features:
        raise ValueError(f"Factor data is missing: {sorted(missing_features)}")

    factors = factors.rename(columns={"year": "factor_year"})
    selected_factor_columns = ["msa", "factor_year", *FEATURES]
    data = roster.merge(
        scores[["msa", target_column]], on="msa", how="left", validate="one_to_one"
    ).merge(
        factors[selected_factor_columns], on="msa", how="left", validate="one_to_one"
    )
    data["score_coverage_status"] = np.where(
        data[target_column].notna(), "candidate_score_available", "unknown_not_zero"
    )
    data["factor_coverage_status"] = np.where(
        data["factor_year"].notna(), "factor_row_available", "factor_row_missing"
    )
    data["included_in_xgboost"] = data[target_column].notna() & data["factor_year"].notna()
    return data


def new_model() -> XGBRegressor:
    """Conservative tree settings for a small, cross-sectional sample."""
    return XGBRegressor(
        objective="reg:squarederror",
        n_estimators=220,
        max_depth=2,
        min_child_weight=6,
        learning_rate=0.025,
        subsample=0.80,
        colsample_bytree=0.85,
        reg_alpha=0.25,
        reg_lambda=25.0,
        random_state=RANDOM_SEED,
        n_jobs=1,
    )


def evaluate_cohort(
    data: pd.DataFrame, cohort: str, target_column: str
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Use held-out folds; feature importance is held-out permutation importance."""
    usable = data.loc[data["included_in_xgboost"]].copy().reset_index(drop=True)
    if len(usable) < 30:
        raise ValueError(f"{cohort} has only {len(usable)} usable MSAs; need at least 30")

    folds = KFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
    target = usable[target_column].astype(float).to_numpy()
    predictions: list[dict[str, object]] = []
    importance_rows: list[dict[str, object]] = []

    for fold, (train_index, test_index) in enumerate(folds.split(usable), start=1):
        train, test = usable.iloc[train_index], usable.iloc[test_index]
        imputer = SimpleImputer(strategy="median", keep_empty_features=True)
        x_train = imputer.fit_transform(train[FEATURES])
        x_test = imputer.transform(test[FEATURES])
        model = new_model()
        model.fit(x_train, np.log1p(target[train_index]))
        predicted = np.maximum(np.expm1(model.predict(x_test)), 0)
        baseline = np.full(len(test), target[train_index].mean())

        for row_number, position in enumerate(test_index):
            row = usable.iloc[position]
            predictions.extend(
                [
                    {
                        "cohort": cohort,
                        "fold": fold,
                        "model": "xgboost_candidate_location_proxy",
                        "msa": row["msa"],
                        "msa_title": row["msa_title"],
                        "actual_candidate_count": target[position],
                        "predicted_candidate_count": predicted[row_number],
                    },
                    {
                        "cohort": cohort,
                        "fold": fold,
                        "model": "training_mean_baseline",
                        "msa": row["msa"],
                        "msa_title": row["msa_title"],
                        "actual_candidate_count": target[position],
                        "predicted_candidate_count": baseline[row_number],
                    },
                ]
            )

        base_mae = mean_absolute_error(target[test_index], predicted)
        rng = np.random.default_rng(RANDOM_SEED + fold)
        for feature_number, feature in enumerate(FEATURES):
            for repeat in range(40):
                shuffled = x_test.copy()
                shuffled[:, feature_number] = rng.permutation(shuffled[:, feature_number])
                permuted = np.maximum(np.expm1(model.predict(shuffled)), 0)
                importance_rows.append(
                    {
                        "cohort": cohort,
                        "fold": fold,
                        "feature": feature,
                        "repeat": repeat + 1,
                        "mae_increase": mean_absolute_error(target[test_index], permuted) - base_mae,
                    }
                )

    prediction_frame = pd.DataFrame(predictions)
    metrics = []
    for model_name, group in prediction_frame.groupby("model", sort=False):
        actual = group["actual_candidate_count"].to_numpy()
        predicted = group["predicted_candidate_count"].to_numpy()
        metrics.append(
            {
                "cohort": cohort,
                "model": model_name,
                "held_out_msas": len(group),
                "mae_candidate_companies": mean_absolute_error(actual, predicted),
                "rmse_candidate_companies": mean_squared_error(actual, predicted) ** 0.5,
                "held_out_r2": r2_score(actual, predicted),
                "target_definition": f"{target_column}; Data Axle candidate evidence, not verified office presence",
            }
        )
    importance = (
        pd.DataFrame(importance_rows)
        .groupby(["cohort", "feature"], as_index=False)
        .agg(
            held_out_mae_increase=("mae_increase", "mean"),
            permutation_std=("mae_increase", "std"),
            folds=("fold", "nunique"),
            permutations=("repeat", "size"),
        )
        .sort_values(["cohort", "held_out_mae_increase"], ascending=[True, False])
    )
    importance["interpretation"] = (
        "Held-out predictive association with incomplete candidate-location coverage; not causal and not office-location evidence."
    )
    return prediction_frame, pd.DataFrame(metrics), importance


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-scores-csv", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--roster-csv", type=Path, default=DEFAULT_ROSTER)
    parser.add_argument("--factors-csv", type=Path, default=DEFAULT_FACTORS)
    parser.add_argument("--factor-year", type=int, default=2022)
    parser.add_argument("--target-column", default=DEFAULT_TARGET)
    parser.add_argument("--all-cohort-name", default="all_roster_msas")
    parser.add_argument(
        "--study-states",
        help="Optional comma-separated state names for a tighter comparator cohort; multi-state MSAs must be fully inside it.",
    )
    parser.add_argument("--study-cohort-name", default="custom_state_subset")
    parser.add_argument("--allow-incomplete-proxy", action="store_true")
    args = parser.parse_args()

    if not args.allow_incomplete_proxy:
        raise ValueError("Refusing to train on an incomplete candidate proxy without --allow-incomplete-proxy")
    for input_path in [args.candidate_scores_csv, args.roster_csv, args.factors_csv]:
        if not input_path.expanduser().is_file():
            raise FileNotFoundError(input_path)
    output_dir = reject_repo_output(args.output_dir)
    data = load_data(
        args.candidate_scores_csv,
        args.roster_csv,
        args.factors_csv,
        args.factor_year,
        args.target_column,
    )
    data.to_csv(output_dir / "fortune100_candidate_xgb_input_audit.csv", index=False, quoting=csv.QUOTE_MINIMAL)

    cohorts = {args.all_cohort_name: data}
    if "panel_south_sunbelt" in data.columns:
        cohorts["south_sunbelt_top100_subset"] = data.loc[data["panel_south_sunbelt"].eq(True)]
    if args.study_states:
        study_states = parse_study_states(args.study_states)
        cohorts[args.study_cohort_name] = data.loc[
            data["member_states"].map(lambda value: msa_is_within_states(value, study_states))
        ]
    results = [evaluate_cohort(frame, name, args.target_column) for name, frame in cohorts.items()]
    pd.concat([result[0] for result in results], ignore_index=True).to_csv(
        output_dir / "fortune100_candidate_xgb_fold_predictions.csv", index=False
    )
    metrics = pd.concat([result[1] for result in results], ignore_index=True)
    metrics.to_csv(output_dir / "fortune100_candidate_xgb_metrics.csv", index=False)
    pd.concat([result[2] for result in results], ignore_index=True).to_csv(
        output_dir / "fortune100_candidate_xgb_permutation_importance.csv", index=False
    )
    study_scope = ""
    if args.study_states:
        study_scope = (
            f" Custom comparator cohort {args.study_cohort_name!r} contains MSAs wholly within: "
            f"{', '.join(sorted(parse_study_states(args.study_states)))}."
        )
    (output_dir / "README.txt").write_text(
        f"EXPLORATORY ONLY. The target is {args.target_column}, a Data Axle candidate-location measure, not a verified Fortune office-presence score. "
        "The source export does not cover every top-100 MSA; absent scores are unknown, not zero. "
        f"Do not use these feature rankings as causal policy drivers.{study_scope}\n",
        encoding="utf-8",
    )
    print("Coverage:")
    print(data.groupby(["score_coverage_status", "factor_coverage_status"]).size().to_string())
    print("\nHeld-out metrics:")
    print(metrics.to_string(index=False))
    print(f"\nOutput: {output_dir}")


if __name__ == "__main__":
    main()
