# Green-Map 100-MSA Fortune Presence Experiment

> **Status update:** This document preserves the original experiment. Later
> auditing found incomplete company and geographic coverage plus name-matching
> errors in the underlying Data Axle export. Do not use the results below as
> findings or policy weights. Start with
> `Artem/INVEST_ATLANTA_RESEARCH_DISCOVERIES.md` and
> `Artem/FORTUNE100_NATIONAL_COVERAGE_AUDIT.md` instead.

## Purpose

This is an exploratory comparison of Atlanta with the 100 largest MSAs wholly
inside the states selected on the team’s green map. It tests whether public
workforce, industry, tax, housing, and price variables are associated with a
screened **Fortune 100 commercial-location candidate** count.

It is not a causal model, and it is not yet the project’s final verified
Fortune office-presence score.

## Geographic scope

The selected states are Alabama, Arkansas, Colorado, Delaware, Florida,
Georgia, Kansas, Kentucky, Louisiana, Maryland, Mississippi, Missouri, New
Mexico, North Carolina, Oklahoma, South Carolina, Tennessee, Texas, and
Virginia.

An MSA is included only when every state in that MSA is selected. This excludes
MSAs that cross into unselected states, including Washington-Arlington-
Alexandria (DC/MD/VA/WV) and Philadelphia-Camden-Wilmington (PA/NJ/DE/MD).

The 100 eligible MSAs are ranked by 2023 Census Business Dynamics Statistics
(BDS) employer establishments. The roster begins with Miami, Dallas, Houston,
Atlanta, Tampa, Denver, and Orlando; the 100th MSA is Topeka, Kansas.

Public roster files:

- [`msa_roster.csv`](data/map_green_state_100/msa_roster.csv)
- [`metro_county_crosswalk_2023.csv`](data/map_green_state_100/metro_county_crosswalk_2023.csv)

## Outcome used for this experiment

The target is:

`distinct_matched_current_f100_nonexcluded_candidate_companies`

For each MSA, this counts distinct current Fortune 100 firms with at least one
Data Axle commercial-location candidate after an automated exclusion screen.
The screen removes records explicitly described as:

- warehouses, warehousing, distribution, fulfillment, or logistics centers;
- mailing or shipping sites;
- retail/consumer sites; and
- kiosks.

This gives a cleaner proxy than counting every company location, but it does
not prove that every remaining location is an office. An insurance branch,
bank branch, retail-adjacent site, or unclassified location can remain. The
final Big Business Presence Score must remain: **distinct Fortune firms with
source-verified headquarters or qualifying offices in the MSA**.

Licensed ArcGIS/Data Axle rows and all location-level outputs stay outside the
repository. They are ignored by Git. This document contains methodology and
aggregate diagnostic results only.

## Coverage check

- 100 MSAs in the new roster
- 99 MSAs with a screened candidate score and a 2022 public-factor row
- El Paso, Texas has no candidate score; it is treated as unknown coverage,
  not zero presence
- 2022 is the common latest factor year for this panel

The near-complete roster match does not eliminate source-coverage risk. For
example, some markets with likely major-company presence still have unusually
low candidate counts. That is why this model is a diagnostic rather than a
published metro ranking.

## Predictors

All predictors are public and precede the static candidate-location outcome:

- BLS QCEW employment, employment growth, average weekly wage, and
  establishments per 100 jobs
- QCEW employment shares for manufacturing, information, finance,
  professional services, health, and hospitality
- employment-weighted state corporate-income-tax rate and gross-receipts-tax
  exposure
- BEA regional price parity
- FHFA year-over-year house-price-index growth

The factor builder uses 2017–2022 data to construct the panel; the model uses
the 2022 cross-section. Multi-state MSAs use employment-weighted state tax
values.

## Model design

- Model: `XGBRegressor` with shallow, regularized trees
- Target transformation: `log1p(candidate count)`
- Validation: five shuffled held-out MSA folds
- Benchmark: training-fold mean candidate count
- Importance: held-out permutation importance, not built-in tree gain

This is cross-sectional validation, not a future forecast. It measures whether
the model can predict held-out candidate counts among similar selected MSAs.

## Results

| Model | Held-out MSAs | MAE (companies) | RMSE (companies) | Held-out R² |
| --- | ---: | ---: | ---: | ---: |
| XGBoost screened-candidate proxy | 99 | 7.15 | 9.40 | 0.31 |
| Training-mean baseline | 99 | 9.20 | 11.58 | -0.04 |

XGBoost improves on the simple mean benchmark, so the public factors carry
some predictive signal for this *screened candidate proxy*. That does not show
that changing any one factor would cause a company to open an office.

The largest held-out permutation signals were:

1. Employment-weighted corporate tax rate: +1.49 candidate-company MAE when
   permuted
2. Log QCEW employment: +0.96
3. FHFA house-price growth: +0.45
4. Finance employment share: +0.45

These are model associations. They are not recommendations to raise or lower
taxes, nor proof that house-price growth attracts companies. The large
uncertainty across folds reinforces that caution.

## Optuna tuning and SHAP explanation check

On 2026-10-25, the model was rerun with Optuna and SHAP as a robustness and
explainability check.

- Optuna tested 40 constrained parameter combinations inside each outer
  training fold. Each candidate was evaluated with three inner folds.
- Five outer held-out folds remained untouched by tuning.
- SHAP values were calculated only for those outer-fold held-out predictions.
  This means the explanation table does not describe a model that already saw
  the MSA being explained.

