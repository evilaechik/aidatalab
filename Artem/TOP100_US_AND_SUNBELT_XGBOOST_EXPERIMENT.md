# Top-100 U.S. vs. Southern/Sunbelt Metro Experiment

> **Status update — do not use the national comparison for findings.** A
> follow-up audit found that the supplied Data Axle export has no raw location
> records for 14 of the 17 missing top-100 metros and includes only 86
> distinct matched current Fortune 100 companies. Some generic company-name
> searches also return unrelated businesses. The national results below are
> retained only as a record of the experiment; they are not a valid national
> benchmark. See `Artem/FORTUNE100_NATIONAL_COVERAGE_AUDIT.md`. A more
> conservative, source-covered sensitivity is in
> `Artem/SOURCE_COVERED_METRO_DIAGNOSTIC.md`.

## Purpose

Test whether the exploratory Fortune 100 candidate-location model behaves
similarly in two comparison groups:

1. **U.S. Top 100:** the 100 MSAs with the most 2023 employer establishments
   in Census Business Dynamics Statistics (BDS).
2. **Southern/Sunbelt Top 100:** the 100 largest eligible MSAs within the
   states selected on the team's green map: AL, AR, CO, DE, FL, GA, KS, KY, LA,
   MD, MS, MO, NM, NC, OK, SC, TN, TX, and VA.

The rosters overlap in 43 MSAs. The second group is therefore a focused
regional comparison set, not an independent replication sample and not a
standard Census-region definition of the South or Sunbelt.

## Outcome: important limitation

The attempted outcome was the number of distinct queried Fortune 100 company
labels with a **screened Data Axle candidate location** in an MSA. Warehouses,
distribution/fulfillment/logistics sites, retail/consumer locations, mailing
addresses, and similar non-office candidates were screened out.

This is **not a verified count of Fortune 100 offices**, and the supplied
export is neither a complete Fortune 100 universe nor a complete U.S.
geographic extract. A candidate can still be a branch or another non-HQ
worksite, and a missing score is unknown—not zero. The raw and location-level
derived data remain outside this repository because they are licensed.

Coverage used in the experiments:

| Scope | Roster MSAs | Candidate score available | Usable model rows |
| --- | ---: | ---: | ---: |
| U.S. Top 100 | 100 | 83 | 80 |
| Southern/Sunbelt Top 100 | 100 | 99 | 99 |

The three U.S. candidate-scored MSAs excluded for missing factor rows are
Hartford, Bridgeport, and New Haven. Seventeen U.S. Top-100 MSAs have no
candidate score, concentrated in California and the West; they were excluded,
not assigned a zero. The audit later showed this is a source-export coverage
failure, so the U.S. result is **retired**, not merely incomplete.

## Features tested

### Context features (2022)

- Metro employment, job growth, average weekly wage, establishments per 100
  jobs, and sector employment shares from BLS QCEW
- Employment-weighted state corporate income-tax rate and gross-receipts-tax
  exposure
- BEA regional price parity and FHFA house-price growth

### Added public features

- **Housing pipeline (2024):** Census Building Permits Survey units permitted
  per 1,000 QCEW jobs and multifamily share of permitted units.
- **Recent talent pipeline (2024):** IPEDS business/STEM bachelor’s-and-above
  completions per 1,000 QCEW jobs, allocated to the MSA of the reporting
  institution.

The talent measure is not graduate retention or employment, and the housing
measure is not office vacancy, commercial real estate availability, or a
permit-processing metric. Both are proxies.

Large-employer establishment counts from Census County Business Patterns were
compiled as a descriptive table only. They were deliberately excluded from
the model because they are too close to the Fortune-location outcome and would
leak the answer into the prediction.

## Method

- Compare a context-only feature set with context + housing + talent.
- Predict `log1p(candidate count)` with XGBoost, then convert predictions back
  to the candidate-count scale.
- Use five shuffled outer folds for holdout scoring. Within each outer-training
  fold, Optuna selects XGBoost parameters through three-fold CV (40 trials).
- Median imputation, scaling for linear models, and Ridge penalty selection are
  all fit within the relevant training folds.
- Report the same outer-fold test MSAs for tuned XGBoost, ordinary least
  squares (OLS), and nested Ridge. SHAP values describe XGBoost’s held-out
  predictions only.

