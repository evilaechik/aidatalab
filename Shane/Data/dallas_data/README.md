# Dallas datasets

Verified October 15, 2026. This folder contains **nine data files**, one for each row of the requested source table, plus this README, a source manifest, and a data dictionary. No acquisition or automation script is included.

Regional data use **Dallas-Fort Worth-Arlington, TX (CBSA 19100)**. The label “Dallas” represents the metropolitan economy, not municipal boundaries. The tax file is state-level. GDP includes the metro’s individual counties and explicitly identified derived metro totals.

## Requested file inventory

| Table row | Dataset | File | Reference year(s) | Data rows | Action |
| --- | --- | --- | --- | ---: | --- |
| 1 | Quarterly Census of Employment and Wages (QCEW) | [qcew_annual_2023_2025.csv](qcew_annual_2023_2025.csv) | 2023–2025 | 4,070 | replaced |
| 2 | County Business Patterns (CBP) | [cbp_employment_2023.csv](cbp_employment_2023.csv) | 2023 | 232 | replaced |
| 3 | 2022 Economic Census: Geographic Area Statistics | [economic_census_2022_detail.csv.gz](economic_census_2022_detail.csv.gz) | 2022 | 2,102 | retained_verified |
| 4 | 2022 Economic Census: All Sectors Summary Statistics (EC2200BASIC) | [economic_census_2022_sectors.csv](economic_census_2022_sectors.csv) | 2022 | 15 | retained_verified |
| 5 | Gross Domestic Product by County (CAGDP2) | [bea_county_gdp_2023_2024.csv](bea_county_gdp_2023_2024.csv) | 2023–2024 | 750 | replaced |
| 6 | State Corporate Income Tax Rates and Brackets, 2026 | [state_corporate_tax_2026.csv](state_corporate_tax_2026.csv) | 2026 | 1 | retained_verified |
| 7 | Fortune 500 Annual Ranking | [fortune500_headquarters_2025.csv](fortune500_headquarters_2025.csv) | 2025 | 21 | replaced |
| 8 | County Business Patterns: Number of Establishments (ESTAB) | [cbp_establishments_2023.csv](cbp_establishments_2023.csv) | 2023 | 232 | new_projection |
| 9 | Business Dynamics Statistics: Metro (BDSMETRO) | [bds_metro_2023.csv](bds_metro_2023.csv) | 2023 | 20 | replaced |

`download_manifest.csv` records direct download URLs, publisher landing links, reference periods, observed source vintages, row counts, checksums, units and verification methods. `data_dictionary.json` lists every file’s columns, geography, key variables and handling rules.

## Dates and source checks

