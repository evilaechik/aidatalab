# Atlanta business attraction and retention: research plan

Updated October 27, 2026. **Current phase: collection is complete for all 50 metros in the supplied list, including Atlanta and 49 potential comparison areas (450 data files). The consistency audit passed for the required files, schemas, reference windows and supporting metadata. Source availability and headquarters-verification limits remain documented below. Benchmarking specifications and analysis remain to be completed.**

## Aim

**Where is Atlanta lagging in business attraction and retention, what factors are causing this, and what incentives can be implemented or expanded to increase business attraction and retention?**

Identify persistent gaps by industry and firm type, investigate their causes, and recommend feasible incentive strategies tied to those gaps. Expansion is a related outcome to examine alongside attraction and retention. The intended result is a prioritized set of industries/business types and policy opportunities, with an evidence-based rationale and a plan to evaluate results.

## Scope and definitions to settle first

- **Geography:** The shared collection covers Atlanta (12060) and the other 49 metros in the inventory below. County GDP uses July 2023 OMB metro membership; other programs retain their source geography vintages. Charlotte spans NC and SC, and Raleigh excludes Durham. Separately define the City of Atlanta policy jurisdiction; metro results do not establish city outcomes or Invest Atlanta program effects.
- **Peers:** The original eight candidate peers were Austin, Charlotte, Dallas, Denver, Houston, Miami, Nashville and Raleigh. The expanded collection provides 49 potential comparison areas, rather than establishing a final peer group. Select and justify peers using baseline size, industry mix, growth conditions, and relevant regional characteristics before ranking performance.
- **Time:** The annual collection starts in 2023, with the explicitly requested 2022 Economic Census exception. QCEW, CBP and BDS contain 2023 observations for all 50 metros, subject to native geography and suppression rules. **2023 GDP totals are available for 48 metros; Hartford and Bridgeport lack 2023 GDP on the collected planning-region boundaries.** GDP totals cover all 50 metros in 2024. QCEW extends to 2025, with metro totals only in that year; revenue, tax and headquarters observations have separate reference years. The earlier proposed 2015–2023 window is not represented in these shared folders. Set the research window and geographic comparability explicitly before making trend or recovery claims.
- **Segments:** The collection supports source-specific industry comparisons and CBP establishment-size groups. Finalize compatible industry groupings and distinguish establishment size from firm size; the current files do not provide a common firm-size dimension across all sources.

| Outcome | Working definition | Measurement decision |
| --- | --- | --- |
| Attraction | Businesses establish a new local presence from outside the area | Prefer verified new-location/relocation events, jobs, and investment. Aggregate entry counts also include local startups; classify them separately where possible. |
| Expansion | Existing local businesses increase activity | Prefer verified expansions and employment/investment changes at existing businesses. Aggregate growth and job creation are broader proxies. |
| Retention | Existing businesses continue operating locally | Define a starting cohort and follow continued presence, closures, relocations, and employment. Aggregate exit rates indicate risk but do not identify why businesses leave. |

Set denominators, units, and comparison periods for each measure. Distinguish direct observations from proxies; net employment or establishment growth alone cannot separate these three outcomes.

## Available collected evidence

Each of the 50 city folders contains the same nine data files, plus `README.md`, `download_manifest.csv` and `data_dictionary.json`: **450 data files and 150 supporting city files** under the shared [data directory](data/README.md). The original nine metros were followed by batches of 10, 10, 10 and 11, adding 41 metros. Detailed sources, acquisition dates, units and handling rules remain in the [dataset context](data/datasets_context.md) and each city's supporting files.

