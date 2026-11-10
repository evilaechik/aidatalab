# Study 1 source guide

The completed [regional feature comparison](feature_refinement/README.md) uses the 498-firm HQ roster and inherited 31 regional predictors, plus three CBP/BDS additions. The source access dates and historical vintages are unchanged by the November 10 cleanup.

- [Expanded company and geography sources](expanded_500/SOURCES.md), including all 500 company-specific supplementary routes in its CSV ledgers.
- [Linked source evidence](linked_msa/raw_archive/README.md), including the 150 CBP/QCEW/BDS payloads now retained under `source_data/`.
- [Feature-refinement geography evidence](feature_refinement/raw_archive/README.md).
- [Cleanup and source dependencies](CLEANUP.md).

## Economic sources

| Program | Reference used | Official collection link |
| --- | --- | --- |
| BLS QCEW private employment, establishments, pay | 2024 annual | [QCEW](https://www.bls.gov/cew/data.htm) |
| Fixed-county employment growth | Q4 2023–Q4 2024, July 2023 counties | [2023 industry10 slice](https://data.bls.gov/cew/data/api/2023/4/industry/10.csv), [2024 slice](https://data.bls.gov/cew/data/api/2024/4/industry/10.csv) |
| Census CBP sector employment | 2023, same universe across all 50 | [CBP](https://www.census.gov/programs-surveys/cbp/data.html) |
| BEA county GDP | 2024 current dollars, revised2026 vintage, complete fixed-county sums | [CAGDP2 ZIP](https://apps.bea.gov/regional/zip/CAGDP2.zip) |
| Census population estimates | July 2024, vintage2024; same-vintage2023 comparison | [PEP metro CSV](https://www2.census.gov/programs-surveys/popest/datasets/2020-2024/metro/totals/cbsa-est2024-alldata.csv) |
| ACS bachelor-plus share | 2024 one-year, released2025-09-11 | [B15003 bulk data](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/1YRData/acsdt1y2024-b15003.dat) |
| ACS income | 2024 one-year | [B19013 bulk data](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/1YRData/acsdt1y2024-b19013.dat) |
| ACS residential gross rent | 2024 one-year | [B25064 bulk data](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/1YRData/acsdt1y2024-b25064.dat) |
| ACS transit commuting | 2024 one-year | [B08301 bulk data](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/1YRData/acsdt1y2024-b08301.dat) |
| BLS OEWS occupational intensity/pay | May 2024; released2025-04-02, archive timestamps2025-07-08 | [Metro ZIP](https://blsmon1.bls.gov/oes/special-requests/oesm24ma.zip), [national ZIP](https://blsmon1.bls.gov/oes/special-requests/oesm24nat.zip) |
| BEA all-items regional price parity | 2024; released2026-02-19 | [MARPP ZIP](https://apps.bea.gov/regional/zip/MARPP.zip) |

[economic_source_registry.csv](expanded_500/tables/economic_source_registry.csv) retains 262
source-route records, including exact inherited metro requests and original
combined-file hashes. A record is not necessarily a distinct download; source
URLs can repeat for multiple metros. Retained normalized tables preserve source
flags, sampling uncertainty, geography status, and missingness. No2026 tax data
are used as predictors. Raw-dependent source extraction is retired; the compact
builder starts from these retained normalized economic values.

