#!/usr/bin/env python3
"""Find public, *unverified* Fortune 500 regional-HQ leads in SEC 10-K text.

This is a broad discovery pass, not a source-verification step. It asks the
SEC's official full-text search for a small set of headquarters phrases,
matches result issuers to the project's Fortune 500 universe, and saves only a
short context snippet plus the public filing URL. It never calls a warehouse,
store, or ordinary office a regional HQ.

The resulting leads must still be checked against a current company-owned
location, investor-relations, or division page before they are added to the
verified regional/divisional-HQ dataset or used as model labels.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import ssl
import time
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd
import certifi


ARTEM = Path(__file__).resolve().parents[1]
FORTUNE = ARTEM / "data" / "big_business_presence" / "fortune_500_universe_2025.csv"
OUTPUT = ARTEM / "data" / "big_business_presence"
SEC_SEARCH_URL = "https://efts.sec.gov/LATEST/search-index"
SEC_ARCHIVES = "https://www.sec.gov/Archives/edgar/data"
USER_AGENT = "Mozilla/5.0 (compatible; AidataLab research)"
SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
PHRASES = [
    "regional headquarters",
    "regional headquarter",
    "division headquarters",
    "divisional headquarters",
    "business unit headquarters",
    "north america headquarters",
    "north american headquarters",
    "americas headquarters",
    "americas regional headquarters",
    "u.s. headquarters",
    "us headquarters",
    "operational headquarters",
    "operations headquarters",
    "sector headquarters",
    "business segment headquarters",
    "business headquarters",
    "division headquarter",
    "operating segment headquarters",
    "segment operational headquarters",
    "u.s. divisional headquarters",
]
LEGAL_WORDS = {
    "inc", "incorporated", "corporation", "corp", "company", "co", "llc",
    "ltd", "limited", "plc", "holdings", "holding", "group", "the", "class",
}


def fetch_json(url: str) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30, context=SSL_CONTEXT) as response:  # nosec B310 - fixed official SEC hosts
        payload = response.read()
    return json.loads(payload.decode("utf-8"))


def fetch_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30, context=SSL_CONTEXT) as response:  # nosec B310 - fixed official SEC hosts
        payload = response.read()
    decoded = payload.decode("utf-8", errors="replace")
    decoded = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", decoded, flags=re.IGNORECASE | re.DOTALL)
    decoded = re.sub(r"<[^>]+>", " ", decoded)
    return " ".join(html.unescape(decoded).split())


def normalize_name(value: object) -> str:
    text = re.sub(r"[^a-z0-9]+", " ", str(value).lower())
    tokens = [token for token in text.split() if token not in LEGAL_WORDS]
    return " ".join(tokens)


def name_similarity(left: str, right: str) -> tuple[float, str]:
    """Conservative name linkage; ambiguous matches are intentionally omitted."""
    left_key, right_key = normalize_name(left), normalize_name(right)
    if left_key == right_key:
        return 1.0, "normalized_exact"
    if min(len(left_key), len(right_key)) >= 6 and (left_key in right_key or right_key in left_key):
        return 0.97, "normalized_containment"
    left_tokens, right_tokens = set(left_key.split()), set(right_key.split())
    if len(left_tokens) >= 2 and len(right_tokens) >= 2:
        overlap = len(left_tokens & right_tokens) / len(left_tokens | right_tokens)
        if overlap >= 0.75:
            return overlap, "token_overlap"
    return SequenceMatcher(None, left_key, right_key).ratio(), "sequence_similarity"


def issuer_name(display_names: object) -> str:
    """Remove SEC's ticker/CIK parentheticals from its search display name."""
    if not isinstance(display_names, list) or not display_names:
        return ""
    return re.split(r"\s+\(", str(display_names[0]), maxsplit=1)[0].strip()


def match_issuer_to_fortune(issuer: str, fortune: pd.DataFrame) -> dict[str, object] | None:
    """Link a search-result issuer to Fortune only when one match is clear."""
    scored: list[tuple[float, str, object]] = []
    for company in fortune[["company", "fortune_2025_rank", "fortune_slug"]].itertuples(index=False):
        score, method = name_similarity(issuer, company.company)
        if score >= 0.87:
            scored.append((score, method, company))
    scored.sort(key=lambda value: value[0], reverse=True)
    if not scored:
        return None
    score, method, company = scored[0]
    if len(scored) > 1 and scored[1][0] >= score - 0.02:
        return None
    return {
        "company": company.company,
        "fortune_2025_rank": company.fortune_2025_rank,
        "fortune_slug": company.fortune_slug,
        "sec_match_method": method,
        "sec_match_score": round(score, 3),
    }


def sec_search(phrase: str, start_date: str, end_date: str, max_hits: int) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    offset = 0
    while offset < max_hits:
        parameters = {
            "q": f'"{phrase}"', "forms": "10-K", "dateRange": "custom",
            "startdt": start_date, "enddt": end_date, "from": offset, "size": min(100, max_hits - offset),
        }
        payload = fetch_json(f"{SEC_SEARCH_URL}?{urlencode(parameters)}")
        hits = payload.get("hits", {}).get("hits", [])
        if not hits:
            break
        records.extend(hits)
        if len(hits) < parameters["size"]:
            break
        offset += len(hits)
        time.sleep(0.12)
    return records


