"""Build the public research scaffold for the Metro Big Business Presence Score.

The outcome is *not* employer-establishment entry.  It is the number of
distinct 2025 Fortune 500 firms with a source-verified qualifying headquarters
or office in a metropolitan area.

This script downloads Fortune's public 2025 *ranking* page,
extracts its embedded ranking data, and produces an auditable 500-company by
200-MSA review queue. All presence cells begin as ``unreviewed``. The
companion score-status file intentionally leaves scores blank until every
company/metro cell has been reviewed or an explicit scope decision is made.

Run from the repository root:
    python3 Artem/scripts/build_big_business_presence_research.py
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from pathlib import Path
from typing import Any

import pandas as pd
from bs4 import BeautifulSoup


ARTEM_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ARTEM_ROOT / "data" / "big_business_presence"
RAW_DIR = OUTPUT_DIR / "raw_inputs"
BDS_PATH = (
    ARTEM_ROOT
    / "data"
    / "business_entry_models"
    / "raw_inputs"
    / "census_bds_2023_msa.csv"
)
DELINEATION_PATH = (
    ARTEM_ROOT
    / "data"
    / "business_entry_models"
    / "raw_inputs"
    / "census_cbsa_delineation_list1_2023.xlsx"
)
VERIFIED_ATLANTA_SOURCES_PATH = ARTEM_ROOT / "data" / "verified_location_sources.csv"
ATLANTA_SCREEN_PATH = ARTEM_ROOT / "data" / "fortune_100_atlanta_presence_2025.csv"
ATLANTA_CBSA = "12060"

FORTUNE_RANKING_URL = "https://fortune.com/ranking/fortune500/2025/"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
)

REVIEW_COLUMNS = [
    "fortune_2025_list_position",
    "fortune_2025_rank",
    "company",
    "fortune_slug",
    "msa_cbsa",
    "metro_name",
    "office_presence_class",
    "review_status",
    "evidence_url",
    "evidence_publisher",
    "source_published_or_accessed",
    "street_address",
    "municipality",
    "qualifying_rationale",
    "reviewer_notes",
]


def fetch_ranking_page(refresh: bool) -> str:
    """Fetch Fortune's public 2025 ranking page and retain it as provenance.

    The separate directory API exposes a live company-profile revenue field;
    it is not the historical ranking field. The ranking page embeds the actual
    2025 list, including the rank and FY2024 revenue used by Fortune.
    """
    destination = RAW_DIR / "fortune_2025_ranking_page.html"
    if destination.exists() and not refresh:
        return destination.read_text(encoding="utf-8")

    completed = subprocess.run(
        [
            "curl",
            "--fail",
            "--location",
            "--silent",
            "--show-error",
            "--max-time",
            "60",
            "-A",
            USER_AGENT,
            "-H",
            "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            FORTUNE_RANKING_URL,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(completed.stdout, encoding="utf-8")
    return completed.stdout


def revenue_to_millions(value: object) -> float:
    """Convert Fortune's displayed dollar amount, expressed in millions, to float."""
    cleaned = re.sub(r"[^0-9.]", "", str(value or ""))
    if not cleaned:
        raise ValueError(f"Missing or unparseable revenue: {value!r}")
    return float(cleaned)


