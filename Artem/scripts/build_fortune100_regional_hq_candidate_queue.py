"""Build a licensed-only Fortune 100 HQ/regional-office review queue.

The ArcGIS/Data Axle POI exports are licensed and ignored by Git. This script
reads them locally, creates candidate and coverage files only under the
separate licensed-data directory, and never writes location-level output to
the repository. A Branch record is only a candidate regional-office record;
it must be confirmed by a company source before being called a regional HQ.
"""

from __future__ import annotations

from pathlib import Path
import re
import warnings

import pandas as pd


ARTEM = Path(__file__).resolve().parents[1]
SOURCE = ARTEM / "data" / "fortune-100-data"
OUTPUT = Path("/Users/society/Documents/InvestAtlanta_Licensed_Data") / "fortune100_regional_hq_candidate_queue_2026-11-05"

ALIASES = {
    "UnitedHealth Group": ["UnitedHealth"],
    "McKesson Corporation": ["McKesson"],
    "AmerisourceBergen": ["Cencora"],
    "Alphabet": ["Google", "Alphabet"],
    "Meta Platforms": ["Meta"],
    "Citigroup": ["Citibank"],
    "Target Corporation": ["Target"],
    "Dell Technologies": ["Dell"],
    "Bunge Limited": ["Bunge"],
    "RTX Corporation": ["Raytheon", "RTX Corporation"],
    "StoneX Group": ["StoneX "],
    "Dow Chemical Company": ["Dow "],
    "Procter & Gamble": ["Procter & Gamble", "Procter & Gamble (1)"],
}

OFFICE_LIKE_SECTORS = {
    "Finance & Insurance",
    "Information",
    "Professional, Scientific & Tech Services",
    "Management of Companies & Enterprises",
    "Administrative & Support & Waste Management & Remediation Services",
    "Real Estate and Rental and Leasing",
    "Wholesale Trade",
}

NON_OFFICE_TERMS = (
    "retail",
    "store",
    "grocery",
    "pharmacy",
    "warehouse",
    "distribution",
    "shipping",
    "mailing",
    "restaurant",
    "hotel",
    "gas station",
    "convenience",
)

# These terms are an efficient way to prioritize a reviewer’s queue.  They are
# not proof that the site is a regional headquarters: only a company-owned or
# similarly authoritative source can establish that classification.
REGIONAL_OPERATION_TERMS = re.compile(
    r"\b(regional|region|divisional|division|district|territory|area office|operating hub)\b",
    flags=re.IGNORECASE,
)


def source_filename(name: str) -> Path:
    return SOURCE / f"Points of interest (POI) search - {name}.xlsx"


def normalize_text(value: object) -> str:
    return " ".join(str(value or "").lower().split())


def is_non_office(row: pd.Series) -> bool:
    text = " ".join(
        normalize_text(row.get(column, ""))
        for column in ("Industry Description", "Esri Category Description", "Primary NAICS")
    )
    return any(term in text for term in NON_OFFICE_TERMS)


