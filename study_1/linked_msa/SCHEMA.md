# Schema and analytical rules

Updated November 10, 2026 for the [current training handoff](TRAINING_HANDOFF.md). This document describes the collected tables; the handoff separately specifies the next limited regional-feature experiment. Collection-time predictor-selection flags do not mean that new training matrices or fitted models already exist.

The company key is the existing `company_id`; the metro key is the text `cbsa` code in the fixed 50-MSA frame. Company names and geographic labels are display fields. The 2025 roster remains fixed through later mergers and name changes. July 2023 is the frame/boundary reference; a matching CBSA code does not independently establish that every source program used identical county membership.

## Tables and joins

| Table | Grain / key | Main fields and use |
| --- | --- | --- |
| `metro_indicators` | `cbsa, metric_id, reference_period, sector_code, soc_code` | Numeric `value`, status, original source flags, geography status and `evidence_id`. Blank sector/SOC means not applicable. |
| `company_locations` | `location_id` | Company, reported locality/point, CBSA, resolution, coordinates, geographic status, benchmark eligibility, broader-presence eligibility and evidence IDs. Explicit local employment/office area have their own year, scope, status and evidence ID. |
| `location_functions` | `function_observation_id` | `location_id`, company, function code, source-reference year/date, date basis, evidence status and origin. Several supported functions may belong to one locality. |
| `company_msa_coverage` | `company_id, cbsa, reference_year` | Frozen HQ label where available, reported broader presence, specific-function observation flag, screening availability and explicit completeness/absence flags. |
| `metric_dictionary` | `metric_id` | Definitions, units, source program, block, formula, missingness policy and analytical role. It includes indicator definitions, function categories and scorecard measures. |
| `msa_scorecard` | `cbsa` | Frozen 2025 HQ count, dated distinct-company/function lower bounds, unknown-company counts, observation shares and broad management-sector measures. |

Join locations to functions on `location_id`, then company attributes on `company_id`. Join a metro indicator using CBSA **and its metric, period, sector/SOC and scope**; CBSA alone would multiply rows. Aggregate locations/functions to distinct company–MSA observations before joining company-level outcomes. Never repeat a metro aggregate as an independent outcome on every company/office row.

The SQLite reference tables contain only reused company identity/industry and frame fields. CSV keys and joins are checked by the builder; SQLite also has unique-key indexes. Detailed evidence is held in the separate raw archive, rather than copied into the analytical database.

## Coding, nulls and evidence references

Read `company_id`, `location_id`, function/evidence/source IDs, five-character `cbsa`, sector codes and SOC codes as strings. In CSV, numeric nulls are empty; SQL uses NULL. A blank sector/SOC code means not applicable in the composite indicator key, so preserve it when filtering or reshaping. Numeric estimates are nullable numbers; reference years are integer annotations; the separate reference-period/date fields retain their stated granularity.

Counts and eligibility/completeness flags use numeric integers/0–1. `usable_indexed_excerpt` is a Boolean availability flag. It is not an observed economic factor. Distinguish numeric-null outcomes from zero-valued observation/audit flags. In particular, a zero function-observation flag is not a verified absence. `weighted_score` is null and `office_ranking_valid=0` throughout.

`evidence_id`, and populated `employment_evidence_id`/`area_evidence_id`, resolve to raw `evidence_index.csv:evidence_id`. That index's `source_id` resolves to raw `source_registry.csv:source_id`. Despite its field name, `geography_evidence_id` resolves directly to `source_registry.csv:source_id`. The raw registry/index hold URLs and detailed locators. Retain those relationships in audit exports without adding them to X.

## Collected metro features

- The exact 31 existing predictors, with their original values: metro scale and growth; education; income, housing and price levels; transit commuting; establishment intensity; original industry shares; six general occupation concentrations and relative pay measures.
- Underlying economic levels and available margins of error, including employment, establishments, average pay, GDP, population, household income and residential rent. Residential rent is not office rent.
- CBP 2023: employment, establishments, annual payroll, employment share, payroll per March job and jobs per establishment for the same total/broad-sector universe in all 50 MSAs. `EMPSZES=001` and `LFO=001` select totals; size bins are not added to totals. Payroll is converted from thousand USD to USD.
- QCEW 2023/2024: private employment, establishments, annual payroll, average annual pay and employment location quotient, for all broad sectors and the all-industry total. Missing source rows are explicit nulls. N-suppressed employment/wages remain null; disclosed establishment counts remain available with the original flag. The inherited 2025 all-ownership total is not substituted for private-sector detail.
- BDS 2023: jobs, firms, establishments, establishment entry/exit counts and rates, job creation/destruction and net job creation/rate, across the same broad industries. These are regional dynamics, not named-company relocations.
- OEWS May 2024: all occupations plus management, business/finance, computer/math, architecture/engineering, legal and office/administration. Employment, concentration, mean/median pay, US-relative mean pay and available relative standard errors are retained. No additional sector-specific occupation selection was made.

