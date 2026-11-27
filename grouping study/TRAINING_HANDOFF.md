# Training handoff

Protocol version 1.0 · November 25, 2026 · **Future implementation instructions; no code or run exists yet.**

## Objective and starting point

Implement the Atlanta-focused company–metro HQ study described in [STUDY_DESIGN.md](STUDY_DESIGN.md), using only inputs allowed by [DATA_CONTRACT.md](DATA_CONTRACT.md). Preserve all existing Study 1/Artem artifacts. New code, configurations, matrices, models, and reports belong under `grouping study/` when an execution task is undertaken.

The primary estimator is a regularized global company logistic probability blended with a company-and-metro kernel probability. This is a local predictive benchmark. Do not substitute fixed clusters, a metro-only regression, case-only actual-office rows, or a causal matching estimator.

## Models and references

| ID | Specification | Role |
| --- | --- | --- |
| `EMP` | Training-fold HQ total / private-job total, multiplied by query employment; divide expected count by 498 for equal company probabilities | Transparent scale baseline, eligible reference. |
| `R1_GLOBAL` | Existing R1 `B_logistic`, tuned by the original equal-metro rule; unchanged stored OOF predictions | Historical performance reference, eligible reference. |
| `FOCUS_GLOBAL` | Same R1 regression and C grid, tuned by the new Atlanta-focused validation rule | Control for the change in tuning population, eligible reference. |
| `GROUPED` | Same regression plus the exact soft row-kernel blend; jointly tune C and neighborhood/blend parameters | Primary new procedure, eligible challenger. |

All four must return 498 probabilities for every evaluation metro and a reconciled metro count. `EMP` and `R1_GLOBAL` do not acquire new tuning parameters. Check baseline probabilities are in [0,1]; if the employment baseline is invalid in a split, report it ineligible for probability comparison rather than silently clipping or modifying the count.

An unblended `p_local` may be saved as a diagnostic of smoothing behavior, but is not an additional eligible model. No XGBoost, new sector interaction, calibration model, feature-search loop, feasibility penalty, or alternative outcome is required.

## Fixed environment and search

Use Python 3.12 and the package versions recorded by the existing completed run. Portable requirements are in `study_1/requirements-training.txt`; read actual versions from the R1 run metadata and verify compatibility. Do not silently upgrade serialized-model dependencies. Use one CPU thread. Seed: `20261125`; bootstrap replicates: 2,000.

The regression uses the inherited R1 42-column allowlist. Numeric preprocessing: median imputation, added missing indicators, and `StandardScaler`; categorical preprocessing: training-fold `OneHotEncoder(handle_unknown='ignore')`. Use L2 logistic regression, intercept enabled, solver `lbfgs`, `max_iter=1500`, `tol=1e-8`, `class_weight=None`. Preserve all labels and natural prevalence. Do not fit a calibration correction.

Freeze the following candidate sets:

- C: `{0.01, 0.1, 1.0}` in that order.
- Regional bandwidth rank `k_m`: `{5, 10, 20}`.
- Company bandwidth rank `k_c`: `{25, 75, 150}`.
- Blend `alpha`: `{0, 0.25, 0.5, 0.75}`.

`FOCUS_GLOBAL` has three candidates. `GROUPED` has 84 distinct candidates: three C-only alpha-zero cases, plus 3 C × 3 regional ranks × 3 company ranks × 3 positive alpha cases. Do not duplicate the alpha-zero case for every bandwidth. `k` values set adaptive Gaussian bandwidths rather than hard exclusions. All ranks are feasible within the supplied nested fold sizes; verify that before fitting.

This small fixed grid is a pragmatic starting design, not proof that these are optimal values. Do not expand it after seeing an Atlanta gap or outer-fold results.

## Support fallback

Use the label-independent local-support rule from [VALIDATION.md](VALIDATION.md) in every inner, outer, and final prediction. If the query has effective regional donors below 10 or effective company donors below 25, set its effective alpha to zero and return the candidate's global regression probability. Retain the requested alpha, reason, and support metrics. This is part of the estimator, not a discretionary adjustment made after observing errors.

