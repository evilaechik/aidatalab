"""Test external workforce and industry factors without lagged business entry.

The target is next-year Census BDS employer-establishment entry rate.  The
predictors come only from the preceding year's BLS QCEW workforce and industry
data.  In particular, this script excludes lagged BDS entry/exit rates so it
tests factors other than business-entry momentum.
"""

from __future__ import annotations

import csv
from io import BytesIO, StringIO
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from xgboost import XGBRegressor


ARTEM = Path(__file__).resolve().parents[1]
ENTRY_DIR = ARTEM / "data" / "business_entry_models"
TOP100_DIR = ENTRY_DIR / "top100_xgboost"
OUT = ENTRY_DIR / "external_qcew_factors"
RAW_QCEW = ARTEM / "data" / "nine_metro_models" / "raw_qcew_industry_slices"
DELINEATION = ENTRY_DIR / "raw_inputs" / "census_cbsa_delineation_list1_2023.xlsx"
BDS = ENTRY_DIR / "raw_inputs" / "census_bds_2023_msa.csv"
FHFA_HPI = ENTRY_DIR / "raw_inputs" / "fhfa_hpi_master.csv"
BEA_MARPP = ENTRY_DIR / "raw_inputs" / "bea_marpp_msa_2008_2024.csv"

# Inputs end in 2022 because the BDS outcome ends in 2023. The comparable
# public corporate-tax tables begin in 2017, so temporal testing begins in 2020.
INPUT_YEARS = range(2017, 2023)
TEST_YEARS = range(2020, 2024)
INDUSTRIES = {
    "10": "total",
    "1013": "manufacturing",
    "51": "information",
    "52": "finance",
    "54": "professional",
    "62": "health",
    "72": "hospitality",
}
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
URL = "https://data.bls.gov/cew/data/api/{year}/4/industry/{industry}.csv"
FHFA_HPI_URL = "https://www.fhfa.gov/hpi/download/monthly/hpi_master.csv"
BEA_MARPP_URL = "https://apps.bea.gov/regional/zip/MARPP.zip"
TAX_URLS = {
    2017: "https://taxfoundation.org/data/all/state/state-corporate-income-tax-rates-brackets-2017/",
    2018: "https://taxfoundation.org/data/all/state/state-corporate-income-tax-rates-brackets-2018/",
    2019: "https://taxfoundation.org/data/all/state/state-corporate-rates-brackets-2019/",
    2020: "https://taxfoundation.org/data/all/state/state-corporate-income-tax-rates-brackets-2020/",
    2021: "https://taxfoundation.org/data/all/state/state-corporate-tax-rates-2021/",
    2022: "https://taxfoundation.org/data/all/state/state-corporate-income-tax-rates-brackets-2022/",
}
STATE_ALIASES = {
    "Ala": "Alabama", "Alaska": "Alaska", "Ariz": "Arizona", "Ark": "Arkansas", "Calif": "California",
    "Colo": "Colorado", "Conn": "Connecticut", "Del": "Delaware", "Fla": "Florida", "Ga": "Georgia",
    "Hawaii": "Hawaii", "Idaho": "Idaho", "Ill": "Illinois", "Ind": "Indiana", "Iowa": "Iowa",
    "Kans": "Kansas", "Ky": "Kentucky", "La": "Louisiana", "Maine": "Maine", "Md": "Maryland",
    "Mass": "Massachusetts", "Mich": "Michigan", "Minn": "Minnesota", "Miss": "Mississippi", "Mo": "Missouri",
    "Mont": "Montana", "Nebr": "Nebraska", "Nev": "Nevada", "N.H": "New Hampshire", "N.J": "New Jersey",
    "N.M": "New Mexico", "N.Y": "New York", "N.C": "North Carolina", "N.D": "North Dakota", "Ohio": "Ohio",
    "Okla": "Oklahoma", "Ore": "Oregon", "Pa": "Pennsylvania", "R.I": "Rhode Island", "S.C": "South Carolina",
    "S.D": "South Dakota", "Tenn": "Tennessee", "Tex": "Texas", "Utah": "Utah", "Vt": "Vermont",
    "Va": "Virginia", "Wash": "Washington", "W.Va": "West Virginia", "Wis": "Wisconsin", "Wyo": "Wyoming",
    "D.C": "District of Columbia",
}
GROSS_RECEIPTS_STATES = {"Delaware", "Nevada", "Ohio", "Oregon", "Tennessee", "Texas", "Washington"}


