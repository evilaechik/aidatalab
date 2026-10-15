#!/usr/bin/env python3
"""Build a public county-panel baseline for Atlanta, Austin, and Charlotte.

The model is descriptive. It estimates associations between county employment
growth and prior-year industry mix, wages, size, metro, and year. It does not
identify the causal effect of incentives, taxes, or individual firm decisions.
"""

from __future__ import annotations

import argparse
import csv
import math
import subprocess
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from openpyxl import load_workbook


ROOT = Path(__file__).resolve().parents[2]
ARTEM_DIR = ROOT / "Artem"
OUTPUT_DIR = ARTEM_DIR / "data" / "peer_metro_regression"
RAW_INPUT_DIR = OUTPUT_DIR / "raw_inputs"
DELINEATION_URL = (
    "https://www2.census.gov/programs-surveys/metro-micro/geographies/"
    "reference-files/2023/delineation-files/list1_2023.xlsx"
)
QCEW_URL = "https://data.bls.gov/cew/data/api/{year}/4/area/{county}.csv"

METROS = {
    "12060": "Atlanta-Sandy Springs-Roswell",
    "12420": "Austin-Round Rock-San Marcos",
    "16740": "Charlotte-Concord-Gastonia",
}
SECTORS = {
    "51": "information",
    "52": "finance_insurance",
    "54": "professional_scientific_technical",
    "31-33": "manufacturing",
    "48-49": "transportation_warehousing",
    "62": "health_care_social_assistance",
}


def download(url: str, destination: Path) -> None:
    if destination.exists() and destination.stat().st_size > 0:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["curl", "--fail", "--location", "--silent", "--show-error", url, "--output", str(destination)],
        check=True,
    )


def metro_counties(delineation_path: Path) -> dict[str, set[str]]:
    sheet = load_workbook(delineation_path, read_only=True, data_only=True).active
    rows = sheet.iter_rows(min_row=3, values_only=True)
    columns = next(rows)
    counties: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        record = dict(zip(columns, row))
        cbsa = str(record["CBSA Code"]).zfill(5)
        if cbsa in METROS:
            counties[METROS[cbsa]].add(
                str(record["FIPS State Code"]).zfill(2)
                + str(record["FIPS County Code"]).zfill(3)
            )
    return counties


def read_qcew_year(year: int, counties: dict[str, set[str]]) -> list[dict]:
    rows: list[dict] = []
    for metro, fips_codes in counties.items():
        for fips in fips_codes:
            raw_file = RAW_INPUT_DIR / "qcew" / f"qcew_{year}_q4_{fips}.csv"
            legacy_file = ARTEM_DIR / "data" / "public_sources" / "qcew" / f"qcew_{year}_q4_{fips}.csv"
            source_file = raw_file if raw_file.exists() else legacy_file
            if not source_file.exists():
                source_file = raw_file
                download(QCEW_URL.format(year=year, county=fips), source_file)
            values: dict[str, dict[str, float]] = {}
            with source_file.open(encoding="utf-8-sig") as file:
                reader = csv.DictReader(file)
                for record in reader:
                    if record["own_code"] != "5" or record["size_code"] != "0":
                        continue
                    industry = record["industry_code"]
                    if industry not in {"10", *SECTORS}:
                        continue
                    values[industry] = {
                        "establishments": float(record["qtrly_estabs"] or 0),
                        "employment": float(record["month3_emplvl"] or 0),
                        "quarterly_wages": float(record["total_qtrly_wages"] or 0),
                        "average_weekly_wage": float(record["avg_wkly_wage"] or 0),
                    }
            total = values.get("10")
            if total is None or total["employment"] <= 0:
                raise ValueError(f"Missing private total for {fips} in {year}")
            row = {
                "metro": metro,
                "county_fips": fips,
                "year": year,
                "private_establishments_q4": total["establishments"],
                "private_employment_q4": total["employment"],
                "private_quarterly_wages_q4": total["quarterly_wages"],
                "average_weekly_wage_q4": total["average_weekly_wage"],
            }
            for code, name in SECTORS.items():
                row[f"share_{name}"] = values.get(code, {"employment": 0})["employment"] / total["employment"]
            rows.append(row)
    return rows


