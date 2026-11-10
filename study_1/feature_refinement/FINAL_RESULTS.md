# Feature-refinement model results

Run: November 10, 2026. R0 is the unchanged expanded-cohort reference; R1 adds three general regional features. The same 498 HQ firms and 49 development metros are used.

MAE is average absolute HQ-count error; RMSE penalizes large errors; lower is better. Atlanta observed 15 HQs. Positive observed-minus-expected gaps mean the count exceeds the benchmark.

| Model | R0 MAE | R1 MAE | Change | R0 RMSE | R1 RMSE | R0 Atlanta expected | R1 Atlanta expected | R1 Atlanta gap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A: employment baseline | 4.016 | 4.016 | +0.000 | 5.961 | 5.961 | 14.38 | 14.38 | +0.62 |
| A: mean-count baseline | 6.600 | 6.600 | +0.000 | 10.470 | 10.470 | 8.57 | 8.57 | +6.43 |
| A: regularized Poisson | 4.560 | 4.220 | -0.340 | 6.613 | 6.051 | 9.27 | 9.14 | +5.86 |
| A: count XGBoost | 4.578 | 4.206 | -0.372 | 8.741 | 8.381 | 9.80 | 11.98 | +3.02 |
| B: shared employment baseline | 4.016 | 4.016 | +0.000 | 5.961 | 5.961 | 14.38 | 14.38 | +0.62 |
| B: shared mean baseline | 6.600 | 6.600 | +0.000 | 10.470 | 10.470 | 8.57 | 8.57 | +6.43 |
| B: regularized logistic | 4.113 | 3.564 | -0.549 | 5.286 | 4.697 | 9.15 | 9.17 | +5.83 |
| B: probability XGBoost | 4.762 | 4.465 | -0.297 | 8.481 | 8.220 | 8.98 | 9.68 | +5.32 |
| B: logistic, main effects only | 4.183 | 3.634 | -0.549 | 5.368 | 4.840 | 9.16 | 9.24 | +5.76 |
| B: XGBoost, main effects only | 4.755 | 4.444 | -0.311 | 8.624 | 8.365 | 9.05 | 10.74 | +4.26 |

The two B baselines duplicate A after dividing/summing over 498 firms. Main-effects-only fits are diagnostic and are excluded from primary model selection.

## What each model means

- **A: employment baseline:** Scales expected HQs with private employment; ignores the new feature bundle. R1 changes MAE by +0.000 HQs per metro; the paired 95% fixed-prediction interval is +0.000 to +0.000.
- **A: mean-count baseline:** Uses the training-metro average count; ignores differences in metro conditions. R1 changes MAE by +0.000 HQs per metro; the paired 95% fixed-prediction interval is +0.000 to +0.000.
- **A: regularized Poisson:** Tests whether the regional factors improve direct HQ-count prediction. R1 changes MAE by -0.340 HQs per metro; the paired 95% fixed-prediction interval is -0.899 to +0.214.
- **A: count XGBoost:** Tests shallow nonlinear relationships among the regional factors. R1 changes MAE by -0.372 HQs per metro; the paired 95% fixed-prediction interval is -0.829 to +0.060.
- **B: shared employment baseline:** Expresses the shared employment expectation as 498 equal company probabilities. R1 changes MAE by +0.000 HQs per metro; the paired 95% fixed-prediction interval is +0.000 to +0.000.
- **B: shared mean baseline:** Expresses the shared mean-count expectation as 498 equal company probabilities. R1 changes MAE by +0.000 HQs per metro; the paired 95% fixed-prediction interval is +0.000 to +0.000.
- **B: regularized logistic:** Uses company attributes and regional conditions to estimate company probabilities, then sums them. R1 changes MAE by -0.549 HQs per metro; the paired 95% fixed-prediction interval is -0.914 to -0.224.
- **B: probability XGBoost:** Tests shallow nonlinear company–metro probability relationships, then sums them. R1 changes MAE by -0.297 HQs per metro; the paired 95% fixed-prediction interval is -0.579 to -0.021.
- **B: logistic, main effects only:** Removes the four preset company–metro interactions from logistic regression. R1 changes MAE by -0.549 HQs per metro; the paired 95% fixed-prediction interval is -0.900 to -0.229.
- **B: XGBoost, main effects only:** Removes explicit interaction columns; trees can still represent interactions. R1 changes MAE by -0.311 HQs per metro; the paired 95% fixed-prediction interval is -0.631 to +0.010.

## Conclusions

