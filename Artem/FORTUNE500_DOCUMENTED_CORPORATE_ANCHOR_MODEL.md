# Fortune 500 Documented Corporate-Anchor Model

Updated: 2026-11-19

## Purpose

This rerun expands the earlier **listed global-HQ** outcome with the project's
new direct-company-source evidence of Fortune 500 regional, divisional,
subsidiary, and additional corporate headquarters. It answers a narrower,
more useful sensitivity question:

> Do the same cross-metro factors explain the count of listed global HQs plus
> currently documented non-global corporate anchors?

It is **not** a score of every office in each metro and is not a causal estimate
of what an Invest Atlanta incentive would change.

## Outcome construction

The 200-MSA outcome starts with Fortune 2025's complete listed-global-HQ field,
then adds only a regional/divisional record when all of the following are true:

1. The site is explicitly an additional corporate HQ, regional HQ, division HQ,
   business-unit HQ, or subsidiary HQ;
2. The evidence is direct company or investor-relations material;
3. The parent company has not already been counted as a listed global HQ in the
   same MSA; and
4. Multiple sites from the same Fortune parent in one MSA are deduplicated.

Two labelled evidence exceptions that still need direct company confirmation
are retained in the research file but excluded from the model target.

| Inventory | Count |
| --- | ---: |
| Fortune 500 listed global-HQ anchors in the 200-MSA roster | 463 |
| Direct-source regional/divisional parent-company × MSA pairs added | 75 |
| Combined documented corporate-anchor count | 538 |
| Top-100 MSA regional/divisional pairs added | 68 |
| Top-100 MSAs with at least one such addition | 35 |

The direct-source evidence file has 77 eligible pairs overall; two are outside
the current 200-MSA roster. The full 500-company coverage tracker remains
important: an MSA with zero documented regional/divisional records has a true
zero for the global-HQ component, but an **unknown/not-yet-documented** value
for the regional component.

## Model design

- **Cohort:** 97 of the top 100 MSAs; Hartford, Bridgeport-Stamford, and New
  Haven lack the selected 2022 factor row.
- **Predictors:** 2022 QCEW employment, employment growth, wage, establishment
  density, sector mix, state tax context, regional price parity, and housing
  price growth.
- **Evaluation:** five outer held-out folds. Inside each training fold, Optuna
  selects a regularized Poisson XGBoost specification over 25 trials. The
  untouched held-out metros supply every reported metric and permutation test.
- **Comparison:** exact same cohort, features, seed, and evaluation as the
  global-HQ-only recheck.

## Results

Lower MAE/RMSE is better. R² is the share of held-out variation captured
relative to the held-out mean; it is not a causal claim.

| Outcome and model | Held-out MAE | Held-out RMSE | Held-out R² |
| --- | ---: | ---: | ---: |
| Global HQ only — mean baseline | 5.074 | 8.132 | -0.018 |
| Global HQ only — nested XGBoost | **2.673** | 6.123 | 0.423 |
| Global + documented regional/divisional — mean baseline | 5.849 | 9.078 | -0.030 |
| Global + documented regional/divisional — nested XGBoost | **2.941** | 6.385 | 0.491 |

The expanded target has a higher raw error because its average count is higher.
Relative to its own mean baseline, nested XGBoost reduces MAE by **49.7%**;
the global-only version reduces MAE by **47.3%**. This is modest evidence that
the expanded, documented target is usable as a sensitivity analysis—not proof
that it is a complete regional-HQ model.

## Factor findings

Out-of-fold permutation importance shows how much test error rose when one
feature was shuffled. It does not establish direction or causality.

| Factor | Increase in held-out MAE when shuffled |
| --- | ---: |
| Log QCEW employment | 1.799 |
| Average weekly wage | 0.332 |
| Establishments per 100 jobs | 0.012 |
| Employment growth | 0.005 |
| Professional-services employment share | 0.005 |

The clear pattern is metro **scale** first, with wages a distant second. The
remaining measured features have near-zero incremental importance in this
small cross-section. Do not translate these numbers into policy “weights” or
claim that changing a tax rate, wage, or office supply would produce the same
change in corporate anchors.

## Atlanta readout

Atlanta's documented corporate-anchor count is **18**: 15 Fortune listed
global HQs plus three direct-source regional/divisional parent-company × MSA
pairs (CarMax, Comcast, and Kroger). Comcast's two documented sites are one
parent-company × MSA pair. The held-out nested XGBoost prediction was 10.04,
versus a 4.44 mean-baseline prediction. That underprediction is a useful
warning: Atlanta has attributes not fully represented by this generic public
feature set; it is not evidence that Atlanta is underperforming.

Suburban sites count for the **Atlanta MSA** measure but must not be described
as City of Atlanta corporate locations. City-versus-metro capture should be a
separate analysis using municipal boundaries.

## Files and rerun

- `data/big_business_presence/fortune500_documented_corporate_anchor_msa_outcome_2026.csv`
- `data/big_business_presence/fortune500_documented_corporate_anchor_xgb_2026/`
- `data/big_business_presence/fortune500_global_hq_xgb_recheck_2026/`
- `scripts/build_fortune500_documented_corporate_anchor_outcome.py`
- `scripts/run_fortune500_global_hq_xgboost.py`

```bash
python3 Artem/scripts/build_fortune500_documented_corporate_anchor_outcome.py

python3 Artem/scripts/run_fortune500_global_hq_xgboost.py \
  --outcome-csv Artem/data/big_business_presence/fortune500_documented_corporate_anchor_msa_outcome_2026.csv \
  --target-column documented_corporate_anchor_count \
  --outcome-description 'Complete global-HQ count plus documented regional/divisional evidence; sensitivity analysis, not a complete office census.' \
  --output-prefix fortune500_documented_corporate_anchor_xgb \
  --output-dir Artem/data/big_business_presence/fortune500_documented_corporate_anchor_xgb_2026 \
  --optuna-trials 25
```

The direct-source regional/divisional records and their public source links are
in `data/big_business_presence/fortune500_verified_regional_divisional_sites_2026.csv`.