def build_fortune_universe(refresh: bool) -> pd.DataFrame:
    """Extract the official 2025 Fortune 500 rank order from the public page."""
    page = fetch_ranking_page(refresh)
    soup = BeautifulSoup(page, "html.parser")
    data_tag = soup.find("script", id="__NEXT_DATA__")
    if data_tag is None or not data_tag.string:
        raise ValueError("The Fortune ranking page has no embedded Next.js data.")
    payload = json.loads(data_tag.string)
    try:
        items = payload["props"]["pageProps"]["franchiseSearch"]["items"]
    except KeyError as error:
        raise ValueError("The Fortune ranking page no longer contains ranking items.") from error

    rows: list[dict[str, object]] = []
    for item in items:
        position = item.get("order")
        rank = item.get("rank")
        if not isinstance(position, int) or not 1 <= position <= 500:
            continue
        attributes = item.get("data", {})
        slug_path = str(item["slug"])
        rows.append(
            {
                "fortune_2025_list_position": position,
                "fortune_2025_rank": rank,
                "company": item["name"],
                "fortune_slug": slug_path.strip("/").removeprefix("company/"),
                "revenue_usd_millions": revenue_to_millions(attributes.get("Revenues ($M)")),
                "fortune_permalink": f"https://fortune.com{slug_path}",
                "headquarters_city": attributes.get("Headquarters City", ""),
                "headquarters_state": attributes.get("State", ""),
                "industry": attributes.get("Industry", ""),
            }
        )
    universe = pd.DataFrame(rows).sort_values("fortune_2025_list_position").reset_index(drop=True)
    if len(universe) != 500 or set(universe["fortune_2025_list_position"]) != set(range(1, 501)):
        raise ValueError("Expected exactly one company at every Fortune 2025 list position from 1 through 500.")
    expected_top_ten = [
        "Walmart", "Amazon", "UnitedHealth Group", "Apple", "CVS Health",
        "Berkshire Hathaway", "Alphabet", "Exxon Mobil Holdings", "McKesson", "Cencora",
    ]
    if universe.head(10)["company"].tolist() != expected_top_ten:
        raise ValueError("Top-ten validation failed; do not treat this as the 2025 Fortune 500 list.")
    universe["ranking_source_url"] = FORTUNE_RANKING_URL
    return universe[
        [
            "fortune_2025_rank",
            "fortune_2025_list_position",
            "company",
            "fortune_slug",
            "revenue_usd_millions",
            "fortune_permalink",
            "headquarters_city",
            "headquarters_state",
            "industry",
            "ranking_source_url",
        ]
    ]


def load_delineation() -> pd.DataFrame:
    """Read the official July 2023 Census county-to-CBSA delineation table."""
    if not DELINEATION_PATH.exists():
        raise FileNotFoundError(f"Missing Census CBSA delineation table: {DELINEATION_PATH}")
    delineation = pd.read_excel(DELINEATION_PATH, header=2)
    delineation.columns = [str(column).strip() for column in delineation.columns]
    delineation["CBSA Code"] = pd.to_numeric(delineation["CBSA Code"], errors="coerce")
    delineation["FIPS State Code"] = pd.to_numeric(delineation["FIPS State Code"], errors="coerce")
    delineation["FIPS County Code"] = pd.to_numeric(delineation["FIPS County Code"], errors="coerce")
    return delineation.dropna(subset=["CBSA Code", "FIPS State Code", "FIPS County Code"]).copy()


def build_default_metro_roster(metro_count: int) -> pd.DataFrame:
    """Select the largest requested number of official MSAs by 2023 BDS establishments."""
    if metro_count < 1:
        raise ValueError("Metro count must be positive.")
    if not BDS_PATH.exists():
        raise FileNotFoundError(f"Missing public BDS MSA data: {BDS_PATH}")
    bds = pd.read_csv(BDS_PATH, usecols=["year", "msa", "estabs"], low_memory=False)
    bds["msa"] = pd.to_numeric(bds["msa"], errors="coerce")
    bds["estabs"] = pd.to_numeric(bds["estabs"], errors="coerce")
    latest = bds[bds["year"].eq(2023)].dropna(subset=["msa", "estabs"])

    delineation = load_delineation()
    metros = delineation[
        delineation["Metropolitan/Micropolitan Statistical Area"].eq("Metropolitan Statistical Area")
    ].copy()
    metadata = (
        metros.groupby("CBSA Code", as_index=False)
        .agg(
            metro_name=("CBSA Title", "first"),
            member_states=("State Name", lambda values: "; ".join(sorted(set(values)))),
        )
        .rename(columns={"CBSA Code": "msa"})
    )
    roster = (
        latest.merge(metadata, on="msa", how="inner")
        .nlargest(metro_count, "estabs")
        .sort_values("estabs", ascending=False)
        .reset_index(drop=True)
        .rename(columns={"msa": "msa_cbsa", "estabs": "establishments_2023"})
    )
    roster["msa_cbsa"] = roster["msa_cbsa"].astype(int).astype(str).str.zfill(5)
    roster["selection_method"] = f"Top {metro_count} MSAs by 2023 Census BDS establishments"
    if len(roster) != metro_count or roster["msa_cbsa"].nunique() != metro_count:
        raise ValueError(f"Could not construct {metro_count} distinct MSAs from the public BDS roster.")
    return roster[["msa_cbsa", "metro_name", "member_states", "establishments_2023", "selection_method"]]


