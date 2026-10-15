# U.S. City Economic and Business Dataset Context

Companion to [the research aim and planning framework](research_context.md). This file focuses on candidate data sources, variables, coverage, interpretation, and collection methods. Research definitions, peer-selection decisions, hypotheses, and policy objectives belong in the research context.

## Objective
Document candidate public-data inputs for benchmarking **Atlanta** against peer metros and investigating the drivers of performance. An AI agent should identify, retrieve, and harmonize statistics for the geography, period, and measures established in [research_context.md](research_context.md). The catalog below is a source inventory, not confirmation that files have been downloaded or that every variable is required for the initial benchmark; verify current source availability and definitions before collection.

## Required variables and dataset links

| Variable | Exact dataset / source | Search or download link | Geography and notes |
|---|---|---|---|
| Employment | **BLS Quarterly Census of Employment and Wages (QCEW)** | https://www.bls.gov/cew/data.htm | County and metropolitan-area industry employment, wages, establishments; quarterly/annual. |
| Employment; establishments; payroll | **U.S. Census County Business Patterns (CBP)** | https://www.census.gov/programs-surveys/cbp/data.html | County, metro, ZIP (depending on release); NAICS employment, payroll, establishment counts. |
| Industry revenue / sales / receipts | **2022 Economic Census: Geographic Area Statistics** | https://data.census.gov/ | Search Economic Census geographic statistics; select geographic areas and NAICS industries. Geographic coverage varies; suppression possible. |
| Industry revenue / sales / receipts | **2022 Economic Census: All Sectors Summary Statistics (EC2200BASIC)** | https://data.census.gov/table/ECNBASIC2022.EC2200BASIC | Summary table with sales/receipts and related measures where available. Economic Census is periodic, not annual. |
| Economic output / GDP | **BEA Gross Domestic Product by County (CAGDP2)** | https://apps.bea.gov/itable/?ReqID=70&step=1 | County GDP, total and by industry; aggregate counties for region. The originally supplied SAGDP2N code identifies state GDP. No standardized GDP for municipality boundaries. |
| State corporate income tax | **State Corporate Income Tax Rates and Brackets (2026)**, Tax Foundation | https://taxfoundation.org/data/all/state/state-corporate-income-tax-rates-brackets/ | State-level statutory rates; account for brackets, alternative taxes and local taxes where relevant. |
| Large corporate headquarters | **Fortune 500 Annual Ranking** | https://fortune.com/ranking/fortune500/ | Company names, revenues, headquarters city/state; public ranking but structured/bulk reuse may require licensing. |
| Number of operating company locations (proxy for offices) | **County Business Patterns: Number of Establishments (ESTAB)** | https://www.census.gov/data/developers/data-sets/cbp-zbp.html | Counts physical establishments, not named company office locations; includes retail/industrial sites. |
| Business entry/exit / retention proxy | **Census Business Dynamics Statistics: Metro (BDSMETRO)** | https://data.census.gov/table/BDSTIMESERIES.BDSMETRO | Metro-level establishment births, deaths and job creation/destruction; check available geographies, vintages and metrics. |

## Core interpretation and coverage limitations

- **Employment:** Strong public coverage for industry-level employment and business counts; company-level employment is generally not public in a national city dataset.
- **Revenue:** Economic Census provides **aggregate industry sales/receipts**, not a comprehensive directory of individual private-company revenues.
- **GDP:** Use BEA county GDP and aggregate a documented set of counties if a metro-area measure is needed. BEA's previously published metropolitan GDP series was discontinued in 2026; check current BEA data and aggregation options before use.
- **Corporate tax:** State tax is applicable to a city but may not represent the full corporate tax burden; clearly distinguish state statutory rate from effective taxes and local levies.
- **Fortune 500:** Headquarters concentration is measurable by matching headquarters cities to the annual Fortune 500 list; distinguish municipal HQ location from metro HQ location. Check licensing before bulk extraction.
- **Company offices:** No comprehensive free, nationwide public list of *named firms and all their office addresses*. CBP's establishment count is a proxy, **not** a company-office roster. For named offices, investigate SEC filings (public issuers), local business licenses, company websites, or licensed commercial establishment data.
- **Business dynamics:** Birth/death counts are useful proxies for attraction and retention, but they do **not** directly prove inter-city corporate relocation. Business formation, closure, and relocation are distinct events.

## Recommended data structure

Choose one geography standard, preferably **metropolitan statistical areas (MSAs)** for comparing regional economies (and avoid mixing municipalities, counties, and MSAs). If municipal data is required, flag missing or proxy values. Record every metric as follows:

`city_name | metro_name | geo_type | geo_id | year | variable | value | units | NAICS_code | source_dataset | source_url | release/vintage | notes`