def main() -> None:
    warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    roster = pd.read_csv(SOURCE / "List of largest companies in the United States.csv")
    coverage_rows: list[dict[str, object]] = []
    candidates: list[pd.DataFrame] = []

    for row in roster.itertuples(index=False):
        company = row.Name
        names = [company] + ALIASES.get(company, [])
        files = [source_filename(name) for name in names if source_filename(name).exists()]
        coverage_rows.append(
            {
                "fortune_rank": row.Rank,
                "fortune_company": company,
                "source_files_found": len(files),
                "source_file_names": "; ".join(path.name for path in files),
                "coverage_status": "available" if files else "missing_source_file",
                "review_note": (
                    "Run a licensed ArcGIS Places/Data Axle search for this company or current corporate name."
                    if not files else "Candidate locations screened; public regional-HQ verification still required."
                ),
            }
        )
        for path in files:
            data = pd.read_excel(path, engine="openpyxl")
            if data.empty:
                continue
            data["fortune_rank"] = row.Rank
            data["fortune_company"] = company
            data["source_file"] = path.name
            data["employee_count_numeric"] = pd.to_numeric(data["Employee Count"], errors="coerce")
            data["location_confidence_ok"] = data["Location Confidence"].isin(["High", "Very High"])
            data["non_office_signal"] = data.apply(is_non_office, axis=1)
            data["regional_keyword_signal"] = data.apply(
                lambda record: bool(
                    REGIONAL_OPERATION_TERMS.search(
                        " ".join(
                            str(record.get(column, ""))
                            for column in ("Company/Business Name", "Industry Description", "Esri Category Description")
                        )
                    )
                ),
                axis=1,
            )
            data["candidate_type"] = pd.NA

            hq = (data["Business Category"] == "Headquarters") & data["location_confidence_ok"]
            data.loc[hq, "candidate_type"] = "data_axle_headquarters_candidate"

            branch = (
                (data["Business Category"] == "Branch")
                & data["location_confidence_ok"]
                & data["NAICS Industry Sector"].isin(OFFICE_LIKE_SECTORS)
                & (data["employee_count_numeric"] >= 100)
                & ~data["non_office_signal"]
            )
            data.loc[branch, "candidate_type"] = "large_office_like_branch_candidate"

            subset = data[data["candidate_type"].notna()].copy()
            if not subset.empty:
                subset["regional_hq_status"] = "unknown_needs_company_source"
                subset["review_rule"] = (
                    "Confirm a regional-HQ, divisional-HQ, operating-hub, or office function with a company website,"
                    " press release, SEC filing, or comparable first-party source."
                )
                candidates.append(subset)

    coverage = pd.DataFrame(coverage_rows).sort_values("fortune_rank")
    coverage.to_csv(OUTPUT / "fortune100_source_file_coverage.csv", index=False)
    if candidates:
        result = pd.concat(candidates, ignore_index=True)
        columns = [
            "fortune_rank", "fortune_company", "source_file", "Company/Business Name", "City",
            "State Abbreviation", "ZIP Code", "Business Category", "Headquarters Name",
            "Corporate Parent Name", "NAICS Industry Sector", "Industry Description",
            "Esri Category Description", "Employee Count", "Square Footage", "Location Confidence",
            "Location Precision Level", "candidate_type", "regional_keyword_signal", "regional_hq_status", "review_rule",
        ]
        result = result[columns].drop_duplicates().sort_values(
            ["candidate_type", "Employee Count"], ascending=[True, False]
        )
        result.to_csv(OUTPUT / "fortune100_hq_or_large_office_candidates.csv", index=False)

        # This row-level licensed file is intentionally external-only.  It is
        # the input to the existing city-place-centroid → MSA assignment tool;
        # its results remain candidates until a reviewer verifies function and
        # regional-HQ status from a company source.
        msa_input = result.reset_index(drop=True).rename(
            columns={
                "fortune_company": "company_name",
                "City": "city",
                "State Abbreviation": "state",
                "ZIP Code": "postal_code",
                "Business Category": "source_business_category",
                "Industry Description": "source_industry_description",
                "Esri Category Description": "source_esri_category_description",
            }
        )
        msa_input.insert(0, "source_record_id", [f"f100-candidate-{index:06d}" for index in range(1, len(msa_input) + 1)])
        msa_input.to_csv(OUTPUT / "fortune100_hq_candidates_for_msa_assignment.csv", index=False)

        summary = (
            result.groupby("candidate_type", as_index=False)
            .agg(
                candidate_records=("fortune_company", "size"),
                distinct_companies=("fortune_company", "nunique"),
                records_with_regional_keyword_signal=("regional_keyword_signal", "sum"),
            )
        )
        summary.to_csv(OUTPUT / "candidate_queue_summary.csv", index=False)
    else:
        pd.DataFrame(columns=["candidate_type", "candidate_records", "distinct_companies"]).to_csv(
            OUTPUT / "candidate_queue_summary.csv", index=False
        )

    print(f"Wrote licensed-only outputs to: {OUTPUT}")
    print(coverage["coverage_status"].value_counts().to_string())
    print(pd.read_csv(OUTPUT / "candidate_queue_summary.csv").to_string(index=False))


if __name__ == "__main__":
    main()
