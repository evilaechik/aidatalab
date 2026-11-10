# Feature and measurement catalog — both HQ tracks

Historical design/method record for the initial sample. The current completed study uses 498 eligible firms and three additional regional features; use the [current run index](README.md) and [feature-refinement contract](feature_refinement/config/training_contract.json). Original methodological choices and collection dates below remain documented.

**Scope update — November 10, 2026:** this catalog describes the completed original HQ experiment. The [linked schema](linked_msa/SCHEMA.md) and [current training handoff](linked_msa/TRAINING_HANDOFF.md) cover the additional regional detail, reported locations/functions and sparse local jobs/space. Their collection does not automatically expand either frozen model's predictor list.

Updated November 9, 2026 · Separate predictor specifications govern each track.

Track A predicts `reported_hq_count_2025` from 31 metro features. Track B predicts
`reported_hq_presence` from the same metro features plus company characteristics
and four preset interactions, then sums probabilities into a metro benchmark.
Both retain the same covered firms, source periods and reported-HQ definition.

## Shared metro predictors: 31 numeric fields

| Block | Features | Count | Reference |
| --- | --- | --- | --- |
| Regional scale | Log private employment, log population, log nominal GDP | 3 | 2024; GDP revised 2026 vintage |
| Growth | Fixed-county Q4 employment growth; same-vintage population growth | 2 | Q4 2023–2024; July 2023–2024 |
| Skills | Bachelor-plus share among residents age 25+ | 1 | ACS 2024 |
| Costs/income | Log household income, log residential gross rent, all-items RPP, log private average pay | 4 | 2024; RPP released 2026 |
| Transport | Transit commute share excluding taxi | 1 | ACS 2024 |
| Business structure | Private establishments per 1,000 private jobs | 1 | QCEW 2024 |
| Industry mix | Manufacturing, retail, transport/warehousing, information, finance/insurance, professional/technical, health/social employment shares | 7 | CBP 2023, NAICS 2017 |
| Occupational mix | Management, business/financial, computer/math, architecture/engineering, legal, office/admin jobs per 1,000 | 6 | OEWS May 2024 |
| Occupational pay | Same six groups' local mean wages / national same-occupation mean wages | 6 | OEWS May 2024 |

The [metro dictionary](expanded_500/tables/feature_dictionary.csv) supplies exact columns,
formulas, units, periods, source programs and null counts. Track A's authoritative
allowlist is [feature_spec.json](expanded_500/reference_inputs/feature_spec.json).

There are 1,546 observed values among 1,550 regional predictor cells. Missing
values are Hartford/Bridgeport employment growth, Sacramento management intensity,
and Las Vegas legal relative wage. Source geography gaps and suppressions remain
null. These four gaps repeat across 98 firms as 392 missing numeric cells in
Track B; they remain four regional measurement gaps, not new independent evidence.

## Additional company–metro predictors

Track B uses [company_hq_feature_spec.json](expanded_500/reference_inputs/company_hq_feature_spec.json)
and the [company–metro dictionary](expanded_500/tables/company_hq_feature_dictionary.csv).
Its 39 primary input columns comprise 37 numeric and 2 categorical fields:

| Added block | Primary fields | Count |
| --- | --- | --- |
| Company scale | `log_company_revenue`, `log_company_workforce` | 2 |
| Company categories | `company_broad_industry`, `ownership_listing_type_2025` | 2 |
| Preset company–metro interactions | Technology × computer/math intensity; financials × finance share; health care × health share; selected industrial sectors × manufacturing share | 4 |

Exact interaction indicator groups and formulas are frozen in the dictionary
and builder. The main-effects-only comparison has 35 raw input columns. One-hot
encoding changes the fitted design-matrix size, not the number of collected
variables. All primary company predictors are complete for the covered roster.

Log assets, profit margin and revenue-growth fraction are three **optional
sensitivity** fields, excluded from primary inputs by default. The company
dictionary therefore includes 42 primary-plus-optional fields. Preprocessing
statistics and category encoders must be fitted inside training folds.

Company attributes are allowed in Track B because they vary across companies.
They are not regional predictors in Track A. Summing financials only for firms
whose HQs are in a metro would disclose the response; such target-derived
resident-company aggregates remain prohibited in both tracks.

## Retained normalized inputs

| Table | Role |
| --- | --- |
| [Metro economic inputs](expanded_500/tables/metro_economic_inputs_2024.csv) | Employment, GDP, population, education, income, rent, transit, prices, source-geography context and ACS uncertainty |
| [Metro sector inputs](expanded_500/tables/metro_sector_inputs.csv) | 350 MSA-sector records; complete CBP shares and separate QCEW alternatives with disclosure flags |
| [Metro occupation inputs](expanded_500/tables/metro_occupation_inputs_2024.csv) | 350 records: all-occupation totals and six major groups, source flags, estimates, standard errors and national wage denominators |
| [Fixed-geography growth](expanded_500/tables/fixed_geography_employment_growth.csv) | 50-row county-sum diagnostic; incomplete sums stay unknown |
| [Selected company cohort](expanded_500/reference_inputs/company_cohort_100.csv) | 100 identities, industries, listing categories, company-wide financials, reported HQ geography and sampling metadata |
| [Derived company features](expanded_500/tables/company_hq_features_2025.csv) | Company predictor transforms for all 100 selected firms; only 98 enter supervised exports |

Company financials use the Fortune 2025 edition's primarily FY2024 basis; fiscal
calendars differ. Workforce is the publisher's global employee-equivalent measure,
not local jobs. Listing categories are not a fully verified private/cooperative/
mutual ownership taxonomy. Do not invent exact fiscal-end dates or current status.

## Outcomes, metadata and prohibited fields

Track A's count sums Track B's known binary labels; the count share divides by
98. Both definitions concern the publisher-selected HQ point. A zero does not
exclude ordinary offices or additional HQ functions. The excluded firms' null
labels remain only in the audit grid and must never be imputed.

IDs, CBSA/name, company name, splits, coverage/source statuses, reported HQ
city/state/CBSA, known inside-frame status and target-derived HQ/sector counts
are excluded from predictors in both tracks. Additional-HQ counts, selected-100
bounds and unreviewed publisher totals are outcome diagnostics, not default
responses or predictor fields. Follow the track-specific allowlists rather than
passing every numeric table column to a learner.

## Interpretation and uncollected fields

Residential rent is not commercial office rent; RPP is not office operating cost;
occupation intensity is workforce stock, not job vacancies. GDP inputs are nominal
thousand USD. Shares are fractions; employment growth is Q4-to-Q4, not annual-average
growth. Primary sector shares consistently use lagged CBP rather than mixing
suppressed QCEW estimates with available values.

For the original experiment described here, no new collection of commercial-office rent/vacancy, air service, local site
employment, floor area, regional/R&D/sales functions, subsidiary networks, or
verified 2025 state taxes was performed for the extension. The old 2026 statutory
tax context is excluded. These are possible later diagnostics, not required
inputs for either agreed HQ track. Industry diversity does not establish
unobserved office-function diversity, and correlated predictors need held-out
assessment before their importance is interpreted.