def counties() -> pd.DataFrame:
    """Return county-to-MSA membership for the fixed top-100 roster."""
    roster = pd.read_csv(TOP100_DIR / "top_100_msa_roster.csv", dtype={"msa": int})
    delineation = pd.read_excel(DELINEATION, header=2)
    delineation.columns = [str(column).strip() for column in delineation.columns]
    delineation["CBSA Code"] = pd.to_numeric(delineation["CBSA Code"], errors="coerce")
    data = delineation[delineation["CBSA Code"].isin(roster["msa"])].copy()
    data["county_fips"] = data["FIPS State Code"].astype(int).astype(str).str.zfill(2) + data["FIPS County Code"].astype(int).astype(str).str.zfill(3)
    membership = data[["CBSA Code", "Metropolitan Division Code", "county_fips", "County/County Equivalent", "State Name"]].rename(
        columns={
            "CBSA Code": "msa",
            "Metropolitan Division Code": "division_msa",
            "County/County Equivalent": "county",
            "State Name": "state",
        }
    )
    membership["division_msa"] = pd.to_numeric(membership["division_msa"], errors="coerce")
    membership = membership.merge(roster[["msa", "msa_title", "member_states", "panel_south_sunbelt"]], on="msa", how="left")
    if membership.duplicated("county_fips").any():
        raise ValueError("A county cannot belong to more than one top-100 CBSA.")
    return membership


def state_corporate_tax_rates() -> pd.DataFrame:
    """Parse annual top statutory corporate rates from Tax Foundation tables.

    A top statutory rate is not an effective tax rate.  Gross-receipts-tax
    states receive a separate flag because a zero corporate-income-tax rate is
    not equivalent to zero business taxation.
    """
    rows: list[dict[str, object]] = []
    for year, url in TAX_URLS.items():
        html = subprocess.run(
            ["curl", "--fail", "--location", "--silent", "--show-error", url],
            check=True,
            capture_output=True,
        ).stdout.decode("utf-8", errors="replace")
        table = pd.read_html(StringIO(html), flavor="lxml")[0].iloc[:, :2].copy()
        table.columns = ["state_raw", "rate_raw"]
        table["state_raw"] = table["state_raw"].ffill()
        table["state_key"] = (
            table["state_raw"].astype(str).str.replace(r"\s*\([^)]*\)", "", regex=True).str.strip().str.rstrip(".")
        )
        table["state"] = table["state_key"].map(STATE_ALIASES).fillna(table["state_key"])
        table["numeric_rate"] = table["rate_raw"].astype(str).str.extract(r"([0-9]+(?:\.[0-9]+)?)")[0].astype(float)
        rates = table.groupby("state", as_index=False)["numeric_rate"].max().rename(columns={"numeric_rate": "top_corporate_tax_rate"})
        rate_lookup = rates.set_index("state")["top_corporate_tax_rate"].to_dict()
        for state in sorted(set(STATE_ALIASES.values())):
            reported_rate = rate_lookup.get(state, np.nan)
            rows.append(
                {
                    "year": year,
                    "state": state,
                    "top_corporate_tax_rate": 0.0 if pd.isna(reported_rate) else float(reported_rate),
                    "no_corporate_income_tax": pd.isna(reported_rate),
                    "gross_receipts_tax_flag": state in GROSS_RECEIPTS_STATES,
                    "source_url": url,
                }
            )
    output = pd.DataFrame(rows)
    output.to_csv(OUT / "state_corporate_tax_rates_2017_2022.csv", index=False)
    return output