- All annual files begin in 2023. QCEW includes annual 2023, 2024 and 2025 data. [BLS changed MSA publication to totals only beginning in second quarter 2025](https://www.bls.gov/cew/about-data/data-availability.htm); this metro’s 2025 annual area file contains only the all-ownership, all-industry total. Missing 2025 industry detail is unavailable, not zero. Do not compare a private-sector subtotal in 2024 with the all-ownership total in 2025.
- [CBP currently stops at reference year 2023](https://www.census.gov/programs-surveys/cbp/data.html). [BDSMETRO currently stops at 2023](https://www.census.gov/programs-surveys/bds/data.Tables.html). Their existing 2023 source values were checked against fresh Census responses before the older years were removed. These extracts cover totals and broad industry sectors; CBP also includes establishment employment-size bands.
- The two Economic Census files are the explicit **2022 exception** in the request. The existing files were retained byte-for-byte after comparison with a fresh official EC2200BASIC response. Detail has the published industry and operation/tax-category rows; the sector file selects broad sectors with TYPOP=00 and TAXSTAT=00. [Census explains that the geographic release uses EC2200BASIC across sectors](https://www.census.gov/programs-surveys/economic-census/year/2022/news-updates/whats-new.html). These are overlapping views of the same release, not two independent revenue measurements.
- The existing 2026 tax file was retained byte-for-byte after checking [the requested Tax Foundation table](https://taxfoundation.org/data/all/state/state-corporate-income-tax-rates-brackets/). Colorado’s published rate is 4.4%, with a source caveat about a revenue-triggered reduction. Texas has no corporate income tax but imposes a franchise/margin tax; the file’s 0 is an explicit encoding of no corporate income tax, not an effective total tax burden. Colorado’s flat bracket starts above $0; Texas has no comparable corporate-income-tax bracket.
- Fortune uses the **2025 annual ranking**, an eligible post-2023 edition; it is not the newest 2026 ranking. National ranks for every included company were verified against [Fortune’s 2025 list](https://fortune.com/ranking/fortune500/2025/). Per-row Fortune profiles and original location-report links are included. All 21 rows have 2025 national ranks verified on Fortune and reported HQ cities within this metro. Fortune currently spells McKesson and Caterpillar’s city “Irvine, Tex.”; the 2025 Dallas Regional Chamber roster identifies Irving. The file retains Irving with a note. Yum China follows Fortune’s Plano classification; its operating headquarters are in Shanghai.

## GDP geography and units

The request’s county-GDP label is correct, but **SAGDP2N is a state table**. This folder uses BEA **CAGDP2, Gross domestic product by county**, replacing the former discontinued metro series distributed by FRED. The official [February 5, 2026 release](https://www.bea.gov/data/gdp/gdp-by-county) supplies 2024 and revised 2023 estimates. Values are **thousand current USD** and are not comparable to the old file’s million-USD column without conversion.

The file preserves all published county industry lines for 2023–2024 and adds only the complete all-industry metro sums. `geo_type=county` denotes published county values; `geo_type=metro` and `value_status=derived_sum_of_counties` denote local arithmetic sums. To select metro GDP use `geo_type=metro` and `LineCode=1`. Do not add those rows to their constituent counties. Non-numeric source markers remain intact.

County membership comes from [Census’s July 2023 OMB delineation file](https://www2.census.gov/programs-surveys/metro-micro/geographies/reference-files/2023/delineation-files/list1_2023.xlsx):

48085 Collin County; 48113 Dallas County; 48121 Denton County; 48139 Ellis County; 48231 Hunt County; 48251 Johnson County; 48257 Kaufman County; 48367 Parker County; 48397 Rockwall County; 48439 Tarrant County; 48497 Wise County.

## Interpretation and importing

- Preserve CBSA, FIPS, NAICS, ownership, legal-form and size-class codes as **text**. `economic_census_2022_detail.csv.gz` is gzip-compressed UTF-8 CSV; other data files are UTF-8 CSV.
- QCEW employment is an annual average; CBP employment is a March reference-period measure. Their scopes differ. Payroll in CBP and receipts/payroll in the Economic Census are **thousand USD**; QCEW wages/pay are **USD**.
- Preserve disclosure, imputation and noise flags. Source-encoded zero with a nondisclosure/unavailable flag is not an observed zero. Never sum industry totals with their components, size totals with individual size bands, or the two Economic Census views together.
- The establishment-specific CBP file preserves `ESTAB`, its flags, industry, employment-size and legal-form identifiers. It is a projection of the same CBP table as the employment file. Establishments count operating locations and are a proxy for offices, not a named company-office directory.
- BDS establishment entry/exit and job flows measure births/deaths and economic dynamics. They do not identify corporate relocations, business attraction from outside the region, or program effects.
- Source NAICS and geography vintages are preserved. No industry crosswalk or rebasing across source programs was performed. The county GDP aggregation uses the explicitly documented 2023 boundaries.

Older 2015–2022 annual observations, duplicate QCEW sector/detail files, the old FRED GDP file and the cross-source derived city-year file were removed from this folder. The two verified 2022 Economic Census files and the verified 2026 tax file were preserved.

See [dataset context](../../us_city_economic_datasets_context.md) and [research context](../../research_context.md).
