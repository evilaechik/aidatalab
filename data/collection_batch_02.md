# Metro collection batch 2

Completed October 27, 2026, following user confirmation after [batch 1](collection_batch_01.md). This batch covers the **next ten metros without existing data folders**, working down [the top-50 GDP list](top_50_us_metro_areas_by_gdp.md). Denver, Charlotte, Austin and Nashville were skipped within this part of the list because their folders already existed.

**90 new data files across ten folders**, plus a README, source manifest and data dictionary in each folder. At batch 2 completion, the collection had **261 data files across 29 metro folders**, leaving 21 listed metros for future batches. All 19 pre-existing metro folders and the supplied ranking list were preserved byte-for-byte.

| GDP rank | Metro folder | CBSA | OMB counties / equivalents | Data files | File rows |
| ---: | --- | --- | ---: | ---: | ---: |
| 15 | [Minneapolis–St. Paul](minneapolis_data/README.md) | 33460 | 15 | 9 | 7,472 |
| 16 | [Detroit](detroit_data/README.md) | 19820 | 6 | 9 | 6,874 |
| 17 | [San Diego](san_diego_data/README.md) | 41740 | 1 | 9 | 6,401 |
| 20 | [Baltimore](baltimore_data/README.md) | 12580 | 7 | 9 | 6,755 |
| 21 | [Riverside–San Bernardino](riverside_data/README.md) | 40140 | 2 | 9 | 6,491 |
| 23 | [Tampa–St. Petersburg](tampa_data/README.md) | 45300 | 4 | 9 | 6,687 |
| 24 | [St. Louis](st_louis_data/README.md) | 41180 | 15 | 9 | 7,334 |
| 25 | [Orlando](orlando_data/README.md) | 36740 | 4 | 9 | 6,571 |
| 26 | [Portland](portland_data/README.md) | 38900 | 7 | 9 | 6,761 |
| 28 | [Indianapolis](indianapolis_data/README.md) | 26900 | 11 | 9 | 6,847 |
| | **Batch total** | | | **90** | **68,193** |

Rows include overlapping Census projections and calculated metro GDP totals; this is not a count of unique businesses or nonoverlapping observations.

## Matching files and reference windows

Every folder has the same filenames, column names and column order as Dallas/Denver and batch 1:

| File | Reference years |
| --- | --- |
| `qcew_annual_2023_2025.csv` | 2023–2025; 2025 all-industry/all-ownership metro total only |
| `cbp_employment_2023.csv` | 2023 |
| `economic_census_2022_detail.csv.gz` | 2022 |
| `economic_census_2022_sectors.csv` | 2022; same 15 broad sectors |
| `bea_county_gdp_2023_2024.csv` | 2023–2024 |
| `state_corporate_tax_2026.csv` | 2026 |
| `fortune500_headquarters_2025.csv` | 2025 edition |
| `cbp_establishments_2023.csv` | 2023 |
| `bds_metro_2023.csv` | 2023 |

The source programs, units, native geography/industry vintages, filters, suppression flags and date exceptions follow [datasets_context.md](datasets_context.md). GDP county membership follows the July 2023 OMB delineation. Newly downloaded QCEW and Census responses cover these ten metros. Shared BEA, OMB, Census boundary, Fortune and tax sources reuse the unchanged same-day batch 1 downloads, with reuse notes and raw-response checksums in the dictionaries.

## Validation

All 90 files passed source reconciliation, schema, reference-year, identifier, projection, county coverage, aggregation, row-count, byte-count and SHA-256 checks. Every federal source row matches the downloaded response after the documented transformations. Economic Census has the same 15-sector projection; BDS has 20 rows per metro. Artifact Tool CSV imports also preserve the headers and first two available records in every new file, including leading-zero identifiers.

All GDP county values match CAGDP2 and every derived metro sum equals its complete set of county totals. Nine of ten 2024 totals also reproduce the ranking list at its displayed $0.1 billion precision. Indianapolis has the documented reference-year/vintage exception below; official county-source reconciliation still passes. Baseline SHA-256 checks confirm all 228 files in the 19 pre-existing city folders, plus the supplied ranking list, are unchanged.

## Indianapolis ranking discrepancy

The selection list reports **$199.2 billion** for Indianapolis. This matches the discontinued [BEA/FRED series NGMP26900](https://fred.stlouisfed.org/series/NGMP26900), which reports **2023: $199,197.977 million** and was last updated December 4, 2024.

Using the same [BEA CAGDP2 source](https://apps.bea.gov/regional/zip/CAGDP2.zip), February 5, 2026 release and July 2023 OMB definition as the other folders, the collected Indianapolis sums are:

| Reference year | GDP, thousand current USD | GDP, billion current USD |
| --- | ---: | ---: |
| 2023, revised | 197,646,363 | 197.646363 |
| 2024 | 209,842,586 | 209.842586 |

The official county values, requested reference windows and supplied ranking file are preserved. The older FRED value explains the discrepancy rather than replacing the collected data. Collection order continues to follow the supplied list.

## Geography, tax and headquarters qualifications

Baltimore city (24510) and Baltimore County (24005) are separate GDP areas. St. Louis city (29510) and St. Louis County (29189) are likewise separate. Each is included once in its metro sum. Indianapolis uses its July 2023 OMB title, Indianapolis–Carmel–Greenwood, with all 11 counties; other programs retain their native titles/vintages.

Multi-state metros retain separate tax regimes. Portland includes Oregon's full 6.6%/7.6% graduated schedule, with 7.6 in the numeric top-rate field, and a separate Washington zero explicitly indicating no corporate income tax. Oregon's corporate activity tax and Washington's business and occupation tax remain outside the corporate income-tax rate measure. Tax observations are the requested 2026 snapshot, not effective burdens or 2023 conditions.

Fortune uses the public [2025 publisher map](https://interactives.fortune.com/f500-dataviz-2025/) and [linked dataset](https://interactives.fortune.com/f500-dataviz-2025/map/data.csv). Metro assignment follows publisher coordinates and Census 2023 polygons. The reported US location may differ from legal domicile, global executive offices, current headquarters or co-headquarters; no complete independent current-HQ audit was performed. Blank current-verification fields remain unknown.

Detroit's nine publisher-mapped entries include a flagged **Autoliv** conflict. Fortune reports Auburn Hills, Michigan, but its [Form 10-K filed in February 2025](https://www.sec.gov/Archives/edgar/data/1034670/000095017025023852/alv-20241231.htm) identifies principal executive offices in Stockholm, Sweden. The original US location is retained with `hq_verification_status=publisher_location_conflicts_with_2025_company_filing`; exclude that row from independently established Detroit global-headquarters counts.

## Next batch

**Stopped after these ten metros.** At that point, the next missing metro was **Cincinnati, OH–KY–IN, rank 29**, and no batch 3 folders or datasets had been created. The user subsequently confirmed [batch 3](collection_batch_03.md), which is now completed. All batch 2 city folders remain unchanged.
