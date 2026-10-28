"""Standardize ArcGIS Business Analyst Data Axle POI exports for local analysis.

This is a local-processing helper, not a browser automation tool. It combines
Excel exports that were obtained through the ArcGIS interface, matches the
search term to the project Fortune 500 universe, and writes a single input file
for ``geocode_company_locations_to_msas.py``.

Licensed source rows and all derived location-level outputs must remain outside
this repository. The script therefore rejects an output directory within the
repository. It does not upload, scrape, or call ArcGIS/Data Axle.

Example:
    python3 Artem/scripts/ingest_arcgis_data_axle_exports.py \
      --input-dir /path/to/arcgis_exports \
      --output-dir /path/outside/repo/arcgis_data_axle_processed
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path

import pandas as pd


ARTEM_ROOT = Path(__file__).resolve().parents[1]
FORTUNE_PATH = ARTEM_ROOT / "data" / "big_business_presence" / "fortune_500_universe_2025.csv"
FILENAME_PREFIX = "Points of interest (POI) search - "
REQUIRED_EXPORT_COLUMNS = {
    "Company/Business Name",
    "City",
    "State Abbreviation",
    "ZIP Code",
    "Primary NAICS",
    "Industry Description",
    "Business Category",
    "Headquarters Name",
    "Corporate Parent Name",
    "Address *",
    "Esri Category Description",
    "Location Precision Level",
}

# ArcGIS query labels are not always the legal name used in Fortune's ranking.
# These are transparent entity-resolution decisions, kept in the output audit.
QUERY_NAME_TO_FORTUNE_COMPANY = {
    "american airlines": "American Airlines Group",
    "chevron": "Chevron",
    "cigna": "Cigna Group",
    "cisco": "Cisco Systems",
    "citibank": "Citigroup",
    "costco": "Costco Wholesale",
    "dell": "Dell Technologies",
    "enterprise products": "Enterprise Products Partners",
    "exxon mobil": "Exxon Mobil Holdings",
    "ford motor": "Ford Motor",
    "goldman sachs": "Goldman Sachs Group",
    "google": "Alphabet",
    "ibm": "International Business Machines",
    "john deere": "Deere",
    "liberty mutual": "Liberty Mutual Insurance Group",
    "merck": "Merck",
    "merck and": "Merck",
    "meta": "Meta Platforms",
    "nationwide mutual insurance": "Nationwide",
    "new york life insurance": "New York Life Insurance",
    "plains all american pipeline": "Plains GP Holdings",
    "progressive": "Progressive",
    "publix": "Publix Super Markets",
    "raytheon": "RTX",
    "rtx": "RTX",
    "state farm": "State Farm Insurance",
    "stonex": "StoneX Group",
    "the home depot": "Home Depot",
    "the walt disney": "Walt Disney",
    "united airlines": "United Airlines Holdings",
    "united parcel service": "UPS",
    "world fuel services": "World Kinect",
}


def normalize_company_name(value: str) -> str:
    """Normalize superficial legal-name variation without fuzzy matching."""
    value = str(value).lower().replace("&", " and ")
    value = re.sub(
        r"\b(incorporated|inc|corporation|corp|company|co|llc|ltd|limited|plc)\b",
        "",
        value,
    )
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def clean_rank(value: object) -> str:
    """Keep a Fortune rank as an integer-looking identifier in CSV outputs."""
    text = str(value).strip()
    try:
        return str(int(float(text)))
    except ValueError:
        return text


def query_name_from_path(path: Path) -> str:
    """Recover the human query name from ArcGIS' default export filename."""
    name = path.stem.removeprefix(FILENAME_PREFIX)
    return re.sub(r" \(\d+\)$", "", name).strip()


def source_file_key(path: Path) -> str:
    """Create a stable, readable identifier safe for a source-record ID."""
    return re.sub(r"[^a-z0-9]+", "_", query_name_from_path(path).lower()).strip("_")