def fetch_public_macro_sources() -> None:
    """Fetch public housing-price and regional-price data only if absent.

    These inputs are intentionally metro-level and dated in the same year as
    the QCEW predictors.  They do not use BDS business-entry information.
    """
    FHFA_HPI.parent.mkdir(parents=True, exist_ok=True)
    if not FHFA_HPI.exists() or FHFA_HPI.stat().st_size < 1_000_000:
        response = subprocess.run(
            ["curl", "--fail", "--location", "--silent", "--show-error", "--max-time", "180", FHFA_HPI_URL],
            check=True,
            capture_output=True,
        ).stdout
        FHFA_HPI.write_bytes(response)
    if not BEA_MARPP.exists() or BEA_MARPP.stat().st_size < 10_000:
        response = subprocess.run(
            ["curl", "--fail", "--location", "--silent", "--show-error", "--max-time", "180", BEA_MARPP_URL],
            check=True,
            capture_output=True,
        ).stdout
        with ZipFile(BytesIO(response)) as archive:
            BEA_MARPP.write_bytes(archive.read("MARPP_MSA_2008_2024.csv"))


def metro_macro_factors() -> pd.DataFrame:
    """Create year-t housing-growth and cost-level predictors at the MSA level.

    The FHFA index is used only as a one-year change, since its index level is
    not a cross-metro dollar price measure.  BEA regional price parity is an
    all-items price-level index (United States = 100), so its level is
    comparable across metros.
    """
    fetch_public_macro_sources()

    hpi = pd.read_csv(FHFA_HPI, low_memory=False)
    hpi = hpi[
        (hpi["hpi_type"] == "traditional")
        & (hpi["hpi_flavor"] == "all-transactions")
        & (hpi["frequency"] == "quarterly")
        & (hpi["level"] == "MSA")
        & (hpi["period"] == 4)
    ].copy()
    hpi["msa"] = pd.to_numeric(hpi["place_id"], errors="coerce")
    hpi = hpi.rename(columns={"yr": "year", "index_nsa": "fhfa_hpi_q4"})
    hpi = hpi[["msa", "year", "fhfa_hpi_q4"]].dropna(subset=["msa"])
    hpi["msa"] = hpi["msa"].astype(int)
    hpi = hpi.sort_values(["msa", "year"])
    hpi["fhfa_hpi_yoy_growth"] = hpi.groupby("msa")["fhfa_hpi_q4"].pct_change(fill_method=None)

    # FHFA reports metropolitan divisions instead of a single MSA index in
    # markets with divisions (including Atlanta).  Aggregate division growth
    # rates to the parent MSA using same-year private-sector QCEW employment
    # weights. This preserves each division's valid year-over-year change.
    county_qcew = pd.read_csv(OUT / "county_qcew_input_rows.csv", low_memory=False)
    division_weights = county_qcew[
        (county_qcew["industry"] == "total") & county_qcew["division_msa"].notna()
    ].groupby(["msa", "year", "division_msa"], as_index=False)["employment"].sum()
    division_weights["division_msa"] = division_weights["division_msa"].astype(int)
    division_hpi = hpi.rename(columns={"msa": "division_msa"}).merge(
        division_weights, on=["division_msa", "year"], how="inner", validate="many_to_many"
    )
    division_hpi["weighted_growth"] = division_hpi["fhfa_hpi_yoy_growth"] * division_hpi["employment"]
    division_hpi = division_hpi.groupby(["msa", "year"], as_index=False).agg(
        weighted_growth=("weighted_growth", "sum"), employment=("employment", "sum")
    )
    division_hpi["fhfa_hpi_yoy_growth"] = division_hpi["weighted_growth"] / division_hpi["employment"]
    division_hpi = division_hpi[["msa", "year", "fhfa_hpi_yoy_growth"]]

    direct_hpi = hpi[["msa", "year", "fhfa_hpi_yoy_growth"]].copy()
    direct_hpi["source_priority"] = 0
    division_hpi["source_priority"] = 1
    hpi = pd.concat([direct_hpi, division_hpi], ignore_index=True)
    hpi = hpi.sort_values(["msa", "year", "source_priority"]).drop_duplicates(["msa", "year"], keep="first")
    hpi = hpi[["msa", "year", "fhfa_hpi_yoy_growth"]]

    rpp = pd.read_csv(BEA_MARPP)
    rpp["msa"] = pd.to_numeric(
        rpp["GeoFIPS"].astype(str).str.strip().str.strip('"'), errors="coerce"
    )
    rpp = rpp[(rpp["LineCode"] == 1) & rpp["msa"].notna()].copy()
    year_columns = [str(year) for year in INPUT_YEARS]
    rpp = rpp.melt(id_vars="msa", value_vars=year_columns, var_name="year", value_name="regional_price_parity")
    rpp["msa"] = rpp["msa"].astype(int)
    rpp["year"] = rpp["year"].astype(int)
    rpp["regional_price_parity"] = pd.to_numeric(rpp["regional_price_parity"], errors="coerce")

    factors = rpp.merge(hpi, on=["msa", "year"], how="outer", validate="one_to_one")
    return factors[factors["year"].isin(INPUT_YEARS)].sort_values(["msa", "year"])


