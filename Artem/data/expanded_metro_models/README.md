# Expanded metro modeling data

Start with `../../EXPANDED_METRO_ML_EXPERIMENT.md` for the complete interpretation and caveats.

- `metro_counties_2023_census.csv`: 290 county-to-metro assignments from the 2023 Census definitions.
- `county_qcew_input_rows.csv`: selected public BLS QCEW observations, with disclosure flags retained.
- `metro_year_qcew_2018_2025.csv`: 31 metro totals, industry shares, and suppression counts for 2018–2025.
- `model_panel.csv`: 186 feature/outcome rows. Inputs are from year t and the target is December employment growth from t to t+1; blank sector shares remain missing in this file.
- `held_out_predictions.csv`, `model_comparison.csv`, `heldout_permutation_importance.csv`: held-out predictions, comparison metrics, and feature-shuffle importance. Importance is change in MAE percentage points, not a causal coefficient.
- `recent_history_sensitivity/`: same outputs for the shorter 2021–2025 input window and 2023–2025 outcome panel.

Raw nationwide QCEW slices are stored once in `../nine_metro_models/raw_qcew_industry_slices/`. The original Census workbook is in `../peer_metro_regression/raw_inputs/`. Only public data was used.