Suggested derived measures: year-over-year employment growth, industry employment shares, payroll per worker, establishments per 1,000 residents, establishment births/deaths, GDP growth, Fortune 500 HQ count, and state corporate tax rate. Label denominators and transformations clearly.

## Instructions for the AI data-collection agent

1. Accept one or more target U.S. cities and a year or time span; resolve each city to its **official geographic identifier** (e.g., CBSA/MSA, county FIPS, place FIPS) and explicitly record the boundary definition.
2. Use the **primary datasets above**, selecting the most recent common year where feasible; report each dataset's actual reference year and release date. The 2022 Economic Census revenue statistics cannot be treated as current-year values.
3. Locate direct data-table/API/download links for the selected geography (not just publisher landing pages), record field names, units, and source notes, and extract the requested variables.
4. For GDP, aggregate constituent counties only when the geography and year are consistent. For Fortune 500 headquarters, map location names to the chosen municipality or metro boundary.
5. Report suppressed/missing data as unavailable, never as zero; distinguish measured values from estimates and proxies. Do not infer office locations, corporate relocation, or individual-company revenue from establishment counts.
6. Return a tidy city-year comparison dataset and a source/limitations log. Validate at least a sample of extracted values against the official tables.

## Verified Dallas and Denver files — October 15, 2026

[Dallas](Data/dallas_data/README.md) and [Denver](Data/denver_data/README.md) each contain nine data files, one per row of the requested source table. The target regional geographies remain Dallas–Fort Worth–Arlington (CBSA 19100) and Denver–Aurora–Centennial (CBSA 19740). These are metropolitan economies, not municipal boundaries.

| Requested row | File in each city folder | Reference year(s) |
| --- | --- | --- |
| QCEW employment | `qcew_annual_2023_2025.csv` | 2023–2025 |
| CBP employment | `cbp_employment_2023.csv` | 2023 |
| Economic Census geographic revenue detail | `economic_census_2022_detail.csv.gz` | 2022 |
| Economic Census EC2200BASIC sector summary | `economic_census_2022_sectors.csv` | 2022 |
| County GDP and derived metro totals | `bea_county_gdp_2023_2024.csv` | 2023–2024 |
| State corporate income tax | `state_corporate_tax_2026.csv` | 2026 |
| Fortune 500 annual roster | `fortune500_headquarters_2025.csv` | 2025 |
| CBP establishments | `cbp_establishments_2023.csv` | 2023 |
| BDS metro entry/exit | `bds_metro_2023.csv` | 2023 |

The two 2022 Economic Census files and the 2026 tax file in each folder were verified against the requested sources and retained byte-for-byte. The 2023 values in the former CBP and BDS panels also matched fresh official Census responses; their pre-2023 observations were removed. QCEW was retrieved directly from BLS for 2023–2025. BLS's 2025 metro annual file contains only an all-ownership, all-industry total after the MSA publication change; the absence of industry detail must remain explicit. CBP and BDS currently stop at 2023.

The Economic Census geographic release and all-sectors table share EC2200BASIC, so the detailed and sector files overlap. The 2022 reference year is an explicit exception to the requested 2023-onward window. CBP employment and establishment files are two views of CB2300CBP. These overlaps do not provide independent observations to add together.

GDP now comes directly from BEA's CAGDP2 county release of February 5, 2026, replacing the discontinued metro series from FRED. All constituent-county industry lines are retained for 2023–2024, and only complete all-industry county values are summed into explicitly marked metro totals. The aggregation uses Census's July 2023 OMB delineation file: 11 Dallas counties and 10 Denver counties. Values are thousand current USD, unlike the old million-USD file.

Fortune 2025 national ranks were checked for all 21 Dallas and eight historically reported Denver entries. Every row includes the primary ranking link, a Fortune company profile, and the original location-report source. QVC changed its principal executive office to West Chester, Pennsylvania effective May 29, 2025, and its retrieved Fortune profile agrees. Its Denver row preserves the reported Englewood history but has `in_target_metro_as_verified=0`; only seven Denver entries are verified within the metro at retrieval. The 2025 roster is not a claim about the newer 2026 ranking. Dallas's Yum China row follows Fortune's Plano classification; the company also has operating headquarters in Shanghai.

Each folder's README explains units, geography, flags, overlaps and exceptions. `download_manifest.csv` gives one record per data file, direct source requests, verification date, row count and SHA-256. `data_dictionary.json` lists the actual columns. Older annual panels, duplicate QCEW sector/detail files, old GDP and derived cross-source metrics were removed. No acquisition or automation scripts were created.

## Original requested variables

1. Employment
2. Revenue
3. City GDP / regional economic output
4. State corporate income tax (general)
5. Fortune 500 corporate presence
6. Company offices / locations

**Supplementary variable introduced during discussion:** business openings, closures, and establishment growth as indicators relevant to attraction and retention.
