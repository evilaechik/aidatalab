# U.S. City Economic and Business Dataset Research Context

## Objective
Build a comparable public-data dataset for large U.S. cities, particularly to benchmark **Atlanta** against peer cities on economic strength, business attraction, retention, and corporate presence. An AI agent should identify, retrieve, and harmonize statistics for any requested city and year.

## Required variables and dataset links

| Variable | Exact dataset / source | Search or download link | Geography and notes |
|---|---|---|---|
| Employment | **BLS Quarterly Census of Employment and Wages (QCEW)** | https://www.bls.gov/cew/data.htm | County and metropolitan-area industry employment, wages, establishments; quarterly/annual. |
| Employment; establishments; payroll | **U.S. Census County Business Patterns (CBP)** | https://www.census.gov/programs-surveys/cbp/data.html | County, metro, ZIP (depending on release); NAICS employment, payroll, establishment counts. |
| Industry revenue / sales / receipts | **2022 Economic Census: Geographic Area Statistics** | https://data.census.gov/ | Search Economic Census geographic statistics; select geographic areas and NAICS industries. Geographic coverage varies; suppression possible. |
| Industry revenue / sales / receipts | **2022 Economic Census: All Sectors Summary Statistics (EC2200BASIC)** | https://data.census.gov/table/ECNBASIC2022.EC2200BASIC | Summary table with sales/receipts and related measures where available. Economic Census is periodic, not annual. |
| Economic output / GDP | **BEA Gross Domestic Product by County (SAGDP2N)** | https://apps.bea.gov/itable/?ReqID=70&step=1 | County GDP, total and by industry; aggregate counties for region. No standardized GDP for municipality boundaries. |
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

## Original requested variables

1. Employment
2. Revenue
3. City GDP / regional economic output
4. State corporate income tax (general)
5. Fortune 500 corporate presence
6. Company offices / locations

**Supplementary variable introduced during discussion:** business openings, closures, and establishment growth as indicators relevant to attraction and retention.
