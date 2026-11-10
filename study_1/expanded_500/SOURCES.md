# Sources for the expanded HQ collection

**Later collection — November 10, 2026:** new regional/location/function citations and detailed evidence are kept only in the [linked raw archive](../linked_msa/raw_archive/README.md). The source descriptions below retain their original expanded-HQ scope and dates. Follow the [current training handoff](../linked_msa/TRAINING_HANDOFF.md) for the next experiment.

Extracted and checked November 9, 2026. New raw HTML, CSV, ZIP and SEC JSON
responses were used in temporary storage only. This expansion retains citations,
hashes, normalized fields and compact ledgers, rather than raw source payloads.

| Source | Fields or purpose | Collection treatment |
| --- | --- | --- |
| [Fortune 2025 ranking](https://fortune.com/ranking/fortune500/2025/) | Fixed 500 list positions, displayed rank, company identity, industry, sector, revenue, workforce, profits, assets and revenue growth | Reused the retained public page response already documented under `Artem/data/big_business_presence`; extracted the first 500 list positions. A fresh ranking-page request returned HTTP 403, so no fresh remote ranking retrieval is claimed. |
| [Fortune 2025 map CSV](https://interactives.fortune.com/f500-dataviz-2025/map/data.csv) | All 500 publisher names, map IDs, selected-HQ coordinates, reported place, industry, revenue and rank diagnostics | Downloaded for the feasibility check; hash exactly matches the original study's source. The CSV's accented name is decoded as Mac Roman, then outputs use UTF-8. |
| [Census 2023 cartographic CBSAs](https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_cbsa_500k.zip) | Primary coordinate-to-CBSA assignment | Fresh download; hash exactly matches the original source. Same July 2023 membership. |
| [Census 2023 full TIGER CBSAs](https://www2.census.gov/geo/tiger/TIGER2023/CBSA/tl_2023_us_cbsa.zip) | One waterfront geometry exception | Prologis's publisher point falls outside the generalized 500k land outline. The full-resolution polygon assigns it to San Francisco CBSA 41860. No nearest-metro reassignment is used. |
| [SEC company ticker/exchange directory](https://www.sec.gov/files/company_tickers_exchange.json) | Efficient supplementary issuer-identity lookup | Downloaded once and searched locally; reviewed historical/legal-name aliases are retained separately. Absence from the directory is not evidence of HQ absence. |
| [SEC submissions API](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) | Identity, current business address and available 2025 annual-filing routes | 476 individual issuer metadata responses read at a limited sequential request rate. These are later-vintage supplements, not independently verified 2025 HQ labels. |

Financials use the 2025 edition's primarily FY2024 basis. Subsequent company
renames and acquisitions do not change the historical list-position identity or
automatically establish physical closure. The unique company ID uses list position,
not the displayed rank, which can be tied or inconsistent between publisher views.

The publisher page cache predates this extraction and remains in its pre-existing
location; it was not copied into the expansion. Exact raw-response SHA-256 hashes,
byte counts, extraction date and reuse treatment are in
[collection_source_registry.csv](tables/collection_source_registry.csv).

## Company-specific supplementary evidence

[firm_source_checks.csv](tables/firm_source_checks.csv) cites a supplementary
official route for every company, with query, access date and actual review scope.
The original 100 firms' bounded checks and dates are preserved. For the 400 added
firms, 385 SEC metadata checks and 15 targeted official-company searches supply
the supplementary routes. Only source discovery/excerpts were reviewed for the
15 company-site routes; full independent historical verification is not claimed.

- [sec_source_checks.csv](tables/sec_source_checks.csv): 476 completed metadata
  reads; source URL, hash, current business address, and 2025 annual-filing URL
  when present in the response. The other 24 rows explicitly state that no
  unambiguous identity was found in the ticker directory; they have company-site
  or inherited supplementary routes instead.
- [SEC identity overrides](config/sec_identity_overrides.csv): 22 reviewed
  legal-name/historical-issuer matches, including acquired or renamed companies.
- [Official company supplements](config/official_company_supplements.csv): the
  15 added-company routes that avoid relying on ticker-directory coverage.
- [Identity matches](tables/company_identity_matches.csv): all 500 primary
  matches, coordinates, reviewed aliases, rank/industry diagnostics and geography
  assignment method. Revenue agrees for all 500 under the documented tolerance.

Current SEC address metadata must not overwrite the historical publisher point.
The existing Lululemon/Autoliv exclusions remain governed by their earlier
documented 2025 filing conflicts, even when later metadata differs.

## Inherited economic inputs

No regional source recollection was needed. The 31 factors, normalized economic
inputs, dictionaries, source registry, missingness and vintages are copied
byte-for-byte from the original study. [The original economic source links](../SOURCES.md#economic-sources)
and [economic_source_registry.csv](tables/economic_source_registry.csv) document
QCEW, CBP, ACS, BEA, population and OEWS sources. Later revisions remain explicit;
this is a retrospective comparison, not an as-of-2025 forecast.

## Reproduction code

The original network collector and collection-only dependency file were retired during cleanup. The retained normalized publisher, identity, SEC and economic tables, source routes and hashes reproduce the completed study offline with [build_expanded_500.py](../scripts/build_expanded_500.py). The ten files under `reference_inputs/` preserve inherited company checks and the original labels, specifications, fold contract and comparison metrics. No network request, external `Artem` file or top-level `data/` folder is needed for this pipeline.
