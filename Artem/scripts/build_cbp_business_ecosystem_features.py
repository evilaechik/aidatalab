#!/usr/bin/env python3
"""Build descriptive large-employer ecosystem measures from Census CBP MSA data.

These measures describe an existing metro business ecosystem. They must not be
used as predictors of the Fortune-office-presence outcome, because a metro's
existing large establishments are too close to the thing being predicted.
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
DEFAULT_RAW_DIR = ARTEM / "data" / "map_green_state_100" / "raw_inputs" / "cbp_2023"
DEFAULT_OUTPUT = ARTEM / "data" / "map_green_state_100" / "descriptive_business_ecosystem_2023.csv"


def source_url(year: int) -> str:
    return f"https://www2.census.gov/programs-surveys/cbp/datasets/{year}/cbp{str(year)[-2:]}msa.zip"


def fetch_cbp(year: int, raw_dir: Path) -> Path:
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / f"cbp{str(year)[-2:]}msa.zip"
    if path.exists() and path.stat().st_size > 10_000:
        return path
    result = subprocess.run(
        ["curl", "--fail", "--location", "--silent", "--show-error", source_url(year)],
        check=True,
        capture_output=True,
    )
    path.write_bytes(result.stdout)
    return path


def load_cbp_totals(path: Path) -> pd.DataFrame:
    with ZipFile(path) as archive:
        names = [name for name in archive.namelist() if name.lower().endswith((".txt", ".csv"))]
        if len(names) != 1:
            raise ValueError(f"Expected one CBP flat file in {path}, found {names}")
        data = pd.read_csv(archive.open(names[0]), dtype=str, low_memory=False)
    required = {"msa", "naics", "est", "n250_499", "n500_999", "n1000"}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"CBP file is missing: {sorted(missing)}")
    return data.loc[data["naics"].eq("------")].copy()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int, default=2023)
    parser.add_argument("--roster-csv", type=Path, default=DEFAULT_ROSTER)
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if not args.roster_csv.exists():
        raise FileNotFoundError(args.roster_csv)

    roster = pd.read_csv(args.roster_csv, dtype={"msa": str})
    roster["msa"] = roster["msa"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5)
    cbp = load_cbp_totals(fetch_cbp(args.year, args.raw_dir))
    cbp["msa"] = cbp["msa"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5)
    year = str(args.year)
    output = cbp[["msa", "est", "n250_499", "n500_999", "n1000"]].copy()
    output = output.rename(columns={"est": f"cbp_total_establishments_{year}"})
    component_columns = ["n250_499", "n500_999", "n1000"]
    output[[f"cbp_total_establishments_{year}", *component_columns]] = output[
        [f"cbp_total_establishments_{year}", *component_columns]
    ].apply(pd.to_numeric, errors="coerce")
    output[f"cbp_large_establishment_coverage_{year}"] = np.where(
        output[component_columns].notna().all(axis=1),
        "complete_size_bands",
        "suppressed_or_unavailable_size_band",
    )
    output[f"cbp_establishments_250plus_{year}"] = output[component_columns].sum(
        axis=1, min_count=len(component_columns)
    )
    output[f"cbp_establishments_1000plus_{year}"] = output["n1000"]
    output[f"cbp_large_establishment_share_250plus_{year}"] = (
        output[f"cbp_establishments_250plus_{year}"]
        / output[f"cbp_total_establishments_{year}"]
    )
    output = output.drop(columns=component_columns)
    output = roster.merge(output, on="msa", how="left", validate="one_to_one")
    output["cbp_source_url"] = source_url(args.year)
    output["feature_caveat"] = (
        "Existing paid-employer establishments by employment-size band; descriptive ecosystem measure, not a Fortune-office model predictor"
    )
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output_csv, index=False)
    print(f"Roster MSAs: {len(output)}")
    print(f"CBP total rows matched: {output[f'cbp_total_establishments_{year}'].notna().sum()}")
    print(f"Complete large-size bands: {output[f'cbp_large_establishment_coverage_{year}'].eq('complete_size_bands').sum()}")
    print(f"Output: {args.output_csv.resolve()}")


if __name__ == "__main__":
    main()
