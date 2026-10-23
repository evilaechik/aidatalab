# XGBoost: 100 largest MSAs vs. South/Sun Belt subset

## Design

This expands the entry-rate study from 31 metros to the **100 U.S. MSAs with the largest number of employer establishments in 2023**. It then trains the same model on a second, region-specific panel with **59 South/Sun Belt MSAs** from that same top-100 roster.

The target is next-year employer-establishment entries per prior-year establishment. All model features come from the prior year. The tests are rolling future-year holdouts from 2018 to 2023, rather than random train/test splits.

The South/Sun Belt label is a study definition, not an official Census region. An MSA is included only when all of its member states fall in the documented state set. This includes Atlanta and avoids classifying a multi-state metro as Southern simply because one member county is in a Southern state. The exact roster and membership flags are in `Artem/data/business_entry_models/top100_xgboost/top_100_msa_roster.csv`.

## Results

| Training panel | Training panel size | Held-out cases | XGBoost rate MAE | Prior-year-rate baseline MAE | XGBoost improvement |
| --- | ---: | ---: | ---: | ---: | ---: |
| 100 largest MSAs | 1,300 metro-years | 600 | **0.727 pp** | 0.737 pp | 0.010 pp |
| South/Sun Belt subset | 767 metro-years | 354 | **0.764 pp** | 0.766 pp | 0.002 pp |

Lower error is better. XGBoost technically outperformed the simple baseline in both panels, but the improvement is extremely small, especially in the regional panel. The best honest conclusion is:

> Use XGBoost as an exploratory nonlinear model and keep the prior-year entry-rate baseline beside it. The current public BDS variables do not support a claim that complex ML delivers a material forecast advantage.

The larger 100-MSA sample is more stable and produces lower error than the South/Sun Belt-only sample. If the team needs one model for a first presentation, use the all-100 panel and state that it has the larger validation set.

## Predictive factor pattern

In both panels, prior-year establishment-entry rate dominated held-out XGBoost permutation importance:

| Feature | All-100 MAE increase when shuffled | South/Sun Belt MAE increase when shuffled |
| --- | ---: | ---: |
| Prior-year entry rate | 0.956 pp | 0.820 pp |
| Prior-year exit rate | 0.047 pp | 0.035 pp |
| Prior-year job creation from births | 0.009 pp | 0.006 pp |
| All remaining features | approximately 0 pp | approximately 0 pp |

This is evidence of **persistence**, not a policy effect: metros with higher recent establishment-entry rates tend to retain higher entry rates. The model does not show that changing an incentive, tax, or workforce program will produce the same change. Those questions need policy/incentive data and a project-level outcome such as firm location announcements, jobs committed, and City-versus-metro address.

## Files to use

- `Artem/scripts/top_100_msa_xgboost.py` — reproducible analysis.
- `Artem/data/business_entry_models/top100_xgboost/xgboost_model_comparison.csv` — headline model results.
- `Artem/data/business_entry_models/top100_xgboost/xgboost_permutation_importance.csv` — feature-association results.
- `Artem/data/business_entry_models/top100_xgboost/xgboost_held_out_predictions.csv` — every forecast used in testing.

The raw sources are public Census BDS metro data and the Census July 2023 CBSA delineation file. The BDS entry measure captures employer-establishment openings overall; it does not identify large-company relocations or City of Atlanta activity on its own.
