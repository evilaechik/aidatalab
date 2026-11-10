# Expanded Fortune 500 model results

Run: November 9, 2026.

All 500 roster firms were collected; **498 covered firms** enter both HQ modeling tracks. The same 49 development metros, five whole-metro outer folds, nested inner tuning, predictors, seed and restricted grids were used as in the original experiment. Atlanta stayed out of fitting and model selection.

MAE is the average absolute HQ-count error on held-out development metros. RMSE penalizes large errors; Poisson deviance measures count fit. Lower is better. Counts refer to publisher-selected reported 2025 HQs.

## Every model's results

Atlanta observed **15 covered HQs**. A positive gap means observed exceeds expected; a negative gap means observed is below the benchmark.

| Model | OOF MAE | RMSE | Poisson deviance | Atlanta expected | Observed − expected |
| --- | ---: | ---: | ---: | ---: | ---: |
| A: employment baseline | 4.016 | 5.961 | 3.473 | 14.38 | +0.62 |
| A: mean-count baseline | 6.600 | 10.470 | 8.970 | 8.57 | +6.43 |
| A: regularized Poisson | 4.560 | 6.613 | 3.812 | 9.27 | +5.73 |
| A: count XGBoost | 4.578 | 8.741 | 5.034 | 9.80 | +5.20 |
| B: shared employment baseline | 4.016 | 5.961 | 3.473 | 14.38 | +0.62 |
| B: shared mean baseline | 6.600 | 10.470 | 8.970 | 8.57 | +6.43 |
| B: regularized logistic | 4.113 | 5.286 | 3.341 | 9.15 | +5.85 |
| B: probability XGBoost | 4.762 | 8.481 | 4.726 | 8.98 | +6.02 |
| B: logistic, main effects only | 4.183 | 5.368 | 3.283 | 9.16 | +5.84 |
| B: XGBoost, main effects only | 4.755 | 8.624 | 4.970 | 9.05 | +5.95 |

The two shared B baselines duplicate A's counts. Main-effects ablations are diagnostic and were excluded from the unchanged primary selection rule.

- **A: employment baseline:** The size-only reference scales HQ expectations with private employment. Its MAE matches the employment baseline.
- **A: mean-count baseline:** The average-count reference ignores differences between metros. Its MAE has more error than the employment baseline by 2.584 HQs per metro.
- **A: regularized Poisson:** Regularized regression uses all 31 regional factors to predict counts directly. Its MAE has more error than the employment baseline by 0.544 HQs per metro.
- **A: count XGBoost:** Shallow trees test nonlinear regional relationships. Its MAE has more error than the employment baseline by 0.561 HQs per metro.
- **B: shared employment baseline:** The same employment expectation is divided over 498 firms and summed back; counts match A exactly. Its MAE matches the employment baseline.
- **B: shared mean baseline:** The common event-rate baseline reproduces the average-count reference. Its MAE has more error than the employment baseline by 2.584 HQs per metro.
- **B: regularized logistic:** Regularized company probabilities use regional factors, company traits and four preset interactions. Its MAE has more error than the employment baseline by 0.097 HQs per metro.
- **B: probability XGBoost:** Shallow trees estimate company probabilities, then sum them into metro counts. Its MAE has more error than the employment baseline by 0.745 HQs per metro.
- **B: logistic, main effects only:** The logistic diagnostic removes the four explicit interactions. Its MAE has more error than the employment baseline by 0.167 HQs per metro.
- **B: XGBoost, main effects only:** The XGBoost diagnostic removes explicit interactions; trees can still learn interactions. Its MAE has more error than the employment baseline by 0.739 HQs per metro.

## Probability quality

| Company model | Log loss | Brier score | Mean probability | Observed rate |
| --- | ---: | ---: | ---: | ---: |
| B: shared employment baseline | 0.08153 | 0.01662 | 1.73% | 1.72% |
| B: shared mean baseline | 0.08721 | 0.01692 | 1.72% | 1.72% |
| B: regularized logistic | 0.08121 | 0.01658 | 1.64% | 1.72% |
| B: probability XGBoost | 0.08248 | 0.01675 | 1.45% | 1.72% |
| B: logistic, main effects only | 0.08173 | 0.01662 | 1.64% | 1.72% |
| B: XGBoost, main effects only | 0.08349 | 0.01680 | 1.45% | 1.72% |

Lower log loss and Brier score are better. Matching average rates alone does not establish calibration across individual risk levels; bins and diagnostic slopes are saved separately.

## Conclusions

- The frozen development rule selects **A: employment baseline**: MAE **4.016** (95% fixed-roster metro-bootstrap interval 2.881–5.336). This is a development selection score and does not account for selecting the best model.
- Its Atlanta expectation is **14.38** versus **15** observed: a gap of **+0.62 HQs (+4.3%)**. The heuristic 90% OOF-error band is **4.76–24.01** HQs.
- Atlanta meets or exceeds the selected model's expectation. The expanded cohort does not show an Atlanta total-HQ deficit against that benchmark.
- The added primary-model complexity does not beat the employment baseline on the frozen MAE rule.
- Best primary company-model MAE: 4.113; best aggregate MAE: 4.016. Company detail does not improve the best aggregate count benchmark on this measure.
- Company logistic regression has RMSE 5.286 versus employment's 5.961 (+11.3% reduction). Its log loss is 0.08121 versus 0.08153, and Brier score 0.01658 versus 0.01662. These secondary point comparisons show where company detail may help; they do not change the MAE-based selection or establish a reliable overall improvement.
- Across all reported specifications, Atlanta expectations range from 8.57 to 14.38 against 15 observed. These are related models using shared data, rather than independent confirmations.
- Including the preset interactions changes logistic MAE by -0.070 HQs versus main effects alone; negative values favor including them.
- Including the preset interactions changes xgboost MAE by +0.006 HQs versus main effects alone; negative values favor including them.
- Compare improvement over the employment baseline within each experiment. Raw errors from the 98-firm and 498-firm studies have different count scales; neither experiment is independent of the other.
- Only 49 development metro environments remain. Bootstrap intervals reuse fixed OOF predictions; the additional crossed company/metro intervals reflect roster composition and omit model refitting and selection uncertainty. Atlanta bands are heuristic prediction-error bands, not confidence intervals for expected counts.
- The two unresolved firms remain excluded. The Pittsburgh co-HQ remains scorecard sensitivity only. These results concern reported HQ points, not ordinary offices, local corporate employment, causal policy effects or potential recruits.

Training and reporting took 52.3 seconds. [Run details](TRAINING_RUN.md), [metrics](reports/training/model_comparison.csv), [Atlanta assessment](reports/training/atlanta_assessment.csv), [paired comparisons](reports/training/paired_mae_vs_employment.csv), and [original versus expanded](reports/training/original_vs_expanded.csv) contain supporting results.