Broad-sector detail includes every published industry consistently, including technology-related and health sectors at the same broad level as all others. It does not implement the deferred sector-specific outcome study. No office-rent, vacancy, accessibility or realized policy-impact series is silently substituted or invented.

## Locations, functions and dates

`publisher_selected_point` records preserve the old HQ target. `city_function_cluster` records represent a named locality in a primary source, potentially containing several sites. A Census representative point is a geographic assignment aid, not an office address. Addresses/precise physical sites are not inferred from locality names. Eight locality groups remain unresolved and are excluded from metro aggregates.

The eight function codes are defined in [function_codes.csv](config/function_codes.csv). They apply across industries. A laboratory is not automatically classified as R&D; a finance-sector office is not automatically an internal finance/shared-service center. Retail stores, hospital/clinical sites, plants, warehouses and investment properties are not qualifying corporate offices merely because a company owns them. Mixed-use properties enter only for a supported qualifying office/function component. Sources that describe several functions collectively without identifying the locality's role are handled conservatively.

The new facts are annual-report observations from reports filed in 2025. `reference_year`/`reference_date` preserve their **source fiscal period**; this is an annotation, not independent proof of occupancy on the fiscal closing date. Exact filing dates and this limitation remain in the archive. The 2025 publisher HQ records instead use the edition year. The 2024 and 2025 columns therefore do not constitute a balanced historical office panel and must not be differenced as openings/closures or growth. Historical/current mismatches need further dated verification before such a study.

Only explicitly reported local employment/office area is retained, with the source's scope and approximation status. Function-level job/area fields remain null because no allocation across roles is supported. Company global workforce is not local workforce; metro-sector employment is not allocated to Fortune firms. Sparse reported space/jobs must not be summed into a supposedly complete metro total.

Block's filing says it designates no HQ under its distributed model. Its publisher point remains in the frozen selected-point target but is flagged as contested and excluded as broader-presence evidence. Its separately documented ordinary offices remain observations. The two original HQ-role exclusions also remain excluded from the HQ benchmark; ordinary-office eligibility is assessed separately for the full 500-firm roster. See raw `evidence_qualifications.csv`.

## Coverage and scorecard interpretation

`corporate_presence=1` is a supported **reported** presence; blank means unresolved. Evidence grades distinguish inherited publisher roles from primary company location/function statements. There are no verified office-absence zeros. The separate `reported_hq_benchmark` has the original selected-point zeros for 498 firms in 2025; they say nothing about ordinary offices.

Screening flags refer to one company-level source-screening attempt, not 50,000 independently audited MSA/year searches. `specific_function_observed=0` means no retained specific-function observation, not that the work is absent. The office census and absence-verification flags are zero throughout.

Scorecard counts deduplicate companies within each MSA/year/category. A company may appear in multiple function categories, so category counts cannot be added. Empty observed sets yield a lower bound of zero, not a confirmed zero. `observation_share` measures retained evidence out of the fixed 500-firm roster; it is not the percentage of actual offices captured. `unknown_company_n` is unresolved company presence, not a statistically estimated missing count.

HQ counts and the 2024 private-job denominator have explicit different dates. NAICS 55 management-sector employment/establishments describe **all covered sector businesses**, including holding companies, and are separate from Fortune-company office counts. They do not capture every managerial occupation or identify corporate attraction. Their source-native geography and suppression limitations remain in `metro_indicators`.

No weighted score is computed, and office ranking validity is false. The [training handoff](TRAINING_HANDOFF.md) specifies a three-feature candidate bundle for the next HQ comparison: CBP 2023 management-sector employment share and BDS 2023 all-industry establishment entry/exit rates. These are not yet implemented training matrices; resolve geographic/date comparability and write a versioned allowlist before fitting. All other additions remain descriptive candidates. Separate predictors from proposed outcomes and preserve whole-MSA validation and the reserved Atlanta assessment. This collection adds detail, not new independent metros or causal identification.
