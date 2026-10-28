# Final metro collection batch and completion audit

Completed October 27, 2026, after the user explicitly authorized **the final eleven metros** following [batch 3](collection_batch_03.md). This batch covers ranks 40–50 in [the supplied GDP ranking](top_50_us_metro_areas_by_gdp.md).

**99 new data files across eleven separate city folders**, plus a README, source manifest and data dictionary in each folder. The full collection is complete: **50 metro folders, 450 data files and 150 supporting city files**. Every ranking position from 1 through 50 is represented exactly once. All 468 files in the 39 pre-existing city folders, plus the supplied ranking list, remain byte-for-byte unchanged.

| GDP rank | Metro folder | CBSA | OMB counties / equivalents | BEA reporting areas | Data files | File rows |
| ---: | --- | --- | ---: | ---: | ---: | ---: |
| 40 | [Jacksonville](jacksonville_data/README.md) | 27260 | 5 | 5 | 9 | 6,405 |
| 41 | [Virginia Beach–Norfolk](virginia_beach_data/README.md) | 47260 | 18 | 16 | 9 | 6,978 |
| 42 | [Hartford](hartford_data/README.md) | 25540 | 2 planning regions | 2 | 9 | 5,729 |
| 43 | [Richmond](richmond_data/README.md) | 40060 | 17 | 14 | 9 | 6,828 |
| 44 | [Bridgeport–Stamford](bridgeport_data/README.md) | 14860 | 2 planning regions | 2 | 9 | 5,656 |
| 45 | [Providence](providence_data/README.md) | 39300 | 6 | 6 | 9 | 6,317 |
| 46 | [Memphis](memphis_data/README.md) | 32820 | 9 | 9 | 9 | 6,484 |
| 47 | [New Orleans](new_orleans_data/README.md) | 35380 | 7 parishes | 7 | 9 | 6,221 |
| 48 | [Oklahoma City](oklahoma_city_data/README.md) | 36420 | 7 | 7 | 9 | 6,284 |
| 49 | [Louisville](louisville_data/README.md) | 31140 | 12 | 12 | 9 | 6,903 |
| 50 | [Omaha](omaha_data/README.md) | 36540 | 8 | 8 | 9 | 6,068 |
| | **Final-batch total** | | | | **99** | **69,873** |

Row counts include overlapping Census projections, source missing-value rows and calculated GDP totals. They are not counts of unique businesses or nonoverlapping observations.

## Files and reference windows

All eleven folders retain the same filenames, columns and column order as the existing metros:

| File | Reference years |
| --- | --- |
| `qcew_annual_2023_2025.csv` | 2023–2025; 2025 all-industry/all-ownership metro total only |
| `cbp_employment_2023.csv` | 2023 |
| `economic_census_2022_detail.csv.gz` | 2022 |
| `economic_census_2022_sectors.csv` | 2022; same 15 broad sectors |
| `bea_county_gdp_2023_2024.csv` | 2023–2024; Hartford/Bridgeport's 2023 planning-region values are unavailable source markers |
| `state_corporate_tax_2026.csv` | 2026 |
| `fortune500_headquarters_2025.csv` | 2025 edition |
| `cbp_establishments_2023.csv` | 2023 |
| `bds_metro_2023.csv` | 2023 |

Source programs, units, filters, native industry/geography vintages and date exceptions follow [datasets_context.md](datasets_context.md). GDP membership uses the July 2023 OMB definition. QCEW and Census table responses were newly downloaded for these eleven metros. Shared BEA, OMB, Census boundary, Fortune and tax sources reuse the unchanged same-day downloads from batch 1, with raw hashes and reuse notes in the dictionaries. No acquisition scripts are included in the folders.

## Connecticut GDP availability

**BEA does not publish 2023 GDP for Connecticut's new planning-region county equivalents.** Its [February 5, 2026 release](https://www.bea.gov/news/2026/gross-domestic-product-county-and-personal-income-county-2024) and the CAGDP2 archive footnotes specify planning-region estimates from 2024 onward.

| Metro | Planning regions used for GDP | Complete 2024 GDP, thousand USD |
| --- | --- | ---: |
| Hartford | Capitol (09110); Lower Connecticut River Valley (09130) | 127,010,297 |
| Bridgeport | Greater Bridgeport (09120); Western Connecticut (09190) | 110,273,434 |

Each GDP file retains all requested 2023 planning-region industry rows as the source marker `(NA)`, with `value_status=source_flag`. Only the complete **2024** metro sum is derived. There is **no 2023 metro total**, no zero substitution and no imputation from old counties. Each file contains 136 planning-region/industry/year records, including 68 unavailable 2023 rows, plus one derived 2024 metro total. The manifest status is `collected_verified_2023_source_unavailable` and the dictionary explicitly records the missing metro-total year.