def load_custom_metro_roster(path: Path) -> pd.DataFrame:
    """Accept a user-supplied MSA roster instead of the default top-200 selection."""
    roster = pd.read_csv(path, dtype=str, keep_default_na=False)
    code_column = "msa_cbsa" if "msa_cbsa" in roster.columns else "msa"
    title_column = "metro_name" if "metro_name" in roster.columns else "msa_title"
    if code_column not in roster.columns or title_column not in roster.columns:
        raise ValueError("Custom roster needs msa_cbsa (or msa) and metro_name (or msa_title) columns.")
    roster = roster.rename(columns={code_column: "msa_cbsa", title_column: "metro_name"})
    roster["msa_cbsa"] = roster["msa_cbsa"].astype(str).str.replace(r"\\.0$", "", regex=True).str.zfill(5)
    roster = roster[["msa_cbsa", "metro_name"]].drop_duplicates("msa_cbsa")
    if roster.empty:
        raise ValueError("Custom MSA roster has no usable rows.")
    roster["selection_method"] = f"Custom roster from {path.name}"
    return roster


def build_county_crosswalk(metros: pd.DataFrame) -> pd.DataFrame:
    """Create an MSA county crosswalk for assigning geocoded locations."""
    delineation = load_delineation()
    delineation = delineation[
        delineation["Metropolitan/Micropolitan Statistical Area"].eq("Metropolitan Statistical Area")
    ].copy()
    delineation["msa_cbsa"] = delineation["CBSA Code"].astype(int).astype(str).str.zfill(5)
    delineation["county_fips"] = (
        delineation["FIPS State Code"].astype(int).astype(str).str.zfill(2)
        + delineation["FIPS County Code"].astype(int).astype(str).str.zfill(3)
    )
    crosswalk = delineation[delineation["msa_cbsa"].isin(metros["msa_cbsa"])][
        ["county_fips", "msa_cbsa", "CBSA Title", "State Name", "County/County Equivalent", "Central/Outlying County"]
    ].rename(
        columns={
            "CBSA Title": "metro_name",
            "State Name": "county_state",
            "County/County Equivalent": "county_name",
            "Central/Outlying County": "county_role",
        }
    )
    if crosswalk["county_fips"].duplicated().any():
        raise ValueError("A county was assigned to more than one selected MSA.")
    return crosswalk.sort_values(["msa_cbsa", "county_fips"]).reset_index(drop=True)


def build_review_queue(fortune: pd.DataFrame, metros: pd.DataFrame) -> pd.DataFrame:
    """Create one auditable decision cell per Fortune 500 company and metro."""
    fortune_key = fortune[["fortune_2025_list_position", "fortune_2025_rank", "company", "fortune_slug"]].copy()
    fortune_key["_key"] = 1
    metro_key = metros.copy()
    metro_key["_key"] = 1
    queue = fortune_key.merge(metro_key, on="_key", how="inner").drop(columns="_key")
    queue["office_presence_class"] = "unreviewed"
    queue["review_status"] = "not_started"
    for column in REVIEW_COLUMNS[8:]:
        queue[column] = ""
    queue = queue[REVIEW_COLUMNS].sort_values(
        ["msa_cbsa", "fortune_2025_list_position"], kind="stable"
    )
    expected_cells = len(fortune) * len(metros)
    if len(queue) != expected_cells:
        raise ValueError(f"Expected {expected_cells:,} review cells, created {len(queue):,}.")
    return queue


