"""Run time-ordered XGBoost entry-rate models for two 2023 MSA panels.

Panels:
1. The 100 U.S. metropolitan statistical areas with the most establishments
   in the 2023 Census BDS release.
2. The South/Sun Belt subset of that roster, defined in the accompanying README.

The target is next-year employer-establishment entries divided by prior-year
establishments.  No contemporaneous variables or constructed scores are used.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from xgboost import XGBRegressor


ARTEM_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ARTEM_ROOT / "data" / "business_entry_models" / "raw_inputs"
OUTPUT_DIR = ARTEM_ROOT / "data" / "business_entry_models" / "top100_xgboost"
BDS_PATH = SOURCE_DIR / "census_bds_2023_msa.csv"
DELINEATION_PATH = SOURCE_DIR / "census_cbsa_delineation_list1_2023.xlsx"

# Census South states plus the western Sun Belt states used in this study subset.
# An MSA is included only if every member state is in this set, preventing a
# predominantly non-Sun-Belt multi-state metro from qualifying on one county.
SOUTH_SUNBELT_STATES = {
    "Alabama", "Arizona", "Arkansas", "California", "Colorado", "Delaware",
    "District of Columbia", "Florida", "Georgia", "Kentucky", "Louisiana",
    "Maryland", "Mississippi", "Nevada", "New Mexico", "North Carolina",
    "Oklahoma", "South Carolina", "Tennessee", "Texas", "Utah", "Virginia",
    "West Virginia",
}

NUMERIC_COLUMNS = [
    "firms", "estabs", "emp", "estabs_entry", "estabs_entry_rate",
    "estabs_exit_rate", "job_creation_rate", "job_creation_rate_births",
    "job_destruction_rate", "net_job_creation_rate", "reallocation_rate",
]
FEATURES = [
    "lag_entry_rate", "lag_exit_rate", "lag_job_creation_rate",
    "lag_birth_job_creation_rate", "lag_job_destruction_rate",
    "lag_net_job_creation_rate", "lag_reallocation_rate", "log_lag_estabs",
    "log_lag_emp",
]
TEST_YEARS = range(2018, 2024)


def metro_roster() -> pd.DataFrame:
    """Identify the 100 largest 2023 MSAs and tag the defined study subset."""
    if not BDS_PATH.exists() or not DELINEATION_PATH.exists():
        raise FileNotFoundError("Missing public BDS or Census delineation source file.")

    bds = pd.read_csv(BDS_PATH, usecols=["year", "msa", "estabs"], low_memory=False)
    bds["estabs"] = pd.to_numeric(bds["estabs"], errors="coerce")
    latest = bds[bds["year"].eq(2023)].dropna(subset=["estabs"])

    delineation = pd.read_excel(DELINEATION_PATH, header=2)
    delineation.columns = [str(column).strip() for column in delineation.columns]
    delineation["CBSA Code"] = pd.to_numeric(delineation["CBSA Code"], errors="coerce")
    metros = delineation[
        delineation["Metropolitan/Micropolitan Statistical Area"].eq("Metropolitan Statistical Area")
    ].copy()
    metadata = (
        metros.groupby("CBSA Code", as_index=False)
        .agg(
            msa_title=("CBSA Title", "first"),
            member_states=("State Name", lambda values: "; ".join(sorted(set(values)))),
        )
        .rename(columns={"CBSA Code": "msa"})
    )
    roster = (
        latest.merge(metadata, on="msa", how="inner")
        .nlargest(100, "estabs")
        .sort_values("estabs", ascending=False)
        .reset_index(drop=True)
    )
    roster["panel_all_100"] = True
    roster["panel_south_sunbelt"] = roster["member_states"].apply(
        lambda value: set(value.split("; ")).issubset(SOUTH_SUNBELT_STATES)
    )
    roster["region_definition"] = np.where(
        roster["panel_south_sunbelt"],
        "All member states are in the study's South/Sun Belt state set",
        "Not in the study's South/Sun Belt subset",
    )
    return roster.rename(columns={"estabs": "establishments_2023"})


def build_panel(roster: pd.DataFrame) -> pd.DataFrame:
    """Create a lag-safe, 2011–2023 panel for roster MSAs."""
    bds = pd.read_csv(BDS_PATH, usecols=["year", "msa", *NUMERIC_COLUMNS], low_memory=False)
    data = bds[bds["msa"].isin(roster["msa"])].copy()
    data = data.merge(roster[["msa", "msa_title", "member_states", "panel_south_sunbelt"]], on="msa", how="left")
    for column in NUMERIC_COLUMNS:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    data = data.sort_values(["msa", "year"]).reset_index(drop=True)

    lag_map = {
        "estabs_entry_rate": "lag_entry_rate",
        "estabs_exit_rate": "lag_exit_rate",
        "job_creation_rate": "lag_job_creation_rate",
        "job_creation_rate_births": "lag_birth_job_creation_rate",
        "job_destruction_rate": "lag_job_destruction_rate",
        "net_job_creation_rate": "lag_net_job_creation_rate",
        "reallocation_rate": "lag_reallocation_rate",
        "estabs": "lag_estabs",
        "emp": "lag_emp",
    }
    for source, destination in lag_map.items():
        data[destination] = data.groupby("msa", sort=False)[source].shift(1)
    data["log_lag_estabs"] = np.log1p(data["lag_estabs"])
    data["log_lag_emp"] = np.log1p(data["lag_emp"])
    data["entry_rate_from_count"] = 100 * data["estabs_entry"] / data["lag_estabs"]
    return data[(data["year"] >= 2011) & data["lag_estabs"].gt(0) & data["estabs_entry"].notna()].copy()


def predict_xgboost(train: pd.DataFrame, test: pd.DataFrame, seed: int) -> np.ndarray:
    """Forecast entry rate, then convert forecast to an expected entry count."""
    imputer = SimpleImputer(strategy="median")
    x_train = imputer.fit_transform(train[FEATURES])
    x_test = imputer.transform(test[FEATURES])
    y_rate = train["estabs_entry"].to_numpy() / train["lag_estabs"].to_numpy()
    model = XGBRegressor(
        objective="reg:squarederror",
        n_estimators=350,
        max_depth=2,
        min_child_weight=5,
        learning_rate=0.025,
        subsample=0.80,
        colsample_bytree=0.90,
        reg_lambda=20.0,
        random_state=seed,
        n_jobs=1,
    )
    model.fit(x_train, y_rate)
    return np.clip(model.predict(x_test), 0, None) * test["lag_estabs"].to_numpy()


def evaluate(panel: pd.DataFrame, panel_name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Evaluate XGBoost and a persistence benchmark on future years only."""
    results: list[pd.DataFrame] = []
    for year in TEST_YEARS:
        train = panel[panel["year"] < year].copy()
        test = panel[panel["year"] == year].copy()
        xgb_entries = predict_xgboost(train, test, seed=year)
        baseline_entries = test["lag_entry_rate"].to_numpy() / 100 * test["lag_estabs"].to_numpy()
        for model, predictions in {
            "xgboost_rate": xgb_entries,
            "lagged_entry_rate_baseline": baseline_entries,
        }.items():
            output = test[["year", "msa", "msa_title", "member_states", "estabs_entry", "lag_estabs", "entry_rate_from_count"]].copy()
            output["panel"] = panel_name
            output["model"] = model
            output["predicted_entries"] = predictions
            output["predicted_entry_rate"] = 100 * predictions / output["lag_estabs"]
            output["absolute_error_rate_pp"] = abs(output["predicted_entry_rate"] - output["entry_rate_from_count"])
            output["absolute_error_entries"] = abs(output["predicted_entries"] - output["estabs_entry"])
            results.append(output)
    predictions = pd.concat(results, ignore_index=True)
    summary = (
        predictions.groupby(["panel", "model"], as_index=False)
        .agg(
            held_out_observations=("msa", "size"),
            msas=("msa", "nunique"),
            entry_rate_mae_pp=("absolute_error_rate_pp", "mean"),
            entry_count_mae=("absolute_error_entries", "mean"),
        )
        .sort_values(["panel", "entry_rate_mae_pp"])
        .reset_index(drop=True)
    )
    return predictions, summary


