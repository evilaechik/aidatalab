# Metro collection batch 1

Completed October 27, 2026. This batch covers the **first ten metros without an existing data folder**, working in order down [the top-50 GDP list](top_50_us_metro_areas_by_gdp.md). Dallas, Houston, Atlanta and Miami were skipped while selecting these ten because their folders already existed.

**90 new data files across ten folders**, plus one README, manifest and dictionary per metro. At batch 1 completion, the collection had **171 data files across 19 metro folders**. The original nine metro folders and the supplied ranking list were preserved.

| GDP rank | Metro folder | CBSA | OMB counties / equivalents | Data files | File rows |
| ---: | --- | --- | ---: | ---: | ---: |
| 1 | [New York](new_york_data/README.md) | 35620 | 22 | 9 | 8,316 |
| 2 | [Los Angeles](los_angeles_data/README.md) | 31080 | 2 | 9 | 6,926 |
| 3 | [Chicago](chicago_data/README.md) | 16980 | 13 | 9 | 7,621 |
| 4 | [San Francisco–Oakland](san_francisco_data/README.md) | 41860 | 5 | 9 | 6,819 |
| 7 | [Washington](washington_data/README.md) | 47900 | 23 | 9 | 7,647 |
| 8 | [Boston](boston_data/README.md) | 14460 | 7 | 9 | 6,908 |
| 10 | [Seattle](seattle_data/README.md) | 42660 | 3 | 9 | 6,635 |
| 11 | [Philadelphia](philadelphia_data/README.md) | 37980 | 11 | 9 | 7,349 |
| 13 | [San Jose](san_jose_data/README.md) | 41940 | 2 | 9 | 6,015 |
| 14 | [Phoenix](phoenix_data/README.md) | 38060 | 2 | 9 | 6,621 |
| | **Batch total** | | | **90** | **70,857** |

File-row counts include overlapping projections and calculated metro totals; they are not counts of unique businesses or nonoverlapping observations. Washington's 23 OMB county equivalents are covered by 18 published BEA reporting areas.

## Matching files and reference windows

Every new folder contains the same filenames and column order as Dallas and Denver:

| File | Reference years |
| --- | --- |
| `qcew_annual_2023_2025.csv` | 2023–2025; 2025 metro total only |
| `cbp_employment_2023.csv` | 2023 |
| `economic_census_2022_detail.csv.gz` | 2022 |
| `economic_census_2022_sectors.csv` | 2022; 15 broad sectors |
| `bea_county_gdp_2023_2024.csv` | 2023–2024 |
| `state_corporate_tax_2026.csv` | 2026 |
| `fortune500_headquarters_2025.csv` | 2025 edition |
| `cbp_establishments_2023.csv` | 2023 |
| `bds_metro_2023.csv` | 2023 |

The source programs, units, suppression flags, industry/size selections and date exceptions follow [datasets_context.md](datasets_context.md). Each city manifest contains the exact source request URLs, retrieval date, observed vintage, output row count, bytes, SHA-256 and transformation method. Dictionaries include column order, units, county membership, BEA reporting-area mapping and raw-source checksums.

## Validation

All ten metros passed the following checks:

- All 90 outputs reopen successfully, with exact Dallas/Denver column names and order, complete required supporting files, correct target labels and reference years, and manifest row counts, byte counts and checksums that match saved files.
- Every QCEW, CBP, Economic Census and BDS output row reconciles to the downloaded official response after the documented projection, alias and null-to-blank transformations. Source flags, zeroes and identifiers are preserved. Each 2025 QCEW response contains one all-industry/all-ownership total; each BDS file has 20 rows.
- CBP establishment files exactly match their projection from the employment files. Economic Census sector files exactly match the documented 15-sector selection from detail.
- Every county GDP observation reconciles to BEA CAGDP2. Reporting-area membership covers the full OMB metro with no duplicated components. The two calculated metro totals equal complete all-industry reporting-area sums. **All ten 2024 metro GDP totals reproduce the ranking file's GDP to its displayed $0.1 billion precision.**
- Tax rows cover every constituent state, using only the 2026 table. Numeric rates match the published top rate, with full graduated brackets retained in `source_display`. Washington's zero explicitly means absence of corporate income tax.
- Fortune roster rows reconcile to the public 2025 map dataset and their calculated CBSA assignment. Current-verification blanks remain unknown. The known Seattle publisher-location conflict is explicitly flagged.
- Artifact Tool CSV import checks preserved the headers and first two available records in all 90 files, including leading-zero identifiers. All pre-existing city folders remain unchanged.

## Source and geography qualifications

GDP and tax membership follow the same **July 2023 OMB definition** used in the existing collection. New York is NY–NJ and Chicago is IL–IN under that definition, despite the broader older labels in the ranking file. Other federal programs retain their native geography vintages.

BEA combines Fairfax County/Fairfax city/Falls Church, Prince William County/Manassas/Manassas Park, and Spotsylvania County/Fredericksburg into reporting areas. The Washington folder preserves those source rows and codes and documents the full component mapping. All components belong to the target metro; no separate component GDP is invented.

Fortune data use the public [2025 headquarters map](https://interactives.fortune.com/f500-dataviz-2025/) and its [linked CSV](https://interactives.fortune.com/f500-dataviz-2025/map/data.csv). Metro membership is derived from the publisher coordinates and [Census 2023 cartographic CBSA boundaries](https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_cbsa_500k.zip). The 2025 roster is historical reported evidence, with no complete independent current-headquarters audit. The single-location map places Amazon in Seattle; its Arlington co-headquarters is not added again to Washington.

Seattle has 11 publisher-mapped records, including one disputed Lululemon entry. Fortune maps Sumner, Washington, while the [company's Form 10-K filed in March 2025](https://www.sec.gov/Archives/edgar/data/1397187/000139718725000013/lulu-20250202.htm) identifies executive offices in Vancouver, Canada and Sumner as a distribution center. The row is retained with `hq_verification_status=publisher_location_conflicts_with_2025_company_filing`; exclude it from independently established Seattle headquarters counts.

## Next batch

**Stopped after these ten metros.** At that point, the next missing metro was **Minneapolis–St. Paul, MN–WI, rank 15**, and no folders or datasets for the next batch had been created. The user subsequently confirmed [batch 2](collection_batch_02.md), which is now completed. All batch 1 city folders remain unchanged.