def fetch(pair: tuple[int, str]) -> Path:
    """Reuse prior public QCEW slices and fetch only missing historic slices."""
    year, industry = pair
    RAW_QCEW.mkdir(parents=True, exist_ok=True)
    path = RAW_QCEW / f"qcew_{year}_q4_industry_{industry}.csv"
    if path.exists() and path.stat().st_size > 1_000:
        return path
    url = URL.format(year=year, industry=industry)
    for attempt in range(3):
        try:
            response = subprocess.run(
                ["curl", "--fail", "--location", "--silent", "--show-error", "--max-time", "90", url],
                check=True,
                capture_output=True,
            ).stdout
            if not response.startswith(b'"area_fips"'):
                raise ValueError(f"Unexpected BLS response: {url}")
            path.write_bytes(response)
            return path
        except Exception:
            if attempt == 2:
                raise
            time.sleep(attempt + 1)
    raise RuntimeError("Unreachable")


def qcew_metro_panel(membership: pd.DataFrame, tax_rates: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Aggregate county QCEW inputs to the fixed top-100 metro roster."""
    items = [(year, industry) for year in INPUT_YEARS for industry in INDUSTRIES]
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(fetch, items))

    county_set = set(membership["county_fips"])
    rows: list[dict[str, object]] = []
    for year, industry in items:
        path = RAW_QCEW / f"qcew_{year}_q4_industry_{industry}.csv"
        with path.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                if (
                    row["area_fips"] not in county_set
                    or row["own_code"] != "5"
                    or row["industry_code"] != industry
                    or row["size_code"] != "0"
                ):
                    continue
                rows.append(
                    {
                        "county_fips": row["area_fips"],
                        "year": year,
                        "industry": INDUSTRIES[industry],
                        "disclosure_code": row["disclosure_code"],
                        "employment": float(row["month3_emplvl"]),
                        "average_q4_employment": sum(float(row[f"month{month}_emplvl"]) for month in (1, 2, 3)) / 3,
                        "quarterly_wages": float(row["total_qtrly_wages"]),
                        "establishments": float(row["qtrly_estabs"]),
                    }
                )
    source = pd.DataFrame(rows).merge(membership, on="county_fips", validate="many_to_one")
    source.to_csv(OUT / "county_qcew_input_rows.csv", index=False)

    result: list[dict[str, object]] = []
    coverage_issues: list[dict[str, object]] = []
    for msa, msa_counties in membership.groupby("msa"):
        for year in INPUT_YEARS:
            total = source[(source["msa"] == msa) & (source["year"] == year) & (source["industry"] == "total")]
            if len(total) != len(msa_counties) or total["disclosure_code"].ne("").any():
                # Do not replace missing historical county definitions with
                # zero.  This mainly catches Census 2023 delineation changes
                # (for example, Connecticut planning-region FIPS changes).
                coverage_issues.append(
                    {
                        "msa": msa,
                        "year": year,
                        "expected_counties": len(msa_counties),
                        "available_qcew_totals": len(total),
                        "suppressed_qcew_totals": int(total["disclosure_code"].ne("").sum()),
                        "reason": "historical QCEW county coverage does not match the 2023 MSA delineation",
                    }
                )
                continue
            employment = total["employment"].sum()
            tax = total.merge(tax_rates, on=["year", "state"], how="left", validate="many_to_one")
            if tax["top_corporate_tax_rate"].isna().any():
                raise ValueError(f"Tax source missing a state for MSA {msa}, {year}")
            item = {
                "msa": msa,
                "year": year,
                "qcew_employment": employment,
                "avg_weekly_wage": total["quarterly_wages"].sum() / (13 * total["average_q4_employment"].sum()),
                "establishments_per_100_jobs": 100 * total["establishments"].sum() / employment,
                "employment_weighted_corporate_tax_rate": np.average(tax["top_corporate_tax_rate"], weights=tax["employment"]),
                "employment_share_in_gross_receipts_tax_states": np.average(tax["gross_receipts_tax_flag"].astype(float), weights=tax["employment"]),
            }
            for industry in INDUSTRIES.values():
                if industry == "total":
                    continue
                sector = source[(source["msa"] == msa) & (source["year"] == year) & (source["industry"] == industry)]
                item[f"share_{industry}"] = np.nan if sector["disclosure_code"].ne("").any() else sector["employment"].sum() / employment
            result.append(item)
    panel = pd.DataFrame(result).sort_values(["msa", "year"])
    panel["qcew_employment_growth"] = panel.groupby("msa")["qcew_employment"].pct_change(fill_method=None)
    panel["log_qcew_employment"] = np.log1p(panel["qcew_employment"])
    return panel, pd.DataFrame(coverage_issues)


def attach_outcome(qcew: pd.DataFrame, roster: pd.DataFrame) -> pd.DataFrame:
    """Merge QCEW year t factors to BDS entry outcome at t+1."""
    bds = pd.read_csv(BDS, usecols=["year", "msa", "estabs", "estabs_entry"], low_memory=False)
    bds = bds[bds["msa"].isin(roster["msa"])].copy()
    bds["estabs"] = pd.to_numeric(bds["estabs"], errors="coerce")
    bds["estabs_entry"] = pd.to_numeric(bds["estabs_entry"], errors="coerce")
    bds = bds.sort_values(["msa", "year"])
    bds["prior_estabs"] = bds.groupby("msa")["estabs"].shift(1)
    bds["target_entry_rate"] = 100 * bds["estabs_entry"] / bds["prior_estabs"]
    outcome = bds[["msa", "year", "estabs_entry", "prior_estabs", "target_entry_rate"]].rename(columns={"year": "target_year"})
    qcew = qcew.copy()
    qcew["target_year"] = qcew["year"] + 1
    panel = qcew.merge(outcome, on=["msa", "target_year"], how="inner", validate="one_to_one")
    panel = panel.merge(roster[["msa", "msa_title", "member_states", "panel_south_sunbelt"]], on="msa", how="left")
    return panel.dropna(subset=["target_entry_rate", "prior_estabs"]).copy()


def xgb_predictions(train: pd.DataFrame, test: pd.DataFrame, seed: int) -> np.ndarray:
    imputer = SimpleImputer(strategy="median")
    x_train = imputer.fit_transform(train[FEATURES])
    x_test = imputer.transform(test[FEATURES])
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


def evaluate(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    predictions: list[pd.DataFrame] = []
    importance_rows: list[dict[str, object]] = []
    for year in TEST_YEARS:
        train = panel[panel["target_year"] < year].copy()
        test = panel[panel["target_year"] == year].copy()
        xgb = xgb_predictions(train, test, seed=year)
        baseline = np.full(len(test), train["target_entry_rate"].mean())
        for model, predicted in {"xgboost_external_factors": xgb, "historical_mean_rate_baseline": baseline}.items():
            result = test[["target_year", "msa", "msa_title", "target_entry_rate", "estabs_entry", "prior_estabs"]].copy()
            result["model"] = model
            result["predicted_entry_rate"] = predicted
            result["predicted_entries"] = predicted / 100 * result["prior_estabs"]
            result["absolute_error_rate_pp"] = abs(result["predicted_entry_rate"] - result["target_entry_rate"])
            predictions.append(result)

        base_mae = np.mean(abs(xgb - test["target_entry_rate"].to_numpy()))
        for number, feature in enumerate(FEATURES):
            shuffled = test.copy()
            shuffled[feature] = np.random.default_rng(year * 100 + number).permutation(shuffled[feature].to_numpy())
            changed = xgb_predictions(train, shuffled, seed=year)
            importance_rows.append(
                {
                    "feature": feature,
                    "test_year": year,
                    "mae_increase_pp": np.mean(abs(changed - test["target_entry_rate"].to_numpy())) - base_mae,
                }
            )
    predictions_df = pd.concat(predictions, ignore_index=True)
    comparison = (
        predictions_df.groupby("model", as_index=False)
        .agg(held_out_observations=("msa", "size"), entry_rate_mae_pp=("absolute_error_rate_pp", "mean"))
        .sort_values("entry_rate_mae_pp")
    )
    importance = (
        pd.DataFrame(importance_rows)
        .groupby("feature", as_index=False)
        .agg(mae_increase_pp=("mae_increase_pp", "mean"), folds=("test_year", "nunique"))
        .sort_values("mae_increase_pp", ascending=False)
    )
    importance["interpretation"] = "Predictive association only; not a causal policy effect."
    return predictions_df, comparison, importance


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    membership = counties()
    membership.to_csv(OUT / "top_100_msa_counties.csv", index=False)
    roster = pd.read_csv(TOP100_DIR / "top_100_msa_roster.csv")
    tax_rates = state_corporate_tax_rates()
    qcew, coverage_issues = qcew_metro_panel(membership, tax_rates)
    macro = metro_macro_factors()
    macro = macro[macro["msa"].isin(roster["msa"])].copy()
    macro.to_csv(OUT / "metro_macro_factors.csv", index=False)
    macro_coverage = (
        macro.groupby("year", as_index=False)[["regional_price_parity", "fhfa_hpi_yoy_growth"]]
        .count()
        .rename(columns={"regional_price_parity": "rpp_available_msas", "fhfa_hpi_yoy_growth": "hpi_growth_available_msas"})
    )
    macro_coverage.to_csv(OUT / "macro_feature_coverage.csv", index=False)
    qcew = qcew.merge(macro, on=["msa", "year"], how="left", validate="one_to_one")
    qcew.to_csv(OUT / "top_100_msa_qcew_inputs.csv", index=False)
    coverage_issues.to_csv(OUT / "qcew_coverage_issues.csv", index=False)
    panel = attach_outcome(qcew, roster)
    panel.to_csv(OUT / "external_factor_model_panel.csv", index=False)
    predictions, comparison, importance = evaluate(panel)
    predictions.to_csv(OUT / "external_factor_held_out_predictions.csv", index=False)
    comparison.to_csv(OUT / "external_factor_model_comparison.csv", index=False)
    importance.to_csv(OUT / "external_factor_permutation_importance.csv", index=False)
    print(f"Model panel: {len(panel):,} rows, {panel['msa'].nunique()} MSAs, target years {panel.target_year.min()}–{panel.target_year.max()}")
    print(comparison.to_string(index=False))
    print(importance.to_string(index=False))


if __name__ == "__main__":
    main()
