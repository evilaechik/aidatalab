#!/usr/bin/env python3
"""Create a city-jurisdiction context table for Fortune 500 global HQs.

The public Fortune dataset reports headquarters at city/state precision. This
script maps that reported city to an official Census *place* (a municipality or
CDP) and attaches the current state corporate-income-tax context. It does not
calculate a company's tax bill: municipal business-license fees, payroll taxes,
property tax, incentive agreements, nexus, income apportionment, and assessed
value require address- and company-specific research.
"""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
from io import StringIO
from pathlib import Path

import pandas as pd

from assign_data_axle_locations_to_msas import choose_place, normalize_text, read_gazetteer
from build_fortune500_global_hq_msa_outcome import STATE_ABBREVIATIONS


ARTEM = Path(__file__).resolve().parents[1]
FORTUNE = ARTEM / "data" / "big_business_presence" / "fortune_500_universe_2025.csv"
MSA_ASSIGNMENTS = ARTEM / "data" / "big_business_presence" / "fortune500_global_hq_city_msa_assignments_2025.csv"
OUTPUT = ARTEM / "data" / "big_business_presence"
TAX_URL = "https://taxfoundation.org/data/all/state/state-corporate-income-tax-rates-brackets/"
GROSS_RECEIPTS_STATES = {"Delaware", "Nevada", "Ohio", "Oregon", "Tennessee", "Texas", "Washington"}
STATE_NAME_NORMALIZATION = {"District Of Columbia": "District of Columbia"}


def census_city_lookup(fortune: pd.DataFrame, places: pd.DataFrame) -> pd.DataFrame:
    """Map Fortune's reported city to a Census place without inventing a street point."""
    place_groups = {key: group for key, group in places.groupby(["state", "city_key"], sort=False)}
    city_rows: list[dict[str, object]] = []
    for state, city in fortune[["headquarters_state", "headquarters_city"]].drop_duplicates().itertuples(index=False):
        state_abbr = STATE_ABBREVIATIONS.get(str(state), str(state))
        candidates = place_groups.get((state_abbr, normalize_text(city)), pd.DataFrame(columns=places.columns))
        place, status = choose_place(candidates)
        if place is None:
            city_rows.append(
                {
                    "headquarters_state": state,
                    "headquarters_city": city,
                    "census_place_geoid": "",
                    "census_place_name": "",
                    "census_place_lsad": "",
                    "census_place_functional_status": "",
                    "census_place_land_area_sq_m": pd.NA,
                    "city_place_match_status": status,
                    "city_boundary_assignment_precision": "unassigned_city_label",
                }
            )
        else:
            city_rows.append(
                {
                    "headquarters_state": state,
                    "headquarters_city": city,
                    "census_place_geoid": place["GEOID"],
                    "census_place_name": place["NAME"],
                    "census_place_lsad": place["LSAD"],
                    "census_place_functional_status": place["FUNCSTAT"],
                    "census_place_land_area_sq_m": place["area_sq_m"],
                    "city_place_match_status": status,
                    "city_boundary_assignment_precision": "Fortune_listed_city_matched_to_Census_place_not_street_address",
                }
            )
    return pd.DataFrame(city_rows)


