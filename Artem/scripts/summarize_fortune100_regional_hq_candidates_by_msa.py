"""Summarize external Fortune 100 regional-HQ *candidates* by project MSA.

This script never creates a final regional-HQ score.  The input comes from a
licensed Data Axle/ArcGIS candidate file and is intentionally located outside
the repository.  The outputs remain beside that input and must be read as a
prioritized verification queue: an MSA count is not evidence that any site is
a confirmed regional headquarters.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]


def reject_repo_output(path: Path) -> None:
    """Prevent licensed/derived location outputs from entering the Git repo."""
    try:
        path.expanduser().resolve().relative_to(REPO_ROOT)
    except ValueError:
        return
    raise ValueError(f"Output directory must be outside the repository: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assigned-candidates", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    reject_repo_output(args.output_dir)

    candidates = pd.read_csv(
        args.assigned_candidates,
        dtype={"msa_cbsa": str, "census_place_geoid": str},
        keep_default_na=False,
    )
    # The external handoff file standardizes the source-company field to
    # ``company_name`` for geographic tooling.  Retain a Fortune-specific name
    # in the review queue so its intended universe stays explicit.
    if "fortune_company" not in candidates.columns and "company_name" in candidates.columns:
        candidates = candidates.rename(columns={"company_name": "fortune_company"})
    required = {
        "fortune_company", "candidate_type", "regional_keyword_signal", "msa_cbsa",
        "msa_name", "msa_assignment_method", "census_place_geoid", "census_place_name",
    }
    missing = required - set(candidates.columns)
    if missing:
        raise ValueError(f"Input is missing columns: {sorted(missing)}")

    assigned = candidates.loc[
        candidates["msa_assignment_method"].eq("city_place_centroid_within_cbsa")
    ].copy()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    company_msa = (
        assigned.groupby(["msa_cbsa", "msa_name", "fortune_company"], as_index=False)
        .agg(
            hq_category_candidate_records=(
                "candidate_type", lambda values: (values == "data_axle_headquarters_candidate").sum()
            ),
            large_office_candidate_records=(
                "candidate_type", lambda values: (values == "large_office_like_branch_candidate").sum()
            ),
            regional_keyword_candidate_records=("regional_keyword_signal", "sum"),
        )
    )
    company_msa["regional_hq_verification_status"] = "unverified_candidate"
    company_msa["verification_rule"] = (
        "Count only after a company-owned site, company press release, SEC filing, or equivalent "
        "source confirms a regional/divisional HQ or qualifying office function."
    )
    company_msa.to_csv(
        args.output_dir / "fortune100_msa_company_regional_hq_review_queue.csv",
        index=False,
        quoting=csv.QUOTE_MINIMAL,
    )

    summary = (
        company_msa.groupby(["msa_cbsa", "msa_name"], as_index=False)
        .agg(
            candidate_f100_companies=("fortune_company", "nunique"),
            companies_with_hq_category_candidate=(
                "hq_category_candidate_records", lambda values: values.gt(0).sum()
            ),
            companies_with_large_office_candidate=(
                "large_office_candidate_records", lambda values: values.gt(0).sum()
            ),
            companies_with_regional_keyword_candidate=(
                "regional_keyword_candidate_records", lambda values: values.gt(0).sum()
            ),
        )
        .sort_values(["candidate_f100_companies", "msa_name"], ascending=[False, True])
    )
    summary["publication_status"] = "candidate_only_not_a_regional_hq_score"
    summary["assignment_method"] = "city_place_centroid_within_cbsa"
    summary["required_next_step"] = "company_source_verification"
    summary.to_csv(
        args.output_dir / "fortune100_msa_regional_hq_candidate_summary.csv",
        index=False,
        quoting=csv.QUOTE_MINIMAL,
    )

    city_company = (
        assigned.loc[assigned["census_place_geoid"].ne("")]
        .groupby(["census_place_geoid", "census_place_name", "state", "fortune_company"], as_index=False)
        .agg(
            hq_category_candidate_records=(
                "candidate_type", lambda values: (values == "data_axle_headquarters_candidate").sum()
            ),
            large_office_candidate_records=(
                "candidate_type", lambda values: (values == "large_office_like_branch_candidate").sum()
            ),
            regional_keyword_candidate_records=("regional_keyword_signal", "sum"),
        )
    )
    city_summary = (
        city_company.groupby(["census_place_geoid", "census_place_name", "state"], as_index=False)
        .agg(
            candidate_f100_companies=("fortune_company", "nunique"),
            companies_with_hq_category_candidate=(
                "hq_category_candidate_records", lambda values: values.gt(0).sum()
            ),
            companies_with_large_office_candidate=(
                "large_office_candidate_records", lambda values: values.gt(0).sum()
            ),
            companies_with_regional_keyword_candidate=(
                "regional_keyword_candidate_records", lambda values: values.gt(0).sum()
            ),
        )
        .sort_values(["candidate_f100_companies", "census_place_name"], ascending=[False, True])
    )
    city_summary["publication_status"] = "candidate_only_not_a_regional_hq_score"
    city_summary["city_assignment_method"] = "source_city_label_matched_to_Census_place_centroid"
    city_summary["required_next_step"] = "company_source_and_exact_address_verification"
    city_summary.to_csv(
        args.output_dir / "fortune100_city_regional_hq_candidate_summary.csv",
        index=False,
        quoting=csv.QUOTE_MINIMAL,
    )

    print(
        f"Wrote {len(company_msa):,} company-MSA review rows across {len(summary):,} MSAs "
        f"and {len(city_summary):,} Census places."
    )
    print(f"Output: {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