| Required file in every city folder | Reference year(s) | Columns | Required information and research use |
| --- | --- | ---: | --- |
| `qcew_annual_2023_2025.csv` | 2023–2025 | 40 | Employment, wages, establishments, ownership/industry identifiers and disclosure flags. Industry detail covers 2023–2024; 2025 contains one all-ownership, all-industry total per metro. |
| `cbp_employment_2023.csv` | 2023 | 31 | Employment, payroll, establishment counts, industry/establishment-size/legal-form identifiers, labels, flags and noise fields. |
| `economic_census_2022_detail.csv.gz` | 2022 | 32 | Detailed industry sales/receipts, employment, establishments, payroll, NAICS 2022 identifiers and source flags from EC2200BASIC. |
| `economic_census_2022_sectors.csv` | 2022 | 32 | The same fields for 15 specified broad sectors, restricted to total operation and tax status. This is a subset of the detail file. |
| `bea_county_gdp_2023_2024.csv` | 2023–2024 | 18 | Nominal county/equivalent output, all 34 source industry lines, source status/vintage and complete derived all-industry metro sums. Connecticut's unavailable 2023 observations are qualified below. |
| `state_corporate_tax_2026.csv` | 2026 | 9 | One row per constituent state, including DC where applicable, with statutory corporate income-tax rate, published schedule, source and qualifications. These observations do not measure effective tax burdens or 2023 conditions. |
| `fortune500_headquarters_2025.csv` | 2025 edition | 17 | National rank, company, reported location, separately dated location evidence and verification status. Current-location fields can be unknown; two metros have zero matched publisher locations. |
| `cbp_establishments_2023.csv` | 2023 | 14 | An exact establishment-focused projection of the CBP employment file, preserving industry, size, legal form and flags. Counts are business-location proxies, rather than a named office roster. |
| `bds_metro_2023.csv` | 2023 | 58 | All 20 returned total/broad-sector rows with establishment entry/exit, job flows, rates and source flags. These are attraction/retention proxies; they do not identify relocations or establish a trend. |

### Dataset consistency audit

The October 27 audit checked **all 450 saved data files** against the original Dallas/Denver schemas, city dictionaries and manifests. All 50 ranking positions are represented once. The audit confirmed:

- Exact filenames, compression format, column names/order, required metric and flag columns, units, reference periods, and metro identifiers; all three supporting files are present in every folder.
- Matching saved row counts, byte counts and SHA-256 checksums; parseable records with nonblank, unique observation keys; source URLs, vintages, verification dates and methods recorded in the supporting metadata.
- Exact CBP establishment projections and Economic Census sector selections, 20 BDS rows per metro, and one QCEW total for each requested year. All 50 QCEW files contain exactly one 2025 row.
- Complete constituent-county/equivalent coverage in the BEA reporting-area mappings, every available metro GDP sum reconciled to its constituent all-industry values, and tax rows covering every constituent state separately.

File and schema consistency does not establish that every observation is available or comparable. Source suppression and documented unknowns are retained. GDP, Economic Census receipts and Census payroll are in **thousand USD**; QCEW wages/pay are in **USD**. A suppressed zero is not an observed zero. CBP's two views, Economic Census detail/summary, and GDP county/metro rows overlap and must not be added together. No common industry crosswalk or geographic backcast has been applied.

### Coverage and comparison limits

