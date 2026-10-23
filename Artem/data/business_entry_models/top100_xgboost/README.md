# 100-MSA XGBoost comparison

This folder runs the employer-establishment entry-rate model on two different training panels, both from the public Census Business Dynamics Statistics (BDS) annual MSA file.

## Panels

1. **All 100 largest MSAs:** the 100 metropolitan statistical areas with the largest 2023 BDS establishment count.
2. **South/Sun Belt subset:** the MSAs in the top-100 roster where all member states are in this study's stated South/Sun Belt set: Alabama, Arizona, Arkansas, California, Colorado, Delaware, District of Columbia, Florida, Georgia, Kentucky, Louisiana, Maryland, Mississippi, Nevada, New Mexico, North Carolina, Oklahoma, South Carolina, Tennessee, Texas, Utah, Virginia, or West Virginia.

This is an explicit study definition, not a claim that there is one official definition of the Sun Belt. The roster records each MSA's member states and its inclusion flag, so it is easy to change the definition without changing the raw source.

## Target and test design

The target is next-year employer-establishment entries divided by prior-year establishments. Features are all lagged one year. XGBoost forecasts the rate and the script then converts it to a count using prior-year establishments.

The test is time ordered: train only on years before each test year, then predict 2018 through 2023. The accompanying persistence benchmark uses the prior year's entry rate. The primary comparison is MAE in entry-rate percentage points; raw count errors would overemphasize very large metros.

## Files

- `top_100_msa_roster.csv` — selected MSAs, official 2023 title, member states, and panel flags.
- `top_100_msa_entry_panel.csv` and `south_sunbelt_msa_entry_panel.csv` — lag-safe model panels.
- `xgboost_model_comparison.csv` — held-out XGBoost and baseline results.
- `xgboost_held_out_predictions.csv` — every test prediction.
- `xgboost_permutation_importance.csv` — held-out feature associations, not causal effects.

Source files are stored one directory above under `raw_inputs/`: Census BDS metro data and Census July 2023 CBSA delineation List 1.
