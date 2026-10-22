# Houston datasets

Collected October 21, 2026. **Nine data files**, matching the Dallas/Denver filenames, column order, source programs and reference windows, plus this README, `download_manifest.csv` and `data_dictionary.json`. No acquisition scripts are included.

Regional label: **Houston-Pasadena-The Woodlands, TX (CBSA 26420)**. Regional measures describe the metro economy, not municipal boundaries. Native source geography/industry vintages remain intact; county GDP uses the documented July 2023 OMB county definition.

| Requested row | Dataset | File | Years | Rows |
| --- | --- | --- | --- | ---: |
| 1 | Quarterly Census of Employment and Wages (QCEW) | [qcew_annual_2023_2025.csv](qcew_annual_2023_2025.csv) | 2023–2025 | 4,067 |
| 2 | County Business Patterns (CBP) | [cbp_employment_2023.csv](cbp_employment_2023.csv) | 2023 | 216 |
| 3 | 2022 Economic Census: Geographic Area Statistics | [economic_census_2022_detail.csv.gz](economic_census_2022_detail.csv.gz) | 2022 | 2,117 |
| 4 | 2022 Economic Census: All Sectors Summary Statistics (EC2200BASIC) | [economic_census_2022_sectors.csv](economic_census_2022_sectors.csv) | 2022 | 15 |
| 5 | Gross Domestic Product by County (CAGDP2) | [bea_county_gdp_2023_2024.csv](bea_county_gdp_2023_2024.csv) | 2023–2024 | 682 |
| 6 | State Corporate Income Tax Rates and Brackets, 2026 | [state_corporate_tax_2026.csv](state_corporate_tax_2026.csv) | 2026 | 1 |
| 7 | Fortune 500 Annual Ranking | [fortune500_headquarters_2025.csv](fortune500_headquarters_2025.csv) | 2025 | 26 |
| 8 | County Business Patterns: Number of Establishments (ESTAB) | [cbp_establishments_2023.csv](cbp_establishments_2023.csv) | 2023 | 216 |
| 9 | Business Dynamics Statistics: Metro (BDSMETRO) | [bds_metro_2023.csv](bds_metro_2023.csv) | 2023 | 20 |

The manifest provides exact source requests, reference periods, observed vintages, checksums, row counts, units and extraction methods. The dictionary records every column and the county membership. The federal-source values were compared with the downloaded official responses after the documented transformations.

## Coverage and interpretation

- QCEW includes every annual area row for 2023–2025. The 2025 file has only the all-ownership/all-industry total; missing industry detail is unavailable, not zero. Do not compare a 2024 private-sector subtotal with a 2025 all-ownership total.
- CBP employment/payroll and establishment files are two projections of the same 2023 table, with broad industry and establishment-size categories. Establishments are business locations, not named corporate offices.
- Both revenue files use EC2200BASIC, reference year 2022, the explicitly requested exception. The sector file selects 15 broad sectors with TYPOP=00 and TAXSTAT=00. The two views overlap.
- GDP uses CAGDP2, the county table; SAGDP2N is state GDP. Values are thousand current USD. County rows retain all published industry lines and markers; only complete all-industry metro sums are derived. Select `geo_type=metro` and `LineCode=1` for those sums, and do not add them to county rows.
- Tax is the requested 2026 statutory snapshot. It does not measure effective business tax burden or 2023 conditions. Texas has no corporate income tax but does impose a franchise/margin tax. Florida’s published bracket starts above $50,000. Preserve state rows separately.
- Fortune is the **2025 edition**, not 2026. Published regional rosters and public company/report or indexed ranking entries are cited per row. Municipality and current-location fields remain blank where not independently captured. Blank `in_target_metro_as_verified` means unknown, not zero; these additions do not have a complete independent current-HQ audit. Do not compare their partial verified-current counts with Dallas/Denver’s checked counts.
- BDS entry/exit and job flows are economic-dynamics proxies. They do not identify company relocations or establish incentive effects.
- Keep CBSA, FIPS, NAICS, ownership, size and legal-form codes as text. Preserve suppression/noise/imputation flags and source zeroes; flagged zero is not necessarily an observed zero. Never add totals to their components. No industry crosswalk was applied.

## County GDP membership

48015 Austin County, Texas; 48039 Brazoria County, Texas; 48071 Chambers County, Texas; 48157 Fort Bend County, Texas; 48167 Galveston County, Texas; 48201 Harris County, Texas; 48291 Liberty County, Texas; 48339 Montgomery County, Texas; 48407 San Jacinto County, Texas; 48473 Waller County, Texas.

## Headquarters source qualifications

26 Houston-area entries selected from the published 2025 Texas ranking roster, with the count cross-checked against the Greater Houston Partnership’s Houston Facts 2025 publication. Exact 2025 municipalities are not independently captured and are blank; the region must not be read as the City of Houston.

Primary roster/reference: [published source](https://www.statesman.com/story/business/2025/06/06/tesla-falls-on-fortune-500-list-of-biggest-companies-dell-and-oracle-rise/84075295007/).

See [dataset context](../datasets_context.md) and [research context](../../research_context.md).