def context_for_phrase(text: str, phrase: str) -> str:
    match = re.search(re.escape(phrase), text, flags=re.IGNORECASE)
    if match is None:
        return ""
    start = max(0, match.start() - 260)
    end = min(len(text), match.end() + 360)
    return text[start:end].strip()


def document_url(source: dict[str, Any], cik: str) -> str:
    filing = str(source.get("adsh", "")).replace("-", "")
    filename = str(source.get("source_file_name", ""))
    if not filename:
        raise ValueError("SEC search result did not identify a source document filename.")
    return f"{SEC_ARCHIVES}/{int(cik)}/{filing}/{filename}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fortune-csv", type=Path, default=FORTUNE)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    parser.add_argument("--start-date", default="2020-01-01")
    parser.add_argument("--end-date", default="2026-11-09")
    parser.add_argument("--max-sec-hits-per-phrase", type=int, default=600)
    parser.add_argument("--max-filing-downloads", type=int, default=120)
    args = parser.parse_args()
    if not args.fortune_csv.is_file():
        raise FileNotFoundError(args.fortune_csv)
    if args.max_sec_hits_per_phrase < 1 or args.max_filing_downloads < 1:
        raise ValueError("Maximums must be positive.")

    fortune = pd.read_csv(args.fortune_csv, dtype=str, keep_default_na=False)
    candidate_documents: dict[tuple[str, str, str], tuple[dict[str, Any], dict[str, object], str]] = {}
    for phrase in PHRASES:
        for hit in sec_search(phrase, args.start_date, args.end_date, args.max_sec_hits_per_phrase):
            source = dict(hit.get("_source", {}))
            source_id = str(hit.get("_id", ""))
            if ":" in source_id:
                source["source_file_name"] = source_id.split(":", 1)[1]
            # The full-text endpoint returns exhibit hits too. Limit discovery to
            # the primary 10-K, where a location/function statement is auditable.
            if str(source.get("file_type", "")).upper() not in {"10-K", "10-K/A"}:
                continue
            issuer = issuer_name(source.get("display_names"))
            matched_company = match_issuer_to_fortune(issuer, fortune)
            if matched_company is None:
                continue
            ciks = [str(cik).zfill(10) for cik in source.get("ciks", [])]
            for cik in ciks:
                key = (str(matched_company["company"]), cik, phrase)
                previous = candidate_documents.get(key)
                if previous is None or str(source.get("file_date", "")) > str(previous[0].get("file_date", "")):
                    candidate_documents[key] = (source, matched_company, issuer)

    rows: list[dict[str, object]] = []
    for number, ((company_name, cik, phrase), item) in enumerate(sorted(candidate_documents.items()), start=1):
        if number > args.max_filing_downloads:
            break
        source, company, issuer = item
        url = document_url(source, cik)
        try:
            text = fetch_text(url)
            snippet = context_for_phrase(text, phrase)
        except Exception as error:  # keeps the long scan usable if one filing is malformed
            snippet = f"Retrieval failed: {type(error).__name__}"
        rows.append({
            "fortune_2025_rank": company["fortune_2025_rank"],
            "company_name": company_name,
            "fortune_slug": company["fortune_slug"],
            "sec_cik": cik,
            "sec_issuer_name": issuer,
            "sec_match_method": company["sec_match_method"],
            "sec_match_score": company["sec_match_score"],
            "filing_date": source.get("file_date", ""),
            "filing_period_end": source.get("period_ending", ""),
            "sec_form": source.get("file_type", ""),
            "discovery_phrase": phrase,
            "official_source_url": url,
            "context_snippet": snippet,
            "discovery_status": "public_filing_candidate_needs_current_company_source_verification",
            "caveat": "A filing text match does not prove this is a current regional/divisional HQ or establish its exact location. Verify the function and geography on a current company source before model use.",
        })
        time.sleep(0.12)

    leads = pd.DataFrame(rows).sort_values(
        ["fortune_2025_rank", "filing_date", "discovery_phrase"],
        kind="stable",
    ) if rows else pd.DataFrame(columns=[
        "fortune_2025_rank", "company_name", "fortune_slug", "sec_cik", "sec_issuer_name", "sec_match_method", "sec_match_score", "filing_date",
        "filing_period_end", "sec_form", "discovery_phrase", "official_source_url", "context_snippet",
        "discovery_status", "caveat",
    ])
    summary = pd.DataFrame([{
        "fortune500_companies": len(fortune),
        "automatic_sec_issuer_matches": int(leads[["company_name", "sec_cik"]].drop_duplicates().shape[0]) if not leads.empty else 0,
        "public_filing_lead_rows": len(leads),
        "distinct_fortune500_companies_with_filing_leads": int(leads.company_name.nunique()) if not leads.empty else 0,
        "scan_start_date": args.start_date,
        "scan_end_date": args.end_date,
        "phrases": " | ".join(PHRASES),
        "method_note": "Official SEC filing discovery only; every lead requires current company-source function and geography verification.",
    }])
    args.output_dir.mkdir(parents=True, exist_ok=True)
    leads.to_csv(args.output_dir / "fortune500_public_filing_regional_hq_discovery_leads_2026.csv", index=False, quoting=csv.QUOTE_MINIMAL)
    summary.to_csv(args.output_dir / "fortune500_public_filing_regional_hq_discovery_summary_2026.csv", index=False, quoting=csv.QUOTE_MINIMAL)
    print(summary.to_string(index=False))
    print(f"Output: {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
