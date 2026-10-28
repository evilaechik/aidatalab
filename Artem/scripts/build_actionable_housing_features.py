#!/usr/bin/env python3
"""Build public housing-pipeline features for a selected MSA roster.

The Census Building Permits Survey (BPS) records privately owned residential
units authorized by permits.  It is a housing-supply pipeline proxy, not a
direct measure of office inventory, permit-processing speed, or a city policy.
It is still useful for Invest Atlanta because housing development conditions
affect the ability of employers to recruit and retain workers.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd


ARTEM = Path(__file__).resolve().parents[1]
DEFAULT_ROSTER = ARTEM / "data" / "map_green_state_100" / "msa_roster.csv"
DEFAULT_RAW_DIR = ARTEM / "data" / "map_green_state_100" / "raw_inputs"
DEFAULT_OUTPUT = ARTEM / "data" / "map_green_state_100" / "actionable_housing_features_2024.csv"


def bps_url(year: int) -> str:
    return f"https://www.census.gov/construction/bps/xls/cbsaannual_{year}99.xls"


def fetch_bps(year: int, raw_dir: Path) -> Path:
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / f"cbsaannual_{year}99.xls"
    if path.exists() and path.stat().st_size > 10_000:
        return path
    result = subprocess.run(
        ["curl", "--fail", "--location", "--silent", "--show-error", bps_url(year)],
        check=True,
        capture_output=True,
    )
    path.write_bytes(result.stdout)
    return path


def units_sheet(path: Path) -> pd.DataFrame:
    workbook = pd.ExcelFile(path)
    sheet = next((name for name in workbook.sheet_names if "Units" in name), None)
    if sheet is None:
        raise ValueError(f"No BPS units sheet found in {path}")
    data = pd.read_excel(path, sheet_name=sheet, header=5)
    data.columns = [str(column).strip() for column in data.columns]
    required = {"CBSA", "Name", "Total", "1 Unit", "2 Units", "3 and 4 Units", "5 Units or More"}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"BPS units sheet is missing columns: {sorted(missing)}")
    data["msa"] = pd.to_numeric(data["CBSA"], errors="coerce")
    data = data.dropna(subset=["msa"]).copy()
    data["msa"] = data["msa"].astype(int).astype(str).str.zfill(5)
    for column in ["Total", "1 Unit", "2 Units", "3 and 4 Units", "5 Units or More"]:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int, default=2024)
    parser.add_argument("--roster-csv", type=Path, default=DEFAULT_ROSTER)
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--factors-csv",
        type=Path,
        help="Optional public factor panel; adds a BPS-units-per-2022-QCEW-job intensity column.",
    )
    args = parser.parse_args()
    if not args.roster_csv.exists():
        raise FileNotFoundError(args.roster_csv)
    if args.year < 2019:
        raise ValueError("This helper supports the current BPS annual CBSA workbook format from 2019 onward")

    roster = pd.read_csv(args.roster_csv, dtype={"msa": str})
    roster["msa"] = roster["msa"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5)
    source_path = fetch_bps(args.year, args.raw_dir)
    bps = units_sheet(source_path)
    year_suffix = str(args.year)
    features = bps.rename(
        columns={
            "Name": "bps_cbsa_name",
            "Total": f"bps_total_units_authorized_{year_suffix}",
            "1 Unit": f"bps_single_family_units_{year_suffix}",
            "2 Units": f"bps_two_unit_buildings_{year_suffix}",
            "3 and 4 Units": f"bps_three_four_unit_buildings_{year_suffix}",
            "5 Units or More": f"bps_large_multifamily_units_{year_suffix}",
        }
    )[
        [
            "msa",
            "bps_cbsa_name",
            f"bps_total_units_authorized_{year_suffix}",
            f"bps_single_family_units_{year_suffix}",
            f"bps_two_unit_buildings_{year_suffix}",
            f"bps_three_four_unit_buildings_{year_suffix}",
            f"bps_large_multifamily_units_{year_suffix}",
        ]
    ]
    total = features[f"bps_total_units_authorized_{year_suffix}"]
    features[f"bps_multifamily_unit_share_{year_suffix}"] = np.where(
        total.gt(0),
        (
            features[f"bps_two_unit_buildings_{year_suffix}"]
            + features[f"bps_three_four_unit_buildings_{year_suffix}"]
            + features[f"bps_large_multifamily_units_{year_suffix}"]
        )
        / total,
        np.nan,
    )
    features[f"log_bps_total_units_authorized_{year_suffix}"] = np.log1p(total)
    output = roster.merge(features, on="msa", how="left", validate="one_to_one")

    if args.factors_csv:
        if not args.factors_csv.exists():
            raise FileNotFoundError(args.factors_csv)
        factor = pd.read_csv(args.factors_csv, dtype={"msa": str})
        factor["msa"] = factor["msa"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5)
        factor = factor[pd.to_numeric(factor["year"], errors="coerce").eq(2022)].copy()
        factor = factor[["msa", "qcew_employment"]].drop_duplicates("msa")
        output = output.merge(factor, on="msa", how="left", validate="one_to_one")
        output[f"bps_units_per_1000_qcew_jobs_{year_suffix}"] = (
            1000 * output[f"bps_total_units_authorized_{year_suffix}"] / output["qcew_employment"]
        )
        output = output.drop(columns=["qcew_employment"])

    output["bps_source_url"] = bps_url(args.year)
    output["feature_caveat"] = (
        "Residential units authorized by permits; proxy for housing-supply pipeline, not office availability or permit speed"
    )
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output_csv, index=False)
    print(f"Roster MSAs: {len(output)}")
    print(f"BPS matched MSAs: {output[f'bps_total_units_authorized_{year_suffix}'].notna().sum()}")
    print(f"Output: {args.output_csv.resolve()}")


if __name__ == "__main__":
    main()
