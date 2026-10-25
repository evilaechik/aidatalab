#!/usr/bin/env python3
"""Build a conservative, source-covered Fortune-100 candidate score locally.

This is a repair diagnostic for a geographically incomplete Data Axle export.
It only scores MSAs already represented in the original candidate-score table;
an absent MSA remains unknown rather than becoming zero.  It also requires
stronger company-identity evidence than the original text-query score:

* a corporate-parent or headquarters field exactly matches the queried or
  Fortune company name after light legal-suffix normalization; or
* a Branch/Headquarters record has an exactly matching business name.

The output remains a screened *candidate* count, not a verified office count.
Licensed inputs and outputs must remain outside the repository.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

from assign_data_axle_locations_to_msas import (
    REPO_ROOT,
    classify_site_function,
    normalize_text,
)


TARGET = "distinct_high_confidence_current_f100_nonexcluded_candidate_companies"
LEGAL_SUFFIX = re.compile(
    r"\b(incorporated|inc|corporation|corp|company|co|limited|ltd|llc|plc|lp|l p)\b$"
)


def reject_repo_output(path: Path) -> None:
    resolved = path.expanduser().resolve()
    try:
        resolved.relative_to(REPO_ROOT)
    except ValueError:
        return
    raise ValueError(f"Licensed output must be outside the repository: {resolved}")


def company_key(value: object) -> str:
    """Normalize an identity field without accepting substring matches."""
    text = normalize_text(value)
    text = re.sub(r"^the ", "", text)
    return LEGAL_SUFFIX.sub("", text).strip()


def high_confidence_identity(frame: pd.DataFrame) -> pd.Series:
    """Return a conservative row-level company-identity flag."""
    identity_columns = [
        "company_name",
        "fortune_2025_company",
        "source_business_name",
        "source_headquarters_name",
        "source_corporate_parent_name",
    ]
    keyed = frame[identity_columns].copy()
    for column in identity_columns:
        keyed[column] = keyed[column].map(company_key)

    aliases = keyed[["company_name", "fortune_2025_company"]].apply(
        lambda row: {value for value in row if value}, axis=1
    )
    hq_or_parent = pd.Series(False, index=frame.index)
    for column in ["source_headquarters_name", "source_corporate_parent_name"]:
        hq_or_parent |= keyed.apply(
            lambda row: bool(row[column]) and row[column] in aliases.loc[row.name], axis=1
        )

    exact_branch_business = keyed.apply(
        lambda row: bool(row["source_business_name"])
        and row["source_business_name"] in aliases.loc[row.name],
        axis=1,
    ) & frame["source_business_category"].isin(["Branch", "Headquarters"])
    return hq_or_parent | exact_branch_business


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assigned-locations-csv", required=True, type=Path)
    parser.add_argument("--coverage-template-csv", required=True, type=Path)
    parser.add_argument("--roster-csv", required=True, type=Path)
    parser.add_argument("--output-csv", required=True, type=Path)
    args = parser.parse_args()

    for path in [args.assigned_locations_csv, args.coverage_template_csv, args.roster_csv]:
        if not path.is_file():
            raise FileNotFoundError(path)
    reject_repo_output(args.output_csv)
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)

    roster = pd.read_csv(args.roster_csv, dtype={"msa": str})
    roster["msa"] = roster["msa"].str.zfill(5)
    template = pd.read_csv(args.coverage_template_csv, dtype={"msa_cbsa": str})
    template["msa_cbsa"] = template["msa_cbsa"].str.zfill(5)
    covered = template.loc[template["msa_cbsa"].isin(set(roster["msa"]))].copy()

    assigned = pd.read_csv(args.assigned_locations_csv, dtype={"msa_cbsa": str})
    assigned["msa_cbsa"] = assigned["msa_cbsa"].fillna("").str.zfill(5)
    assigned["fortune_rank_number"] = pd.to_numeric(assigned["fortune_2025_rank"], errors="coerce")
    assigned = assigned.loc[
        assigned["msa_cbsa"].isin(set(covered["msa_cbsa"]))
        & assigned["fortune_rank_number"].le(100)
        & assigned["fortune_match_status"].eq("matched")
    ].copy()
    assigned["has_high_confidence_identity"] = high_confidence_identity(assigned)
    assigned["site_function"] = assigned.apply(classify_site_function, axis=1)
    assigned["has_nonexcluded_site"] = ~assigned["site_function"].str.startswith("excluded_")
    assigned["is_eligible_high_confidence_candidate"] = (
        assigned["has_high_confidence_identity"] & assigned["has_nonexcluded_site"]
    )

    company = (
        assigned.groupby(["msa_cbsa", "msa_name", "fortune_2025_company"], as_index=False)
        .agg(
            high_confidence_location_rows=("has_high_confidence_identity", "sum"),
            high_confidence_nonexcluded_location_rows=("is_eligible_high_confidence_candidate", "sum"),
        )
        .assign(
            has_eligible_high_confidence_candidate=lambda frame: frame[
                "high_confidence_nonexcluded_location_rows"
            ].gt(0)
        )
    )
    scores = (
        company.groupby(["msa_cbsa", "msa_name"], as_index=False)
        .agg(
            distinct_high_confidence_current_f100_location_companies=(
                "high_confidence_location_rows", lambda values: values.gt(0).sum()
            ),
            **{TARGET: ("has_eligible_high_confidence_candidate", "sum")},
        )
    )
    output = covered[["msa_cbsa", "msa_name"]].drop_duplicates().merge(
        scores, on=["msa_cbsa", "msa_name"], how="left", validate="one_to_one"
    )
    numeric_columns = [
        "distinct_high_confidence_current_f100_location_companies",
        TARGET,
    ]
    output[numeric_columns] = output[numeric_columns].fillna(0).astype(int)
    output["source_coverage_status"] = "candidate_score_row_available"
    output["score_definition"] = (
        "Distinct current-Fortune-100 query labels with a high-confidence identity match "
        "and a nonexcluded Data Axle candidate site; not verified office presence"
    )
    output["identity_rule"] = (
        "Exact normalized headquarters/corporate-parent match, or exact normalized "
        "business-name match for Branch/Headquarters categories; no substring matching"
    )
    output["source_limitations"] = (
        "Source export has incomplete company and geographic coverage; use only as a "
        "source-covered diagnostic, not a national Fortune-office score"
    )
    output = output.sort_values("msa_cbsa")
    output.to_csv(args.output_csv, index=False)

    print(f"Covered roster MSAs: {len(output)}")
    print(f"Positive high-confidence candidate scores: {int(output[TARGET].gt(0).sum())}")
    print(f"Distinct eligible company labels: {company.loc[company['has_eligible_high_confidence_candidate'], 'fortune_2025_company'].nunique()}")
    print(f"Output: {args.output_csv.resolve()}")


if __name__ == "__main__":
    main()
