"""Assign an external company-location list to official MSAs and audit candidates.

This tool does *not* discover a comprehensive national office directory. It is
the reproducible geographic step after the team obtains a licensed or otherwise
authorized U.S. business-location export (for example, a Data Axle/Reference
Solutions export). It maps each street address to a Census county, joins that
county to the selected MSA, maps the company to the 2025 Fortune 500 universe,
and creates conservative office/retail/unknown candidate flags.

Because business-location databases are normally licensed, input and output
paths are required to be outside this Git repository. No row-level licensed
location data is written to the repo.

Expected input columns:
    source_record_id,company_name,street_address,city,state,postal_code

Optional columns:
    location_type,naics_code,source_url

Example:
    python3 Artem/scripts/geocode_company_locations_to_msas.py \
      --input-csv /external/fortune500_locations.csv \
      --output-dir /external/fortune500_msa_results \
      --source-name "Data Axle Reference Solutions"
"""

from __future__ import annotations

import argparse
import csv
import io
import re
import time
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests


ARTEM_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ARTEM_ROOT / "data" / "big_business_presence"
FORTUNE_PATH = DATA_DIR / "fortune_500_universe_2025.csv"
COUNTY_CROSSWALK_PATH = DATA_DIR / "metro_county_crosswalk_2023.csv"
CENSUS_BATCH_URL = "https://geocoding.geo.census.gov/geocoder/geographies/addressbatch"
CENSUS_BENCHMARK = "Public_AR_Current"
CENSUS_VINTAGE = "Current_Current"
REQUIRED_COLUMNS = {
    "source_record_id", "company_name", "street_address", "city", "state", "postal_code",
}
OPTIONAL_COLUMNS = {"location_type", "naics_code", "source_url"}


def normalize_company_name(value: str) -> str:
    """Normalize only superficial legal-suffix variation for exact F500 matching."""
    value = str(value).lower().replace("&", " and ")
    value = re.sub(r"\b(incorporated|inc|corporation|corp|company|co|llc|ltd|limited|plc)\b", "", value)
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def load_aliases(path: Path | None) -> dict[str, str]:
    """Load source-company-name → Fortune slug mappings supplied by a reviewer."""
    if path is None:
        return {}
    aliases = pd.read_csv(path, dtype=str, keep_default_na=False)
    if not {"source_company_name", "fortune_slug"}.issubset(aliases.columns):
        raise ValueError("Alias CSV requires source_company_name and fortune_slug columns.")
    return dict(zip(aliases["source_company_name"].map(normalize_company_name), aliases["fortune_slug"]))


def load_and_match_locations(input_path: Path, alias_path: Path | None) -> pd.DataFrame:
    """Validate the external extract and map exact company names to Fortune firms."""
    locations = pd.read_csv(input_path, dtype=str, keep_default_na=False)
    if missing := REQUIRED_COLUMNS.difference(locations.columns):
        raise ValueError(f"Input CSV is missing required columns: {sorted(missing)}")
    for column in OPTIONAL_COLUMNS.difference(locations.columns):
        locations[column] = ""
    if locations["source_record_id"].duplicated().any():
        raise ValueError("source_record_id must be unique in the imported location file.")

    fortune = pd.read_csv(FORTUNE_PATH, dtype=str, keep_default_na=False)
    fortune["normalized_company"] = fortune["company"].map(normalize_company_name)
    exact_map = fortune.set_index("normalized_company")["fortune_slug"].to_dict()
    name_map = fortune.set_index("fortune_slug")["company"].to_dict()
    aliases = load_aliases(alias_path)

    locations["normalized_company"] = locations["company_name"].map(normalize_company_name)
    locations["fortune_slug"] = locations["normalized_company"].map(aliases).fillna("")
    locations["fortune_match_method"] = locations["fortune_slug"].map(
        lambda value: "reviewer_alias" if value else ""
    )
    needs_exact = locations["fortune_slug"].eq("")
    locations.loc[needs_exact, "fortune_slug"] = locations.loc[needs_exact, "normalized_company"].map(exact_map).fillna("")
    locations.loc[needs_exact & locations["fortune_slug"].ne(""), "fortune_match_method"] = "normalized_exact_name"
    locations["fortune_company"] = locations["fortune_slug"].map(name_map).fillna("")
    locations["fortune_match_status"] = locations["fortune_slug"].map(
        lambda value: "matched" if value else "unmatched_needs_alias"
    )
    return locations


def chunks(values: list[str], size: int) -> Iterable[list[str]]:
    for start in range(0, len(values), size):
        yield values[start:start + size]


