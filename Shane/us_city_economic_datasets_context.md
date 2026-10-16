# Economic and Business Dataset Context

Updated October 15, 2026.

These data support the research goal of identifying where **Atlanta is lagging in business attraction, expansion and retention**, investigating the drivers of those gaps, and assessing potential incentive strategies. The collected Dallas and Denver data provide initial comparison areas for a future Atlanta benchmark, covering employment, business activity, economic output, tax conditions and major corporate presence.

Both [Dallas](Data/dallas_data/README.md) and [Denver](Data/denver_data/README.md) contain the same nine data files below. Regional measures describe metropolitan economies, not municipal boundaries; GDP includes constituent counties and calculated metro totals, while tax data describe Texas or Colorado. See [research_context.md](research_context.md) for the research design and remaining decisions.

| File | What it contains and why it matters |
| --- | --- |
| `qcew_annual_2023_2025.csv` | BLS employment, wages and establishment counts; compares job growth and pay. Industry detail covers 2023–2024; 2025 has metro totals only. |
| `cbp_employment_2023.csv` | Census employment and payroll by industry and establishment size; shows the structure of the local business economy. |
| `economic_census_2022_detail.csv.gz` | Detailed Census industry sales and receipts; identifies the scale of business activity across industries. |
| `economic_census_2022_sectors.csv` | Census sales and receipts summarized by broad sector; makes major sectors easier to compare. |
| `bea_county_gdp_2023_2024.csv` | BEA county economic output and calculated metro totals; measures regional economic size and nominal growth. |
| `state_corporate_tax_2026.csv` | Tax Foundation corporate income-tax treatment for Texas or Colorado; provides context for comparing one part of business costs. |
| `fortune500_headquarters_2025.csv` | Fortune 500 companies, national ranks and headquarters checks; measures major corporate presence and flags location changes. |
| `cbp_establishments_2023.csv` | Census business-location counts by industry and establishment size; measures the local business footprint as a proxy for offices. |
| `bds_metro_2023.csv` | Census establishment openings, closures and job flows; measures business turnover and employment dynamics. |

The two Economic Census files overlap, as do the two CBP files; do not add their values together. The Economic Census files retain the explicitly requested 2022 reference year. Business entry and exit are proxies for attraction and retention and do not directly identify corporate relocation or incentive effects.

Each city folder also contains **README.md** for coverage and interpretation guidance, **download_manifest.csv** for sources and verification records, and **data_dictionary.json** for columns, units and handling rules. Detailed source links, geography, suppression flags and headquarters qualifications remain in those supporting files.
