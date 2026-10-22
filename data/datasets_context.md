# Economic and Business Dataset Context

Updated October 21, 2026.

These data support the goal of identifying where **Atlanta lags in business attraction, expansion and retention**, investigating the drivers of those gaps, and assessing possible incentive strategies. Atlanta and eight candidate comparison metros now have the same nine data files, covering employment, business activity, output, tax conditions and major corporate presence. Collection does not by itself justify the peer group or establish incentive effects.

**81 data files are collected**, with nine files in each city folder. Dallas/Denver’s 18 existing data files were moved unchanged; the other 63 were added using the same source programs, reference windows and per-dataset column order. New collection was reviewed October 21; the preserved Dallas/Denver records retain their October 15 verification dates.

| City folder | Metropolitan area (CBSA) | GDP counties |
| --- | --- | ---: |
| [Atlanta](atlanta_data/README.md) | Atlanta–Sandy Springs–Roswell, GA (12060) | 29 |
| [Austin](austin_data/README.md) | Austin–Round Rock–San Marcos, TX (12420) | 5 |
| [Charlotte](charlotte_data/README.md) | Charlotte–Concord–Gastonia, NC–SC (16740) | 11 |
| [Dallas](dallas_data/README.md) | Dallas–Fort Worth–Arlington, TX (19100) | 11 |
| [Denver](denver_data/README.md) | Denver–Aurora–Centennial, CO (19740) | 10 |
| [Houston](houston_data/README.md) | Houston–Pasadena–The Woodlands, TX (26420) | 10 |
| [Miami](miami_data/README.md) | Miami–Fort Lauderdale–West Palm Beach, FL (33100) | 3 |
| [Nashville](nashville_data/README.md) | Nashville-Davidson–Murfreesboro–Franklin, TN (34980) | 14 |
| [Raleigh](raleigh_data/README.md) | Raleigh–Cary, NC (39580) | 3 |

Regional measures describe metropolitan economies, rather than municipal boundaries. GDP retains individual counties and explicitly marked calculated metro totals. Tax observations are state-level. Raleigh excludes Durham; Miami includes Broward and Palm Beach. County GDP membership is documented in every city dictionary using the July 2023 OMB delineation; other programs retain their native geography and industry vintages.

| File in every city folder | Dataset / source organization | Years | What it contains and why it matters |
| --- | --- | --- | --- |
| `qcew_annual_2023_2025.csv` | [Quarterly Census of Employment and Wages — BLS](https://www.bls.gov/cew/data.htm) | 2023–2025 | Employment, wages and establishment counts; compares job growth and pay. Industry detail covers 2023–2024; 2025 has metro totals only. |
| `cbp_employment_2023.csv` | [County Business Patterns — Census Bureau](https://www.census.gov/programs-surveys/cbp/data.html) | 2023 | Employment and payroll by industry and establishment size; shows the structure of the local business economy. |
| `economic_census_2022_detail.csv.gz` | [2022 Economic Census, Geographic Area Statistics — Census Bureau](https://data.census.gov/table/ECNBASIC2022.EC2200BASIC) | 2022 | Detailed industry sales and receipts; identifies the scale of business activity across industries. |
| `economic_census_2022_sectors.csv` | [2022 Economic Census, All Sectors Summary (EC2200BASIC) — Census Bureau](https://data.census.gov/table/ECNBASIC2022.EC2200BASIC) | 2022 | Sales and receipts for 15 broad sectors; makes major sectors easier to compare. |
| `bea_county_gdp_2023_2024.csv` | [Gross Domestic Product by County (CAGDP2) — BEA](https://www.bea.gov/data/gdp/gdp-by-county) | 2023–2024 | County output and calculated metro totals; measures regional economic size and nominal growth. |
| `state_corporate_tax_2026.csv` | [State Corporate Income Tax Rates and Brackets — Tax Foundation](https://taxfoundation.org/data/all/state/state-corporate-income-tax-rates-brackets/) | 2026 | State statutory corporate income-tax treatment; provides context for one part of business costs. |
| `fortune500_headquarters_2025.csv` | [Fortune 500 Annual Ranking — Fortune](https://fortune.com/ranking/fortune500/2025/) | 2025 | National ranks and reported regional headquarters rosters; indicates major corporate presence, with location evidence and missing checks explicitly qualified. |
| `cbp_establishments_2023.csv` | [County Business Patterns, ESTAB — Census Bureau](https://www.census.gov/data/developers/data-sets/cbp-zbp.html) | 2023 | Business-location counts by industry and establishment size; measures the local business footprint as a proxy for offices. |
| `bds_metro_2023.csv` | [Business Dynamics Statistics, BDSMETRO — Census Bureau](https://data.census.gov/table/BDSTIMESERIES.BDSMETRO) | 2023 | Establishment openings, closures and job flows; measures business turnover and employment dynamics. |

The annual windows intentionally match Dallas/Denver. The two Economic Census files retain the requested **2022 exception**; 2025 rankings and 2026 tax conditions are separately dated context. This is not a common multi-year panel across all programs or a claim to contain each publisher’s newest release.

The Economic Census files overlap, as do the two CBP files; do not add their values together or add industry/size totals to their components. GDP uses the county table **CAGDP2** because SAGDP2N is a state table. GDP, receipts and Census payroll are in **thousand USD**, while QCEW wages/pay are **USD**. Metro GDP sums are derived and must not be added to county rows. Preserve source flags and identifiers as text; a suppressed source zero is not an observed zero. No industry crosswalk was applied.

Charlotte’s tax file has **two rows**, North Carolina (2%) and South Carolina (5%); these are separate state regimes, not an averaged metro rate. Texas’s 0 encodes absence of corporate income tax and does not remove its franchise/margin tax. The other state rates follow the requested 2026 Tax Foundation table and do not measure effective tax burdens.

Fortune files use the **2025 edition** and cite public regional/Chamber rosters, primary reports and public indexed ranking entries. New files leave historical municipality and current-HQ fields blank when independently dated evidence was not captured. Blank `in_target_metro_as_verified` means **unknown**, not zero. A complete current-HQ audit across all nine areas remains outstanding; partial verified-current counts should not be compared. Denver’s historical QVC row retains its documented Pennsylvania move. Atlanta’s fresh Chamber roster includes Newell Brands, yielding 15 metro entries; Aflac and Mohawk are excluded because they are outside the metro.

Each city folder also has **README.md** for coverage and interpretation, **download_manifest.csv** for exact source requests, dates, row counts and checksums, and **data_dictionary.json** for columns, units, geography and handling rules. These supporting files preserve the source qualifications. No acquisition scripts are included. See [research context](../research_context.md) for comparison-design decisions and remaining analysis.