def census_batch_geocode(locations: pd.DataFrame, batch_size: int) -> pd.DataFrame:
    """Geocode source addresses in Census-compliant batches and retain every outcome."""
    locations = locations.copy()
    geocode_columns = [
        "census_matched_address", "census_match_indicator", "census_exact_indicator",
        "longitude", "latitude", "census_state_fips", "census_county_fips",
    ]
    for column in geocode_columns:
        locations[column] = ""
    eligible = locations[
        locations["fortune_match_status"].eq("matched")
        & locations["street_address"].str.strip().ne("")
    ].copy()
    if eligible.empty:
        return locations
    eligible["_input_row_index"] = eligible.index
    eligible["geocoder_id"] = [f"L{number:09d}" for number in range(1, len(eligible) + 1)]
    eligible = eligible.drop(columns=geocode_columns)
    results: list[dict[str, str]] = []

    for batch_number, batch_ids in enumerate(chunks(eligible["geocoder_id"].tolist(), batch_size), start=1):
        batch = eligible[eligible["geocoder_id"].isin(batch_ids)].copy()
        upload = io.StringIO()
        writer = csv.writer(upload, lineterminator="\n")
        for record in batch.itertuples(index=False):
            writer.writerow([record.geocoder_id, record.street_address, record.city, record.state, record.postal_code])
        response = requests.post(
            CENSUS_BATCH_URL,
            data={"benchmark": CENSUS_BENCHMARK, "vintage": CENSUS_VINTAGE},
            files={"addressFile": ("locations.csv", upload.getvalue(), "text/csv")},
            timeout=180,
        )
        response.raise_for_status()
        for row in csv.reader(io.StringIO(response.text)):
            # Census batches provide id, matched address, match indicator, exact
            # indicator, input address, coordinates, TIGER line, side, state,
            # county, tract, and block. Failed geocodes may have fewer fields.
            if not row:
                continue
            coordinates = row[5] if len(row) > 5 else ""
            longitude, latitude = (coordinates.split(",", maxsplit=1) + [""])[:2] if coordinates else ("", "")
            results.append(
                {
                    "geocoder_id": row[0],
                    "census_matched_address": row[1] if len(row) > 1 else "",
                    "census_match_indicator": row[2] if len(row) > 2 else "",
                    "census_exact_indicator": row[3] if len(row) > 3 else "",
                    "longitude": longitude,
                    "latitude": latitude,
                    "census_state_fips": row[8].zfill(2) if len(row) > 8 and row[8] else "",
                    "census_county_fips": row[9].zfill(3) if len(row) > 9 and row[9] else "",
                }
            )
        print(f"Census geocoded batch {batch_number}: {len(batch):,} records")
        # The public endpoint permits batches, but small pauses avoid treating it
        # as an unlimited bulk service.
        time.sleep(0.5)

    geocoded = pd.DataFrame(results)
    if geocoded.empty:
        geocoded = pd.DataFrame(columns=["geocoder_id", *geocode_columns])
    eligible = eligible.merge(geocoded, on="geocoder_id", how="left", validate="one_to_one")
    for column in geocode_columns:
        locations.loc[eligible["_input_row_index"].astype(int), column] = eligible[column].fillna("").to_numpy()
    return locations


def candidate_role(location_type: str, naics_code: str) -> str:
    """Produce a conservative candidate role, never a verified office classification."""
    text = f"{location_type} {naics_code}".lower()
    if str(naics_code).replace("-", "").replace(" ", "").startswith("551114"):
        return "candidate_qualifying_office"
    if re.search(r"\b(headquarters|hq|office|administrative|regional|engineering|technology|research|r\s*&\s*d|sales)\b", text):
        return "candidate_qualifying_office"
    if re.search(r"\b(store|retail|warehouse|distribution|fulfillment|plant|factory|airport|terminal)\b", text):
        return "candidate_retail_or_distribution"
    return "candidate_unknown_function"


def assign_msas(locations: pd.DataFrame) -> pd.DataFrame:
    """Join Census county codes to the official MSA county crosswalk."""
    crosswalk = pd.read_csv(COUNTY_CROSSWALK_PATH, dtype=str, keep_default_na=False)
    locations = locations.copy()
    locations["county_fips"] = locations["census_state_fips"] + locations["census_county_fips"]
    locations = locations.merge(
        crosswalk[["county_fips", "msa_cbsa", "metro_name"]],
        on="county_fips",
        how="left",
        validate="many_to_one",
    )
    locations["automated_location_role"] = locations.apply(
        lambda row: candidate_role(row["location_type"], row["naics_code"]), axis=1
    )
    locations["msa_assignment_status"] = "outside_selected_msas_or_not_geocoded"
    locations.loc[
        locations["census_match_indicator"].eq("Match") & locations["msa_cbsa"].notna(),
        "msa_assignment_status",
    ] = "matched_to_msa"
    locations["human_review_status"] = "needs_company_source_or_location_type_review"
    return locations


