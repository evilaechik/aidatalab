# Public Data Catalog and Research Status

This catalog separates shareable, reproducible public research from any restricted Invest Atlanta materials. It is designed to make the project easy for the team to pick up and extend.

## Current public datasets

| Dataset | Geography / period | What it measures | Best use | Important limitation |
| --- | --- | --- | --- | --- |
| `data/peer_metro_baseline_2025.csv` | Atlanta, Austin, Charlotte; 2025 | Private employment, establishments, wages, selected sector shares, GDP context, corporate-tax context | Peer-metro baseline | Indicators, not direct measures of attraction or retention |
| `data/peer_metro_regression/county_q4_growth_panel_2024_2025.csv` | 45 counties in the three MSAs; Q4 2023–2025 | County private-employment growth and sector composition | Exploratory regression and robustness checks | Short panel; no causal interpretation |
| `data/peer_metro_regression/metro_sector_q4_trends_2023_2025.csv` | Three MSAs; Q4 2023–2025 | Sector-level employment trends | Identify sectors for deeper investigation | QCEW is lagged and does not identify individual company decisions |
| `data/peer_metro_decision_tracker_public.csv` | Atlanta, Austin, Charlotte; 2020–2026 announcements | Public company location/expansion announcements, jobs, investment, space, location scope | Direct attraction/expansion evidence and case-study selection | Initial seed sample; announced jobs are not realized jobs |
| `data/fortune_100_atlanta_presence_2025.csv` | City of Atlanta and metro Atlanta | Fortune 100 office/presence classification | Corporate-presence context | Research screen, not a census or measure of jobs |
| `data/verified_location_sources.csv` | Company locations | Source trail for presence checks | Audit and refresh Fortune screen | Coverage is incomplete |
| `fortune500_hq_screen.csv` | Atlanta-area HQs | Fortune 500 headquarters screen | HQ ecosystem context | HQs are not equivalent to local employment or attraction results |
| `data/big_business_presence/fortune_500_universe_2025.csv` | U.S.; 2025 list | Official Fortune 500 company universe, including rank and headquarters context | Defines the major-company universe for the new primary outcome | A 2025 cross-section; not a historical attraction series |
| `data/big_business_presence/fortune500_metro_presence_review_queue.csv` | 500 companies × 200 MSAs | Source-audited office/HQ review ledger | Build the Metro Big Business Presence Score | Most rows are intentionally unreviewed, so zero must never be inferred as no presence |
| `data/big_business_presence/metro_big_business_presence_score_status_2025.csv` | 200 MSAs; 2025 | Review coverage and confirmed qualifying presences | Publication-status guardrail for the new score | A metro score is blank until all 500 company cells are resolved |
| `data/big_business_presence/metro_county_crosswalk_2023.csv` | Counties in the selected 200 MSAs | Official county-to-MSA membership | Assign externally geocoded business locations to the correct MSA | Location sources still need entity/function review |

## What the decision tracker adds

The new tracker makes the analysis more decision-based. It separates:

- **City of Atlanta cases** from **metro-only cases**, so suburban activity is not claimed as a City of Atlanta win.
- **Attraction** (new operation/location) from **expansion** (existing footprint grows) and **new hub/function** cases.
- **Announcements** from outcomes. A press release provides a committed/expected job count; it does not prove the jobs were delivered. The Centene case is deliberately retained as a cancelled announced project, so the tracker does not only record wins.
- Office, R&D, manufacturing, and operations-hub decisions, which have different site and workforce needs.

## Next public-data additions

1. Add every comparable announcement from 2023–2026 using the same fields and a direct primary source.
2. Add a `delivery_status` field after checking later company filings, project updates, or local news: `announced`, `under_construction`, `opened`, `realized`, `cancelled`, or `unknown`.
3. Build a parallel **loss/relocation tracker**. A retention analysis is incomplete if it only records wins.
4. Add site attributes for each geocoded case: city/metro jurisdiction, transit access, zoning, parcel size, and nearby workforce.
5. Assemble peer incentive-policy data with program type, eligibility, award size, clawbacks, geography, and source—not just tax rates.
6. Complete the direct-source Fortune 500 office/HQ review for the study metros; preserve City-versus-metro addresses and never classify an unreviewed company as absent.

## Presentation-safe interpretation

Use the baseline to describe **where each metro is performing**, and use the decision tracker to explain **what kinds of decisions are occurring**. Do not sum announced jobs across sources as an employment estimate, and do not infer that an incentive caused a decision without a documented comparison or company evidence.
