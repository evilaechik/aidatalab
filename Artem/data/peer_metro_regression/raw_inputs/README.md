# Raw public inputs

These are the source files used to build the peer-metro employment panel and the GDP context in the baseline. They are public data and safe to share.

| File or directory | Source | Used for |
| --- | --- | --- |
| `qcew/` | U.S. Bureau of Labor Statistics QCEW county API | 135 fourth-quarter county files: 45 counties in the Atlanta, Austin, and Charlotte MSAs for 2023, 2024, and 2025. These produce the employment panel, sector trends, and exploratory regression. |
| `census_cbsa_county_delineation_2023.xlsx` | U.S. Census Bureau | Assigns counties to the July 2023 Atlanta, Austin, and Charlotte metropolitan areas. |
| `bea_cagdp1.zip` | U.S. Bureau of Economic Analysis | County GDP source table used to construct the 2024 nominal-GDP context in `peer_metro_baseline_2025.csv`. |

## Reproduction

Run `python Artem/scripts/build_peer_metro_regression.py` from the repository root. The script reads these files first and only fetches a missing QCEW or Census input from the public source URL. It writes derived files one directory up.

## Boundaries

- QCEW values are at **county** level and use private ownership totals (`own_code=5`) and the specified NAICS sectors.
- The BLS source files are fourth-quarter snapshots, while `peer_metro_baseline_2025.csv` uses annual QCEW indicators for its annual figures.
- BEA GDP is current-dollar county GDP. Summing it to an MSA provides economic-scale context; it is not a City of Atlanta GDP measure and its growth includes price changes.
- This directory intentionally contains no restricted Invest Atlanta, business-license, parcel, or incentive records.