def summarize_candidates(locations: pd.DataFrame, source_name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Summarize candidate locations without treating them as a final office score."""
    matched = locations[
        locations["fortune_match_status"].eq("matched")
        & locations["msa_assignment_status"].eq("matched_to_msa")
    ].copy()
    if matched.empty:
        empty_company = pd.DataFrame(columns=["msa_cbsa", "metro_name", "fortune_slug", "fortune_company", "candidate_location_count", "automated_presence_class", "source_name"])
        empty_metro = pd.DataFrame(columns=["msa_cbsa", "metro_name", "companies_with_any_matched_location", "candidate_office_or_hq_companies", "candidate_retail_distribution_only_companies", "candidate_unknown_function_companies", "source_name", "publication_status"])
        return empty_company, empty_metro

    role_flags = matched.pivot_table(
        index=["msa_cbsa", "metro_name", "fortune_slug", "fortune_company"],
        columns="automated_location_role",
        values="source_record_id",
        aggfunc="count",
        fill_value=0,
    ).reset_index()
    for column in ["candidate_qualifying_office", "candidate_retail_or_distribution", "candidate_unknown_function"]:
        if column not in role_flags.columns:
            role_flags[column] = 0
    role_flags["candidate_location_count"] = role_flags[
        ["candidate_qualifying_office", "candidate_retail_or_distribution", "candidate_unknown_function"]
    ].sum(axis=1)
    role_flags["automated_presence_class"] = "candidate_unknown_function"
    role_flags.loc[role_flags["candidate_retail_or_distribution"].gt(0), "automated_presence_class"] = "candidate_retail_or_distribution_only"
    role_flags.loc[role_flags["candidate_qualifying_office"].gt(0), "automated_presence_class"] = "candidate_qualifying_office"
    role_flags["source_name"] = source_name
    company_summary = role_flags[
        ["msa_cbsa", "metro_name", "fortune_slug", "fortune_company", "candidate_location_count", "automated_presence_class", "source_name"]
    ].sort_values(["msa_cbsa", "fortune_company"])

    metro_summary = company_summary.groupby(["msa_cbsa", "metro_name"], as_index=False).agg(
        companies_with_any_matched_location=("fortune_slug", "nunique"),
        candidate_office_or_hq_companies=("automated_presence_class", lambda values: int((values == "candidate_qualifying_office").sum())),
        candidate_retail_distribution_only_companies=("automated_presence_class", lambda values: int((values == "candidate_retail_or_distribution_only").sum())),
        candidate_unknown_function_companies=("automated_presence_class", lambda values: int((values == "candidate_unknown_function").sum())),
    )
    metro_summary["source_name"] = source_name
    metro_summary["publication_status"] = "candidate_only_not_big_business_presence_score"
    return company_summary, metro_summary


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, encoding="utf-8", quoting=csv.QUOTE_MINIMAL)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-csv", required=True, type=Path, help="External standardized company-location CSV.")
    parser.add_argument("--output-dir", required=True, type=Path, help="Directory outside this repository for derived location data.")
    parser.add_argument("--source-name", required=True, help="Name of the authorized location-data source.")
    parser.add_argument("--alias-csv", type=Path, help="Optional reviewed source-company-name → Fortune slug mapping CSV.")
    parser.add_argument("--batch-size", type=int, default=5_000, help="Census geocoder records per request; maximum is 10,000.")
    args = parser.parse_args()
    if not 1 <= args.batch_size <= 10_000:
        raise ValueError("Batch size must be between 1 and 10,000.")
    if not FORTUNE_PATH.exists() or not COUNTY_CROSSWALK_PATH.exists():
        raise FileNotFoundError("Run build_big_business_presence_research.py first to create the Fortune universe and MSA crosswalk.")

    output_dir = args.output_dir.resolve()
    if output_dir.is_relative_to(ARTEM_ROOT.resolve()):
        raise ValueError("Use an output directory outside the Git repository for licensed or restricted location data.")
    locations = load_and_match_locations(args.input_csv, args.alias_csv)
    geocoded = census_batch_geocode(locations, args.batch_size)
    assigned = assign_msas(geocoded)
    company_summary, metro_summary = summarize_candidates(assigned, args.source_name)

    write_csv(assigned, output_dir / "fortune500_locations_geocoded_to_msa.csv")
    write_csv(company_summary, output_dir / "fortune500_company_msa_candidates.csv")
    write_csv(metro_summary, output_dir / "fortune500_metro_candidate_rollup.csv")
    print(f"Input locations: {len(locations):,}")
    print(f"Fortune 500 exact/alias matches: {(locations['fortune_match_status'] == 'matched').sum():,}")
    print(f"Locations assigned to selected MSAs: {(assigned['msa_assignment_status'] == 'matched_to_msa').sum():,}")
    print(f"Metro candidate rows: {len(metro_summary):,}")
    print("Outputs are candidates only; direct evidence/function review is still required for the Big Business Presence Score.")


if __name__ == "__main__":
    main()
