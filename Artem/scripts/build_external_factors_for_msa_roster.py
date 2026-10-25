#!/usr/bin/env python3
"""Build public QCEW, tax, price, and housing factors for any MSA roster.

This is the factor-building half of the business-attraction experiment.  It
uses the existing public BLS QCEW slices, public FHFA house-price data, BEA
regional-price-parity data, and an already archived public tax-rate table.
It does not read Data Axle or Invest Atlanta restricted records.

The supplied county crosswalk must include county_fips, msa_cbsa, division_msa,
county_state, and county_name.  Output is a year-by-MSA factor panel suitable
for a cross-sectional MSA model.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

import external_factor_qcew_xgboost as base


ARTEM = Path(__file__).resolve().parents[1]
DEFAULT_TAX = (
    ARTEM
    / "data"
    / "business_entry_models"
    / "external_qcew_factors"
    / "state_corporate_tax_rates_2017_2022.csv"
)


def build_membership(roster_path: Path, crosswalk_path: Path) -> pd.DataFrame:
    roster = pd.read_csv(roster_path, dtype={"msa": str})
    crosswalk = pd.read_csv(crosswalk_path, dtype={"county_fips": str, "msa_cbsa": str})
    # The original national Top-100 crosswalk predates the reusable roster
    # builder and uses the legacy ``msa``, ``county``, and ``state`` headers.
    # Normalize it here so both that roster and newer MSA-scoped crosswalks
    # follow the same factor-construction path.
    crosswalk = crosswalk.rename(
        columns={
            "msa": "msa_cbsa",
            "county": "county_name",
            "state": "county_state",
        }
    )
    required = {"msa", "msa_title", "member_states"}
    missing_roster = required - set(roster.columns)
    required_crosswalk = {"county_fips", "msa_cbsa", "division_msa", "county_state", "county_name"}
    missing_crosswalk = required_crosswalk - set(crosswalk.columns)
    if missing_roster or missing_crosswalk:
        raise ValueError(
            f"Missing roster columns {sorted(missing_roster)}; missing crosswalk columns {sorted(missing_crosswalk)}"
        )

    roster["msa"] = pd.to_numeric(roster["msa"], errors="raise").astype(int)
    crosswalk["msa"] = pd.to_numeric(crosswalk["msa_cbsa"], errors="raise").astype(int)
    membership = crosswalk.rename(
        columns={"county_state": "state", "county_name": "county"}
    )[["msa", "division_msa", "county_fips", "county", "state"]]
    membership["county_fips"] = membership["county_fips"].astype(str).str.zfill(5)
    membership["division_msa"] = pd.to_numeric(membership["division_msa"], errors="coerce")
    if membership.duplicated("county_fips").any():
        raise ValueError("A county appears in more than one roster MSA")
    return membership.merge(
        roster[["msa", "msa_title", "member_states"]], on="msa", how="inner", validate="many_to_one"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--roster-csv", required=True, type=Path)
    parser.add_argument("--county-crosswalk-csv", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--tax-rates-csv", type=Path, default=DEFAULT_TAX)
    args = parser.parse_args()
    for path in [args.roster_csv, args.county_crosswalk_csv, args.tax_rates_csv]:
        if not path.exists():
            raise FileNotFoundError(path)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    base.OUT = args.output_dir
    membership = build_membership(args.roster_csv, args.county_crosswalk_csv)
    membership.to_csv(args.output_dir / "msa_counties_2023.csv", index=False)

    tax_rates = pd.read_csv(args.tax_rates_csv)
    expected_tax_columns = {
        "year",
        "state",
        "top_corporate_tax_rate",
        "gross_receipts_tax_flag",
    }
    if expected_tax_columns - set(tax_rates.columns):
        raise ValueError("Tax rates CSV does not have the required columns")
    qcew, coverage_issues = base.qcew_metro_panel(membership, tax_rates)
    macro = base.metro_macro_factors()
    macro = macro[macro["msa"].isin(set(membership["msa"]))]
    factors = qcew.merge(macro, on=["msa", "year"], how="left", validate="one_to_one")
    factors = factors.merge(
        membership[["msa", "msa_title", "member_states"]].drop_duplicates(),
        on="msa",
        how="left",
        validate="many_to_one",
    ).sort_values(["msa", "year"])
    factors.to_csv(args.output_dir / "external_factor_model_panel.csv", index=False)
    coverage_issues.to_csv(args.output_dir / "qcew_coverage_issues.csv", index=False)
    macro.to_csv(args.output_dir / "metro_macro_factors.csv", index=False)

    latest = factors.sort_values("year").groupby("msa", as_index=False).tail(1)
    latest.to_csv(args.output_dir / "latest_factor_row_by_msa.csv", index=False)
    print(f"Factors: {len(factors):,} rows across {factors['msa'].nunique()} MSAs")
    print(f"Latest factor year range: {latest['year'].min()}–{latest['year'].max()}")
    print(f"QCEW coverage issues: {len(coverage_issues):,}")
    print(f"Output: {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
