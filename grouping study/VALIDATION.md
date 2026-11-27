# Validation and uncertainty plan

Protocol version 1.0 · November 25, 2026 · **Planned checks; none have been executed for this new study.**

Keep structural acceptance, predictive evidence, local support, and causal interpretation distinct. Passing file/shape checks does not show that grouping helps Atlanta.

## Data acceptance

- Verify the hashes and provenance of every consumed table, reference prediction/model, fold file, and protocol.
- Reconcile 500 roster identities, 498 supervised firms, 50 metros, 49 development metros, 24,402 development pairs, and 498 Atlanta pairs.
- Verify 435 full-frame positives, 420 development positives, Atlanta's 15, and 63 covered firms outside the frame. Preserve the two excluded firms' unknowns in the upstream audit only.
- Check unique pair/profile keys, identical 498-company rosters across metros, no unintended many-to-many join, and unchanged target values/folds.
- Check 42 raw regression inputs, exactly 15 regional distance columns in five blocks, the four company distance fields, and all prohibited-field exclusions.
- Verify units, existing log transforms, finite permitted values, categorical integrity, null handling, and consistency of regional values across repeated company rows.
- Reject any office unknown coded as a negative, or any site/function count substituted for a selected-HQ label.

Do not run inherited builders just to validate a new grouping script if they rewrite source reports. Read/check source artifacts directly or validate isolated copies. New validation reports belong here; existing bytes must remain unchanged.

## Leakage and numerical acceptance

- All company rows for a metro share the same supplied outer fold. No outer validation or Atlanta labels enter training donors, fitted preprocessing, or inner tuning.
- Inner transformations use inner training only. Outer transformations use outer training only. Final transformations use the 49 development metros only.
- Region scalers fit unique regional profiles; company scalers fit unique companies. Repeating a macro value across 498 rows does not create 498 environments.
- IDs and category display names are not numeric features. Neighbor selection depends on allowed inputs, never on observed presence or validation error.
- Assert that all component weights are finite, nonnegative, and normalized. Verify block weights and every pair weight's factorization.
- For a small hand-checkable fixture, independently reproduce distances, bandwidth ranks/ties, kernel normalization, local probabilities, and blends. Check identical-distance/constant-column behavior and complete metro exclusion.
- Check pure-local predictions are convex weighted averages in [0,1]. Check blended predictions are in [0,1] and sum to saved counts without rounding, thresholding, or geographic renormalization.
- Independently verify the alpha-zero identity with its corresponding global model and the documented support fallback. Saved `R1_GLOBAL` predictions must match the original exact keys.
- For numerical log loss only, evaluate `clip(p, 1e-12, 1-1e-12)` consistently for every model and record clipped counts. Save original probabilities and use them for count/Brier metrics. Clipping is not fitted calibration or a change of predicted counts.
- Reject nonfinite predictions, changed natural prevalence, silent class balancing, or a failed fit presented as a valid candidate. Record convergence warnings/failures and eligibility; do not quietly increase the search or drop validation metros.

## Effective donor support

For normalized regional kernel weights `b` and company weights `a`, compute:

- Effective regional donors: `N_eff_m = 1 / sum(b_m^2)`.
- Effective company donors: `N_eff_c = 1 / sum(a_f^2)`.
- Formal effective pair weights: `1 / sum((a_f*b_m)^2) = N_eff_m*N_eff_c` on the complete grid. This is a weight-concentration statistic, **not** an independent-observation count.
- Largest regional/company/pair weights, total contribution of the top five donors, and nearest/bandwidth-rank distances.
- Weighted HQ-positive mass and number of distinct positive donor firms/metros. These last diagnostics use training labels and do not determine group membership or trigger an extra outcome-based fallback.

Apply the frozen label-independent fallback in all splits: if `N_eff_m < 10` or `N_eff_c < 25`, use effective alpha zero for that query. Retain requested alpha and the fallback reason. These are practical design thresholds, not established power guarantees. Do not change them after observing errors.

For the pooled evaluation focus weights `v`, compute `N_eff_validation = (sum(v))^2 / sum(v^2)`. If below 15, describe comparative local accuracy as insufficiently supported even if a point score improves. Keep the full score and interval visible; do not expand the focus width after viewing outcomes to obtain a preferred conclusion.

