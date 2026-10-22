# Nine-metro model files

Read `../../NINE_METRO_MODEL_BRIEF.md` before interpreting the data or model results.

- `raw_qcew_industry_slices/`: BLS QCEW cross-sectional CSVs for seven industry series. Q4 2021–2025 supports this nine-metro model; Q4 2018–2020 is also used by the expanded-metro model. Source: `https://data.bls.gov/cew/data/api/{year}/4/industry/{industry}.csv`.
- `metro_counties_2023_census.csv`: county membership in the nine 2023 Census CBSAs; the original Census workbook is in `../peer_metro_regression/raw_inputs/`.
- `county_qcew_input_rows.csv`: county-year-industry records selected from the raw source files; suppressed cells keep their disclosure code.
- `metro_year_qcew_2021_2025.csv`: metro totals, industry shares, and suppressed-county counts.
- `model_panel.csv`: features at year t and growth outcome in year t+1. Suppressed metro shares remain blank here and are imputed with the training-fold median only inside the model pipeline.
- `model_comparison.csv`: held-out MAE (percentage points) and pooled R².
- `held_out_predictions.csv`: actual and predicted growth fractions for every held-out test.
- `heldout_permutation_importance.csv`: per-test-year permutation effects for tree models; units are changes in MAE percentage points, not coefficients or causal effects.

The raw industry slices contain the entire United States, but the derived files use only the counties in the nine selected metros. Files are public and exclude restricted Invest Atlanta records.
