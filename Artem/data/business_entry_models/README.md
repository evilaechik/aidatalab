# Public business-entry model data

This folder uses public Census Business Dynamics Statistics (BDS) annual metro data to model **employer-establishment entries**. The raw source is the Census 2023 BDS metro file, covering 1978–2023:

<https://www2.census.gov/programs-surveys/bds/tables/time-series/2023/bds2023_msa.csv>

## What the outcome means

`estabs_entry` is the number of employer establishments that have positive employment in the current year and zero employment in the prior year. The rate is evaluated relative to the prior year's establishment count.

This is a public, consistent proxy for overall business establishment entry. It is **not** a direct count of major-company relocations, announced investment projects, or City of Atlanta activity. The geography is the metropolitan statistical area (MSA), so Atlanta results include the broader metro and must not be reported as City of Atlanta outcomes.

## Files

- `raw_inputs/census_bds_2023_msa.csv` — source download; public Census data.
- `bds_31_metro_entry_panel.csv` — 31-metro analytical panel for 2011–2023, including one-year-lagged features.
- `held_out_entry_predictions.csv` — rolling, future-year predictions for 2018–2023.
- `entry_model_comparison.csv` — model comparison. The primary metric is entry-rate MAE in percentage points, not raw counts, because raw counts mainly measure metro size.
- `tree_model_permutation_importance.csv` — held-out permutation associations for the better tree model. These are not causal effects.
- `descriptive_business_dynamism_score.csv` — an observed cross-metro descriptive index based on entry rate, job creation from births, and net job creation. It is never used as a model target or predictor.

## Modeling choices

The script in `Artem/scripts/business_entry_models.py` uses only the prior year's conditions to forecast the next year's entry rate, then converts that rate to an expected count using the prior year's establishment scale. It compares transparent rate baselines, a regularized Poisson rate model, regularized linear models, random forest, XGBoost, and CatBoost with time-ordered holdouts. The file intentionally does not select a winner from in-sample fit.

For an attraction strategy specifically about large firms, this should later be complemented with a project-level database that records firm, date, facility type, job commitment, and City-versus-metro address. BDS alone cannot make that distinction.
