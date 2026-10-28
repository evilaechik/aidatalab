# Metro collection batch 3

Completed October 27, 2026, following user confirmation after [batch 2](collection_batch_02.md). This batch covers the **next ten metros without existing folders** in [the top-50 GDP list](top_50_us_metro_areas_by_gdp.md). Raleigh, rank 38, was skipped because its folder already existed.

**90 new data files across ten folders**, plus a README, source manifest and data dictionary in every folder. At batch 3 completion, the collection had **351 data files across 39 metros**, leaving **11 listed metros**. All 348 files in the 29 pre-existing city folders, plus the supplied ranking list, were preserved byte-for-byte.

| GDP rank | Metro folder | Canonical CBSA | OMB counties | Data files | File rows |
| ---: | --- | --- | ---: | ---: | ---: |
| 29 | [Cincinnati](cincinnati_data/README.md) | 17140 | 15 | 9 | 7,287 |
| 30 | [Pittsburgh](pittsburgh_data/README.md) | 38300 | 8 | 9 | 6,681 |
| 31 | [Sacramento](sacramento_data/README.md) | 40900 | 4 | 9 | 6,308 |
| 32 | [Kansas City](kansas_city_data/README.md) | 28140 | 14 | 9 | 7,105 |
| 33 | [San Antonio](san_antonio_data/README.md) | 41700 | 8 | 9 | 6,634 |
| 34 | [Columbus](columbus_data/README.md) | 18140 | 10 | 9 | 6,820 |
| 35 | [Las Vegas](las_vegas_data/README.md) | 29820 | 1 | 9 | 5,787 |
| 36 | [Cleveland](cleveland_data/README.md) | 17410 | 6 | 9 | 6,538 |
| 37 | [Salt Lake City](salt_lake_city_data/README.md) | 41620 | 2 | 9 | 6,178 |
| 39 | [Milwaukee](milwaukee_data/README.md) | 33340 | 4 | 9 | 6,175 |
| | **Batch total** | | | **90** | **65,513** |

File-row counts include overlapping Census projections and calculated metro GDP totals. They are not unique-business counts or counts of nonoverlapping observations. The two Fortune files with no matched publisher locations are included in the file count and have zero data rows.

## Matching files and reference windows

Every folder retains the same filenames, column names and column order as Dallas/Denver and the prior batches:

| File | Reference years |
| --- | --- |
| `qcew_annual_2023_2025.csv` | 2023–2025; 2025 all-industry/all-ownership metro total only |
| `cbp_employment_2023.csv` | 2023 |
| `economic_census_2022_detail.csv.gz` | 2022 |
| `economic_census_2022_sectors.csv` | 2022; same 15 broad sectors |
| `bea_county_gdp_2023_2024.csv` | 2023–2024 |
| `state_corporate_tax_2026.csv` | 2026 |
| `fortune500_headquarters_2025.csv` | 2025 edition; zero matched locations for Sacramento and Salt Lake City |
| `cbp_establishments_2023.csv` | 2023 |
| `bds_metro_2023.csv` | 2023 |

Source programs, units, filters, source flags and date exceptions follow [datasets_context.md](datasets_context.md). GDP membership uses the July 2023 OMB delineation. QCEW and Census responses were newly downloaded for this batch. Shared BEA, OMB, Census boundary, Fortune and tax sources reuse unchanged same-day batch 1 downloads, with source hashes and reuse notes in every dictionary. No acquisition scripts are included in the folders.

## Validation

All 90 outputs passed source reconciliation, column/order, identifier, reference-year, row-count, byte-count, SHA-256 and required-support-file checks. Every federal-source output record matches its downloaded source after the documented transformations. CBP establishment projections and the 15-sector Economic Census selection reconcile exactly. Each BDS file has 20 rows. Every GDP county observation matches CAGDP2, county coverage is complete without duplicate components, and each derived metro total equals the complete all-industry county sum.

All ten ranking GDP differences are documented below and in the city dictionaries; source reconciliation passes independently of those older ranking amounts. Cleveland's QCEW source-code change is explicitly checked. The two zero-row Fortune files were verified against the full 500-company publisher map and their CBSA polygons. Artifact Tool CSV import checks preserve each file's header and first two available records, including leading-zero identifiers and the header-only files. Baseline SHA-256 checks confirm all 349 pre-existing files covered by the preservation snapshot are unchanged.

## Ranking GDP reference years