def preserve_existing_reviews(queue: pd.DataFrame) -> pd.DataFrame:
    """Retain completed manual reviews when the public universe is rebuilt."""
    existing_path = OUTPUT_DIR / "fortune500_metro_presence_review_queue.csv"
    if not existing_path.exists():
        return queue
    existing = pd.read_csv(existing_path, dtype=str, keep_default_na=False)
    if not set(REVIEW_COLUMNS).issubset(existing.columns):
        return queue
    existing = existing[REVIEW_COLUMNS].copy()
    completed = existing[
        existing["review_status"].isin({"verified", "needs_follow_up", "scope_complete_no_presence"})
        | existing["office_presence_class"].isin(
            {"qualifying_hq", "qualifying_office", "retail_or_distribution_only", "no_verified_material_presence"}
        )
    ].drop_duplicates(subset=["fortune_slug", "msa_cbsa"], keep="last")
    if completed.empty:
        return queue

    queue = queue.set_index(["fortune_slug", "msa_cbsa"], drop=False)
    completed = completed.set_index(["fortune_slug", "msa_cbsa"], drop=False)
    shared = queue.index.intersection(completed.index)
    evidence_columns = [
        "office_presence_class", "review_status", "evidence_url", "evidence_publisher",
        "source_published_or_accessed", "street_address", "municipality",
        "qualifying_rationale", "reviewer_notes",
    ]
    for column in evidence_columns:
        queue.loc[shared, column] = completed.loc[shared, column]
    return queue.reset_index(drop=True)


def seed_verified_atlanta_evidence(queue: pd.DataFrame, fortune: pd.DataFrame) -> pd.DataFrame:
    """Import the existing direct company-source checks as an initial evidence set.

    These seven rows have direct company URLs in the older Atlanta screen. The
    function does not infer any negative results and does not overwrite a later
    human review of the same company-metro cell.
    """
    if not VERIFIED_ATLANTA_SOURCES_PATH.exists() or not ATLANTA_SCREEN_PATH.exists():
        return queue
    sources = pd.read_csv(VERIFIED_ATLANTA_SOURCES_PATH, dtype=str, keep_default_na=False)
    screen = pd.read_csv(ATLANTA_SCREEN_PATH, dtype=str, keep_default_na=False)
    screen = screen[screen["evidence_status"].eq("company_source_checked")].copy()
    seeds = sources.merge(
        screen[["fortune_2025_rank", "presence_type", "geography"]],
        on="fortune_2025_rank",
        how="inner",
        validate="one_to_one",
    )
    if len(seeds) != 7:
        raise ValueError("Expected seven direct company-source Atlanta checks in the existing screen.")

    rank_to_slug = fortune.set_index("fortune_2025_rank")["fortune_slug"].to_dict()
    queue = queue.set_index(["fortune_slug", "msa_cbsa"], drop=False)
    for row in seeds.itertuples(index=False):
        rank = int(row.fortune_2025_rank)
        slug = rank_to_slug.get(rank)
        key = (slug, ATLANTA_CBSA)
        if slug is None or key not in queue.index:
            raise ValueError(f"Could not map existing Atlanta evidence at Fortune rank {rank}.")
        if queue.loc[key, "review_status"] != "not_started":
            continue
        is_hq = str(row.presence_type).strip().lower() == "headquarters"
        queue.loc[key, "office_presence_class"] = "qualifying_hq" if is_hq else "qualifying_office"
        queue.loc[key, "review_status"] = "verified"
        queue.loc[key, "evidence_url"] = row.source_url
        queue.loc[key, "evidence_publisher"] = "company_owned_source"
        queue.loc[key, "source_published_or_accessed"] = "existing public screen; audit date not retained"
        queue.loc[key, "street_address"] = row.verified_location
        queue.loc[key, "municipality"] = (
            "Atlanta" if row.geography == "City of Atlanta" else "Metro Atlanta; municipality to confirm from address"
        )
        queue.loc[key, "qualifying_rationale"] = str(row.presence_type).replace("_", " ")
        queue.loc[key, "reviewer_notes"] = "Imported from existing direct company-source Atlanta evidence table."
    return queue.reset_index(drop=True)


