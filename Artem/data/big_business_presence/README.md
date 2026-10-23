# Metro Big Business Presence Score

## Purpose

This is the project’s principal **big-business presence outcome**, distinct from
employer-establishment entry or small-business formation.  For each metro:

> **Big Business Presence Score** = the number of distinct companies in the
> 2025 Fortune 500 with a source-verified qualifying headquarters or office in
> the metropolitan statistical area, divided by 500.

The score measures a major-company footprint, not economic success overall and
not a causal result of incentives.

## Files

| File | Purpose |
| --- | --- |
| `fortune_500_universe_2025.csv` | Public 2025 Fortune 500 company universe, retaining Fortune’s official rank label, sequential list position, reported FY2024 revenue, and headquarters context. |
| `msa_roster.csv` | The 200-MSA comparison roster, selected by 2023 Census BDS establishments unless a custom roster is supplied. It supplies the geography; BDS values are **not** the outcome here. |
| `metro_county_crosswalk_2023.csv` | Official Census county-to-selected-MSA crosswalk. This is the geographic join used after an address is geocoded. |
| `MSA_GEOGRAPHY.md` | Definition of the MSA boundary and the county-FIPS assignment rule. |
| `fortune500_metro_presence_review_queue.csv` | One row for every Fortune 500 company × 200 comparison MSAs. This is the evidence ledger, not an assertion that a company has—or lacks—a local office. |
| `metro_big_business_presence_score_status_2025.csv` | Publication status and counts per metro. Score cells remain blank until reviews are complete. |
| `COMPANY_LOCATION_AUTOMATION.md` | Import, Census-geocode, and MSA-assign an authorized external business-location list without treating its candidates as final offices. |
| `raw_inputs/fortune_2025_ranking_page.html` | Saved public 2025 Fortune ranking page, retained for reproducibility. |

## Classification rules

| `office_presence_class` | Count in score? | Definition |
| --- | ---: | --- |
| `qualifying_hq` | Yes | Headquarters physically located in the metro. |
| `qualifying_office` | Yes | Material corporate, regional, administrative, R&D, technology, engineering, finance, sales, or similar office located in the metro. |
| `retail_or_distribution_only` | No | Store, branch, airport counter, distribution/fulfillment warehouse, production site, or comparable presence without a qualifying office. |
| `no_verified_material_presence` | No | Only after the reviewer has checked the defined official sources and documented the scope. It is not a claim that no employee or remote worker exists. |
| `unreviewed` | No score yet | The default for all new cells. It must never be converted to no presence automatically. |

## Evidence standard and review workflow

1. Start with a company-owned office/contact/location/careers page, SEC filing,
   or dated company press release. Record the direct URL and the street address.
2. Confirm the municipality from the address. City of Atlanta and Metro Atlanta
   are different results: an Alpharetta office is metro presence, not City of
   Atlanta presence.
3. Set `review_status` to `verified` only when a direct source supports the
   location and the presence class. Use `needs_follow_up` for ambiguous cases;
   use `scope_complete_no_presence` only after documenting a completed defined
   search for a non-qualifying result.
4. Classify stores, fulfillment centers, and distribution facilities separately
   rather than inflating office counts.
5. Publish a metro score only after the review queue has no `unreviewed` or
   unresolved cells for that metro. The score-status file deliberately makes an
   incomplete metro non-publishable.

Seven pre-existing direct company-source checks for Metro Atlanta are imported
as `verified` starting evidence (one qualifying headquarters and six qualifying
offices). They are a partial confirmed count, not Atlanta's final score: the
other 493 companies must still be reviewed before any metro comparison is
reported.

## Source and limits

The company universe comes from Fortune’s public [2025 Fortune 500 ranking](https://fortune.com/ranking/fortune500/2025/). That ranking is based on revenue for fiscal year 2024. The score is therefore a 2025 cross-sectional benchmark—not a historical time-series target for a 2017–2023 prediction model.

Fortune may assign the same displayed rank to tied companies (for example, two
firms share rank 498 in this edition). `fortune_2025_rank` preserves that
official label; `fortune_2025_list_position` is the unique 1–500 row order used
to select and join the company universe.

No single authoritative public directory gives every Fortune 500 office in every
U.S. MSA. The evidence ledger is therefore intentionally source-audited and
records uncertainty rather than inferring absence. A future historical model
would need repeated annual Fortune universes plus year-specific location
evidence, or a separate panel of dated office/HQ announcements.

## Rebuild

Run from the repository root:

```bash
python3 Artem/scripts/build_big_business_presence_research.py
```

Use `--refresh` only when intentionally updating the public Fortune input. The
default roster has 200 MSAs. Use `--metro-roster /path/to/roster.csv` when the
team has a defined list of 200 metro codes that should replace the default.
