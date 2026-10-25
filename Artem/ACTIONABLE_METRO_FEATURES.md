# Actionable Metro Feature Plan

> **Status update:** The housing and talent tables remain useful peer-scorecard
> inputs. The model results later in this document used an outcome that was
> found to have incomplete Data Axle coverage and company-name matching errors.
> They are archived diagnostics, not evidence that housing or talent does or
> does not matter. See `Artem/INVEST_ATLANTA_RESEARCH_DISCOVERIES.md`.

## Why separate these features

The Fortune-presence experiment needs to distinguish between two different
questions:

1. **Structural context:** What conditions are associated with large-company
   presence across metros?
2. **Invest Atlanta levers:** What can the City, Invest Atlanta, and partners
   credibly improve, coordinate, or target?

Metro size, historic industry mix, and state tax policy may help describe the
first question, but they are not a menu of actions for Invest Atlanta. The
features below are a separate "actionable conditions" layer. They can support
policy prioritization only after the project has a complete, verified Fortune
office-presence outcome.

## Collected now: housing and talent pipelines

The project now includes a 2024 Census Building Permits Survey (BPS) feature
file for all 100 MSAs:

- [`actionable_housing_features_2024.csv`](data/map_green_state_100/actionable_housing_features_2024.csv)
- [`build_actionable_housing_features.py`](scripts/build_actionable_housing_features.py)
- [`actionable_talent_features_2024.csv`](data/map_green_state_100/actionable_talent_features_2024.csv)
- [`build_ipeds_talent_features.py`](scripts/build_ipeds_talent_features.py)

It contains:

| Feature | Meaning | Why it is relevant | Guardrail |
| --- | --- | --- | --- |
| `bps_units_per_1000_qcew_jobs_2024` | New homes authorized in 2024 per 1,000 local jobs | A normalized housing-supply pipeline that can affect whether workers can live near employment | It measures residential permits, not office availability or permit-processing time. |
| `bps_multifamily_unit_share_2024` | Share of authorized units in buildings with 2+ homes | A proxy for the ability to add housing near job centers and transit corridors | It says nothing about affordability, occupancy, or location within the MSA. |

The current BPS feature is deliberately **not** raw permit count: that would
mostly reward the largest metros. Atlanta recorded 40,687 permitted units in
2024, 36.7% in multifamily buildings, or 16.2 units per 1,000 QCEW jobs.

The talent file adds IPEDS 2024 completions from active postsecondary
institutions located in each MSA. The model uses the narrowest, most
business-relevant version: bachelor's-or-higher business/STEM completions per
1,000 QCEW jobs. Atlanta has 30,480 such reported completions, or 12.1 per
1,000 jobs. This is an institution-location pipeline, not a count of graduates
who live in Atlanta, remain in Atlanta, or are immediately available to hire.

## Next collection queue

| Policy-facing factor | Comparable metro measure | Collection source and method | What Invest Atlanta can influence | Collection status |
| --- | --- | --- | --- | --- |
| Housing affordability | Median rent, rent burden, vacancy, and housing-cost growth | Census ACS / HUD; use the same year for every MSA | Housing partnerships, tax allocation districts, site assembly, mixed-income requirements | Needs an ACS download/API key or bulk extract |
| Commute and transit access | Transit commute share, mean commute time, work-from-home share; later, transit service per resident | ACS; National Transit Database agency service data matched to MSA | TOD, first/last-mile investments, employer shuttles, site selection near transit | ACS requires an API key. NTD's native geography is agency/UZA, so use a documented MSA crosswalk rather than a loose city-name match. |
| Talent pipeline | Bachelor's-or-higher business/STEM completions per 1,000 QCEW jobs | NCES IPEDS completions assigned to reporting-institution MSA | Training partnerships, apprenticeships, university/employer programs | Collected for all 100 MSAs for 2024. |
| Digital readiness | Households with broadband subscription; high-speed service availability | ACS plus FCC Broadband Data Collection | Digital-equity partnerships, last-mile infrastructure, site marketing | Needs consistent FCC rollup method |
| Commercial permitting reliability | Median days, predictability, and online-permitting coverage for commercial projects | City planning/building annual reports; manually coded protocol | Direct City lever: intake, review coordination, pre-development support | Manual scorecard needed; no honest national off-the-shelf series |
| Site readiness | Number and acreage of development-ready sites, utilities readiness, environmental/ownership constraints | City/County parcel and economic-development inventories | Direct City/partner lever: land assembly, remediation, utility coordination | Build a locally validated inventory; do not substitute a broker listing count |
| Office-market readiness | Vacancy, asking rent, absorption, and available large blocks of space | Licensed CoStar/CBRE/JLL market data or consistent public reports | Site marketing and redevelopment support, but not market-wide rents directly | Use only if licensing and definitions are consistent across metros |
| Incentive design | Transparent policy taxonomy: target industries, job/wage thresholds, clawbacks, site/readiness support | City/state program documents, normalized by a review rubric | Direct Invest Atlanta and City lever | Manual policy coding; do **not** rank metros by raw disclosed subsidy dollars |
| Small-business pathway | Business formation, survival, and access to capital | Census BDS/BFS, SBA lending, local program records | Supplier diversity, small-business finance, technical assistance | Add after definitions are harmonized |