Every batch 3 GDP amount in the supplied ranking list matches the corresponding **older 2023** discontinued BEA/FRED metro observation, last updated **December 4, 2024**. Collection continues to use the requested **2023–2024 CAGDP2** window and February 5, 2026 release, with July 2023 OMB county membership. The ranking file controls collection order and remains unchanged.

| Metro | Listed GDP, billion USD | Older FRED 2023, million USD | Collected 2024, billion USD |
| --- | ---: | ---: | ---: |
| [Cincinnati](https://fred.stlouisfed.org/series/NGMP17140) | 198.9 | 198,888.723 | 207.3 |
| [Pittsburgh](https://fred.stlouisfed.org/series/NGMP38300) | 194.2 | 194,229.253 | 205.9 |
| [Sacramento](https://fred.stlouisfed.org/series/NGMP40900) | 189.6 | 189,624.282 | 201.9 |
| [Kansas City](https://fred.stlouisfed.org/series/NGMP28140) | 185.7 | 185,746.211 | 188.2 |
| [San Antonio](https://fred.stlouisfed.org/series/NGMP41700) | 182.1 | 182,139.043 | 198.4 |
| [Columbus](https://fred.stlouisfed.org/series/NGMP18140) | 182.1 | 182,087.631 | 193.5 |
| [Las Vegas](https://fred.stlouisfed.org/series/NGMP29820) | 178.4 | 178,388.313 | 195.9 |
| [Cleveland](https://fred.stlouisfed.org/series/NGMP17460) | 173.1 | 173,135.607 | 187.6 |
| [Salt Lake City](https://fred.stlouisfed.org/series/NGMP41620) | 147.5 | 147,519.150 | 157.1 |
| [Milwaukee](https://fred.stlouisfed.org/series/NGMP33340) | 130.9 | 130,856.689 | 137.1 |

Older values are explanatory evidence, not substituted observations. Reference years, revisions and, for Cleveland, geographic boundaries differ. Exact 2023 and 2024 county sums remain in the data files; dictionaries retain each comparison's units, date and source URL.

## Cleveland geography

The canonical July 2023 OMB metro is **Cleveland, OH, CBSA 17410**, with six counties including Ashtabula. Native QCEW geography is preserved:

| Reference year | Source QCEW area | Underlying metro |
| --- | --- | --- |
| 2023 | C1746 | Former five-county Cleveland–Elyria, CBSA 17460 |
| 2024 | C1741 | Six-county Cleveland, CBSA 17410 |
| 2025 | C1741 | Six-county Cleveland, CBSA 17410; metro total only |

Original `area_fips` values remain intact. The helper `metro_cbsa=17410` identifies the folder's canonical target and does not assert constant historical boundaries. **Do not treat the 2023–2024 QCEW change as employment or wage growth on unchanged boundaries.** The [BLS area guide](https://www.bls.gov/cew/classifications/areas/area-guide.htm) documents the 2024 switch to July 2023 metro definitions. Cleveland's CBP, Economic Census and BDS responses return source GEO_ID ending 17410; GDP and Fortune assignment use the documented July 2023 six-county metro. No geographic backcast is applied.

## Zero Fortune map locations

The complete [2025 Fortune map dataset](https://interactives.fortune.com/f500-dataviz-2025/map/data.csv) contains **zero points within the Sacramento and Salt Lake City CBSA polygons**. Each folder therefore retains `fortune500_headquarters_2025.csv` with the standard 17-column header and zero records. Its manifest status is `collected_no_publisher_locations`, and its dictionary records zero matches among the 500 source companies.

This is a publisher-map result rather than missing collection or a claim of no offices, nearby-CSA headquarters, all corporate presence, or a completed independent headquarters audit. No placeholder company is fabricated. For the other rosters, current-HQ verification fields remain blank and mean unknown; the publisher's single reported location is retained without adding co-headquarters.

## Tax interpretation

Ohio, Texas and Nevada have numeric zeroes that explicitly encode absence of corporate income tax. Their separate commercial activity, franchise/margin or commerce taxes are described in the notes. Kansas retains its published graduated schedule in `source_display` and the top rate in the numeric field. Cincinnati has separate Indiana, Kentucky and Ohio rows; Kansas City has separate Kansas and Missouri rows. Statutory 2026 rates are not effective tax burdens, and constituent states must not be averaged into a metro rate.

## Next batch

**Stopped after these ten metros.** At that point, the next missing metro was **Jacksonville, FL, rank 40**, with eleven listed metros remaining and no batch 4 folders created. The user subsequently authorized [the final eleven](collection_batch_04.md), completing all 50 listed metros. All batch 3 city folders remain unchanged.
