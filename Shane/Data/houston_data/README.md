# Houston Economic Data

This folder is the planned location for Houston-area files corresponding to the nine datasets in the project data inventory. The inventory below records the intended file names, source, reference year, and current availability. A row marked **not collected** does not have a CSV in this folder yet.

## Geography

“Houston” needs a defined geography for comparisons. Use the Houston–The Woodlands–Sugar Land metropolitan statistical area (MSA; CBSA 26420) for metro-level series, Harris County (FIPS 48201) when a source only publishes county GDP, and the City of Houston (place FIPS 4835000) only for city-level Census tables. These geographies are not interchangeable. For CBP county files, include the counties in the chosen MSA definition and document the delineation vintage.

## Dataset inventory

| Table row | Dataset | Intended file | Reference year(s) | Data rows | Status |
| ---: | --- | --- | --- | ---: | --- |
| 1 | Quarterly Census of Employment and Wages (QCEW) | `qcew_annual_2023_2025.csv` | 2023–2025 | — | Not collected in this folder. A multi-metro panel with 5 Houston rows is available at [`Artem/data/nine_metro_models/metro_year_qcew_2021_2025.csv`](../../../Artem/data/nine_metro_models/metro_year_qcew_2021_2025.csv); it is not the detailed QCEW extract named here. |
| 2 | County Business Patterns (CBP) | `cbp_employment_2023.csv` | 2023 | — | Not collected in this folder. |
| 3 | 2022 Economic Census: Geographic Area Statistics | `economic_census_2022_detail.csv.gz` | 2022 | — | Not collected in this folder. |
| 4 | 2022 Economic Census: All Sectors Summary Statistics (EC2200BASIC) | `economic_census_2022_sectors.csv` | 2022 | — | Not collected in this folder. |
| 5 | Gross Domestic Product by County (CAGDP2) | `bea_county_gdp_2023_2024.csv` | 2023–2024 | — | Not collected in this folder. Use Harris County as a county-level proxy; BEA does not publish GDP for the City of Houston. |
| 6 | State Corporate Income Tax Rates and Brackets, 2026 | `state_corporate_tax_2026.csv` | 2026 | — | Not collected in this folder. Texas has no corporate income tax; its franchise tax is separate. |
| 7 | Fortune 500 Annual Ranking | `fortune500_headquarters_2025.csv` | 2025 | — | Not collected in this folder. Filter ranked companies by a documented Houston headquarters geography. |
| 8 | County Business Patterns: Number of Establishments (ESTAB) | `cbp_establishments_2023.csv` | 2023 | — | Not collected in this folder. |
| 9 | Business Dynamics Statistics: Metro (BDSMETRO) | `bds_metro_2023.csv` | 2023 | — | Not collected in this folder. |

Data-row counts are intentionally left blank until files are collected and counted. Do not interpret an absent file as zero observations or zero activity.

## Source links

- [BLS QCEW data](https://www.bls.gov/cew/data.htm)
- [Census County Business Patterns data](https://www.census.gov/programs-surveys/cbp/data.html)
- [2022 Economic Census table EC2200BASIC](https://data.census.gov/table/ECNBASIC2022.EC2200BASIC)
- [BEA GDP by County](https://www.bea.gov/data/gdp/gdp-county)
- [Tax Foundation state corporate income tax rates and brackets](https://taxfoundation.org/data/all/state/state-corporate-income-tax-rates-brackets/)
- [Fortune 500 ranking](https://fortune.com/ranking/fortune500/)
- [Census CBP API documentation](https://www.census.gov/data/developers/data-sets/cbp-zbp.html)
- [Census BDSMETRO table](https://data.census.gov/table/BDSTIMESERIES.BDSMETRO)

## File conventions

- Keep original source files unchanged when practical; record retrieval date and source URL.
- Record the geography identifier, industry code, units, and suppression/missing-value codes in each derived file or its accompanying notes.
- Count data rows excluding the header and state that convention in the inventory.
- Keep revenue, payroll, GDP, and tax measures in their published units; do not combine values across geographies or years without documenting the method.