The [BLS Connecticut guidance](https://www.bls.gov/cew/classifications/areas/new-2024-connecticut-counties.htm) also documents the transition from historical counties before 2024 to planning regions from 2024 onward. Hartford and Bridgeport retain native QCEW values on either side of that break. Unchanged CBSA codes do not establish unchanged boundaries, and no direct old-to-new county mapping or backcast is applied. The other Census programs retain their returned geography and titles.

## Virginia reporting areas

Virginia GDP retains BEA's published combination areas, with all component county equivalents documented and included exactly once:

| Metro | Published BEA area | OMB component FIPS |
| --- | --- | --- |
| Virginia Beach | 51931 James City + Williamsburg | 51095; 51830 |
| Virginia Beach | 51958 York + Poquoson | 51199; 51735 |
| Richmond | 51918 Dinwiddie + Colonial Heights + Petersburg | 51053; 51570; 51730 |
| Richmond | 51941 Prince George + Hopewell | 51149; 51670 |

Virginia Beach's 16 reporting areas cover all 18 OMB county equivalents; Richmond's 14 cover all 17. Every combination lies wholly within its target metro. Source codes, names, industry lines and disclosure flags remain intact. Separate component GDP estimates are not fabricated.

## Ranking GDP reference years

All eleven GDP amounts in the ranking file match the corresponding older **2023** discontinued BEA/FRED observations, last updated **December 4, 2024**. The collected county files retain the February 5, 2026 release and requested 2023–2024 window. Reference year, revisions and geography may all differ; the supplied list is used for collection order and remains unchanged.

| Metro | Listed GDP, billion USD | Older FRED 2023, million USD | Collected 2024, billion USD |
| --- | ---: | ---: | ---: |
| [Jacksonville](https://fred.stlouisfed.org/series/NGMP27260) | 129.1 | 129,094.522 | 139.2 |
| [Virginia Beach](https://fred.stlouisfed.org/series/NGMP47260) | 127.5 | 127,459.149 | 134.3 |
| [Hartford](https://fred.stlouisfed.org/series/NGMP25540) | 122.8 | 122,805.302 | 127.0 |
| [Richmond](https://fred.stlouisfed.org/series/NGMP40060) | 117.0 | 116,959.541 | 123.9 |
| [Bridgeport](https://fred.stlouisfed.org/series/NGMP14860) | 116.0 | 116,030.979 | 110.3 |
| [Providence](https://fred.stlouisfed.org/series/NGMP39300) | 111.8 | 111,839.552 | 116.4 |
| [Memphis](https://fred.stlouisfed.org/series/NGMP32820) | 102.9 | 102,934.012 | 107.5 |
| [New Orleans](https://fred.stlouisfed.org/series/NGMP35380) | 102.4 | 102,436.589 | 88.5 |
| [Oklahoma City](https://fred.stlouisfed.org/series/NGMP36420) | 100.1 | 100,054.101 | 103.0 |
| [Louisville](https://fred.stlouisfed.org/series/NGMP31140) | 97.8 | 97,751.023 | 107.9 |
| [Omaha](https://fred.stlouisfed.org/series/NGMP36540) | 92.4 | 92,356.612 | 99.2 |

Hartford and Bridgeport's older FRED figures use historical county geography and are not substitutes for missing 2023 planning-region data. New Orleans's collected GDP and Fortune assignment use the seven-parish July 2023 metro, excluding St. Tammany Parish, which belongs to Slidell–Mandeville–Covington (43640) in the official delineation. Its lower current-boundary total is not evidence of a like-for-like economic decline. Native QCEW geography also changes across the 2024 definition update.

## Tax and headquarters interpretation

Every constituent state remains a separate tax row. Connecticut's numeric 8.25% is the table's qualifying 10% surtax on a 7.5% base; the notes specify the gross-proceeds/combined-unitary-group conditions. All graduated schedules, exemption thresholds and source qualifications are retained in `source_display` and notes. The files describe the requested 2026 statutory snapshot, not an effective total tax burden.

Fortune uses the [2025 publisher map](https://interactives.fortune.com/f500-dataviz-2025/) and its [linked CSV](https://interactives.fortune.com/f500-dataviz-2025/map/data.csv), with coordinates assigned to 2023 Census CBSA polygons. Current-location fields remain blank because a complete independent current-headquarters audit was not performed. Reported US locations can differ from legal domicile, executive offices or co-headquarters. The existing Seattle/Detroit location-conflict flags and Sacramento/Salt Lake City zero-row publisher rosters are preserved unchanged.

## Complete collection validation

The final audit covered **all 50 metro folders and all 450 saved data files**, not just this batch:

- Ranking positions **1–50** are represented exactly once, with no missing metro and no duplicate ranking position.
- Every folder has the same nine dataset filenames plus a README, manifest and dictionary. All 450 CSV/gzip files reopen successfully and match the Dallas/Denver column names and order.
- Saved row counts, byte counts and SHA-256 checksums match every manifest and dictionary. Identifiers and requested reference years are preserved. The collection contains 338,334 file rows, including overlapping projections, unavailable-source rows and calculated totals; this is not a unique-observation count.
- CBP establishment files reconcile to the employment-file projection. Every Economic Census sector file has the same 15-sector view, and every BDS file has 20 rows. Every available metro GDP sum equals the complete all-industry county/reporting-area total.
- Hartford/Bridgeport's unavailable 2023 GDP rows and omitted 2023 metro totals are explicitly checked. The two existing zero-row Fortune rosters are explicitly verified as documented publisher-map results.
- All **99 new files** additionally reconcile to downloaded official responses after documented transformations. Virginia component mappings have complete, nonoverlapping coverage. The older ranking GDP values are separately documented. Artifact Tool CSV import checks preserve the headers and first two available records in all 99 new files.
- Baseline SHA-256 checks confirm all **469 pre-existing files** in the preservation snapshot—468 city-folder files plus the supplied ranking list—are unchanged.

**Collection is complete. No listed metros remain.** Source availability and comparability limits described above remain part of the data rather than being filled with fabricated observations.