def ensure_external_output(output_dir: Path) -> Path:
    output_dir = output_dir.resolve()
    if output_dir.is_relative_to(ARTEM_ROOT.resolve()):
        raise ValueError("Use an output directory outside the Git repository for licensed location data.")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def load_fortune_universe() -> pd.DataFrame:
    """Load the existing project Fortune universe without downloading anything."""
    if not FORTUNE_PATH.exists():
        raise FileNotFoundError(f"Missing Fortune universe: {FORTUNE_PATH}")
    fortune = pd.read_csv(FORTUNE_PATH, dtype=str, keep_default_na=False)
    required = {"company", "fortune_slug", "fortune_2025_rank"}
    missing = required.difference(fortune.columns)
    if missing:
        raise ValueError(f"Fortune universe is missing columns: {sorted(missing)}")
    fortune["normalized_company"] = fortune["company"].map(normalize_company_name)
    return fortune


def resolve_query_name(query_name: str, fortune: pd.DataFrame) -> dict[str, str]:
    """Map one saved ArcGIS query to a Fortune entity or flag it for review."""
    by_normalized = fortune.set_index("normalized_company")
    normalized_query = normalize_company_name(query_name)
    if normalized_query in by_normalized.index:
        row = by_normalized.loc[normalized_query]
        return {
            "fortune_company": str(row["company"]),
            "fortune_slug": str(row["fortune_slug"]),
            "fortune_2025_rank": clean_rank(row["fortune_2025_rank"]),
            "match_method": "normalized_exact_query_name",
            "match_status": "matched",
        }
    target_name = QUERY_NAME_TO_FORTUNE_COMPANY.get(normalized_query)
    if target_name is not None:
        target = fortune[fortune["company"].eq(target_name)]
        if len(target) != 1:
            raise ValueError(f"Manual alias target is not unique in Fortune universe: {target_name}")
        row = target.iloc[0]
        return {
            "fortune_company": str(row["company"]),
            "fortune_slug": str(row["fortune_slug"]),
            "fortune_2025_rank": clean_rank(row["fortune_2025_rank"]),
            "match_method": "reviewed_query_name_alias",
            "match_status": "matched",
        }
    return {
        "fortune_company": "",
        "fortune_slug": "",
        "fortune_2025_rank": "",
        "match_method": "unmatched_query_name",
        "match_status": "unmatched_needs_review",
    }


def text_or_empty(frame: pd.DataFrame, column: str) -> pd.Series:
    """Return a clean text column while retaining empty values as empty strings."""
    return frame[column].fillna("").astype(str).str.strip()