Also compare Atlanta's nearest-donor and bandwidth distances with the corresponding cross-fitted development-query distance distributions. Flag Atlanta distances above their 95th percentiles as an extrapolation warning, not a formal hypothesis test or reason to silently remove rows. Report support separately by company/sector. A few well-supported firms do not justify all-company certainty.

## Predictive metrics

For observed metro counts `Y_j`, summed probabilities `P_j`, and common raw focus weights `v_j`:

`local_count_MAE = sum(v_j*abs(Y_j-P_j)) / sum(v_j)`.

Compute weighted RMSE and Poisson deviance on the same metros. These are HQ-count errors, not percentage changes or estimates of missing recruits. Use natural-log Poisson deviance with a documented numerical epsilon only if needed, retaining the raw predicted count.

For each metro, average company log loss and Brier score across the same 498 firms, then apply `v_j` across metros. Also report mean probability, observed event rate, and fixed probability-bin summaries (0, .005, .01, .02, .05, .1, .2, 1). Sparse bins and regression-based calibration diagnostics are descriptive; do not fit and apply a correction to outer predictions.

Report equal-metro all-49 metrics as diagnostics. Keep focus weights identical across model comparisons. A better overall score does not establish better Atlanta transfer, and a smaller local error does not prove the locality mechanism caused the gain.

Required paired comparisons: `GROUPED` minus `FOCUS_GLOBAL` (isolates grouping beyond focused tuning), `GROUPED` minus `R1_GLOBAL`, and `GROUPED` minus `EMP`. Negative error differences favor grouping. Include per-metro errors/weights, selected hyperparameters per outer fold, and alpha-zero/fallback frequencies.

## Uncertainty

### Development comparisons

Use 2,000 seeded bootstrap draws of the 49 whole metros with replacement, applied to frozen paired outer predictions. In each draw retain a metro's prediction pair, all 498 company rows, and its fixed focus weight together; recompute the weighted-score ratio. Report percentile 95% intervals for scores and paired differences. Use the same draw for all methods. Do not treat individual company–metro rows as independent.

These are descriptive fixed-prediction intervals. They omit refitting, neighborhood/tuning selection, source error, and final-winner uncertainty. The observations are also not a random national sample; geographic dependence can remain. Do not describe an interval excluding zero as proof of causal or universally reliable superiority.

Keep the fixed 498-company roster as the primary estimand. A separately labeled crossed company/metro sensitivity may reuse the earlier study's resampling design, but is not required and must not replace metro-level uncertainty or masquerade as new-company validation.

### Atlanta error and prediction stability

For each prespecified procedure, form a **heuristic** error band by taking the weighted 90th percentile of its 49 absolute outer count residuals using common focus weights, then adding/subtracting it from the final Atlanta expectation. Define the weighted quantile as the first sorted residual whose cumulative normalized weight reaches 0.90. Truncate to [0,498]. Report the unweighted inherited-style error band separately if reproduced.

This is not formal conformal coverage, a confidence interval for an expected count, or proof of coverage at Atlanta. Local weighting, prior inspection, model selection, and small support all weaken interpretation. If validation support is insufficient, show the numeric range only as exploratory and label it accordingly.

For company probabilities and sector sums, report prespecified leave-one-donor-metro prediction ranges from the fixed-settings sensitivity. These are instability ranges, not probability confidence intervals. Do not use independent Bernoulli variance `sum(p*(1-p))` to claim a valid HQ-count interval: firms share regional conditions and the selected HQ structure.

## Sensitivity and implementation acceptance

Perform the exact fixed-settings sensitivities in [REPORTING_AND_INTERPRETATION.md](REPORTING_AND_INTERPRETATION.md), recording every result rather than selecting a favorable variant. Refit preprocessing/global components where a donor is removed; do not merely delete its final displayed weight and call that an influence test.

Before completion, independently recompute all scores from saved probabilities, reload final artifacts and reproduce Atlanta predictions, reconcile sector/company totals, and verify unchanged source hashes. Record real check names/results; do not invent a passed-check count or copy a previous study's acceptance totals.

A failed support gate, materially unstable Atlanta assessment, or no demonstrated advantage is reportable evidence. It is not a reason to keep searching for a favorable specification under this protocol.