This protects against basic tuning leakage, but it does not turn a small,
cross-sectional association into a causal estimate.

## Archived diagnostic results

`R²` is held-out explained variation; higher is better. MAE is the average
absolute error in screened candidate-company counts; lower is better.

| Scope | Feature set | Model | N | MAE | Held-out R² |
| --- | --- | --- | ---: | ---: | ---: |
| U.S. Top 100 | Context | Tuned XGBoost | 80 | 6.318 | 0.525 |
| U.S. Top 100 | Context + housing + talent | Tuned XGBoost | 80 | 5.963 | 0.593 |
| U.S. Top 100 | Context | OLS | 80 | 8.862 | 0.077 |
| U.S. Top 100 | Context + housing + talent | OLS | 80 | 9.526 | 0.032 |
| U.S. Top 100 | Context | Nested Ridge | 80 | 9.278 | 0.027 |
| U.S. Top 100 | Context + housing + talent | Nested Ridge | 80 | 9.233 | 0.028 |
| Southern/Sunbelt Top 100 | Context | Tuned XGBoost | 99 | 5.930 | 0.530 |
| Southern/Sunbelt Top 100 | Context + housing + talent | Tuned XGBoost | 99 | 6.140 | 0.481 |
| Southern/Sunbelt Top 100 | Context | OLS | 99 | 7.400 | 0.227 |
| Southern/Sunbelt Top 100 | Context + housing + talent | OLS | 99 | 7.936 | -0.015 |
| Southern/Sunbelt Top 100 | Context | Nested Ridge | 99 | 6.998 | 0.369 |
| Southern/Sunbelt Top 100 | Context + housing + talent | Nested Ridge | 99 | 7.661 | 0.106 |

## Interpretation of the diagnostic only

- The holdout scores demonstrate how to compare XGBoost, OLS, and Ridge with
  nested validation. They do **not** establish that XGBoost is useful for the
  intended Fortune-office question until the outcome is rebuilt.
- Housing/talent results should not be interpreted because the target has
  company-identity and geographic-coverage errors.
- SHAP ranks in these archived runs are not presentation findings. SHAP cannot
  repair an invalid outcome, and it never proves that a policy change causes
  more Fortune offices.

## What this means for Invest Atlanta

Do not use the current model to prioritize incentives or explain Atlanta’s
performance. The public feature tables remain useful, but the outcome must be
reconstructed before modeling.

The next defensible upgrade is a **source-verified Fortune 100 office-presence
outcome by MSA**, with a coded site type (office, HQ, R&D, manufacturing,
warehouse, retail). Start with a fresh company-by-company Data Axle extract
scoped to each MSA, verify the company identity with corporate-parent/brand
fields, and keep an explicit zero row only after a completed query yields no
eligible sites. Then add variables that Invest Atlanta can more directly
influence or track, such as transit access to job centers, office vacancy and
asking rents, site readiness, incentive terms, and worker commute patterns.

## Public-source links

- [Census Business Dynamics Statistics](https://www.census.gov/programs-surveys/bds.html)
- [BLS Quarterly Census of Employment and Wages](https://www.bls.gov/cew/)
- [FHFA House Price Index](https://www.fhfa.gov/data/hpi/datasets?tab=additional-data)
- [BEA Regional Price Parities](https://www.bea.gov/data/prices-inflation/regional-price-parities)
- [Census Building Permits Survey](https://www.census.gov/construction/bps/index.html)
- [IPEDS complete data files](https://nces.ed.gov/ipeds/use-the-data)
- [Census County Business Patterns](https://www.census.gov/data/datasets/2023/econ/cbp/2023-cbp.html)

## Reproducibility

Public input tables added for the U.S. Top-100 roster:

- `Artem/data/business_entry_models/top100_xgboost/actionable_housing_features_2024.csv`
- `Artem/data/business_entry_models/top100_xgboost/actionable_talent_features_2024.csv`
- `Artem/data/business_entry_models/top100_xgboost/descriptive_business_ecosystem_2023.csv`

The model script is `Artem/scripts/run_fortune100_optuna_shap.py`. Licensed
candidate-score inputs and model outputs are intentionally stored outside the
repository.