def combine_exports(input_dir: Path, fortune: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Read each Excel export and return standardized rows plus two audit tables."""
    files = sorted(input_dir.glob("*.xlsx"))
    if not files:
        raise FileNotFoundError(f"No .xlsx files found in {input_dir}")

    standardized_frames: list[pd.DataFrame] = []
    file_audit_rows: list[dict[str, object]] = []
    query_audit_rows: list[dict[str, object]] = []

    for file_number, path in enumerate(files, start=1):
        query_name = query_name_from_path(path)
        resolved = resolve_query_name(query_name, fortune)
        export = pd.read_excel(path, dtype=str, keep_default_na=False).fillna("")
        missing_columns = REQUIRED_EXPORT_COLUMNS.difference(export.columns)
        if missing_columns:
            raise ValueError(f"{path.name} is missing ArcGIS columns: {sorted(missing_columns)}")

        key = source_file_key(path)
        location_type_columns = [
            "Business Category",
            "Industry Description",
            "Esri Category Description",
            "Headquarters Name",
            "Corporate Parent Name",
        ]
        location_type = export[location_type_columns].astype(str).apply(
            lambda row: " | ".join(value.strip() for value in row if value.strip()), axis=1
        )
        address = text_or_empty(export, "Address *")
        source_ids = [f"arcgis_data_axle_{key}_{row:06d}" for row in range(1, len(export) + 1)]
        standardized = pd.DataFrame(
            {
                "source_record_id": source_ids,
                # The query entity, not a subsidiary's listing name, is the
                # entity tested against the Fortune universe.
                "company_name": resolved["fortune_company"] or query_name,
                "street_address": address,
                "city": text_or_empty(export, "City"),
                "state": text_or_empty(export, "State Abbreviation"),
                "postal_code": text_or_empty(export, "ZIP Code"),
                "location_type": location_type,
                "naics_code": text_or_empty(export, "Primary NAICS"),
                "source_url": "ArcGIS Business Analyst Data Axle POI export",
                "query_company_name": query_name,
                "source_business_name": text_or_empty(export, "Company/Business Name"),
                "source_headquarters_name": text_or_empty(export, "Headquarters Name"),
                "source_corporate_parent_name": text_or_empty(export, "Corporate Parent Name"),
                "source_business_category": text_or_empty(export, "Business Category"),
                "source_industry_description": text_or_empty(export, "Industry Description"),
                "source_esri_category_description": text_or_empty(export, "Esri Category Description"),
                "source_location_precision_level": text_or_empty(export, "Location Precision Level"),
                "source_employee_count": text_or_empty(export, "Employee Count"),
                "source_sales_volume": text_or_empty(export, "Sales Volume"),
                "source_export_file": path.name,
                "fortune_2025_company": resolved["fortune_company"],
                "fortune_slug": resolved["fortune_slug"],
                "fortune_2025_rank": resolved["fortune_2025_rank"],
                "fortune_match_method": resolved["match_method"],
                "fortune_match_status": resolved["match_status"],
                # ArcGIS marks Address with an asterisk and its documentation
                # explains that street numbers are removed in Data Axle exports.
                "address_geocode_quality": address.map(
                    lambda value: "has_street_number" if re.search(r"\d", value) else "street_number_redacted_or_missing"
                ),
            }
        )
        standardized_frames.append(standardized)
        file_audit_rows.append(
            {
                "source_export_file": path.name,
                "query_company_name": query_name,
                "location_rows": len(export),
                "hit_arcgis_result_cap_5000": len(export) == 5000,
                "street_number_redacted_or_missing_rows": int(
                    standardized["address_geocode_quality"].eq("street_number_redacted_or_missing").sum()
                ),
                **resolved,
            }
        )
        query_audit_rows.append({"query_company_name": query_name, **resolved})

    combined = pd.concat(standardized_frames, ignore_index=True)
    file_audit = pd.DataFrame(file_audit_rows).sort_values("query_company_name")
    query_audit = (
        pd.DataFrame(query_audit_rows)
        .drop_duplicates("query_company_name")
        .sort_values("query_company_name")
    )
    return combined, file_audit, query_audit


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    frame.to_csv(path, index=False, encoding="utf-8", quoting=csv.QUOTE_MINIMAL)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", required=True, type=Path, help="Folder containing ArcGIS POI .xlsx exports.")
    parser.add_argument("--output-dir", required=True, type=Path, help="Licensed-data output folder outside the repository.")
    args = parser.parse_args()

    input_dir = args.input_dir.resolve()
    if not input_dir.is_dir():
        raise NotADirectoryError(f"Input directory does not exist: {input_dir}")
    output_dir = ensure_external_output(args.output_dir)
    fortune = load_fortune_universe()
    combined, file_audit, query_audit = combine_exports(input_dir, fortune)

    write_csv(combined, output_dir / "arcgis_data_axle_standardized_locations.csv")
    write_csv(file_audit, output_dir / "arcgis_data_axle_export_file_audit.csv")
    write_csv(query_audit, output_dir / "arcgis_data_axle_query_to_fortune_audit.csv")

    cap_files = int(file_audit["hit_arcgis_result_cap_5000"].sum())
    matched_queries = int(query_audit["match_status"].eq("matched").sum())
    print(f"ArcGIS export files: {len(file_audit):,}")
    print(f"Combined location rows: {len(combined):,}")
    print(f"Distinct query companies: {len(query_audit):,}")
    print(f"Queries matched to 2025 Fortune 500: {matched_queries:,}")
    print(f"Exports at ArcGIS' 5,000-result cap: {cap_files:,}")
    print("Location-level outputs were written outside the repository.")


if __name__ == "__main__":
    main()