- **Unavailable Connecticut GDP:** Hartford and Bridgeport use July 2023 planning-region county equivalents. Their 2023 GDP rows retain the BEA `(NA)` marker and `value_status=source_flag`; only complete 2024 metro sums are derived. A 2023 GDP comparison can cover 48 collected metros. For all 50, use 2024 GDP as a separately dated measure or omit GDP from the 2023 comparison. Historical-county estimates must not be substituted without an explicit geography method.
- **Geography breaks:** QCEW uses February 2013 metro definitions through 2023 and July 2023 definitions from 2024. Cleveland changes from native QCEW area C1746/former CBSA 17460 to C1741/17410; Connecticut shifts from historical counties to planning regions. New Orleans' collected seven-parish GDP geography excludes St. Tammany, unlike older source definitions. Matching metro helper codes do not establish unchanged boundaries. New York and Chicago GDP follow July 2023 NY–NJ and IL–IN membership, despite the older state labels in the selection list. BEA combined Virginia reporting areas are retained and mapped to their constituent counties/cities without double-counting.
- **Empty publisher rosters:** Sacramento and Salt Lake City each have a valid 17-column Fortune file with zero records and manifest status `collected_no_publisher_locations`. The full 500-company map source and target polygons were checked. This means no matched publisher location, rather than missing collection or proof that these metros have no company offices or headquarters under every definition.
- **Headquarters evidence:** The original nine metros use regional/Chamber rosters and primary location evidence; the 41 additions use Fortune's 2025 map coordinates assigned to Census 2023 CBSA polygons, preserving a single publisher location per company. This does not establish global principal offices, all co-headquarters or a consistent current-HQ census. Current-metro verification is unknown in 403 of the 435 reported rows; some historical municipality fields are also unknown. Choose one observation-date and location definition, then complete consistent checks before comparing headquarters counts. Denver's historical QVC entry retains its May 29, 2025 Pennsylvania move; Seattle's Lululemon and Detroit's Autoliv rows retain publisher-location conflicts with company filings and must be excluded from independently established global-headquarters counts. Atlanta's 2025 Chamber roster contains 15 metro entries, including Newell Brands; Aflac and Mohawk are outside the metro.
- **Tax and selection dates:** Tax rows preserve separate state regimes, graduated schedules and qualifying surtaxes; numeric rates are the top published statutory rates where applicable. A zero corporate income-tax rate does not mean absence of other business taxes. The supplied top-50 list controls collection order, but its GDP values include older reference years/vintages and differing geography. It is not a consistent 2024 performance ranking or a justification for the peer group.

The collection supports source-specific comparisons once these rules are settled. It does not by itself provide a common multi-year industry panel across all sources, pre-pandemic comparisons, company-level revenue analysis, or causal estimates of incentive effects. Treat the separately dated revenue, headquarters and tax observations as contextual evidence unless the analysis explicitly accommodates their timing.

## Collected metropolitan areas

All 50 areas below have their own `data/<city>_data` folder with the nine required files and three supporting files. Order follows the [supplied top-50 list](data/top_50_us_metro_areas_by_gdp.md); names and CBSA identifiers below describe the collected July 2023 GDP geography. Other programs retain native source titles and boundaries.

