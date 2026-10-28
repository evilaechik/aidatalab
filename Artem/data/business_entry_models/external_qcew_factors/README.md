# External workforce and industry-factor model

This folder holds the no-entry-history XGBoost experiment. It predicts next-year Census BDS employer-establishment entry rate using prior-year BLS QCEW workforce/sector data, an employment-weighted Tax Foundation state corporate-tax measure, FHFA metro house-price growth, and BEA metro regional price parity. It deliberately excludes BDS entry-rate and exit-rate features.

## Files

- `external_factor_model_panel.csv` — model inputs, next-year outcome, and roster metadata.
- `top_100_msa_qcew_inputs.csv` — annual QCEW metro aggregates before the outcome merge.
- `county_qcew_input_rows.csv` — QCEW county/industry rows used to construct metro factors.
- `external_factor_model_comparison.csv` — rolling held-out XGBoost and historical-mean baseline result.
- `external_factor_held_out_predictions.csv` — each future-year prediction.
- `external_factor_permutation_importance.csv` — predictive associations only, not causal effects.
- `qcew_coverage_issues.csv` — intentionally excluded metro-years where historical county geometry does not match the Census 2023 delineation.
- `state_corporate_tax_rates_2017_2022.csv` — parsed annual state top statutory corporate-income-tax rates and gross-receipts-tax flags.
- `metro_macro_factors.csv` — year-t BEA all-items regional price parity and FHFA year-over-year house-price growth.
- `macro_feature_coverage.csv` — coverage check for the two macro features by input year.

## Sources

- Census BDS annual metro data: <https://www2.census.gov/programs-surveys/bds/tables/time-series/2023/bds2023_msa.csv>
- BLS QCEW, fourth-quarter industry extracts: <https://data.bls.gov/cew/data/api/>
- Census July 2023 CBSA delineation List 1: <https://www2.census.gov/programs-surveys/metro-micro/geographies/reference-files/2023/delineation-files/list1_2023.xlsx>
- Tax Foundation annual corporate-income-tax rate tables, 2017–2022 (the exact source URL is retained in the tax output).
- FHFA House Price Index master file: <https://www.fhfa.gov/hpi/download/monthly/hpi_master.csv>. We use fourth-quarter, traditional all-transactions MSA index growth. Where FHFA supplies metropolitan divisions rather than a parent-MSA index (including Atlanta), the script combines division growth with same-year QCEW employment weights.
- BEA Metropolitan Area Regional Price Parities (MARPP): <https://apps.bea.gov/regional/zip/MARPP.zip>. This is an all-items price-level index with the United States equal to 100; it is not an office-rent series.

Raw QCEW slices are shared with the earlier metro model under `Artem/data/nine_metro_models/raw_qcew_industry_slices/`.
