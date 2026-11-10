#!/usr/bin/env python3
"""Link external regional-HQ candidates to the public current Fortune 500 list.

The source candidate queue contains licensed Data Axle-derived location leads.
This script writes its output only outside the repository and marks every row
as unverified.  It is a research bridge between the current Fortune 500 model
universe and the regional/divisional HQ verification process—not an outcome
builder and not an office-presence score.
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

import pandas as pd


ARTEM = Path(__file__).resolve().parents[1]
REPO_ROOT = ARTEM.parent
DEFAULT_FORTUNE = ARTEM / "data" / "big_business_presence" / "fortune_500_universe_2025.csv"

# The source Fortune-100 roster uses a few historic or legal company labels.
# Keep aliases deliberately small and transparent rather than fuzzy-matching
# unrelated corporate entities.
SOURCE_TO_CURRENT_F500_ALIASES = {
    "AmerisourceBergen": "Cencora",
    "McKesson Corporation": "McKesson",
    "RTX Corporation": "RTX",
    "Citigroup": "Citi",
    "Target Corporation": "Target",
    "Bunge Limited": "Bunge Global SA",
    "Dow Chemical Company": "Dow",
    "Procter & Gamble": "Procter & Gamble",
    "StoneX Group": "StoneX Group",
}


def normalize(value: object) -> str:
    text = str(value or "").lower().replace("&", " and ")
    text = re.sub(r"\b(incorporated|inc|corporation|corp|company|co|llc|ltd|limited|plc)\b", "", text)
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text).split())


def external_output(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    try:
        resolved.relative_to(REPO_ROOT)
    except ValueError:
        resolved.mkdir(parents=True, exist_ok=True)
        return resolved
    raise ValueError("Licensed or derived regional-HQ outputs must be outside the repository.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--regional-candidate-queue", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--fortune-csv", type=Path, default=DEFAULT_FORTUNE)
    args = parser.parse_args()
    for path in [args.regional_candidate_queue, args.fortune_csv]:
        if not path.expanduser().is_file():
            raise FileNotFoundError(path)
    output = external_output(args.output_dir)

    fortune = pd.read_csv(args.fortune_csv, dtype=str, keep_default_na=False)
    candidates = pd.read_csv(args.regional_candidate_queue, dtype={"msa_cbsa": str}, keep_default_na=False)
    required = {
        "msa_cbsa", "msa_name", "fortune_company", "hq_category_candidate_records",
        "large_office_candidate_records", "regional_keyword_candidate_records",
        "regional_hq_verification_status",
    }
    missing = required - set(candidates.columns)
    if missing:
        raise ValueError(f"Candidate queue is missing: {sorted(missing)}")

    fortune["match_key"] = fortune["company"].map(normalize)
    if fortune["match_key"].duplicated().any():
        raise ValueError("Current Fortune 500 normalized company names are not unique.")
    current_lookup = fortune.set_index("match_key")[
        ["fortune_2025_rank", "fortune_2025_list_position", "company", "fortune_slug"]
    ]

    candidates["source_company_name"] = candidates["fortune_company"]
    candidates["candidate_match_key"] = candidates["fortune_company"].map(
        lambda value: normalize(SOURCE_TO_CURRENT_F500_ALIASES.get(str(value), value))
    )
    linked = candidates.merge(
        current_lookup,
        left_on="candidate_match_key",
        right_index=True,
        how="left",
        validate="many_to_one",
    )
    linked["fortune500_match_status"] = "unmatched_needs_entity_review"
    linked.loc[
        linked["fortune_slug"].notna() & linked["fortune_slug"].astype(str).str.strip().ne(""),
        "fortune500_match_status",
    ] = "matched_current_f500"
    linked["regional_hq_model_eligibility"] = "excluded_until_company_source_verifies_function"
    linked["review_priority"] = "standard"
    linked.loc[linked["regional_keyword_candidate_records"].astype(int).gt(0), "review_priority"] = "highest_explicit_regional_keyword"
    linked.loc[
        linked["review_priority"].eq("standard") & linked["hq_category_candidate_records"].astype(int).gt(0),
        "review_priority",
    ] = "high_hq_category_candidate"
    linked["required_evidence"] = (
        "Company website, dated company press release, SEC filing, or comparably authoritative source "
        "that confirms regional/divisional HQ or qualifying corporate-office function."
    )

    columns = [
        "fortune_2025_rank", "fortune_2025_list_position", "company", "fortune_slug",
        "msa_cbsa", "msa_name", "source_company_name", "hq_category_candidate_records",
        "large_office_candidate_records", "regional_keyword_candidate_records", "review_priority",
        "fortune500_match_status", "regional_hq_verification_status", "regional_hq_model_eligibility",
        "required_evidence",
    ]
    ledger = linked[columns].sort_values(["review_priority", "msa_name", "company"], kind="stable")
    ledger.to_csv(output / "fortune500_regional_hq_candidate_verification_ledger.csv", index=False, quoting=csv.QUOTE_MINIMAL)

    audit = (
        linked.groupby("fortune500_match_status", as_index=False)
        .agg(company_msa_candidate_rows=("source_company_name", "size"), source_companies=("source_company_name", "nunique"))
    )
    audit.to_csv(output / "fortune500_regional_hq_candidate_match_audit.csv", index=False, quoting=csv.QUOTE_MINIMAL)
    print(audit.to_string(index=False))
    print(f"Output: {output}")


if __name__ == "__main__":
    main()