def hc3_ols(data: pd.DataFrame, predictors: list[str], outcome: str) -> tuple[pd.DataFrame, float, int]:
    y = data[outcome].to_numpy(dtype=float)
    x = np.column_stack([np.ones(len(data)), *[data[p].to_numpy(dtype=float) for p in predictors]])
    labels = ["Intercept", *predictors]
    inverse = np.linalg.pinv(x.T @ x)
    beta = inverse @ x.T @ y
    residuals = y - x @ beta
    leverage = np.sum((x @ inverse) * x, axis=1)
    adjusted = residuals / np.maximum(1 - leverage, 1e-8)
    covariance = inverse @ (x.T @ ((adjusted**2)[:, None] * x)) @ inverse
    standard_errors = np.sqrt(np.maximum(np.diag(covariance), 0))
    z_scores = np.divide(beta, standard_errors, out=np.full_like(beta, np.nan), where=standard_errors > 0)
    p_values = np.array([math.erfc(abs(value) / math.sqrt(2)) if np.isfinite(value) else np.nan for value in z_scores])
    total_sum_squares = np.sum((y - y.mean()) ** 2)
    r_squared = 1 - np.sum(residuals**2) / total_sum_squares if total_sum_squares else np.nan
    output = pd.DataFrame(
        {
            "term": labels,
            "coefficient_log_points": beta,
            "hc3_standard_error": standard_errors,
            "z_score": z_scores,
            "approx_normal_p_value": p_values,
        }
    )
    return output, r_squared, len(data) - len(labels)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    delineation_path = RAW_INPUT_DIR / "census_cbsa_county_delineation_2023.xlsx"
    download(DELINEATION_URL, delineation_path)
    counties = metro_counties(delineation_path)
    source_rows = []
    for year in (2023, 2024, 2025):
        source_rows.extend(read_qcew_year(year, counties))

    source = pd.DataFrame(source_rows).sort_values(["metro", "county_fips", "year"])
    source.to_csv(args.output_dir / "county_private_employment_q4_2023_2025.csv", index=False)

    sector_trends = []
    for metro, metro_rows in source.groupby("metro"):
        for _, sector_name in SECTORS.items():
            series = metro_rows.assign(
                sector_employment=metro_rows[f"share_{sector_name}"] * metro_rows["private_employment_q4"]
            ).groupby("year")["sector_employment"].sum()
            sector_trends.append(
                {
                    "metro": metro,
                    "sector": sector_name,
                    "employment_2023_q4": round(series.loc[2023]),
                    "employment_2024_q4": round(series.loc[2024]),
                    "employment_2025_q4": round(series.loc[2025]),
                    "employment_change_2024_2025": round(series.loc[2025] - series.loc[2024]),
                    "employment_change_pct_2024_2025": round((series.loc[2025] / series.loc[2024] - 1) * 100, 2),
                }
            )
    pd.DataFrame(sector_trends).to_csv(args.output_dir / "metro_sector_q4_trends_2023_2025.csv", index=False)

    panel = source.copy()
    group = panel.groupby(["metro", "county_fips"], sort=False)
    panel["lag_private_employment"] = group["private_employment_q4"].shift(1)
    panel["lag_average_weekly_wage"] = group["average_weekly_wage_q4"].shift(1)
    for _, name in SECTORS.items():
        panel[f"lag_share_{name}"] = group[f"share_{name}"].shift(1)
    panel = panel.dropna(subset=["lag_private_employment", "lag_average_weekly_wage"]).copy()
    panel["employment_log_growth"] = np.log(panel["private_employment_q4"] / panel["lag_private_employment"])
    panel["log_lag_private_employment"] = np.log(panel["lag_private_employment"])
    panel["log_lag_average_weekly_wage"] = np.log(panel["lag_average_weekly_wage"])
    panel["austin_metro"] = (panel["metro"] == METROS["12420"]).astype(int)
    panel["charlotte_metro"] = (panel["metro"] == METROS["16740"]).astype(int)
    panel["year_2025"] = (panel["year"] == 2025).astype(int)

    predictors = [
        "log_lag_private_employment",
        "log_lag_average_weekly_wage",
        *[f"lag_share_{name}" for name in SECTORS.values()],
        "austin_metro",
        "charlotte_metro",
        "year_2025",
    ]
    coefficients, r_squared, residual_df = hc3_ols(panel, predictors, "employment_log_growth")
    coefficients.to_csv(args.output_dir / "county_q4_employment_growth_regression.csv", index=False)
    panel.to_csv(args.output_dir / "county_q4_growth_panel_2024_2025.csv", index=False)

    county_counts = source.groupby("metro")["county_fips"].nunique().to_dict()
    summary = f"""# County Q4 employment-growth regression

## Model

**Outcome:** year-over-year log growth in Q4 private employment for a county.

**Observations:** {len(panel)} county-year observations: 45 counties in Atlanta, Austin, and Charlotte, observed for the 2023–24 and 2024–25 changes. County counts are Atlanta {county_counts[METROS['12060']]}, Austin {county_counts[METROS['12420']]}, and Charlotte {county_counts[METROS['16740']]}.

**Predictors:** prior-year Q4 county employment, prior-year average weekly wage, prior-year shares of six industry groups, Austin and Charlotte metro indicators with Atlanta as the reference, and a 2025 year indicator.

**Fit:** R-squared = {r_squared:.3f}; residual degrees of freedom = {residual_df}.

## Interpretation rules

- Coefficients use log points. For small values, multiplying a coefficient by 100 approximates a percentage-point change in annual employment growth.
- Industry-share coefficients estimate association after controlling for the other listed predictors. They are not evidence that changing a county's industry mix would cause the same change in growth.
- Metro indicators absorb many unobserved metro differences. State tax cannot be estimated separately in this model because each metro is located in one state and the tax rate does not vary within a metro.
- Approximate p-values use HC3 heteroskedasticity-robust standard errors and a normal approximation. With only 90 observations and two annual changes, treat them as screening evidence rather than a final causal result.

## Data

The model uses BLS QCEW fourth-quarter county files for 2023, 2024, and 2025 and the Census Bureau's July 2023 metropolitan-area delineation file. It uses private ownership totals and six NAICS-sector employment shares.
"""
    (args.output_dir / "REGRESSION_README.md").write_text(summary)


if __name__ == "__main__":
    main()