Never widen a neighborhood or omit a metro because its HQ target makes a result inconvenient. Outcome-based positive-support summaries are reporting diagnostics only, not an extra target-dependent grouping rule.

## Nested execution algorithm

Use the existing five whole-MSA development fold assignments without reshuffling. Atlanta labels are excluded throughout. Atlanta covariates can define the evaluation focus as specified. The 49-metro development set is the complete donor universe; an outer training set has 39 or 40 metros, and inner training uses only its remaining folds.

For each outer fold:

1. Separate outer training and outer validation by CBSA. All company rows of a held-out metro remain together. Verify no Atlanta rows are in either set.
2. For each inner fold within outer training, fit regression and distance preprocessing only on inner training. Fit one global logistic model per C. Produce its predictions on inner validation and cache them.
3. Build inner-training company and metro distance representations. Compute donor weights and local probabilities for inner-validation queries. Donor labels contain no rows from the inner-validation metro set. Cache weight matrices by bandwidth rank; use stable, vectorized matrix operations rather than fitting 498 separate regressions.
4. Compute common inner validation focus weights from the inner-training transform and rank-10 Atlanta reference bandwidth. Score each `FOCUS_GLOBAL` or `GROUPED` candidate by pooled focus-weighted count MAE across the available inner-held-out metros. Normalize the raw focus weights once across this pooled set. Compute the secondary criteria on the same weights.
5. Select each procedure's settings using the tie rule below. The group candidate's C and locality settings are chosen jointly from these inner scores. Do not first tune a global model using inner-validation labels and then claim its already-tuned inner predictions are independent evidence for additional tuning.
6. Refit the selected global component and distance preprocessing on all outer training. Predict all 498 firms in every outer-validation metro; apply the same support fallback. Save predictions, counts, donor/support diagnostics, tuning scores, and common outer focus weights.
7. Fit/predict `EMP` using outer training only. Join the unchanged `R1_GLOBAL` OOF reference predictions on exact keys and verify labels/folds. These references must be evaluated on exactly the same held-out rows and focus weights.

Each metro supplies one outer prediction per eligible procedure; no second split of its company rows is allowed. A known company can appear in training in other metros, which is intentional for this fixed-roster task. It is not validation on unseen companies.

Cache preprocessing and predictions across candidates. The 84 blends mostly reuse three global fits and nine local distance combinations per inner split. Do not rebuild source data or retrain the old R0 models. Verify any imported Study 1 helper is free of writes on import; do not invoke its legacy main entry point.

## Scores and deterministic selection

Primary candidate score: Atlanta-focus weighted metro-count MAE. Secondary: focus-weighted company log loss, averaged over the same 498 firms per metro. Then prefer smaller alpha, larger `k_m`, larger `k_c`, and smaller C, in that order. Omit inapplicable bandwidth criteria for alpha-zero or global-only candidates. Treat score differences smaller than `1e-10` as ties; compare at full stored precision.

After all outer predictions are frozen, compare `EMP`, `R1_GLOBAL`, `FOCUS_GLOBAL`, and the **nested `GROUPED` procedure**, using common outer focus weights and the same MAE/log-loss rule. Final exact family ties prefer `EMP`, `R1_GLOBAL`, `FOCUS_GLOBAL`, then `GROUPED`. Report this as development selection; selecting the best outer score introduces winner-selection uncertainty.

The effect attributable to grouping is the paired `GROUPED` versus `FOCUS_GLOBAL` comparison. Improvement only versus `R1_GLOBAL` may instead reflect tuning for Atlanta-like metros. `GROUPED` is a full tuning procedure; outer folds need not choose identical settings. Report how often it selected alpha zero and how often support fallback occurred.

Use all-metro equal-weight scores as secondary diagnostics, not the selection objective. Poor predictions for unrelated metros do not automatically disqualify an Atlanta-focused model, but all failures and results remain auditable.