| List rank | Collected metropolitan area / folder documentation | CBSA |
| ---: | --- | --- |
| 1 | [New York–Newark–Jersey City, NY–NJ](data/new_york_data/README.md) | 35620 |
| 2 | [Los Angeles–Long Beach–Anaheim, CA](data/los_angeles_data/README.md) | 31080 |
| 3 | [Chicago–Naperville–Elgin, IL–IN](data/chicago_data/README.md) | 16980 |
| 4 | [San Francisco–Oakland–Fremont, CA](data/san_francisco_data/README.md) | 41860 |
| 5 | [Dallas–Fort Worth–Arlington, TX](data/dallas_data/README.md) | 19100 |
| 6 | [Houston–Pasadena–The Woodlands, TX](data/houston_data/README.md) | 26420 |
| 7 | [Washington–Arlington–Alexandria, DC–VA–MD–WV](data/washington_data/README.md) | 47900 |
| 8 | [Boston–Cambridge–Newton, MA–NH](data/boston_data/README.md) | 14460 |
| 9 | [Atlanta–Sandy Springs–Roswell, GA](data/atlanta_data/README.md) | 12060 |
| 10 | [Seattle–Tacoma–Bellevue, WA](data/seattle_data/README.md) | 42660 |
| 11 | [Philadelphia–Camden–Wilmington, PA–NJ–DE–MD](data/philadelphia_data/README.md) | 37980 |
| 12 | [Miami–Fort Lauderdale–West Palm Beach, FL](data/miami_data/README.md) | 33100 |
| 13 | [San Jose–Sunnyvale–Santa Clara, CA](data/san_jose_data/README.md) | 41940 |
| 14 | [Phoenix–Mesa–Chandler, AZ](data/phoenix_data/README.md) | 38060 |
| 15 | [Minneapolis–St. Paul–Bloomington, MN–WI](data/minneapolis_data/README.md) | 33460 |
| 16 | [Detroit–Warren–Dearborn, MI](data/detroit_data/README.md) | 19820 |
| 17 | [San Diego–Chula Vista–Carlsbad, CA](data/san_diego_data/README.md) | 41740 |
| 18 | [Denver–Aurora–Centennial, CO](data/denver_data/README.md) | 19740 |
| 19 | [Charlotte–Concord–Gastonia, NC–SC](data/charlotte_data/README.md) | 16740 |
| 20 | [Baltimore–Columbia–Towson, MD](data/baltimore_data/README.md) | 12580 |
| 21 | [Riverside–San Bernardino–Ontario, CA](data/riverside_data/README.md) | 40140 |
| 22 | [Austin–Round Rock–San Marcos, TX](data/austin_data/README.md) | 12420 |
| 23 | [Tampa–St. Petersburg–Clearwater, FL](data/tampa_data/README.md) | 45300 |
| 24 | [St. Louis, MO–IL](data/st_louis_data/README.md) | 41180 |
| 25 | [Orlando–Kissimmee–Sanford, FL](data/orlando_data/README.md) | 36740 |
| 26 | [Portland–Vancouver–Hillsboro, OR–WA](data/portland_data/README.md) | 38900 |
| 27 | [Nashville-Davidson–Murfreesboro–Franklin, TN](data/nashville_data/README.md) | 34980 |
| 28 | [Indianapolis–Carmel–Greenwood, IN](data/indianapolis_data/README.md) | 26900 |
| 29 | [Cincinnati, OH–KY–IN](data/cincinnati_data/README.md) | 17140 |
| 30 | [Pittsburgh, PA](data/pittsburgh_data/README.md) | 38300 |
| 31 | [Sacramento–Roseville–Folsom, CA](data/sacramento_data/README.md) | 40900 |
| 32 | [Kansas City, MO–KS](data/kansas_city_data/README.md) | 28140 |
| 33 | [San Antonio–New Braunfels, TX](data/san_antonio_data/README.md) | 41700 |
| 34 | [Columbus, OH](data/columbus_data/README.md) | 18140 |
| 35 | [Las Vegas–Henderson–North Las Vegas, NV](data/las_vegas_data/README.md) | 29820 |
| 36 | [Cleveland, OH](data/cleveland_data/README.md) | 17410 |
| 37 | [Salt Lake City–Murray, UT](data/salt_lake_city_data/README.md) | 41620 |
| 38 | [Raleigh–Cary, NC](data/raleigh_data/README.md) | 39580 |
| 39 | [Milwaukee–Waukesha, WI](data/milwaukee_data/README.md) | 33340 |
| 40 | [Jacksonville, FL](data/jacksonville_data/README.md) | 27260 |
| 41 | [Virginia Beach–Chesapeake–Norfolk, VA–NC](data/virginia_beach_data/README.md) | 47260 |
| 42 | [Hartford–West Hartford–East Hartford, CT](data/hartford_data/README.md) | 25540 |
| 43 | [Richmond, VA](data/richmond_data/README.md) | 40060 |
| 44 | [Bridgeport–Stamford–Danbury, CT](data/bridgeport_data/README.md) | 14860 |
| 45 | [Providence–Warwick, RI–MA](data/providence_data/README.md) | 39300 |
| 46 | [Memphis, TN–MS–AR](data/memphis_data/README.md) | 32820 |
| 47 | [New Orleans–Metairie, LA](data/new_orleans_data/README.md) | 35380 |
| 48 | [Oklahoma City, OK](data/oklahoma_city_data/README.md) | 36420 |
| 49 | [Louisville/Jefferson County, KY–IN](data/louisville_data/README.md) | 31140 |
| 50 | [Omaha, NE–IA](data/omaha_data/README.md) | 36540 |