## Modeling rule

Do not put every available variable into one model and label the resulting
importance chart "what Atlanta should do." Use two tracks:

1. A **descriptive context model** with predetermined public conditions.
2. An **actionable opportunity scorecard** that compares Atlanta with a
   selected peer set on the policy-facing features above.

For any variable that enters the model, retain its year, source URL,
geographic unit, transformation, missingness, and whether it is a direct
policy lever or only a proxy. SHAP can explain a fitted model's prediction; it
cannot turn a correlation into proof that a policy change will produce more
Fortune offices.

## Model check: does the expanded feature set help?

Every result below uses the same 99 MSAs, five outer held-out folds, and the
same screened Data Axle candidate-location proxy. Ridge is a linear regression
with its penalty selected inside each outer training fold. It is a better
linear benchmark than ordinary least squares when predictors overlap.

| Feature set | Model | Held-out MAE | Held-out R² |
| --- | --- | ---: | ---: |
| Context only | Tuned XGBoost | 5.93 | 0.53 |
| Context only | Nested Ridge regression | 7.00 | 0.37 |
| Context only | Ordinary linear regression | 7.40 | 0.23 |
| Context + housing | Tuned XGBoost | 6.65 | 0.39 |
| Context + housing | Nested Ridge regression | 7.51 | 0.16 |
| Context + housing | Ordinary linear regression | 7.81 | -0.03 |
| Context + housing + talent | Tuned XGBoost | 6.14 | 0.48 |
| Context + housing + talent | Nested Ridge regression | 7.66 | 0.11 |
| Context + housing + talent | Ordinary linear regression | 7.94 | -0.02 |

**Answer: not better than the context-only XGBoost.** The graduate feature
recovered part of the decline from adding housing, but the best expanded model
(R² 0.48) remains below the context-only result (0.53). XGBoost beats both
linear specifications under every feature set. This is a small-sample
cross-sectional exercise, so treat the difference as a signal to investigate,
not a final model-selection verdict.

In the expanded XGBoost test, housing-permit intensity was fifth in mean
absolute out-of-fold SHAP value (0.104) and business/STEM completions sixth
(0.097). They have some predictive contribution inside that fitted model, but
neither is a causal policy weight. The linear models also illustrate why not to
turn coefficients into recommendations: their held-out fit deteriorates as the
new related predictors enter.

## Sources

- [Census Building Permits Survey](https://www.census.gov/construction/bps/index.html)
- [BPS annual CBSA tables](https://www.census.gov/construction/bps/msamonthly.html)
- [Census ACS data via API](https://www.census.gov/programs-surveys/acs/data/data-via-api.html)
- [National Transit Database](https://www.transit.dot.gov/ntd)
- [IPEDS data center](https://nces.ed.gov/ipeds/use-the-data)
- [IPEDS complete data files](https://nces.ed.gov/ipeds/help/complete-data-files)
- [FCC National Broadband Map](https://broadbandmap.fcc.gov/data-download/nationwide-data)
