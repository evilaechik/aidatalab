# Source-Covered Metro Diagnostic

## What this is

This is a **restricted diagnostic**, not a U.S. Top-100 MSA result. It uses
only the 80 top-100 MSAs that have both:

- a row in the supplied Data Axle candidate-score export; and
- a complete 2022 public-factor row.

It excludes the 17 MSAs absent from the source export and Hartford,
Bridgeport, and New Haven, which lack a public-factor row. See
`Artem/FORTUNE100_NATIONAL_COVERAGE_AUDIT.md` for the excluded metros and
their coverage status.

## Stricter outcome screen

The original candidate count used a company-search label, which could admit
unrelated businesses with a similar name. This diagnostic rebuilds the score
with a stricter row-level identity rule:

1. The source headquarters or corporate-parent field must exactly match the
   queried/Fortune company after light legal-suffix normalization; **or**
2. The business name must exactly match and the source category must be
   `Branch` or `Headquarters`.

Explicit warehouse/distribution, shipping/mailing, retail/consumer, and kiosk
signals are then excluded. There is no substring matching.

The result has 66 MSAs with at least one high-confidence candidate and 14
with no such observed candidate. Those 14 zeros are **not verified zero-office
metros**; they mean the incomplete export produced no eligible
high-confidence candidate. The outcome remains a lower-confidence,
source-covered candidate proxy.

## Model comparison

All scores use five outer holdout folds. XGBoost parameters are selected in
three-fold CV inside each outer-training fold using 40 Optuna trials. OLS and
Ridge use the same outer folds; Ridge selection, feature scaling, and median
imputation are fitted on outer-training data only.

| Feature set | Model | Usable MSAs | MAE | Held-out R² |
| --- | --- | ---: | ---: | ---: |
| Context only | Tuned XGBoost | 80 | 2.730 | 0.633 |
| Context only | OLS | 80 | 3.723 | 0.392 |
| Context only | Nested Ridge | 80 | 3.642 | 0.403 |
| Context + housing + talent | Tuned XGBoost | 80 | 2.889 | 0.546 |
| Context + housing + talent | OLS | 80 | 3.967 | 0.339 |
| Context + housing + talent | Nested Ridge | 80 | 3.966 | 0.303 |

For this restricted proxy, the context-only XGBoost specification has the
best observed holdout score among the tested specifications. The housing and
talent version has a lower observed score, but this is not evidence that
housing or graduates do not matter: feature-set selection on a small,
iteratively analyzed sample has substantial uncertainty.

## Southern/Sunbelt comparison

The same high-confidence identity screen was run on the 99 source-covered
MSAs in the team's green-map state scope. This is a regional comparison set,
not a standard Census definition of the South or Sunbelt.

| Feature set | Model | Usable MSAs | MAE | Held-out R² |
| --- | --- | ---: | ---: | ---: |
| Context only | Tuned XGBoost | 99 | **2.709** | 0.492 |
| Context only | OLS | 99 | 3.041 | **0.528** |
| Context only | Nested Ridge | 99 | 2.971 | 0.513 |
| Context + housing + talent | Tuned XGBoost | 99 | 3.125 | 0.371 |
| Context + housing + talent | OLS | 99 | 3.197 | 0.466 |
| Context + housing + talent | Nested Ridge | 99 | 3.033 | 0.473 |

For the southern/sunbelt scope, XGBoost has the lowest average error in the
context-only run, while OLS has the highest held-out R². Ridge is close to
both. The models therefore do not identify a decisive single winner in this
regional sample. Adding the housing and talent proxies lowers the observed
holdout scores in these runs, but that is not a basis for rejecting those
factors or making a policy conclusion.

## Exploratory factor-importance shares

XGBoost does not have one set of linear coefficients. The table below reports
each factor's share of total **mean absolute SHAP value** across held-out
predictions. Shares sum to 100% within each model and show relative model
reliance, not causal effect size, direction, or a final policy weight.

| Context factor | Top-metro XGBoost (80) | Southern/Sunbelt XGBoost (99) |
| --- | ---: | ---: |
| House-price growth | 31.2% | 13.7% |
| Metro employment | 13.3% | 17.5% |
| Average weekly wage | 12.0% | 9.5% |
| Corporate tax rate | 7.5% | 16.8% |
| Finance-sector employment share | 2.6% | 12.0% |
| Professional-sector employment share | 6.8% | 4.0% |
| Employment growth | 1.9% | 5.4% |
| Regional price parity | 6.5% | 4.8% |
| Establishments per 100 jobs | 4.1% | 4.2% |
| Information-sector employment share | 4.9% | 4.1% |
| Manufacturing-sector employment share | 1.6% | 4.0% |
| Hospitality-sector employment share | 3.5% | 2.9% |
| Health-sector employment share | 3.7% | 0.8% |
| Gross-receipts-tax exposure | 0.3% | 0.4% |

For the Invest Atlanta-facing southern/sunbelt comparison, metro employment,
corporate tax rate, house-price growth, finance share, and wage are the most
used factors in this one XGBoost diagnostic. Together they account for 69.5%
of its SHAP importance. The ranks are unstable enough that they should be
treated as hypotheses to investigate, not final weights. Housing and
new-graduate measures are omitted from this table because they were not in
the context-only specification, not because the analysis disproved them.

## What can and cannot be concluded

The run confirms a limited technical point: XGBoost is strongest in the
80-MSA source-covered sample, but the regional sample has no decisive winner.
Model choice must therefore be evaluated separately for the chosen comparison
geography rather than assumed in advance.

The experiment also has model-selection uncertainty: the feature sets and
model families were compared after inspecting related results in a small
cross-section. Nested folds prevent parameter tuning from seeing its own test
fold, but they do not make the overall research process immune to iterative
selection. A decision-ready version needs a pre-specified factor set, a
source-verified office outcome, repeated nested CV with confidence intervals
for paired model differences, and a final untouched validation cohort.

It does **not** show which policy causes firms to locate in a metro. It cannot
be labeled a national comparison because the export omits specific regions,
contains only 86 matched Fortune 100 companies, and does not prove that
unobserved candidates are absent offices. SHAP ranks from this run are not
presentation findings.

## Reproducibility

The conservative score builder is
`Artem/scripts/build_source_covered_high_confidence_f100_scores.py`. It reads
licensed inputs and refuses to write its candidate-score output inside the
repository. The model runner is `Artem/scripts/run_fortune100_optuna_shap.py`.
