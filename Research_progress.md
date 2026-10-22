# Atlanta business attraction and retention research

Current phase: **collection is complete for nine metropolitan areas**, with nine requested data files per area. Benchmark design and analysis remain next.

- [Research context](research_context.md): research goal, definitions, comparison decisions and research steps.
- [Dataset context](data/datasets_context.md): the nine files, their purpose, coverage and interpretation limits.
- [Data folder](data/README.md): links to all nine city folders and their acquisition records.

## Data progress — October 21, 2026

The shared `data/` directory contains **81 data files across Atlanta, Austin, Charlotte, Dallas, Denver, Houston, Miami, Nashville and Raleigh**. Each city has a separate `<city>_data/` folder with the same nine filenames and matching per-dataset columns, plus a README, source manifest and data dictionary. The 63 new files extend the Dallas/Denver collection; the original 18 Dallas/Denver data files were moved byte-for-byte unchanged, with their October 15 verification records preserved.

| Collected source | Matching reference window | Progress |
| --- | --- | --- |
| QCEW | 2023–2025 | Annual metro area files; 2023–2024 industry detail and 2025 all-ownership/all-industry total. |
| CBP employment and establishments | 2023 | Two views of the same official table, retaining industry, size categories and flags. |
| Economic Census detail and sector summary | 2022 | Same EC2200BASIC release; the explicitly requested year exception. |
| BEA county GDP | 2023–2024 | Published county industry data plus complete all-industry metro sums using July 2023 OMB counties. |
| State corporate income tax | 2026 | Requested Tax Foundation snapshot; Charlotte has separate North and South Carolina rows. |
| Fortune 500 | 2025 | Regional rosters and national ranks documented. Current-location audit coverage varies and is explicitly flagged. |
| BDS metro entry/exit | 2023 | Official single-year metro extracts with all returned source measures and flags. |

Validation covered exact new federal-source values, headers, date windows, geography, row counts, duplicate keys, GDP county sums, manifests and checksums. No acquisition scripts were added. These are fixed windows chosen to match the existing collection, rather than a claim that every file is the publisher’s newest release. Private Atlanta data and unrelated project folders were not used or changed.

Fortune’s 2025 roster is separate from a current headquarters census. New files leave unverified historical municipalities or current-location fields blank; blank is unknown, not outside the metro. Dallas/Denver’s existing checks remain intact, including Denver’s historical QVC entry and documented move to Pennsylvania. A complete current-HQ comparison still requires consistent verification across the new areas.

## Next research work

- Justify the final comparison group and distinguish the Atlanta metro economy from the City of Atlanta policy jurisdiction.
- Specify the 2023 annual baseline and source-specific follow-up periods, keeping the 2022 revenue, 2025 ranking and 2026 tax observations separately dated.
- Align industry groups, ownership coverage, denominators, establishment-size categories and suppression rules before comparing values.
- Produce comparable benchmark tables, then investigate drivers and incentive strategies. Data collection does not establish causal findings or policy recommendations.