## Immediate research decisions

1. Confirm the collected Atlanta metro scope for the intended comparison and define the City of Atlanta policy jurisdiction separately; assess source-geography differences before combining programs.
2. Establish final peer-selection criteria and justify the comparison group drawn from the 49 collected potential peers; assess whether the original eight candidates remain suitable.
3. Specify a 2023 baseline and the supported source-specific follow-up periods, or revise the research window with an explicit acquisition plan. Decide whether to restrict 2023 GDP comparisons to 48 metros, omit that measure for Hartford/Bridgeport, or use separately dated 2024 GDP. Keep the 2022 revenue, 2025 headquarters and 2026 tax dates visible.
4. Set compatible industry groups, denominators, ownership coverage, size definitions, and suppression rules. Account for the overlaps between source views before calculating totals.
5. Produce the first comparable benchmark tables and identify gaps worth investigating. Driver analysis, incentive comparisons and policy recommendations follow that evidence.

No industry performance ranking, causal driver finding, or incentive recommendation has been established by this collection step.

## Research steps and planning outputs

### 1. Benchmark Atlanta's performance

Compare Atlanta with similar metros across industries and firm types to identify persistent over- and underperformance in attraction, expansion, and retention.

**Plan:** Finalize definitions, peer-selection rules, geography, time window, segment classifications, and a metric-to-source map. Specify how to handle missing/suppressed values and how to test whether rankings change with peer or period choices.

**Output:** A benchmarking specification, followed by comparable tables and a shortlist of gaps that warrant explanation.

### 2. Identify key drivers of performance

Investigate whether workforce availability, costs, real estate, industry trends, infrastructure, and the local business environment explain the identified gaps.

**Plan:** Develop hypotheses for each gap, identify measurable drivers and plausible mechanisms, and consider competing explanations. Choose an analysis design that separates association from stronger causal evidence, accounting for baseline conditions, timing, and confounding factors.

**Output:** A hypothesis/evidence matrix and a proposed driver-analysis design. Describe causal explanations as provisional until the evidence supports them.

### 3. Compare incentive strategies

Review programs in regions performing well in Atlanta's weak segments, alongside Atlanta's existing programs.

**Plan:** Compare program type, eligibility, industry/firm targeting, award structure, job/investment requirements, funding, delivery, and accountability. Seek evaluations and realized outcomes as well as program descriptions; distinguish commitments, payouts, and achieved results.

**Output:** A program-comparison framework and evidence-quality assessment. Strong regional performance alone does not establish that incentives caused it.

### 4. Identify actionable opportunities

Determine which incentives could be implemented or expanded to address Atlanta's specific gaps, and which industries or business types are suitable targets.

**Plan:** Assess the mechanism connecting each proposal to the gap, policy jurisdiction, feasibility, costs, likely additional activity, and risks. Specify implementation conditions and success measures before recommending adoption.

**Output:** Prioritized policy options and target segments, with rationale, uncertainties, and an evaluation plan. Firm-level targeting follows the segment and policy analysis.

## Context files and references

- This file defines the research aim, planning decisions, and intended outputs. Record unresolved design choices explicitly; do not present proposed measures or hypotheses as findings.
- [Dataset context](data/datasets_context.md) summarizes the collected files, sources, geography, year windows and interpretation limits. City manifests and dictionaries preserve exact acquisition details and schemas; the [data index](data/README.md) records collection progress.
- The [top-50 list](data/top_50_us_metro_areas_by_gdp.md) controls acquisition order. Collection reports cover [batch 1](data/collection_batch_01.md), [batch 2](data/collection_batch_02.md), [batch 3](data/collection_batch_03.md) and the [final batch/completion audit](data/collection_batch_04.md).