## Final fit and Atlanta assessment

1. Freeze the selected procedure, outer comparison, support qualifications, protocol/input hashes, and interpretation rules before reading Atlanta outcome objects for modeled assessment.
2. For a selected `FOCUS_GLOBAL` or `GROUPED` procedure, repeat inner candidate evaluation using all five supplied folds across the 49 development metros and the same focus rule. Freeze settings and fit the final global component and distance transforms on all 49 metros.
3. If `R1_GLOBAL` is selected, use its unchanged final saved model after compatibility checks; if `EMP`, use all 49 development metros for its rate. Also generate final Atlanta comparison predictions for all four prespecified procedures, with no subsequent reselection.
4. Produce 498 Atlanta probabilities, requested/effective alphas, support statistics, and donor explanations. Sum probabilities into expected HQ and sector counts. Do not force expected totals to 15 or per-firm geography probabilities to sum to one.
5. Only then join observed Atlanta labels and report observed minus expected. This preserves fitting boundaries but does not make Atlanta analyst-blind: its previous results are already known.
6. Run the prespecified sensitivities and uncertainty summaries. They qualify the result; they do not choose a replacement winner.

If final target support is weak, label the local result unsupported or inconclusive and show the global fallback. Do not claim that a selected blend was used locally when its effective alpha is zero.

## Implementation deliverables

Future entry points should cover preparation, fitting/reporting, and saved-artifact verification. Record their actual filenames in a later run guide; do not document nonexistent scripts as runnable commands today. Prefer small reusable functions for distances, kernel predictions, scores, and split orchestration.

Create future machine-readable configuration with the complete outcome, feature, distance, grid, focus-weight, fallback, seed, split, and selection rules above. Include the input and code hashes. Log every attempted candidate and failure; do not omit unfavorable specifications.

Required future artifacts:

| Location / artifact | Contents |
| --- | --- |
| `config/` | Frozen execution contract, exact feature lists, grids, input hashes, and final selection. |
| `tables/` | Unique company/metro input views, split membership, predictor-only Atlanta view, separately stored assessment labels. |
| `reports/tuning_scores.csv` | Inner split/context, candidate parameters, scores, support/fallback counts, failures, selected flags. |
| `reports/oof_company_probabilities.csv` | Procedure, fold, company ID, CBSA, observed label, probability, focus weight, support/fallback fields. |
| `reports/oof_metro_predictions.csv` | Procedure/fold/CBSA, observed and summed expected counts, residuals, raw/common focus weights. |
| `reports/model_comparison.csv` | Local and all-metro count/probability scores for all procedures. |
| `reports/paired_comparisons.csv` | Grouped versus focus-global, R1, and employment, including uncertainty and affected-metro diagnostics. |
| `reports/atlanta_company_predictions.csv` | All 498 company probabilities and observed labels, sector, support, and effective alpha. |
| `reports/atlanta_assessment.csv` | All four expected counts, observed 15, gaps, heuristic error summaries, and support status. |
| `reports/atlanta_donor_metros.csv`, `reports/atlanta_donor_companies.csv` | Distances, normalized kernel weights, ranks, blocks, and evidence of low-weight donor treatment. |
| `reports/atlanta_top_donor_rows.csv` | Top 20 company–metro weights per Atlanta query; report omitted weight mass. |
| `reports/support.csv`, `reports/sensitivities.csv` | Effective donors, concentration, lack of support, and fixed sensitivity outputs. |
| `models/` | Final global pipeline, fitted distance transforms, normalized training donor views/labels, parameters and hashes needed to reproduce predictions. |
| `reports/run_metadata.json`, validation reports | Environment, seeds, runtime, source/code hashes, acceptance results, and actual artifact inventory. |
| `FINAL_RESULTS.md`, `RUN_GUIDE.md` | Future results and instructions describing the actual implementation. Do not create empty results claims now. |

Complete [VALIDATION.md](VALIDATION.md) before declaring execution successful. A weaker or unsupported grouped result is a valid scientific completion.
