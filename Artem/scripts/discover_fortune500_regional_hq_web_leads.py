#!/usr/bin/env python3
"""Build a public-web discovery queue for Fortune 500 regional-HQ research.

The public web has no complete registry of U.S. regional headquarters.  This
script therefore runs the same headquarters-focused query for every company in
the project's Fortune 500 universe and saves search-result metadata as a
*review queue*.  It does not treat a search result as proof, does not collect
employee-level data, and does not add a result to a model outcome.  A lead is
eligible for the separate verified-site file only after a current first-party
source explicitly supports both its headquarters-type function and geography.

The crawl is deliberately resumable and rate-limited.  Its output contains
only public result titles, snippets, and URLs, allowing another researcher to
repeat the review without depending on paid business-location data.
"""

from __future__ import annotations

import argparse
import base64
import csv
import ssl
import time
from datetime import date
from pathlib import Path
from typing import Iterable
from urllib.parse import parse_qs, quote_plus, urlparse
from urllib.request import Request, urlopen

import certifi
import pandas as pd
from bs4 import BeautifulSoup


ARTEM = Path(__file__).resolve().parents[1]
FORTUNE = ARTEM / "data" / "big_business_presence" / "fortune_500_universe_2025.csv"
OUTPUT = ARTEM / "data" / "big_business_presence"
SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
USER_AGENT = "Mozilla/5.0 (compatible; AidataLab regional-HQ research)"
SEARCH_TERMS = (
    '"regional headquarters" OR "regional HQ" OR "division headquarters" '
    'OR "divisional headquarters" OR "business unit headquarters" '
    'OR "North America headquarters" OR "Americas headquarters" '
    'OR "operational headquarters" OR "sector headquarters"'
)
NON_EVIDENCE_DOMAINS = {
    "linkedin.com", "indeed.com", "glassdoor.com", "wikipedia.org", "facebook.com",
    "instagram.com", "x.com", "twitter.com", "reddit.com", "youtube.com",
}


def direct_bing_url(value: str) -> str:
    """Decode Bing's redirect URL when it contains the standard ``u=a1`` form."""
    parsed = urlparse(value)
    if parsed.netloc.lower() != "www.bing.com" or not parsed.path.startswith("/ck/"):
        return value
    encoded = parse_qs(parsed.query).get("u", [""])[0]
    if not encoded.startswith("a1"):
        return value
    try:
        padding = "=" * (-len(encoded[2:]) % 4)
        return base64.urlsafe_b64decode(encoded[2:] + padding).decode("utf-8")
    except Exception:
        return value


def result_domain(url: str) -> str:
    return urlparse(url).netloc.lower().removeprefix("www.")


def is_low_value_domain(domain: str) -> bool:
    return any(domain == blocked or domain.endswith("." + blocked) for blocked in NON_EVIDENCE_DOMAINS)


def search(query: str) -> Iterable[dict[str, str]]:
    url = f"https://www.bing.com/search?q={quote_plus(query)}&count=10"
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"})
    with urlopen(request, timeout=30, context=SSL_CONTEXT) as response:  # nosec B310 - fixed public search endpoint
        page = response.read().decode("utf-8", errors="replace")
    soup = BeautifulSoup(page, "html.parser")
    for item in soup.select("li.b_algo"):
        link = item.select_one("h2 a")
        if link is None:
            continue
        destination = direct_bing_url(str(link.get("href", "")))
        if not destination.startswith(("https://", "http://")):
            continue
        title = link.get_text(" ", strip=True)
        snippet_node = item.select_one(".b_caption p") or item.select_one("p")
        snippet = snippet_node.get_text(" ", strip=True) if snippet_node else ""
        yield {
            "result_title": title,
            "result_snippet": snippet,
            "result_url": destination,
            "result_domain": result_domain(destination),
        }


