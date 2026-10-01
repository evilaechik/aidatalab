# Dataset summary

Retrieved October 1, 2026. All ten planned dataset groups are available in this folder. OEWS uses official tables for ten selected metros after the national ZIP repeatedly arrived truncated. ACS uses public table exports, with no API key. Originals are preserved; extracted tables are supplied where useful.

`download_manifest.csv` records each data/support file's source URL, retrieval date, size, SHA-256 checksum, and extraction method. The collection has not yet been harmonized or merged with the existing Atlanta files.

## Data and intended uses

### 1. Industry employment, establishments, and wages — QCEW

- **Files:** `qcew/2015_annual_singlefile.zip` through `qcew/2025_annual_singlefile.zip` (11 annual archives, each containing a CSV).
- **Source:** [Bureau of Labor Statistics, Quarterly Census of Employment and Wages](https://www.bls.gov/cew/downloadable-data-files.htm).
- **Information:** Industry/NAICS, ownership, geographic codes, annual average employment and establishment counts, total wages, average pay, location quotients, and disclosure indicators. Multiple geographic and industry aggregation levels are included.
- **Use:** Establish Atlanta and peer-region industry trends, identify employment/establishment growth gaps, and compare industry pay and concentration. Start with a common 2015–2023 window shared with CBP and BDS, then extend the QCEW trends through 2025.
- **Care:** Select consistent ownership and aggregation levels; do not double-count totals and their components or interpret suppressed values as zero. Detailed metro reporting changed in 2025; county aggregation may be needed. Check county-to-metro boundaries and NAICS revisions before comparing years.

### 2. Establishment size distribution — County Business Patterns

- **Files:** `cbp/cbp15msa.zip` through `cbp/cbp23msa.zip` (nine archives; the `.txt` members are comma-separated tables).
- **Source:** [U.S. Census Bureau, County Business Patterns](https://www.census.gov/data/datasets/2023/econ/cbp/2023-cbp.html).
- **Information:** Metro code, NAICS, employment, first-quarter and annual payroll, establishment totals, establishment counts by employee-size band, and disclosure/noise flags.
- **Use:** Compare Atlanta's industry mix and small/medium/large establishment shares with peers; locate segments where establishment growth lags.
- **Care:** Size bands describe establishments, not the total size of a multi-location firm. Preserve suppression flags, normalize changing column names, and harmonize NAICS and metro definitions across years.

### 3. Business entry, exit, and job flows — BDS by sector

- **File:** `bds/bds2023_msa_sec.csv` (808,450 rows, 1978–2023).
- **Source:** [U.S. Census Bureau, Business Dynamics Statistics](https://www.census.gov/data/datasets/time-series/econ/bds/bds-datasets.html).
- **Information:** Year, MSA code, sector, firms, establishments, employment, establishment entry/exit, and job creation/destruction measures and rates.
- **Use:** Distinguish weak business formation from elevated exits or weak expansion, and compare Atlanta's business turnover with peer regions and sector trends.
- **Care:** These are aggregate business dynamics. Entries/exits do not establish individual relocations, and the table does not directly provide firm-level survival histories.

### 4. Business dynamics by firm size — BDS sector × size

- **File:** `bds/bds2023_msa_sec_fzc.csv` (2,425,350 rows, 1978–2023).
- **Source:** Same official [BDS release](https://www.census.gov/data/datasets/time-series/econ/bds/bds-datasets.html).
- **Information:** The sector table's business and job-flow measures plus `fsizecoarse`, a coarse firm-size category.
- **Use:** Test whether Atlanta's performance gaps concentrate in particular industry/firm-size combinations.
- **Care:** Firm size and CBP establishment size are different concepts. Keep the BDS size categories and publication definitions; avoid summing overlapping industry or geographic totals.

### 5. Announced layoffs and closures — WARN

- **Files:** `warn/warn_notices.csv`, `warn/coverage.json`, and `warn/SOURCE_README.md`.
- **Source:** [APVentureEngine / WARNFeed](https://github.com/APVentureEngine/warn-act-notices), a third-party compilation of state WARN notices. Its documentation identifies coverage and a CC BY 4.0 attribution requirement.
- **Information:** 61,431 notices across 48 states, with company names and normalized names, locations, affected employees, notice/effective dates, notice type, and first-seen date. Georgia has 284 notices dated January 2023–September 2026 in this snapshot.
- **Use:** Identify large layoff/closure events, investigate industry-specific retention concerns, and create dated leads for checking against Atlanta business records.
- **Care:** State coverage varies substantially. WARN misses many small closures and does not verify completed layoffs or relocations. Validate company/address matches against the originating state notice before making firm-level claims.

### 6. Comparable-region incentive awards — North Carolina grants

- **Files:** `nc_grants/DOC_ED-Grants_Spreadsheet_01Oct25_asPublished-Web.xlsx` and `nc_grants/economic_development_grant_report_2025.pdf`.
- **Source:** [North Carolina Department of Commerce, 2025 Economic Development Grant Report appendix](https://www.commerce.nc.gov/data-tools-reports/reports-policymakers/incentive-programs-reports/appendix-economic-development-grant-report).
- **Information:** Workbook tabs include `Data`, `Local`, pivots, and report tables. Fields include award program/date, awardee, county, required jobs/wages, disbursements, status, reported jobs, project identifiers, and site/expansion details. The report covers awards from 2007 through June 2025; performance reporting periods differ by program.
- **Use:** Compare incentive structure, job commitments, payouts, and reported performance with Invest Atlanta records, especially in North Carolina peer regions.
- **Care:** Requirements differ from achieved outcomes. A project can receive multiple awards; deduplicate project identifiers and map counties to metros. Observed awards and outcomes alone do not establish an incentive's causal effect.

### 7. Occupational workforce and wages — OEWS selected metros

- **Files:** `oews/oews_may2025_selected_metros.csv`, ten `oews_may2025_<MSA>.csv` files, ten corresponding `_raw.json` responses, `selected_metros_sources.json`, and datatype/footnote definition JSONs.
- **Source:** [BLS May 2025 metro estimates](https://www.bls.gov/oes/2025/may/oessrcma.htm), extracted from the official public metro-table service. The source/request file records the exact public requests.
- **Coverage:** Atlanta (12060), Austin (12420), Charlotte (16740), Dallas (19100), Denver (19740), Houston (26420), Nashville (34980), Phoenix (38060), Raleigh (39580), and Tampa (45300). These are an initial comparison set, not a finalized peer-selection methodology.
- **Information:** 6,791 unique metro/occupation rows, including occupational aggregates; 17 measures cover employment, mean/median and percentile wages, relative standard errors, employment per 1,000 jobs, and location quotients. CSVs retain source URLs and measure-specific footnote codes.
- **Use:** Compare occupation-specific labor costs and concentrations, and examine workforce conditions associated with industry performance gaps. Use the combined file or the individual metro files, not both together.
- **Care:** Cross-industry estimates include private and government employment and exclude self-employment. Aggregate and detailed SOC rows overlap. A `-` means a footnoted unavailable/top-coded value, not zero; retain the footnotes. These are May 2025 estimates, not a historical panel or a direct measure of unfilled job demand.

### 8. Resident workforce and socioeconomic characteristics — ACS

- **Files:** `acs/acs5_dp02_metros_2019_2024.zip`, `acs5_dp03_metros_2019_2024.zip`, and their extracted `ACSDP5Y<year>.<table>-Data.csv`, `-Column-Metadata.csv`, and `-Table-Notes.txt` members.
- **Source:** Census public exports of [DP02 social characteristics](https://data.census.gov/table/ACSDP5Y2024.DP02?g=010XX00US$31000M1) and [DP03 economic characteristics](https://data.census.gov/table/ACSDP5Y2024.DP03?g=010XX00US$31000M1), for all available metropolitan areas in the United States and Puerto Rico.
- **Information:** Four data tables: DP02 and DP03 for the 2015–2019 and 2020–2024 five-year periods. Each 2019 table has 392 metros; each 2024 table has 393. DP02 covers education, language, households, and other social characteristics. DP03 covers labor-force status, commuting, employment characteristics, income, and poverty. Estimates, percentages, and margins of error are included.
- **Use:** Investigate education/talent supply, labor participation, commuting, and socioeconomic conditions associated with Atlanta's gaps; compare non-overlapping five-year periods.
- **Care:** Each data CSV has a variable-code header followed by a descriptive-label row; skip the label row when loading numeric data. GEOID prefixes change between vintages (Atlanta: `310M500US12060` in 2019 versus `310M700US12060` in 2024). Extract the five-digit CBSA code for a candidate join, then verify boundary comparability. Keep margins of error and align variable definitions. ACS measures residents, while QCEW/OEWS measure workplaces.

### 9. Office-market conditions

- **Files:** `real_estate/us_office_marketbeat_q4_2025.pdf` (seven pages) and `atlanta_office_marketbeat_q4_2025.pdf` (four pages).
- **Source:** [Cushman & Wakefield U.S. Office MarketBeat](https://www.cushmanwakefield.com/en/united-states/insights/us-marketbeats/us-office-marketbeat-reports).
- **Information:** Q4 2025 market comparisons and Atlanta detail, including office inventory, vacancy, asking rent, absorption, and construction indicators.
- **Use:** Compare office space costs and slack across regions and identify Atlanta submarkets relevant to later site screening.
- **Care:** PDF tables require extraction before numeric merging. Broker market/submarket boundaries do not necessarily match Census metros or Atlanta city limits; record rent definitions and units.

### 10. Industrial-market conditions

- **Files:** `real_estate/us_industrial_marketbeat_q4_2025.pdf` (seven pages) and `atlanta_industrial_marketbeat_q4_2025.pdf` (four pages).
- **Source:** [Cushman & Wakefield U.S. Industrial MarketBeat](https://www.cushmanwakefield.com/en/united-states/insights/us-marketbeats/us-industrial-marketbeat).
- **Information:** Q4 2025 industrial inventory, vacancy, asking rent, absorption, and construction, with national market comparisons and Atlanta detail.
- **Use:** Assess logistics/manufacturing space constraints and costs as potential explanations for industry gaps.
- **Care:** Extract PDF tables and standardize broker geography. Industrial and office rent conventions differ; these reports do not provide a complete inventory of available individual parcels.

## First analysis steps

1. Define peer regions and a consistent geographic crosswalk. Treat metro evidence as regional context, not City of Atlanta outcomes.
2. Build the 2015–2023 industry/size benchmarking panel from QCEW, CBP, and BDS; extend QCEW through 2025 separately.
3. Add ACS and OEWS explanatory measures and the Q4 2025 property snapshots, preserving their different reference periods.
4. Use WARN and incentive records to investigate specific gaps after the aggregate benchmarking. Existing licenses, grants, and parcels need their own company/address/geographic matching; these new aggregate files have no shared firm identifier.
