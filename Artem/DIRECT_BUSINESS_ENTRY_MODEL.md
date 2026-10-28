# Direct employer-establishment entry model

## Why this model exists

The previous peer-metro work used employment growth as a proxy for business performance. This experiment changes the outcome to a direct public business-dynamism measure: **the count of employer establishments entering a metro in a year**.

It does **not** create a score from the same variables and then train a model to reproduce that score. The outcome is observed Census data, and every input is lagged one year before the outcome.

## Source and geography

- **Source:** U.S. Census Bureau, Business Dynamics Statistics (BDS), annual MSA file, 1978–2023.
- **Analytical sample:** 31 peer and comparison metros, 2011–2023 (403 metro-years).
- **Validation period:** six rolling, future-year holdouts: 2018–2023 (186 metro-year predictions).
- **Geography:** MSA / metro area. This supports metro benchmarking only; it must not be reported as a City of Atlanta result. An Alpharetta or other suburban establishment is part of the Atlanta metro result, but not a City of Atlanta win.

The BDS entry count measures employer establishments with positive employment in the current year and no employment in the preceding year. It is a solid metro-level measure of overall employer-establishment entry, but it does not identify whether an entry is a large corporate move, a local startup, a franchise, or a new location opened by an existing firm.

## Target and inputs

The model predicts the next year's `estabs_entry` count. To make metro sizes comparable, it predicts the entry rate first:

`next-year entries / prior-year establishments`

and then converts that forecast to a predicted count using the prior-year establishment count. The primary error metric is therefore percentage points of entry rate rather than raw number of entries.

Inputs, all from the prior year:

- establishment entry and exit rates;
- overall and birth-related job-creation rates;
- job-destruction, net-job-creation, and reallocation rates;
- log establishment and employment scale.

## Held-out model comparison

| Model | Entry-rate MAE (pp) | Meaning |
| --- | ---: | --- |
| CatBoost rate model | **0.709** | Best result in this experiment; nonlinear rate forecast |
| XGBoost rate model | 0.726 | Essentially tied with the top result |
| Random forest rate model | 0.728 | Essentially tied with the top result |
| Last year's entry rate | 0.737 | Strong transparent benchmark |
| Ridge log-rate model | 0.803 | Regularized linear benchmark |
| Lasso log-rate model | 0.843 | Sparse linear benchmark |
| Poisson rate model | 0.923 | Count/rate statistical benchmark |
| Historical mean rate | 1.422 | Simple low-information baseline |

Lower is better. CatBoost's advantage over XGBoost is only 0.017 percentage points and over the last-year-rate benchmark is 0.029 percentage points. With only 186 held-out observations, the defensible conclusion is that **CatBoost is a useful provisional model, not a decisively established winner**. The transparent last-year-rate benchmark should stay in every future presentation.

## What the model says about predictive factors

Held-out permutation testing for the leading tree model, CatBoost, ranks the inputs as follows:

1. Prior-year entry rate (+0.691 pp MAE when shuffled)
2. Prior-year exit rate (+0.061 pp)
3. Birth-related job-creation rate (+0.047 pp)
4. Other labor-market and size variables (near zero incremental signal in this sample)

This is a prediction result, not a causal finding. In particular, it does **not** demonstrate that changing a policy lever will raise establishment entry by the same amount. The strongest takeaway is persistence: metros that recently had high entry rates tend to continue doing so, while churn and new-firm job creation add a modest amount of forecasting value.

## Atlanta context from the same public source

Atlanta had 17,782 employer-establishment entries in 2023. The model's consistent count-over-prior-establishments rate was 12.65%; after a 2021 spike, it remained stronger than the 2018–2020 range. The descriptive cross-metro dynamism index places Atlanta at 75.8 out of 100 in 2023. That index is exploratory and is deliberately excluded from all model training.

## What this can and cannot answer for Invest Atlanta

This model helps answer: *Is overall employer-establishment entry in Metro Atlanta improving or lagging peers, and which broad labor-market patterns move with it?*

It cannot by itself answer: *Which large companies did Invest Atlanta attract or retain, where did they locate, how many jobs did they commit to, and why?* That needs a project-level panel with a firm identifier, announcement/opening date, address, facility type, job commitment, industry, and a City-versus-metro flag. Combining that panel with BDS would make the large-business attraction question measurable without confusing regional activity with City activity.

## Reproduce

Run:

```bash
python3 Artem/scripts/business_entry_models.py
```

Inputs and outputs are in `Artem/data/business_entry_models/`. See its README for the exact public Census source and file descriptions.
