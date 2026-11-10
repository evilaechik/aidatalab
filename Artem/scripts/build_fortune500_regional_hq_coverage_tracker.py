#!/usr/bin/env python3
"""Create an auditable Fortune 500 regional/divisional-HQ coverage tracker.

The tracker deliberately distinguishes confirmed source-verified sites from
SEC discovery leads and companies not yet reached by either process. It is a
research-control file, not evidence that an unlisted company lacks a regional
or business-unit headquarters.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


ARTEM = Path(__file__).resolve().parents[1]
DATA = ARTEM / "data" / "big_business_presence"
FORTUNE = DATA / "fortune_500_universe_2025.csv"
VERIFIED = DATA / "fortune500_verified_regional_divisional_sites_2026.csv"
SEC_LEADS = DATA / "fortune500_public_filing_regional_hq_discovery_leads_2026.csv"
OUTPUT = DATA / "fortune500_regional_divisional_hq_coverage_tracker_2026.csv"


def joined_unique(frame: pd.DataFrame, values: list[str]) -> pd.Series:
    """Return a stable, readable company-level join for columns in *values*."""
    if frame.empty:
        return pd.Series(dtype=str)
    return (
        frame.assign(_joined=frame[values].fillna("").astype(str).agg(" | ".join, axis=1))
        .groupby("company_name", sort=False)["_joined"].agg(lambda records: "; ".join(dict.fromkeys(records)))
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fortune-csv", type=Path, default=FORTUNE)
    parser.add_argument("--verified-csv", type=Path, default=VERIFIED)
    parser.add_argument("--sec-leads-csv", type=Path, default=SEC_LEADS)
    parser.add_argument("--output-csv", type=Path, default=OUTPUT)
    args = parser.parse_args()

    for path in [args.fortune_csv, args.verified_csv, args.sec_leads_csv]:
        if not path.is_file():
            raise FileNotFoundError(path)

    fortune = pd.read_csv(args.fortune_csv, dtype=str, keep_default_na=False).rename(columns={"company": "company_name"})
    verified = pd.read_csv(args.verified_csv, dtype=str, keep_default_na=False)
    leads = pd.read_csv(args.sec_leads_csv, dtype=str, keep_default_na=False)

    verified["count_in_future_regional_hq_outcome"] = (
        verified["count_in_future_regional_hq_outcome"].str.lower().eq("true")
    )
    verified["is_assigned_to_model_msa"] = verified["msa_cbsa"].str.len().gt(0)

    eligible = verified[verified["count_in_future_regional_hq_outcome"]].copy()
    nonincremental = verified[~verified["count_in_future_regional_hq_outcome"]].copy()
    eligible_summary = (
        eligible.groupby("company_name", as_index=False)
        .agg(
            verified_eligible_site_rows=("site_name", "size"),
            verified_eligible_assigned_msa_pairs=("msa_cbsa", lambda values: values[values.ne("")].nunique()),
            verified_eligible_unassigned_site_rows=("is_assigned_to_model_msa", lambda values: int((~values).sum())),
        )
    )
    nonincremental_summary = (
        nonincremental.groupby("company_name", as_index=False)
        .agg(verified_nonincremental_or_footprint_rows=("site_name", "size"))
    )
    site_names = joined_unique(eligible, ["site_name", "city", "state"])
    msa_names = joined_unique(eligible[eligible["is_assigned_to_model_msa"]], ["msa_name", "msa_cbsa"])
    lead_summary = (
        leads.groupby("company_name", as_index=False)
        .agg(public_filing_lead_rows=("official_source_url", "size"))
    )

    tracker = fortune.merge(eligible_summary, on="company_name", how="left")
    tracker = tracker.merge(nonincremental_summary, on="company_name", how="left")
    tracker = tracker.merge(lead_summary, on="company_name", how="left")
    tracker["verified_eligible_site_rows"] = tracker["verified_eligible_site_rows"].fillna(0).astype(int)
    tracker["verified_eligible_assigned_msa_pairs"] = tracker["verified_eligible_assigned_msa_pairs"].fillna(0).astype(int)
    tracker["verified_eligible_unassigned_site_rows"] = tracker["verified_eligible_unassigned_site_rows"].fillna(0).astype(int)
    tracker["verified_nonincremental_or_footprint_rows"] = tracker["verified_nonincremental_or_footprint_rows"].fillna(0).astype(int)
    tracker["public_filing_lead_rows"] = tracker["public_filing_lead_rows"].fillna(0).astype(int)
    tracker["verified_eligible_sites"] = tracker["company_name"].map(site_names).fillna("")
    tracker["verified_eligible_msas"] = tracker["company_name"].map(msa_names).fillna("")

    tracker["research_status"] = "not_yet_in_public_research_queue"
    tracker.loc[tracker["public_filing_lead_rows"].gt(0), "research_status"] = "public_filing_lead_needs_current_company_source"
    tracker.loc[tracker["verified_nonincremental_or_footprint_rows"].gt(0), "research_status"] = "verified_nonincremental_or_footprint_only"
    tracker.loc[tracker["verified_eligible_site_rows"].gt(0), "research_status"] = "verified_eligible_regional_or_business_unit_hq"

    next_actions = {
        "verified_eligible_regional_or_business_unit_hq": "Recheck source currentness before scoring; retain site and MSA evidence.",
        "verified_nonincremental_or_footprint_only": "Keep as context; do not count toward the incremental company-MSA outcome unless its HQ role is confirmed.",
        "public_filing_lead_needs_current_company_source": "Use current company or investor-relations materials to validate HQ function, parent linkage, and location.",
        "not_yet_in_public_research_queue": "Search the company, operating segments, acquisitions, and named brands for an explicit current HQ statement.",
    }
    tracker["next_action"] = tracker["research_status"].map(next_actions)
    tracker["tracker_caveat"] = (
        "This row records research coverage, not the absence of a regional/divisional HQ. "
        "Only source-verified sites should be used in the outcome."
    )
    columns = [
        "fortune_2025_rank", "fortune_2025_list_position", "company_name", "fortune_slug", "headquarters_city", "headquarters_state", "industry",
        "research_status", "verified_eligible_site_rows", "verified_eligible_assigned_msa_pairs", "verified_eligible_unassigned_site_rows",
        "verified_nonincremental_or_footprint_rows", "public_filing_lead_rows", "verified_eligible_sites", "verified_eligible_msas", "next_action", "tracker_caveat",
    ]
    tracker = tracker[columns].sort_values("fortune_2025_rank", key=lambda values: values.astype(int))
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    tracker.to_csv(args.output_csv, index=False)

    print(tracker["research_status"].value_counts().rename_axis("research_status").to_string())
    print(f"Output: {args.output_csv.resolve()}")


if __name__ == "__main__":
    main()