- The frozen primary rule selects **R1 / B: regularized logistic**, with OOF MAE **3.564** versus employment baseline **4.016**.
- Its Atlanta expectation is **9.17** versus **15** observed, a gap of **+5.83 HQs**. Its heuristic 90% prediction-error band is **1.32–17.02**.
- Atlanta does not fall below the selected expectation; this run does not identify an overall HQ deficit.
- The three-feature bundle reduces logistic MAE by **13.3% versus the previous logistic model**, and by **11.3% versus the employment baseline**. RMSE falls by **11.1%** versus the previous logistic model and **21.2%** versus employment. This is a useful predictive improvement in this experiment.
- The paired logistic improvement versus R0 is **−0.549 HQs per metro**, with a 95% fixed-prediction interval of **−0.914 to −0.224**; 32 of 49 metros improve. Against the employment baseline, the difference is **−0.452**, with a wider interval of **−1.479 to +0.460**. Thus the evidence is clearer for improving the old logistic model than for reliably beating the simple baseline.
- Extra **feature detail** helped; extra **tree-model complexity** did not win. All six fitted R1 variants improve their MAE point estimates over R0, but both primary XGBoost models still have more count error than the employment baseline. The simple regularized company model is the preferred fitted model.
- The main-effects logistic model already reaches MAE **3.634**. Adding the four existing interactions reduces this to **3.564**, a further **0.070** HQs per metro. The new bundle's roughly **0.549** improvement occurs with and without those interactions. No additional industry-specific interaction was introduced.
- Atlanta's 15 observed HQs fall **inside** the selected model's 1.32–17.02 error band. The positive point gap does not establish exceptional performance beyond model error, and it is not a count of recruitable or missing firms.
- Paired intervals compare R1 with the corresponding R0 model on identical held-out metros. They are descriptive, reuse fixed OOF predictions, and omit model-refitting and selection uncertainty.
- No model or feature was selected from its Atlanta result. Atlanta has been inspected in prior work, so this remains a follow-up rather than an analyst-blind test.

## Probability quality

| Company model | R0 log loss | R1 log loss | R0 Brier | R1 Brier |
| --- | ---: | ---: | ---: | ---: |
| B: shared employment baseline | 0.08153 | 0.08153 | 0.01662 | 0.01662 |
| B: shared mean baseline | 0.08721 | 0.08721 | 0.01692 | 0.01692 |
| B: regularized logistic | 0.08121 | 0.08036 | 0.01658 | 0.01655 |
| B: probability XGBoost | 0.08248 | 0.08208 | 0.01675 | 0.01673 |
| B: logistic, main effects only | 0.08173 | 0.08082 | 0.01662 | 0.01660 |
| B: XGBoost, main effects only | 0.08349 | 0.08304 | 0.01680 | 0.01678 |

The selected logistic model also reduces count Poisson deviance from **3.341 to 2.462**, against the employment baseline's **3.473**. Its individual-company probability improvements are smaller: log loss moves from about 0.08121 to 0.08036 and Brier score from 0.016579 to 0.016546. Its average held-out probability remains below the observed event rate; these scores do not establish perfect calibration.

## Scope and next steps

The bundle was tested jointly, so this run does not identify how much each of its three factors contributed individually. The retained coefficient table is an association diagnostic from the final fit, not an out-of-sample feature-ablation experiment or evidence that changing any factor would attract firms. Management-sector employment can also reflect existing corporate activity, rather than an independent policy lever.

The selected model's Atlanta sector diagnostics still show zero covered HQs in Technology against an expectation of about **1.40**, and zero in Health Care against about **0.85**. These are small, uncertain sector-level leads rather than established deficits. Transportation has 3 observed against about 0.27 expected. This reinforces the importance of industry mix and the need to verify classifications, comparable metros and observations over time before making sector-specific conclusions. These diagnostic counts are not evidence that ordinary offices or local employment are absent.

The new inputs are CBP 2023 corporate-management employment share and BDS 2023 all-industry establishment entry/exit rates. Geography passed the documented July 2023 gate, including Connecticut and the Providence statewide-code exception. The source metrics are regional activity proxies, not office openings, attraction effects or assigned Fortune-company jobs.

Only 49 development metro environments remain. The office collection has positives and unknowns, and does not support a presence classifier or office-gap rankings. Weighted scoring and bespoke tech/healthcare outcomes remain deferred. SHAP values or coefficients would describe associations, not effects of changing a factor.

This is a retrospective spatial benchmark, not an as-of-2025 forecast or a prediction of future relocations. The economic reference years, publication dates and revision vintages differ; the original predictors already include later releases. Whole-metro holdouts test transfer across the selected metros, not stability across future years.

Use the retained company-function evidence to verify sector/function leads and improve comparable dated office coverage. Any later broader-outcome benchmark needs a separately specified target and must exclude features that mechanically reconstruct it.

New fitting and reporting took 54.0 seconds. R0 was reused after hash/version checks; its models were not retrained. See [README.md](README.md), [VALIDATION.md](VALIDATION.md), [all metrics](reports/training/model_comparison.csv), [paired differences](reports/training/paired_r1_vs_r0.csv), and [Atlanta assessment](reports/training/atlanta_assessment.csv).
