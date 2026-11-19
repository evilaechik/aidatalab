#!/usr/bin/env python3
"""Combine complete Fortune global-HQ counts with documented regional-HQ evidence.

The result is a *documented corporate-anchor* sensitivity outcome, not a
complete national regional-HQ census.  Every Fortune 500 listed global HQ has
a valid zero-or-count value.  The regional/divisional component is limited to
direct-company-source records that meet the project's evidence standard.  An
absent regional record therefore means "not yet documented by this public
research pass," not proof that no regional HQ exists.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import pandas as pd


ARTEM = Path(__file__).resolve().parents[1]
DATA = ARTEM / "data" / "big_business_presence"
DEFAULT_ROSTER = DATA / "msa_roster.csv"
DEFAULT_GLOBAL = DATA / "fortune500_global_hq_msa_outcome_2025.csv"
DEFAULT_GLOBAL_ASSIGNMENTS = DATA / "fortune500_global_hq_city_msa_assignments_2025.csv"
DEFAULT_SITES = DATA / "fortune500_verified_regional_divisional_sites_2026.csv"
DEFAULT_OUTPUT = DATA / "fortune500_documented_corporate_anchor_msa_outcome_2026.csv"


def msa_code(value: object) -> str:
    return str(value).replace(".0", "").zfill(5)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--msa-roster", type=Path, default=DEFAULT_ROSTER)
    parser.add_argument("--global-outcome", type=Path, default=DEFAULT_GLOBAL)
    parser.add_argument("--global-assignments", type=Path, default=DEFAULT_GLOBAL_ASSIGNMENTS)
    parser.add_argument("--verified-sites", type=Path, default=DEFAULT_SITES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    for path in [args.msa_roster, args.global_outcome, args.global_assignments, args.verified_sites]:
        if not path.is_file():
            raise FileNotFoundError(path)

    roster = pd.read_csv(args.msa_roster, dtype={"msa_cbsa": str})
    roster["msa_cbsa"] = roster["msa_cbsa"].map(msa_code)
    if roster["msa_cbsa"].duplicated().any():
        raise ValueError("MSA roster contains duplicate CBSA codes.")

    global_outcome = pd.read_csv(args.global_outcome, dtype={"msa_cbsa": str})
    global_outcome["msa_cbsa"] = global_outcome["msa_cbsa"].map(msa_code)
    if global_outcome["msa_cbsa"].duplicated().any():
        raise ValueError("Global-HQ outcome contains duplicate CBSA codes.")
    if "fortune500_global_hq_count" not in global_outcome.columns:
        raise ValueError("Global-HQ outcome is missing fortune500_global_hq_count.")

    global_assignments = pd.read_csv(args.global_assignments, dtype=str, keep_default_na=False)
    if not {"fortune_slug", "msa_cbsa"}.issubset(global_assignments.columns):
        raise ValueError("Global-HQ assignments must include fortune_slug and msa_cbsa.")
    global_pairs = global_assignments.loc[
        global_assignments["msa_cbsa"].ne(""), ["fortune_slug", "msa_cbsa"]
    ].copy()
    global_pairs["msa_cbsa"] = global_pairs["msa_cbsa"].str.replace(r"\.0$", "", regex=True).str.zfill(5)

    sites = pd.read_csv(args.verified_sites, dtype=str, keep_default_na=False)
    required = {
        "company_name", "fortune_slug", "msa_cbsa", "count_in_future_regional_hq_outcome",
        "verification_status", "model_eligibility",
    }
    missing = required - set(sites.columns)
    if missing:
        raise ValueError(f"Verified-sites file is missing: {sorted(missing)}")
    sites["msa_cbsa"] = sites["msa_cbsa"].str.replace(r"\.0$", "", regex=True).str.zfill(5)

    # Keep only records whose headquarters relationship comes directly from a
    # company or investor-relations source.  The two labelled exception types
    # stay in the evidence file but are intentionally excluded from this score.
    direct_eligible = sites.loc[
        sites["count_in_future_regional_hq_outcome"].eq("True")
        & sites["verification_status"].eq("company_source_verified")
        & sites["model_eligibility"].eq("eligible_after_one_more_currentness_review")
        & sites["msa_cbsa"].ne(""),
        ["company_name", "fortune_slug", "msa_cbsa"],
    ].drop_duplicates()
    # A company contributes at most once in an MSA.  Its listed global HQ
    # already contributes to the base count, so discard any same-company,
    # same-MSA regional record instead of adding a second anchor.
    direct_eligible = direct_eligible.merge(
        global_pairs.assign(_listed_global_hq_same_msa=True),
        on=["fortune_slug", "msa_cbsa"], how="left", validate="one_to_one",
    )
    colocated = direct_eligible["_listed_global_hq_same_msa"].eq(True)
    direct_eligible = direct_eligible.loc[~colocated].drop(columns="_listed_global_hq_same_msa")
    regional_counts = (
        direct_eligible.groupby("msa_cbsa", as_index=False)
        .agg(verified_regional_divisional_hq_parent_msa_pair_count=("company_name", "nunique"))
    )

    summary = roster.merge(
        global_outcome[["msa_cbsa", "fortune500_global_hq_count"]],
        on="msa_cbsa", how="left", validate="one_to_one",
    ).merge(
        regional_counts, on="msa_cbsa", how="left", validate="one_to_one",
    )
    if summary["fortune500_global_hq_count"].isna().any():
        raise ValueError("A roster MSA lacks a complete global-HQ count.")
    summary["fortune500_global_hq_count"] = pd.to_numeric(
        summary["fortune500_global_hq_count"], errors="raise"
    ).astype(int)
    summary["verified_regional_divisional_hq_parent_msa_pair_count"] = (
        summary["verified_regional_divisional_hq_parent_msa_pair_count"].fillna(0).astype(int)
    )
    summary["documented_corporate_anchor_count"] = (
        summary["fortune500_global_hq_count"]
        + summary["verified_regional_divisional_hq_parent_msa_pair_count"]
    )
    summary["outcome_definition"] = (
        "Complete Fortune 2025 listed global-HQ count plus distinct, direct-company-source "
        "verified Fortune 500 regional/divisional/subsidiary HQ parent-company × MSA pairs. "
        "The regional component is documented public evidence, not a complete zero-or-count census."
    )
    summary["coverage_status"] = (
        "global_hq_complete; regional_divisional_component_documented_not_complete"
    )
    summary = summary.sort_values(["documented_corporate_anchor_count", "metro_name"], ascending=[False, True])

    args.output.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.output, index=False, quoting=csv.QUOTE_MINIMAL)
    print(f"Direct-company-source eligible regional/divisional company-MSA pairs: {len(direct_eligible):,}")
    print(f"MSAs with at least one documented regional/divisional pair: {len(regional_counts):,}")
    print(f"Output: {args.output.resolve()}")


if __name__ == "__main__":
    main()
