# St. Louis datasets

Collected October 27, 2026. **Nine data files**, with the same filenames, column order, source programs and reference windows as the existing metro folders. Supporting files are this README, `download_manifest.csv` and `data_dictionary.json`.

Regional label: **St. Louis, MO-IL (CBSA 41180)**. Batch 2 follows rank **24** in [the top-50 list](../top_50_us_metro_areas_by_gdp.md). Measures describe the metropolitan economy rather than municipal boundaries.

| Requested row | File | Reference years | Rows |
| --- | --- | --- | ---: |
| 1 | [qcew_annual_2023_2025.csv](qcew_annual_2023_2025.csv) | 2023–2025 | 3,894 |
| 2 | [cbp_employment_2023.csv](cbp_employment_2023.csv) | 2023 | 193 |
| 3 | [economic_census_2022_detail.csv.gz](economic_census_2022_detail.csv.gz) | 2022 | 1,988 |
| 4 | [economic_census_2022_sectors.csv](economic_census_2022_sectors.csv) | 2022 | 15 |
| 5 | [bea_county_gdp_2023_2024.csv](bea_county_gdp_2023_2024.csv) | 2023–2024 | 1,022 |
| 6 | [state_corporate_tax_2026.csv](state_corporate_tax_2026.csv) | 2026 | 2 |
| 7 | [fortune500_headquarters_2025.csv](fortune500_headquarters_2025.csv) | 2025 | 7 |
| 8 | [cbp_establishments_2023.csv](cbp_establishments_2023.csv) | 2023 | 193 |
| 9 | [bds_metro_2023.csv](bds_metro_2023.csv) | 2023 | 20 |

## Coverage and interpretation

- QCEW preserves all annual area rows. Rows by year: 2023: 1,947; 2024: 1,946; 2025: 1. The 2025 response contains only the all-industry, all-ownership total. Unpublished detail is unavailable, not zero.
- CBP employment/payroll and establishment files are two views of the same 2023 source. Retain broad industry and establishment-size categories, all flags and identifiers as text. Establishments are business locations, not named offices. Do not add the two files together or totals to their components.
- Economic Census detail and the 15-sector view both use EC2200BASIC for 2022, the requested exception. The sector view selects TYPOP=00, TAXSTAT=00 and the same 15 sector codes as existing folders. NAICS2022 aliases and column order match the existing schema. Retain every suppression and imputation flag.
- GDP uses CAGDP2 for all 15 July 2023 OMB constituent counties, every published industry line, and years 2023–2024. The only derived rows are complete all-industry metro sums, marked `geo_type=metro` and `value_status=derived_sum_of_counties`. County rows overlap metro totals. GDP, Census receipts and payroll use thousand USD; QCEW wages/pay use USD.
- Tax contains 2 separate constituent-state regime(s), using the requested 2026 Tax Foundation table. For graduated schedules, the numeric field is the top published rate and `source_display` retains all brackets. Zero in Washington means no corporate income tax; its gross receipts tax remains applicable. Statutory rates exclude local taxes and do not measure effective total business tax burdens. Do not average states.
- Fortune uses the **2025 edition** and the public dataset behind [Fortune’s headquarters map](https://interactives.fortune.com/f500-dataviz-2025/). The roster is assigned to the metro using publisher coordinates and Census 2023 polygons. Reported municipalities are preserved. Current-location fields remain blank because a complete independent current-HQ audit was not performed. These fields mean unknown, not outside-metro. Co-headquarters are not added to the publisher’s single-location roster.
- BDS retains all returned broad-industry rows and job-flow/entry/exit flags for 2023. It measures economic turnover, not verified company relocations or incentive effects.
- Source zeroes and nonnumeric markers are retained. Do not impute suppressed observations, mix units or industry vintages, or add totals to their component rows. No industry crosswalk is applied.

## Geography

- GDP county membership follows the July 2023 OMB list. Each other federal program retains its native geography vintage; no geographic backcast is implied.
- Fortune metro assignment is derived from publisher coordinates and 2023 Census cartographic CBSA polygons (500k). It does not independently verify the publisher headquarters address or all co-headquarters.
- St. Louis city (29510) is a county equivalent distinct from St. Louis County (29189). Both are separate source areas in the GDP file and included once in each metro sum.

## County GDP membership

17005 Bond County, Illinois; 17013 Calhoun County, Illinois; 17027 Clinton County, Illinois; 17083 Jersey County, Illinois; 17117 Macoupin County, Illinois; 17119 Madison County, Illinois; 17133 Monroe County, Illinois; 17163 St. Clair County, Illinois; 29071 Franklin County, Missouri; 29099 Jefferson County, Missouri; 29113 Lincoln County, Missouri; 29183 St. Charles County, Missouri; 29189 St. Louis County, Missouri; 29219 Warren County, Missouri; 29510 St. Louis city, Missouri.

## Verification and provenance

Every federal-source output row was checked against its downloaded official response after the documented transformation. Validation covers columns/order, reference years, target identifiers, complete county coverage, GDP sums, both Census projections, 15 sector rows and 20 BDS rows. The manifest provides exact request URLs, observed vintages, row counts, bytes and SHA-256 checksums. The dictionary also records raw-response checksums and geography rules. Source downloads and transformation helpers are not part of the city folder.

See [dataset context](../datasets_context.md) and [batch 2 summary](../collection_batch_02.md).
