# Public source data for the Business Competitiveness project

This folder contains public-source downloads used to study Atlanta's labor market, commuting patterns, City boundary, and transit access. These files are separate from Invest Atlanta's restricted revenue and employee-count data.

## Contents

| Folder | Source | Purpose |
| --- | --- | --- |
| `qcew/` | BLS Quarterly Census of Employment and Wages | Industry employment, establishments, and wages for the core metro counties. |
| `lodes/` | Census LEHD LODES | Workplace, residence, and origin-destination job counts for Georgia. |
| `boundaries/` | U.S. Census Cartographic Boundary Files | City/place boundaries for City-versus-metro spatial classification. |
| `transit/` | MARTA GTFS | Transit routes, stops, and schedules. |

## Scope and constraints

- QCEW downloads cover Fulton, DeKalb, Cobb, Gwinnett, Clayton, Forsyth, Henry, Douglas, Rockdale, and Cherokee Counties for 2023-2025 Q4. This is a practical **core metro** comparison set, not a formal definition of the full Atlanta MSA.
- LODES is downloaded statewide because its public files are state-based. Filter it to the chosen geography before analysis.
- Do not place restricted Invest Atlanta revenue or employee-count data here. Do not ingest it into AI tools.

## Re-download

Run `bash download_public_sources.sh` from this directory. It downloads only public files and records source URLs in the script.