def tax_foundation_2026_rates() -> pd.DataFrame:
    """Parse current top statutory state corporate-income-tax rates.

    The statistic is a state tax context, not a local tax rate or effective
    company tax rate. States missing from the corporate-income-tax table are
    explicitly identified rather than silently treated as tax-free.
    """
    html = subprocess.run(
        ["curl", "--fail", "--location", "--silent", "--show-error", TAX_URL],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    table = pd.read_html(StringIO(html), flavor="lxml")[0].iloc[:, :2].copy()
    table.columns = ["state", "rate"]
    table["state"] = table["state"].astype(str).str.replace(r"\s*\([^)]*\)", "", regex=True).str.strip()
    table["numeric_rate"] = pd.to_numeric(
        table["rate"].astype(str).str.extract(r"([0-9]+(?:\.[0-9]+)?)")[0], errors="coerce"
    )
    rates = table.groupby("state", as_index=False)["numeric_rate"].max()
    all_states = pd.DataFrame({"headquarters_state": sorted(STATE_ABBREVIATIONS)})
    result = all_states.merge(rates, left_on="headquarters_state", right_on="state", how="left")
    result["no_state_corporate_income_tax"] = result["numeric_rate"].isna()
    result["top_state_corporate_income_tax_rate_2026"] = result["numeric_rate"].fillna(0.0)
    result["state_gross_receipts_tax_flag"] = result["headquarters_state"].isin(GROSS_RECEIPTS_STATES)
    result["state_tax_context_source"] = TAX_URL
    return result[[
        "headquarters_state", "top_state_corporate_income_tax_rate_2026",
        "no_state_corporate_income_tax", "state_gross_receipts_tax_flag", "state_tax_context_source",
    ]]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--place-gazetteer", required=True, type=Path)
    parser.add_argument("--fortune-csv", type=Path, default=FORTUNE)
    parser.add_argument("--msa-assignments-csv", type=Path, default=MSA_ASSIGNMENTS)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    args = parser.parse_args()
    for path in [args.place_gazetteer, args.fortune_csv, args.msa_assignments_csv]:
        if not path.expanduser().is_file():
            raise FileNotFoundError(path)

    fortune = pd.read_csv(args.fortune_csv, dtype=str, keep_default_na=False)
    fortune["headquarters_state"] = fortune["headquarters_state"].replace(STATE_NAME_NORMALIZATION)
    assignments = pd.read_csv(args.msa_assignments_csv, dtype=str, keep_default_na=False)
    places = read_gazetteer(args.place_gazetteer)
    city_lookup = census_city_lookup(fortune, places)
    tax_rates = tax_foundation_2026_rates()

    assignment_columns = [
        "fortune_slug", "msa_cbsa", "msa_name", "msa_assignment_method", "place_match_status",
    ]
    hq_context = (
        fortune.merge(city_lookup, on=["headquarters_state", "headquarters_city"], how="left", validate="many_to_one")
        .merge(assignments[assignment_columns], on="fortune_slug", how="left", validate="one_to_one")
        .merge(tax_rates, on="headquarters_state", how="left", validate="many_to_one")
    )
    hq_context["municipal_tax_data_status"] = "not_standardized_nationally_requires_local_primary_source"
    hq_context["municipal_tax_review_fields"] = (
        "business_license_or_occupation_tax; local_income_or_payroll_tax; property_tax_millage_and_assessed_value; "
        "sales_use_tax; incentive_agreement"
    )
    hq_context["company_tax_bill_status"] = "not_calculable_from_public_geography_and_statutory_rate_only"
    hq_context["city_tax_interpretation"] = (
        "State statutory corporate rate is jurisdiction context only. Municipal tax burden needs exact HQ address, "
        "tax base, incentives, and company-specific filings."
    )
    hq_context = hq_context.sort_values("fortune_2025_list_position")

    matched_city_context = hq_context[hq_context["census_place_geoid"].ne("")].copy()
    city_summary = (
        matched_city_context.groupby(
            ["headquarters_state", "census_place_geoid", "census_place_name", "census_place_lsad"],
            dropna=False,
            as_index=False,
        )
        .agg(
            fortune500_listed_global_hq_count=("fortune_slug", "nunique"),
            fortune500_listed_global_hq_revenue_usd_millions=("revenue_usd_millions", lambda values: pd.to_numeric(values, errors="coerce").sum()),
            top_state_corporate_income_tax_rate_2026=("top_state_corporate_income_tax_rate_2026", "first"),
            no_state_corporate_income_tax=("no_state_corporate_income_tax", "first"),
            state_gross_receipts_tax_flag=("state_gross_receipts_tax_flag", "first"),
            municipal_tax_data_status=("municipal_tax_data_status", "first"),
        )
        .sort_values(["fortune500_listed_global_hq_count", "census_place_name"], ascending=[False, True])
    )
    unmatched_city_labels = hq_context[hq_context["census_place_geoid"].eq("")][
        ["fortune_2025_rank", "company", "headquarters_city", "headquarters_state", "city_place_match_status"]
    ].sort_values(["headquarters_state", "headquarters_city", "company"])

    args.output_dir.mkdir(parents=True, exist_ok=True)
    tax_rates.to_csv(args.output_dir / "state_corporate_tax_context_2026.csv", index=False, quoting=csv.QUOTE_MINIMAL)
    hq_context.to_csv(args.output_dir / "fortune500_hq_city_tax_context_2026.csv", index=False, quoting=csv.QUOTE_MINIMAL)
    city_summary.to_csv(args.output_dir / "fortune500_hq_city_tax_summary_2026.csv", index=False, quoting=csv.QUOTE_MINIMAL)
    unmatched_city_labels.to_csv(
        args.output_dir / "fortune500_hq_city_tax_unassigned_labels_2026.csv",
        index=False,
        quoting=csv.QUOTE_MINIMAL,
    )
    print(f"HQ city/place assignments: {len(hq_context):,}")
    print(f"Matched Census places: {hq_context['census_place_geoid'].ne('').sum():,}")
    print(f"Distinct HQ jurisdictions: {len(city_summary):,}")
    print(f"Output: {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
