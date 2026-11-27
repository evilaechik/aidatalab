# Reporting, sensitivity, and interpretation

Protocol version 1.0 · November 25, 2026 · **Report requirements, not new findings.**

## Atlanta is the presentation target

The main report should answer whether the grouping procedure provides a better-supported Atlanta benchmark, which comparisons it relies on, and whether the conclusion is stable. Other metros serve as donors and validation cases. Do not create a national leaderboard or claim that every metro must be predicted equally well.

Nevertheless, retain all outer prediction/error rows and failures. The primary Atlanta-focused evaluation must not be retrospectively restricted to markets with favorable errors. Explicitly distinguish the user-authorized local objective from the equal-metro objective used by the previous study.

## Required final report structure

1. **Scope/status:** actual execution date, protocol/version, target, roster, geography, source periods, and any deviations. State that this is a reported-HQ stock benchmark and that office fitting remains gated.
2. **What changed:** economic dimensions, company similarity, soft donor weights, global blend, and focused validation. State that ordinary scaling was already handled in Study 1.
3. **Validation table:** `EMP`, unchanged `R1_GLOBAL`, `FOCUS_GLOBAL`, nested `GROUPED`; show local count MAE, RMSE, company log loss/Brier, all-metro diagnostic MAE, paired intervals, and effective validation metros.
4. **Attribution:** compare grouping with `FOCUS_GLOBAL` as well as the historical R1. Distinguish benefit from Atlanta-focused tuning, locality, and any change in C. Show outer settings and fallback frequencies.
5. **Atlanta table:** observed 15, expected count from all four final procedures, observed-minus-expected, heuristic error band, effective donors, and requested/effective alpha. Name the procedure selected without Atlanta outcomes, even if another produces a more appealing Atlanta story.
6. **Company/sector view:** all 498 company probabilities and their uncertainty qualifications; sector sums/counts with roster classifications. Do not threshold probabilities to count expected HQs.
7. **Donor explanation:** highest-weight metros, similar companies, and top 20 company–metro donor rows for each Atlanta company, with omitted weight mass. Distinguish input-similarity weights from fitted feature importance or causal contributions. For positive labels, show `weight * training_HQ_label` separately if explaining the local numerator.
8. **Stability/support:** predefined sensitivities, effective support, extrapolation warnings, and how often reasonable changes alter the interpretation.
9. **Conclusion/limits:** grouping helped, did not help, or remains inconclusive. Identify what collection or future untouched evidence would resolve the limitations, without turning the study into an open-ended model search.

Do not create `FINAL_RESULTS.md` during documentation preparation. An implementing agent should write it only with real results, actual checks, and artifact references.

## Prespecified diagnostic sensitivities

Freeze the primary result and final hyperparameters before these diagnostics. They do not select a new winner. Keep Atlanta labels out of all fitting.

| Diagnostic | Exact procedure | What it checks |
| --- | --- | --- |
| New York influence | Remove CBSA `35620` from final development donors; refit transformations/global components with fixed final hyperparameters, and predict Atlanta again for each fitted method. Separately repeat the nested-selected GROUPED and FOCUS_GLOBAL outer fits with their already-selected outer settings, removing New York from training whenever present. Keep the original test rows; compare errors on the same 48 non-New-York test metros using the original focus weights. | Influence on Atlanta and comparable predictions, rather than deletion from scoring alone. For EMP refit its exposure rate; R1's sensitivity is a new fixed-settings fit, not the untouched original model. |
| Individual donor influence | For GROUPED's final selected settings, remove each of the 49 donor metros once, refit global/distance components, and predict Atlanta. No retuning. | Whether one donor determines the Atlanta total or company pattern. |
| Dimension dependence | Remove one of the five regional distance blocks at a time, equally reweight the remaining four, refit distance transforms and recalculate kernels at frozen settings. Keep regression inputs/global fit unchanged. Do not redefine the primary evaluation focus. | Dependence of the grouped Atlanta estimate on a particular similarity dimension. |
| Wider/narrower neighborhoods | At frozen C/alpha, substitute each of the 3×3 prespecified bandwidth pairs for the final prediction, leaving other rules unchanged. Apply the same support fallback. | Sensitivity to neighborhood width without choosing whichever gives a preferred Atlanta gap. |

For each variant save expected count, delta versus primary, company/sector changes, support/fallback, and top donor changes. For New York, explicitly separate effects through the global component, distance scaling/bandwidths, and local donor labels where feasible. A low direct local weight does not prove that New York has zero indirect influence on the global model or scaling.

For dimension dependence report top-10 donor-metro overlap and rank changes as descriptive stability measures. Top-10 is an explanation cutoff, not a hidden prediction cutoff. If a procedure's primary alpha is zero, state that distance diagnostics cannot establish a grouping benefit for that fit.

New York is not automatically an invalid observation, and size is not automatically an economic nuisance. A failed large-market prediction can be acceptable outside the focal target, but must remain visible. Do not claim improved national accuracy by excluding its test error.

## Statements the evidence can support

- A particular input-defined neighborhood improves—or fails to improve—held-out performance weighted toward Atlanta-like regional conditions.
- The fitted benchmark expects a particular HQ count for the fixed covered roster, with the stated heuristic error and stability qualifications.
- Certain company/sector comparisons warrant source verification or later investigation.

Atlanta observed-minus-expected above zero means more selected HQs than the point benchmark, not a shortfall. Below zero is a descriptive negative residual, not a verified market opportunity. Either sign can fall within substantial model error. Model expectations are not ideal targets.

## Statements this study cannot support

- That similarity establishes a causal effect of taxes, housing, workforce programs, or incentives.
- That a company probability is its chance of accepting an Atlanta offer or relocating in the future.
- That an HQ zero establishes absence of an office, R&D function, local jobs, or additional HQ.
- That a suburban HQ is a City of Atlanta program win, or that an MSA residual measures municipal policy effectiveness.
- That company rows or overlapping donor groups are independent regional environments.
- That uncertainty from fixed predictions covers source errors, all research choices, or an untouched confirmation test.

Management-sector activity, local skills, and industry clusters may reflect firms' earlier location choices as well as conditions relevant to future choices. Conditioning on these is useful for a descriptive benchmark but does not settle reverse causality or omitted-variable bias.

## Incentive applicability remains a separate future product

Keep economic scale and other context variables available even when they are not direct local policy levers. Do not multiply input values, regression coefficients, kernel weights, or SHAP values by subjective feasibility scores and call the result a causal incentive effect.

A later intervention review can score named actions by City/agency authority, mechanism/evidence, delivery time/cost, additionality, and resident/fiscal benefits. Fix those criteria transparently and test alternative decision weights. Such a review can use this study to prioritize questions, but it needs program/project evidence to recommend funding. It is not a prerequisite or fitted component of the grouping run.
