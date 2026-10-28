# External Data Catalog for the Invest Atlanta Study

## What similar site-selection work does

This project should not try to find one universal formula for why every large
company locates somewhere. Public and private site-selection guides use a
sequence instead:

1. Define the operation: office/R&D, headquarters, manufacturing, logistics,
   or a regional service function.
2. Screen a comparable geography on workforce, operating cost, access, and
   business conditions.
3. Test real sites or buildings, delivery timeline, utilities, risk, and
   incentives for a small group of finalists.
4. Build a company-specific cost and risk case before negotiating incentives.

That approach is consistent with the [Minnesota DEED site-selection guide](https://mn.gov/deed/government/shovel-ready/program-overview/location.jsp), which explicitly uses MSAs for headquarters, back-office, and R&D screens and distinguishes them from county-level manufacturing/logistics analysis. The [U.S. Commerce guide](https://www.trade.gov/sites/default/files/2022-07/SiteSelection2022Update.pdf) and the [U.S. DOT transportation primer](https://rosap.ntl.bts.gov/view/dot/54145/dot_54145_DS1.pdf) make the same point: combine quantitative screening with site-specific due diligence.

## Existing metro-performance frameworks to borrow from

| Framework | What it does well | What we should borrow | What not to copy blindly |
| --- | --- | --- | --- |
| [Brookings Metro Monitor](https://www.brookings.edu/articles/metro-monitor-2026/) | Tracks growth, prosperity, and inclusion as distinct outcomes | Keep outcome families separate instead of making one black-box city rank | It measures metro economic performance, not verified corporate office attraction |
| [Milken Best-Performing Cities](https://milkeninstitute.org/content-hub/news-releases/fayetteville-springdale-rogers-ar-and-st-george-ut-top-milken-institutes-2026-annual-ranking-best) | Benchmarks roughly 400 metros across labor-market, technology, housing, and resilience measures | Compare metros to size peers and show the components behind any rank | Its composite is an economic-performance outcome index, not an Invest Atlanta policy recipe |
| State/consultant site-selection playbooks | Use operation-specific, sequential elimination criteria | Separate office/R&D screens from manufacturing/logistics screens and put real-site verification at the finalist stage | Do not use a generic factor weight for every company or industry |

## Public datasets worth adding

| Priority | Data source | Comparable measure we can build | Geography / timing | Why it matters | Model role |
| --- | --- | --- | --- | --- | --- |
| 1 | [BLS OEWS](https://www.bls.gov/oes/tables.htm) | Computer/math, business/financial, and architecture/engineering jobs per 1,000 jobs; occupation-specific wages | Direct MSA estimates, annual | Measures the current talent stock and hiring-cost proxy by job type | Good office/R&D feature after definition checks |
| 1 | [Census LEHD LODES / OnTheMap](https://lehd.ces.census.gov/data/) | Jobs by workplace, high-earnings-job share, and the labor shed entering a job center | Census block data, 2002–2023, aggregate to MSA/city | Directly tests Nicole's point: where workers live and how far a site can draw talent | Excellent city-vs-metro and workforce-access analysis |
| 1 | [Census ACS](https://www.census.gov/data/developers/data-sets/acs-1year.html) | Degree attainment, transit commute share, commute time, work-from-home share, rent burden, broadband | Direct MSA estimates, annual/5-year | Covers livability and access conditions that affect recruitment and retention | Scorecard; API key or bulk extract required |
| 1 | [IPEDS](https://nces.ed.gov/ipeds/use-the-data) | Business/STEM degree completions per 1,000 jobs | Institution location, annual | New talent pipeline and partnership capacity | Already collected; use with retention caveat |
| 1 | [Census Building Permits Survey](https://www.census.gov/construction/bps/index.html) | Permitted homes per 1,000 jobs; multifamily share | Direct CBSA, annual | Housing-supply pipeline near employment centers | Already collected; scorecard more than causal model feature |
| 2 | [EPA Smart Location Database](https://www.epa.gov/smartgrowth/smart-location-mapping) | Intersection density, transit-stop density, household/job density, destination accessibility | Census block group, then aggregate | Quantifies walkability and transit-supportive development around target districts | Good place-based city/submarket layer |
| 2 | [FTA National Transit Database](https://www.transit.dot.gov/ntd/ntd-data) | Passenger trips, vehicle-revenue miles/hours, route/service availability per resident | Agency and urbanized area, annual | Measures transit service supply, not just commuter behavior | Use after a documented UZA-to-MSA crosswalk |
| 2 | [FAA enplanement data](https://www.faa.gov/airports/planning_capacity/passenger_allcargo_stats/passenger/previous_years) | Commercial airport passenger boardings within an MSA; airport presence | Airport, annual; spatially join to MSA | A practical air-access proxy for headquarters and client-facing offices | Scorecard; do not mistake hub traffic for local business demand |
| 2 | [FCC Broadband Data Collection](https://broadbandmap.fcc.gov/data-download/nationwide-data) | Service availability by speed tier, ideally weighted by households/jobs | Location or polygon data, refreshed twice yearly | Relevant to digital operations and underserved districts | Needs a reproducible rollup method |
| 2 | [HUD Fair Market Rents](https://www.huduser.gov/portal/datasets/fmr.html) | Two-bedroom and four-bedroom rent benchmark; change over time | County/metro, annual | Comparable affordability benchmark when ACS cannot be pulled | Scorecard; it is a program rent benchmark, not observed market rent |
| 2 | [BLS LAUS](https://www.bls.gov/lau/) | Unemployment rate, labor-force growth, employment growth | Direct metro-area series, monthly | Labor availability and cyclical conditions | Context only; not a direct City lever |
| 2 | [BEA regional accounts](https://www.bea.gov/data/gdp/gdp-metropolitan-area) | GDP growth, GDP per worker, personal-income growth | Metro/county, annual | Economic depth and growth capacity | Context only |
| 3 | [Census County Business Patterns](https://www.census.gov/data/datasets/2023/econ/cbp/2023-cbp.html) | Establishments by employment-size band, industry diversity, large-establishment share | Direct MSA, annual | Describes the existing employer ecosystem | Collected for all 100 MSAs as a descriptive scorecard; keep it out of the Fortune-office predictor because it is too close to the outcome |
| 3 | [SBA 7(a) and 504 FOIA data](https://data.sba.gov/dataset/7a-504-foia) | SBA-backed loans and dollars per establishment or worker | Business address, quarterly | A partial small-business capital-access signal | Separate small-business analysis; not a large-company location driver |
| 3 | [FEMA National Risk Index](https://hazards.fema.gov/nri/) | Flood, heat, wildfire, hurricane, and composite risk | County/census tract | Resilience and business-continuity context | Risk screen, not a lever score |

## Non-public / manual data that are still necessary

No public national source cleanly measures the things a company cares about at
the actual finalist-site stage. These deserve a transparent manual scorecard,
not a fake automated proxy:

| Factor | Evidence to collect | Suggested scoring protocol |
| --- | --- | --- |
| Commercial site and office readiness | Large-block availability, asking rent, absorption, ownership, zoning, utilities, environmental constraints | For each metro/district, record source date and define a minimum viable office/site requirement before scoring |
| Permitting reliability | Published permit clocks, planning performance reports, online application coverage, pre-development process | Code definitions first. Separate stated target days from actual median completion days. |
| Incentive design | Eligibility, wage/job thresholds, targeted sectors, reimbursement versus up-front support, clawbacks, local match | Compare policy architecture, not raw disclosed subsidy dollars. Disclosure is uneven. |
| Workforce partnerships | Named university/technical-college programs, employer partnerships, apprenticeships, training capacity | Validate with program contacts; count only active, relevant programs. |
| Utility/power readiness | Confirmed capacity, timeline, redundancy, and rate structure for candidate sites | Require provider or site documentation. Do not infer capacity from state averages. |

## Recommended next build order

1. Add OEWS occupation concentration and wage features for office/R&D target
   sectors.
2. Build a LODES labor-shed analysis for City of Atlanta, Alpharetta, Midtown,
   and other target districts. This will show whether a metro office benefits
   the City or primarily reinforces a suburban employment node.
3. Add ACS housing, commute, and broadband measures through a key-protected
   pull or a documented bulk download.
4. Build a manual, source-cited site-readiness and permitting scorecard for a
   tight peer group—not 100 generic metro scores.
5. Keep the Fortune-office presence score separate and source-verify it before
   using any model for recommendations.

## Rules for the eventual model

- Do not treat all variables as levers. Label each as a context condition,
  policy-adjacent proxy, direct local lever, or outcome-adjacent descriptor.
- Do not use CBP large-establishment counts or local Fortune-company counts as
  predictors for the Fortune-office target; that would leak the answer into
  the model.
- Do not convert SHAP values, Ridge coefficients, or rankings into incentive
  dollar amounts. Use them to prioritize investigation, then validate through
  peer-policy review and stakeholder interviews.
- Segment the analysis by operation type. A headquarters/R&D location should
  not be evaluated with the same transport and site-size criteria as a
  manufacturing plant or warehouse.
