#!/usr/bin/env python3
"""Assign Fortune 500's public headquarters field to the project MSA roster.

This creates a *global-HQ* outcome, not a regional-HQ outcome.  Fortune's
ranking supplies a company-level headquarters city and state, while Census
place centroids and matching-vintage CBSA polygons supply a transparent,
repeatable MSA assignment.  It is appropriate as a complete public benchmark
for a first Fortune-500 model; regional/divisional HQs require location-level
evidence and are intentionally kept in a separate review queue.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import pandas as pd

from assign_data_axle_locations_to_msas import (
    build_assignments,
    load_target_cbsa_polygons,
    read_gazetteer,
)


ARTEM = Path(__file__).resolve().parents[1]
DEFAULT_FORTUNE = ARTEM / "data" / "big_business_presence" / "fortune_500_universe_2025.csv"
DEFAULT_ROSTER = ARTEM / "data" / "big_business_presence" / "msa_roster.csv"
DEFAULT_OUTPUT = ARTEM / "data" / "big_business_presence"

STATE_ABBREVIATIONS = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL",
    "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
    "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
    "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR",
    "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
    "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA",
    "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
}


def code(value: object) -> str:
    return str(value).replace(".0", "").zfill(5)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--place-gazetteer", required=True, type=Path)
    parser.add_argument("--cbsa-shapefile", required=True, type=Path)
    parser.add_argument("--fortune-csv", type=Path, default=DEFAULT_FORTUNE)
    parser.add_argument("--msa-roster", type=Path, default=DEFAULT_ROSTER)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    for path in [args.place_gazetteer, args.cbsa_shapefile, args.fortune_csv, args.msa_roster]:
        if not path.expanduser().is_file():
            raise FileNotFoundError(path)

    fortune = pd.read_csv(args.fortune_csv, dtype=str, keep_default_na=False)
    required_fortune = {
        "fortune_2025_list_position", "fortune_2025_rank", "company", "fortune_slug",
        "revenue_usd_millions", "headquarters_city", "headquarters_state",
    }
    missing = required_fortune - set(fortune.columns)
    if missing:
        raise ValueError(f"Fortune file is missing columns: {sorted(missing)}")
    if len(fortune) != 500 or fortune["fortune_slug"].duplicated().any():
        raise ValueError("Expected one unique row for every Fortune 500 company.")

    roster = pd.read_csv(args.msa_roster, dtype=str, keep_default_na=False)
    if not {"msa_cbsa", "metro_name"}.issubset(roster.columns):
        raise ValueError("MSA roster must include msa_cbsa and metro_name.")
    roster["msa_cbsa"] = roster["msa_cbsa"].map(code)
    if roster["msa_cbsa"].duplicated().any():
        raise ValueError("MSA roster has duplicate CBSA codes.")
    metro_names = dict(roster[["msa_cbsa", "metro_name"]].itertuples(index=False, name=None))

    places = read_gazetteer(args.place_gazetteer)
    polygons = load_target_cbsa_polygons(args.cbsa_shapefile, set(metro_names))
    headquarters = fortune.rename(
        columns={"company": "company_name", "headquarters_city": "city", "headquarters_state": "state"}
    ).copy()
    headquarters["state"] = headquarters["state"].map(STATE_ABBREVIATIONS).fillna(headquarters["state"])
    assigned = build_assignments(headquarters, places, polygons, metro_names)
    assigned["global_hq_status"] = "Fortune_2025_listed_global_headquarters"
    assigned["msa_assignment_caveat"] = (
        "Assigned from Census place centroid within 2023 CBSA polygon; validate exact street address for boundary-sensitive cases."
    )

    in_roster = assigned[assigned["msa_assignment_method"].eq("city_place_centroid_within_cbsa")].copy()
    in_roster["revenue_usd_millions"] = pd.to_numeric(in_roster["revenue_usd_millions"], errors="coerce")
    counts = (
        in_roster.groupby("msa_cbsa", as_index=False)
        .agg(
            fortune500_global_hq_count=("fortune_slug", "nunique"),
            fortune500_global_hq_revenue_usd_millions=("revenue_usd_millions", "sum"),
        )
    )
    summary = roster.merge(counts, on="msa_cbsa", how="left", validate="one_to_one")
    summary["fortune500_global_hq_count"] = summary["fortune500_global_hq_count"].fillna(0).astype(int)
    summary["fortune500_global_hq_revenue_usd_millions"] = summary[
        "fortune500_global_hq_revenue_usd_millions"
    ].fillna(0.0)
    summary["fortune500_global_hq_count_per_500"] = summary["fortune500_global_hq_count"] / len(fortune)
    summary["outcome_definition"] = (
        "Distinct Fortune 500 companies whose Fortune 2025 listed global headquarters city maps to this MSA; not regional HQs."
    )
    summary["coverage_status"] = "complete_for_listed_global_hq_field"
    summary = summary.sort_values(["fortune500_global_hq_count", "metro_name"], ascending=[False, True])

    args.output_dir.mkdir(parents=True, exist_ok=True)
    assigned.to_csv(
        args.output_dir / "fortune500_global_hq_city_msa_assignments_2025.csv",
        index=False,
        quoting=csv.QUOTE_MINIMAL,
    )
    summary.to_csv(
        args.output_dir / "fortune500_global_hq_msa_outcome_2025.csv",
        index=False,
        quoting=csv.QUOTE_MINIMAL,
    )
    audit = (
        assigned.groupby(["msa_assignment_method", "place_match_status"], dropna=False)
        .size()
        .reset_index(name="fortune500_companies")
        .sort_values("fortune500_companies", ascending=False)
    )
    audit.to_csv(
        args.output_dir / "fortune500_global_hq_msa_assignment_audit_2025.csv",
        index=False,
        quoting=csv.QUOTE_MINIMAL,
    )

    print(f"Fortune companies: {len(fortune):,}")
    print(f"Assigned to selected MSAs: {len(in_roster):,}")
    print(f"MSAs with at least one listed global HQ: {(summary['fortune500_global_hq_count'] > 0).sum():,}")
    print(f"Output: {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
