#!/usr/bin/env python3
"""Build MSA-level recent-graduate pipeline measures from public IPEDS data.

IPEDS reports completions by postsecondary institution, program and award
level.  This script assigns completions to the MSA containing the reporting
institution, not to where graduates live or ultimately work.  It is therefore
a local talent-supply proxy rather than a count of graduates available to a
specific employer.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pandas as pd


ARTEM = Path(__file__).resolve().parents[1]
DEFAULT_ROSTER = ARTEM / "data" / "map_green_state_100" / "msa_roster.csv"
DEFAULT_RAW_DIR = ARTEM / "data" / "map_green_state_100" / "raw_inputs" / "ipeds_2024"
DEFAULT_OUTPUT = ARTEM / "data" / "map_green_state_100" / "actionable_talent_features_2024.csv"
IPEDS_BASE_URL = "https://nces.ed.gov/ipeds/datacenter/data"
BUSINESS_STEM_CIP2 = {11, 14, 15, 26, 27, 40, 41, 51, 52}
DEGREE_AWARD_LEVELS = {5, 7, 17, 18, 19}


def download_file(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size > 10_000:
        return
    result = subprocess.run(
        ["curl", "--fail", "--location", "--silent", "--show-error", url],
        check=True,
        capture_output=True,
    )
    destination.write_bytes(result.stdout)


def read_zip_csv(path: Path) -> pd.DataFrame:
    with ZipFile(path) as archive:
        csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if len(csv_names) != 1:
            raise ValueError(f"Expected one CSV in {path}, found {csv_names}")
        return pd.read_csv(archive.open(csv_names[0]), encoding="latin1", low_memory=False)


def standardize_msa(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").astype("Int64").astype(str).str.zfill(5)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int, default=2024)
    parser.add_argument("--roster-csv", type=Path, default=DEFAULT_ROSTER)
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--factors-csv",
        type=Path,
        help="Optional public factor panel; adds completions per 1,000 2022 QCEW jobs.",
    )
    args = parser.parse_args()
    if not args.roster_csv.exists():
        raise FileNotFoundError(args.roster_csv)
    if args.year < 2004:
        raise ValueError("IPEDS completion files use this helper's layout from 2004 onward")

    directory = args.raw_dir
    hd_path = directory / f"HD{args.year}.zip"
    completions_path = directory / f"C{args.year}_A.zip"
    download_file(f"{IPEDS_BASE_URL}/HD{args.year}.zip", hd_path)
    download_file(f"{IPEDS_BASE_URL}/C{args.year}_A.zip", completions_path)

    roster = pd.read_csv(args.roster_csv, dtype={"msa": str})
    roster["msa"] = roster["msa"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5)
    institutions = read_zip_csv(hd_path)
    institutions = institutions.rename(columns={institutions.columns[0]: "UNITID"})
    required_hd = {"UNITID", "CBSA", "POSTSEC", "CYACTIVE"}
    if missing := required_hd - set(institutions.columns):
        raise ValueError(f"IPEDS directory file is missing: {sorted(missing)}")
    institutions["msa"] = standardize_msa(institutions["CBSA"])
    institutions = institutions.loc[
        pd.to_numeric(institutions["POSTSEC"], errors="coerce").eq(1)
        & pd.to_numeric(institutions["CYACTIVE"], errors="coerce").eq(1)
        & institutions["msa"].isin(roster["msa"]),
        ["UNITID", "msa"],
    ].drop_duplicates("UNITID")

    completions = read_zip_csv(completions_path)
    completions = completions.rename(columns={completions.columns[0]: "UNITID"})
    required_completions = {"UNITID", "CIPCODE", "AWLEVEL", "CTOTALT"}
    if missing := required_completions - set(completions.columns):
        raise ValueError(f"IPEDS completions file is missing: {sorted(missing)}")
    completions = completions.merge(institutions, on="UNITID", how="inner", validate="many_to_one")
    completions["award_level"] = pd.to_numeric(completions["AWLEVEL"], errors="coerce")
    completions["completions"] = pd.to_numeric(completions["CTOTALT"], errors="coerce").fillna(0)
    completions["cip2"] = pd.to_numeric(completions["CIPCODE"], errors="coerce").floordiv(1).astype("Int64")
    completions["is_degree"] = completions["award_level"].isin(DEGREE_AWARD_LEVELS)
    completions["is_business_stem"] = completions["cip2"].isin(BUSINESS_STEM_CIP2)
    completions["degree_completions"] = completions["completions"].where(
        completions["is_degree"], 0
    )
    completions["business_stem_degree_completions"] = completions["completions"].where(
        completions["is_degree"] & completions["is_business_stem"], 0
    )
    suffix = str(args.year)

    grouped = completions.groupby("msa", as_index=False).agg(
        **{
            f"ipeds_all_completions_{suffix}": ("completions", "sum"),
            f"ipeds_bachelors_plus_completions_{suffix}": ("degree_completions", "sum"),
            f"ipeds_bachelors_plus_business_stem_completions_{suffix}": (
                "business_stem_degree_completions",
                "sum",
            ),
            f"ipeds_reporting_institutions_{suffix}": ("UNITID", "nunique"),
        }
    )
    output = roster.merge(grouped, on="msa", how="left", validate="one_to_one")
    numeric_columns = [column for column in grouped.columns if column != "msa"]
    output[numeric_columns] = output[numeric_columns].fillna(0)

    if args.factors_csv:
        if not args.factors_csv.exists():
            raise FileNotFoundError(args.factors_csv)
        factor = pd.read_csv(args.factors_csv, dtype={"msa": str})
        factor["msa"] = factor["msa"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5)
        factor = factor[pd.to_numeric(factor["year"], errors="coerce").eq(2022)]
        factor = factor[["msa", "qcew_employment"]].drop_duplicates("msa")
        output = output.merge(factor, on="msa", how="left", validate="one_to_one")
        for column in [
            f"ipeds_bachelors_plus_completions_{suffix}",
            f"ipeds_bachelors_plus_business_stem_completions_{suffix}",
        ]:
            output[f"{column}_per_1000_qcew_jobs"] = (
                1000 * output[column] / output["qcew_employment"]
            )
        output = output.drop(columns=["qcew_employment"])

    output["ipeds_directory_source_url"] = f"{IPEDS_BASE_URL}/HD{args.year}.zip"
    output["ipeds_completions_source_url"] = f"{IPEDS_BASE_URL}/C{args.year}_A.zip"
    output["feature_caveat"] = (
        "IPEDS completions assigned to reporting institution MSA; not graduate residence, local retention, or employer-ready supply"
    )
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output_csv, index=False)
    print(f"Roster MSAs: {len(output)}")
    print(f"MSAs with reporting institutions: {(output['ipeds_reporting_institutions_2024'] > 0).sum()}")
    print(f"Output: {args.output_csv.resolve()}")


if __name__ == "__main__":
    main()
