# Atlanta business attraction and retention research

Current phase: Dallas/Denver pilot data collection and source verification are complete. Benchmark design, equivalent Atlanta collection, and analysis are next.

- [Research context](research_context.md): research aim, outcome definitions, planning decisions, four research steps, and intended outputs.
- [Dataset context](us_city_economic_datasets_context.md): candidate sources, variables, geographic coverage, interpretation limits, and collection guidance.

Use the research context to decide what questions and measures to prioritize, then use the dataset context for source coverage and acquisition details. The city manifests record the files actually collected.

## Data progress — October 15, 2026

Completed the review and refresh of [Dallas data](Data/dallas_data/README.md) and [Denver data](Data/denver_data/README.md). Each folder has **nine data files**, matching the nine requested source-table rows, plus a README, source manifest and data dictionary: **18 data files across the two metros**.

| Collected source | Reference year(s) | Progress |
| --- | --- | --- |
| QCEW | 2023–2025 | Annual source files collected and checked; industry detail is available for 2023–2024, with metro totals only in 2025. |
| CBP employment and establishments | 2023 | Two views of the official table prepared; 2023 is the latest available reference year. |
| Economic Census geographic detail and EC2200BASIC sector summary | 2022 | Both existing files verified against Census and retained unchanged in each folder. |
| BEA county GDP | 2023–2024 | Current county data collected; all-industry metro totals calculated from documented constituent counties. |
| State corporate income tax | 2026 | Existing Colorado and Texas rows verified against Tax Foundation and retained unchanged. |
| Fortune 500 | 2025 | All 21 Dallas and eight historically reported Denver entries have national ranks checked against Fortune; headquarters qualifications are documented. |
| BDS metro entry/exit | 2023 | Official metro extracts collected and checked; 2023 is the latest available reference year. |

Validation covered source values, years, geography, row counts, duplicate keys, GDP aggregation and final file checksums. Denver's QVC entry is explicitly flagged because its principal executive office moved to Pennsylvania effective May 29, 2025; seven Denver entries are verified within the metro at retrieval.

Older annual observations, duplicate QCEW extracts, the discontinued FRED metro GDP file, and the derived city-year comparison file were removed from both folders. The two revenue files overlap within EC2200BASIC, and the employment and establishment CBP files are two views of the same table. Named company offices remain outside CBP’s coverage. No acquisition scripts were created. The private Atlanta folder was not used or modified.

## Next research work

- Finalize the Atlanta metro definition and collect or verify equivalent public-source inputs.
- Establish the peer-selection criteria and benchmarking specification. Dallas and Denver remain pilot areas until that decision is made.
- Use 2023 as the available common annual baseline, subject to the research design. Keep the 2022 revenue, 2025 headquarters and 2026 tax observations separately dated; define any trend comparisons around actual source coverage.
- Align industry groupings, ownership coverage, denominators, establishment-size categories and suppression rules, then produce the first comparative tables.

Benchmarking, causal driver analysis, incentive evaluation and policy recommendations remain outstanding. Data collection and verification do not establish research findings.
