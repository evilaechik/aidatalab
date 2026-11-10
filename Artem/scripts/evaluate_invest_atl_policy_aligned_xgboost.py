"""Compare a full metro-context XGBoost model with an Invest Atlanta-aligned screen.

This is intentionally a *predictive screen*, not an incentive-effect model.
Invest Atlanta's programs apply only in Atlanta, so they cannot be added as a
varying feature to a cross-metro model.  Instead, the program inventory is
used to pre-specify a smaller set of metro measures that are plausibly related
to an existing City tool: business density, job and wage outcomes, and target
industry structure.  The script tests whether that narrower set preserves
held-out accuracy relative to the full public-context model.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from xgboost import XGBRegressor


ARTEM = Path(__file__).resolve().parents[1]
SOURCE = ARTEM / "data" / "business_entry_models" / "external_qcew_factors" / "external_factor_model_panel.csv"
OUT = ARTEM / "data" / "business_entry_models" / "invest_atl_policy_screen"
TEST_YEARS = range(2020, 2024)

FEATURE_SETS = {
    "all_public_context": [
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
    ],
    "invest_atlanta_aligned_screen": [
        # Existing-program alignment: business financing/site support,
        # job-quality and workforce support, Industrial Revenue Bonds, and
        # the New and Emerging Technology Business Tax Waiver.
        "establishments_per_100_jobs",
        "qcew_employment_growth",
        "avg_weekly_wage",
        "share_manufacturing",
        "share_information",
        "share_professional",
    ],
}


def predict(train: pd.DataFrame, test: pd.DataFrame, features: list[str], seed: int) -> np.ndarray:
    """Fit the same conservative XGBoost configuration for every feature set."""
    imputer = SimpleImputer(strategy="median")
    x_train = imputer.fit_transform(train[features])
    x_test = imputer.transform(test[features])
    model = XGBRegressor(
        objective="reg:squarederror",
        n_estimators=300,
        max_depth=2,
        min_child_weight=8,
        learning_rate=0.025,
        subsample=0.80,
        colsample_bytree=0.90,
        reg_lambda=25.0,
        random_state=seed,
        n_jobs=1,
    )
    model.fit(x_train, train["target_entry_rate"] / 100)
    return np.clip(model.predict(x_test), 0, None) * 100


def evaluate(panel: pd.DataFrame, name: str, features: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run expanding-window annual tests and held-out permutation importance."""
    predictions: list[pd.DataFrame] = []
    importance_rows: list[dict[str, object]] = []
    for year in TEST_YEARS:
        train = panel[panel["target_year"] < year].copy()
        test = panel[panel["target_year"] == year].copy()
        forecast = predict(train, test, features, seed=year)
        result = test[["target_year", "msa", "msa_title", "target_entry_rate"]].copy()
        result["feature_set"] = name
        result["predicted_entry_rate"] = forecast
        result["absolute_error_rate_pp"] = abs(forecast - test["target_entry_rate"].to_numpy())
        predictions.append(result)

        base_mae = result["absolute_error_rate_pp"].mean()
        for number, feature in enumerate(features):
            shuffled = test.copy()
            shuffled[feature] = np.random.default_rng(year * 100 + number).permutation(shuffled[feature].to_numpy())
            shuffled_forecast = predict(train, shuffled, features, seed=year)
            shuffled_mae = abs(shuffled_forecast - test["target_entry_rate"].to_numpy()).mean()
            importance_rows.append(
                {
                    "feature_set": name,
                    "feature": feature,
                    "test_year": year,
                    "mae_increase_pp": shuffled_mae - base_mae,
                }
            )
    importance = (
        pd.DataFrame(importance_rows)
        .groupby(["feature_set", "feature"], as_index=False)
        .agg(mae_increase_pp=("mae_increase_pp", "mean"), folds=("test_year", "nunique"))
        .sort_values(["feature_set", "mae_increase_pp"], ascending=[True, False])
    )
    importance["interpretation"] = "Predictive association only; not a causal policy effect or incentive weight."
    return pd.concat(predictions, ignore_index=True), importance


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    panel = pd.read_csv(SOURCE)
    if panel["target_year"].min() > min(TEST_YEARS):
        raise ValueError("The source panel does not contain the required rolling test years.")

    all_predictions: list[pd.DataFrame] = []
    all_importance: list[pd.DataFrame] = []
    for name, features in FEATURE_SETS.items():
        missing = sorted(set(features).difference(panel.columns))
        if missing:
            raise ValueError(f"Missing expected feature columns: {missing}")
        predictions, importance = evaluate(panel, name, features)
        all_predictions.append(predictions)
        all_importance.append(importance)

    predictions = pd.concat(all_predictions, ignore_index=True)
    comparison = (
        predictions.groupby("feature_set", as_index=False)
        .agg(
            held_out_observations=("msa", "size"),
            entry_rate_mae_pp=("absolute_error_rate_pp", "mean"),
        )
        .sort_values("entry_rate_mae_pp")
    )
    importance = pd.concat(all_importance, ignore_index=True)
    predictions.to_csv(OUT / "held_out_predictions.csv", index=False)
    comparison.to_csv(OUT / "model_comparison.csv", index=False)
    importance.to_csv(OUT / "permutation_importance.csv", index=False)
    pd.DataFrame(
        [
            {
                "feature_set": name,
                "features": "; ".join(features),
                "purpose": (
                    "Broad public metro context." if name == "all_public_context"
                    else "Factors linked to existing Invest Atlanta tools; tested separately, not used as an Atlanta-only model input."
                ),
            }
            for name, features in FEATURE_SETS.items()
        ]
    ).to_csv(OUT / "feature_set_definitions.csv", index=False)
    print(f"Panel: {len(panel)} rows, {panel.msa.nunique()} MSAs")
    print(comparison.to_string(index=False))
    print("\nHeld-out permutation importance")
    print(importance.to_string(index=False))


if __name__ == "__main__":
    main()