def existing_companies(path: Path) -> set[str]:
    if not path.is_file() or path.stat().st_size == 0:
        return set()
    existing = pd.read_csv(path, dtype=str, keep_default_na=False)
    return set(existing.get("company_name", pd.Series(dtype=str)))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fortune-csv", type=Path, default=FORTUNE)
    parser.add_argument("--output", type=Path, default=OUTPUT / "fortune500_public_web_regional_hq_discovery_leads_2026.csv")
    parser.add_argument("--summary-output", type=Path, default=OUTPUT / "fortune500_public_web_regional_hq_discovery_summary_2026.csv")
    parser.add_argument("--start-rank", type=int, default=1, help="Inclusive Fortune rank for a new batch.")
    parser.add_argument("--end-rank", type=int, default=500, help="Inclusive Fortune rank for a new batch.")
    parser.add_argument("--max-companies", type=int, default=500, help="Safety cap for one run.")
    parser.add_argument("--sleep-seconds", type=float, default=0.75)
    parser.add_argument("--resume", action="store_true", help="Skip companies already represented in the output file.")
    args = parser.parse_args()
    if not args.fortune_csv.is_file():
        raise FileNotFoundError(args.fortune_csv)
    if args.start_rank < 1 or args.end_rank < args.start_rank or args.max_companies < 1:
        raise ValueError("Ranks and maximum companies must be positive, with end rank >= start rank.")
    if args.sleep_seconds < 0:
        raise ValueError("Sleep seconds cannot be negative.")

    fortune = pd.read_csv(args.fortune_csv, dtype=str, keep_default_na=False)
    fortune["fortune_2025_rank_int"] = pd.to_numeric(fortune["fortune_2025_rank"], errors="raise")
    selected = fortune.loc[
        fortune["fortune_2025_rank_int"].between(args.start_rank, args.end_rank),
        ["fortune_2025_rank", "fortune_2025_list_position", "company", "fortune_slug", "headquarters_city", "headquarters_state", "industry"],
    ].sort_values(["fortune_2025_rank", "fortune_2025_list_position"], key=lambda values: pd.to_numeric(values, errors="coerce"))
    already_done = existing_companies(args.output) if args.resume else set()
    selected = selected.loc[~selected["company"].isin(already_done)].head(args.max_companies)

    rows: list[dict[str, str]] = []
    reviewed_companies: list[str] = []
    for position, company in enumerate(selected.itertuples(index=False), start=1):
        query = f'"{company.company}" ({SEARCH_TERMS})'
        try:
            results = list(search(query))
            search_status = "search_completed"
        except Exception as error:
            results = []
            search_status = f"search_failed_{type(error).__name__}"
        reviewed_companies.append(company.company)
        for rank, result in enumerate(results, start=1):
            result["fortune_2025_rank"] = company.fortune_2025_rank
            result["fortune_2025_list_position"] = company.fortune_2025_list_position
            result["company_name"] = company.company
            result["fortune_slug"] = company.fortune_slug
            result["fortune_global_hq_city"] = company.headquarters_city
            result["fortune_global_hq_state"] = company.headquarters_state
            result["fortune_industry"] = company.industry
            result["search_query"] = query
            result["result_rank"] = str(rank)
            result["search_status"] = search_status
            result["candidate_priority"] = (
                "exclude_low_value_domain" if is_low_value_domain(result["result_domain"])
                else "needs_first_party_function_and_geography_verification"
            )
            result["discovery_date"] = date.today().isoformat()
            rows.append(result)
        # A no-result row makes the coverage denominator auditable on resume.
        if not results:
            rows.append({
                "fortune_2025_rank": company.fortune_2025_rank,
                "fortune_2025_list_position": company.fortune_2025_list_position,
                "company_name": company.company,
                "fortune_slug": company.fortune_slug,
                "fortune_global_hq_city": company.headquarters_city,
                "fortune_global_hq_state": company.headquarters_state,
                "fortune_industry": company.industry,
                "search_query": query,
                "result_rank": "",
                "result_title": "",
                "result_snippet": "",
                "result_url": "",
                "result_domain": "",
                "search_status": search_status,
                "candidate_priority": "no_results_or_search_failure_not_evidence_of_absence",
                "discovery_date": date.today().isoformat(),
            })
        if position < len(selected):
            time.sleep(args.sleep_seconds)

    fields = [
        "fortune_2025_rank", "fortune_2025_list_position", "company_name", "fortune_slug",
        "fortune_global_hq_city", "fortune_global_hq_state", "fortune_industry", "search_query",
        "result_rank", "result_title", "result_snippet", "result_url", "result_domain", "search_status",
        "candidate_priority", "discovery_date",
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    append = args.resume and args.output.is_file() and args.output.stat().st_size > 0
    with args.output.open("a" if append else "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        if not append:
            writer.writeheader()
        writer.writerows(rows)

    output = pd.read_csv(args.output, dtype=str, keep_default_na=False)
    summary = pd.DataFrame([{
        "fortune500_companies": len(fortune),
        "companies_covered_by_at_least_one_search": output["company_name"].nunique(),
        "companies_covered_this_run": len(reviewed_companies),
        "search_result_rows": len(output),
        "high_value_review_queue_rows": int(output["candidate_priority"].eq("needs_first_party_function_and_geography_verification").sum()),
        "search_method": "Public Bing web queries; results are discovery leads only, not verification.",
        "function_test": "Count a site only when a current first-party source expressly identifies a regional/divisional/business-unit/second corporate HQ and its geography.",
        "non_hq_exclusions": "Warehouses, stores, retail branches, factories, ordinary offices, job listings, and unsupported directory claims are excluded.",
        "run_date": date.today().isoformat(),
    }])
    summary.to_csv(args.summary_output, index=False, quoting=csv.QUOTE_MINIMAL)
    print(f"Searched {len(reviewed_companies)} companies; output now covers {output['company_name'].nunique()} Fortune 500 companies.")
    print(f"Output: {args.output.resolve()}")


if __name__ == "__main__":
    main()