def permutation_importance(panel: pd.DataFrame, panel_name: str) -> pd.DataFrame:
    """Estimate XGBoost's held-out predictive associations, not causal effects."""
    rows: list[dict[str, object]] = []
    for year in TEST_YEARS:
        train = panel[panel["year"] < year].copy()
        test = panel[panel["year"] == year].copy()
        base = predict_xgboost(train, test, seed=year)
        actual = test["entry_rate_from_count"].to_numpy()
        denominator = test["lag_estabs"].to_numpy()
        base_mae = np.mean(abs(100 * base / denominator - actual))
        for feature_number, feature in enumerate(FEATURES):
            shuffled = test.copy()
            shuffled[feature] = np.random.default_rng(year * 100 + feature_number).permutation(shuffled[feature].to_numpy())
            changed = predict_xgboost(train, shuffled, seed=year)
            changed_mae = np.mean(abs(100 * changed / denominator - actual))
            rows.append({
                "panel": panel_name,
                "feature": feature,
                "test_year": year,
                "mae_increase_pp": changed_mae - base_mae,
            })
    result = (
        pd.DataFrame(rows)
        .groupby(["panel", "feature"], as_index=False)
        .agg(mae_increase_pp=("mae_increase_pp", "mean"), folds=("test_year", "nunique"))
        .sort_values(["panel", "mae_increase_pp"], ascending=[True, False])
    )
    result["interpretation"] = "Predictive association only; a larger positive increase means the feature helped held-out forecasts."
    return result


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    roster = metro_roster()
    roster.to_csv(OUTPUT_DIR / "top_100_msa_roster.csv", index=False)
    all_panel = build_panel(roster)
    south_panel = all_panel[all_panel["panel_south_sunbelt"]].copy()
    all_panel.to_csv(OUTPUT_DIR / "top_100_msa_entry_panel.csv", index=False)
    south_panel.to_csv(OUTPUT_DIR / "south_sunbelt_msa_entry_panel.csv", index=False)

    all_predictions, all_summary = evaluate(all_panel, "all_100_largest_msas")
    south_predictions, south_summary = evaluate(south_panel, "south_sunbelt_subset")
    pd.concat([all_predictions, south_predictions], ignore_index=True).to_csv(
        OUTPUT_DIR / "xgboost_held_out_predictions.csv", index=False
    )
    pd.concat([all_summary, south_summary], ignore_index=True).to_csv(
        OUTPUT_DIR / "xgboost_model_comparison.csv", index=False
    )
    pd.concat(
        [
            permutation_importance(all_panel, "all_100_largest_msas"),
            permutation_importance(south_panel, "south_sunbelt_subset"),
        ],
        ignore_index=True,
    ).to_csv(OUTPUT_DIR / "xgboost_permutation_importance.csv", index=False)

    print(f"All-MSA panel: {len(all_panel):,} rows across {all_panel['msa'].nunique()} MSAs")
    print(f"South/Sun Belt panel: {len(south_panel):,} rows across {south_panel['msa'].nunique()} MSAs")
    print(pd.concat([all_summary, south_summary], ignore_index=True).to_string(index=False))


if __name__ == "__main__":
    main()