| Model | Held-out MSAs | MAE (companies) | RMSE (companies) | Held-out R² |
| --- | ---: | ---: | ---: | ---: |
| Optuna-tuned XGBoost | 99 | 5.93 | 7.78 | 0.53 |
| Fixed-parameter XGBoost | 99 | 7.15 | 9.40 | 0.31 |
| Training-mean baseline | 99 | 9.20 | 11.58 | -0.04 |

The tuning result is better than the fixed setting, but it remains a result on
the screened candidate-location proxy. It should not be described as a
forecast of verified office growth or as proof that any policy lever works.

Out-of-fold SHAP ranked the same general factors near the top: employment-
weighted corporate tax rate, metro employment scale, FHFA house-price growth,
and finance employment share. SHAP shows the contribution of a feature to the
model’s prediction after accounting for the other variables; it does **not**
establish that changing the feature would change business presence.

For Atlanta’s held-out case, the tuned model predicted about 32.9 screened
candidate companies versus 61 observed in the extract. House-price growth,
employment scale, the tax-rate feature, and finance share pushed that model
prediction upward. The still-large residual is another reason to treat the
extract as a data-quality diagnostic rather than an Atlanta performance score.

## Actionable housing feature check

We added two 2024 Census Building Permits Survey features for every MSA:

- authorized residential units per 1,000 QCEW jobs; and
- the share of authorized units in multifamily buildings.

These are policy-adjacent housing-supply indicators, not measures of office
space, commercial permitting speed, affordability, or a direct policy effect.
The normalized intensity measure prevents raw permit totals from merely
reflecting metro size.

The same nested Optuna / held-out SHAP workflow was rerun using the two added
features. On this one held-out split, its results were less accurate than the
context-only tuned model:

| Model | Held-out MSAs | MAE (companies) | RMSE (companies) | Held-out R² |
| --- | ---: | ---: | ---: | ---: |
| Tuned XGBoost + housing features | 99 | 6.65 | 8.83 | 0.39 |
| Context-only tuned XGBoost | 99 | 5.93 | 7.78 | 0.53 |
| Training-mean baseline | 99 | 9.20 | 11.58 | -0.04 |

Housing-permit intensity placed fifth in out-of-fold SHAP importance (0.113),
and multifamily share placed eighth (0.052), but the overall test did not
improve held-out prediction. We should retain the features for peer
scorecards and local strategy—not call them causal weights or claim that they
are a validated explanation of corporate location.

The data, collection status, and next policy-facing variables are documented
in [`ACTIONABLE_METRO_FEATURES.md`](ACTIONABLE_METRO_FEATURES.md).

## Talent feature and linear-model check

IPEDS 2024 institutional-completions data added one normalized talent feature:
bachelor's-or-higher business/STEM completions per 1,000 QCEW jobs. It is
assigned to the MSA of the reporting college or university, not the graduate's
home or employment location. Atlanta's value is 12.1 per 1,000 jobs.

With housing and talent features together, tuned XGBoost achieved held-out MAE
of 6.14 and R² of 0.48. That recovered part of the housing-only performance
(MAE 6.65, R² 0.39), but remained below the context-only result (MAE 5.93, R²
0.53). The graduate feature ranked sixth in out-of-fold SHAP importance (0.097)
behind housing-permit intensity (fifth, 0.104).

For an equal-footing linear benchmark, the script also fits ordinary linear
regression and a training-fold-tuned Ridge regression in the same outer folds.
On the context-only feature set, Ridge reached R² 0.37 and ordinary linear
regression 0.23; both remained below tuned XGBoost at 0.53. With housing and
talent added, Ridge fell to 0.11 and ordinary linear regression to -0.02,
while XGBoost was 0.48. Therefore XGBoost remains the better diagnostic model,
but none of the model outputs should be called a causal policy estimate.

## Atlanta diagnostic

Atlanta has 61 screened Fortune 100 candidate companies in this extract. Its
held-out model prediction was about 23, a positive residual of about 38.

That is useful as a **data-quality flag**, not evidence that Atlanta is
objectively outperforming the region. Comparable red flags appear at the low
end: Albuquerque, Denver, Colorado Springs, Waco, and Lexington have much
lower candidate counts than the model predicts. Before presenting a true
Atlanta-versus-peer ranking, those locations need a complete and consistently
geographic Data Axle extract plus office-function verification.

## Reproducibility

Public-data scripts:

- [`build_map_green_state_msa_roster.py`](scripts/build_map_green_state_msa_roster.py)
- [`build_external_factors_for_msa_roster.py`](scripts/build_external_factors_for_msa_roster.py)
- [`build_actionable_housing_features.py`](scripts/build_actionable_housing_features.py)
- [`build_ipeds_talent_features.py`](scripts/build_ipeds_talent_features.py)

Local-only licensed-data scripts:

- [`ingest_arcgis_data_axle_exports.py`](scripts/ingest_arcgis_data_axle_exports.py)
- [`assign_data_axle_locations_to_msas.py`](scripts/assign_data_axle_locations_to_msas.py)
- [`run_fortune100_candidate_xgboost.py`](scripts/run_fortune100_candidate_xgboost.py)
- [`run_fortune100_optuna_shap.py`](scripts/run_fortune100_optuna_shap.py)

## Recommended next step

Use this roster as the official regional comparison universe. Then replace the
screened candidate proxy with a complete, consistently bounded Fortune office
location extract and a source-reviewed office/HQ classification. Rerun the
same factor model only after that outcome is available.