def build_score_status(metros: pd.DataFrame, queue: pd.DataFrame) -> pd.DataFrame:
    """Make it impossible to mistake an unreviewed queue for zero office presence."""
    completion_statuses = {"verified", "scope_complete_no_presence"}
    queue = queue.copy()
    queue["is_complete"] = queue["review_status"].isin(completion_statuses)
    queue["is_verified_hq"] = queue["review_status"].eq("verified") & queue["office_presence_class"].eq("qualifying_hq")
    queue["is_verified_office"] = queue["review_status"].eq("verified") & queue["office_presence_class"].eq("qualifying_office")
    summary = queue.groupby("msa_cbsa", as_index=False).agg(
        reviewed_company_metro_records=("is_complete", "sum"),
        verified_qualifying_hq_count=("is_verified_hq", "sum"),
        verified_qualifying_office_count=("is_verified_office", "sum"),
    )
    universe_size = queue["fortune_slug"].nunique()
    summary["unreviewed_company_metro_records"] = universe_size - summary["reviewed_company_metro_records"]
    summary["review_coverage_percent"] = 100 * summary["reviewed_company_metro_records"] / universe_size
    summary["verified_combined_presence_count"] = (
        summary["verified_qualifying_hq_count"] + summary["verified_qualifying_office_count"]
    )
    summary["verified_combined_presence_score_per_500"] = ""
    complete = summary["reviewed_company_metro_records"].eq(500)
    summary.loc[complete, "verified_combined_presence_score_per_500"] = (
        summary.loc[complete, "verified_combined_presence_count"] / universe_size
    ).round(4)
    summary["score_status"] = "not_publishable_review_incomplete"
    summary.loc[complete, "score_status"] = "publishable"
    status = metros.merge(summary, on="msa_cbsa", how="left", validate="one_to_one")
    status.insert(2, "fortune500_universe_size", universe_size)
    status["score_definition"] = (
        "Distinct Fortune 500 firms with a source-verified qualifying headquarters or "
        "office in the MSA, divided by 500; excludes stores and distribution-only sites."
    )
    return status


def write_csv(frame: pd.DataFrame, destination: Path) -> None:
    """Write UTF-8 CSV consistently for Excel and repository review."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(destination, index=False, encoding="utf-8", quoting=csv.QUOTE_MINIMAL)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Re-download the Fortune ranking page instead of reusing the saved public response.",
    )
    parser.add_argument(
        "--metro-count",
        type=int,
        default=200,
        help="Number of MSAs to select by 2023 Census BDS establishments when no custom roster is supplied.",
    )
    parser.add_argument(
        "--metro-roster",
        type=Path,
        help="Optional CSV with msa_cbsa/metro_name columns to use instead of the default top-MSA roster.",
    )
    args = parser.parse_args()

    fortune = build_fortune_universe(refresh=args.refresh)
    metros = load_custom_metro_roster(args.metro_roster) if args.metro_roster else build_default_metro_roster(args.metro_count)
    score_metros = metros[["msa_cbsa", "metro_name"]].copy()
    county_crosswalk = build_county_crosswalk(score_metros)
    queue = build_review_queue(fortune, score_metros)
    queue = preserve_existing_reviews(queue)
    queue = seed_verified_atlanta_evidence(queue, fortune)
    status = build_score_status(metros, queue)

    write_csv(fortune, OUTPUT_DIR / "fortune_500_universe_2025.csv")
    write_csv(metros, OUTPUT_DIR / "msa_roster.csv")
    write_csv(county_crosswalk, OUTPUT_DIR / "metro_county_crosswalk_2023.csv")
    write_csv(queue, OUTPUT_DIR / "fortune500_metro_presence_review_queue.csv")
    write_csv(status, OUTPUT_DIR / "metro_big_business_presence_score_status_2025.csv")

    print(f"Fortune 500 universe: {len(fortune):,} companies")
    print("Top 10 by reported revenue:")
    print(fortune.head(10)[["fortune_2025_rank", "company", "revenue_usd_millions"]].to_string(index=False))
    print(f"Metro roster: {len(score_metros):,} MSAs")
    print(f"Review queue: {len(queue):,} company-by-metro cells")
    print("Score status: blank until evidence review is complete for each MSA")


if __name__ == "__main__":
    main()
