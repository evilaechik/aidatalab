# Atlanta company–metro grouping results

Executed November 27, 2026 · Protocol 1.0 · Completed and artifact-verified.

## Result and scope

Retain **R1_GLOBAL**. The prespecified grouping procedure did not improve the Atlanta-focused benchmark. Its held-out focus MAE was 4.204, compared with 4.106 for focused global tuning and 3.812 for unchanged R1. Final grouping tuning selected **alpha=0**, so its Atlanta output uses the global regression throughout.

This is a retrospective benchmark of the publisher-selected 2025 Fortune 500 HQ stock in the July 2023 50-MSA frame. It preserves 498 eligible companies, the 63 outside-frame firms, both exclusions, Block's frozen selected point, 420 development positives and Atlanta's 15. Economic inputs retain their inherited 2023–2024 reference periods and units; company financials follow the 2025 publisher edition. Inputs were reused from Study 1, rather than independently recollected. Ordinary-office fitting remains gated by inadequate absence-capable coverage.

## What changed

The implementation adds five equally weighted regional similarity blocks and a mixed company distance, adaptive Gaussian donor weights, a global/local probability blend, and covariate-only Atlanta-focused validation weights. Study 1 already standardized regression inputs. Distances fit unique training metros and companies; regression preprocessing fits training rows only. Companies remain separate until their 498 probabilities are summed. No extra feature search, outcome change or protocol departure was used.

## Held-out validation

| Procedure | Focus MAE (95% interval) | Focus RMSE | Focus log loss | Focus Brier | All-metro MAE |
| --- | --- | --- | --- | --- | --- |
| EMP | 4.051 (2.854–5.469) | 5.946 | 0.083105 | 0.017109 | 4.016 |
| R1_GLOBAL | 3.812 (2.888–4.925) | 4.984 | 0.082969 | 0.017088 | 3.564 |
| FOCUS_GLOBAL | 4.106 (3.107–5.231) | 5.331 | 0.083248 | 0.017103 | 3.805 |
| GROUPED | 4.204 (3.121–5.390) | 5.503 | 0.083463 | 0.017112 | 3.970 |

All procedures use the same 49 held-out metros and common fold-derived focus weights. Effective validation support is **41.45 metros**, above the frozen minimum of 15. The focus kernel remains broad; these are Atlanta-weighted comparisons across related regional environments. Poisson deviance, clipping counts and all-metro probability diagnostics are in [model_comparison.csv](reports/model_comparison.csv). No probability required log-loss clipping.

| Paired count-MAE difference | Estimate | 95% fixed-prediction interval |
| --- | --- | --- |
| GROUPED minus EMP | +0.152 | -1.124 to +1.299 |
| GROUPED minus R1_GLOBAL | +0.392 | +0.028 to +0.838 |
| GROUPED minus FOCUS_GLOBAL | +0.097 | -0.056 to +0.295 |

Positive differences favor the reference. Grouping's difference from focused global tuning is small and uncertain. Its disadvantage versus R1 has a positive interval under this fixed-prediction calculation. The 2,000 whole-metro bootstrap draws retain each metro's full company roster and focus weight. Their intervals omit refitting, tuning, final-family selection, source error and geographic dependence. Choosing the minimum outer score remains development selection.

## Tuning attribution

| Outer fold | Focus-global C | Grouped C | Grouped alpha | Regional/company rank |
| --- | --- | --- | --- | --- |
| 0 | 0.01 | 0.1 | 0.25 | 10/25 |
| 1 | 0.1 | 0.1 | 0 | inapplicable |
| 2 | 0.01 | 0.01 | 0 | inapplicable |
| 3 | 0.01 | 0.01 | 0 | inapplicable |
| 4 | 0.01 | 0.01 | 0 | inapplicable |

Grouping chose alpha zero in **4/5 outer folds**. Support fallback affected **0/24402 outer company–metro predictions**; zero-alpha choices were tuning decisions rather than support failures. Focus-global selected C=0.1 in fold 1 while R1 retained C=0.01 there. The grouped fold-0 change jointly selected a different C and positive local weight; its comparison is the prespecified full procedure, not an isolated fixed-C kernel effect. Final focused global and grouped settings both use C=0.01, with no local component. Stored R1 OOF probabilities remain unchanged on exact company/CBSA keys.

## Atlanta assessment

| Procedure | Observed | Expected | Observed − expected | Heuristic error band | Requested/effective alpha |
| --- | --- | --- | --- | --- | --- |
| EMP | 15 | 14.383 | +0.617 | 6.348–22.419 | 0/0–0 |
| R1_GLOBAL | 15 | 9.173 | +5.827 | 1.324–17.022 | 0/0–0 |
| FOCUS_GLOBAL | 15 | 9.173 | +5.827 | 0.967–17.379 | 0/0–0 |
| GROUPED | 15 | 9.173 | +5.827 | 0.000–18.792 | 0/0–0 |

The selected benchmark expects **9.17 HQs**, and observed minus expected is **+5.83**. The positive residual indicates more selected HQs than the point benchmark. It is not an Atlanta shortfall, a count of available recruits, or evidence of exceptional policy performance.

Each error band adds/subtracts the first weighted 90th percentile of the procedure's frozen absolute outer count residuals, truncated to [0,498]. These are heuristic error ranges, without formal Atlanta coverage or confidence-interval interpretation. Equal final point predictions can have different bands because their nested outer procedures differed. Atlanta labels were opened for assessment only after family/settings freeze and label-free final prediction export; prior knowledge of Atlanta's outcome still prevents an analyst-blind claim.

## Companies and sectors

[atlanta_company_predictions.csv](reports/atlanta_company_predictions.csv) contains all 498 company probabilities for each procedure, labels and classifications. Grouped support and leave-one-metro ranges are attached only to GROUPED rows. Those ranges describe fixed-settings instability, not probability confidence. No probabilities were thresholded or renormalized across geography.

| Sector | Companies | Observed | Expected (R1_GLOBAL) | Grouped leave-one-metro range |
| --- | --- | --- | --- | --- |
| Aerospace & Defense | 11 | 0 | 0.201 | 0.176–0.224 |
| Apparel | 4 | 0 | 0.063 | 0.056–0.071 |
| Business Services | 18 | 1 | 0.292 | 0.263–0.326 |
| Chemicals | 12 | 0 | 0.215 | 0.194–0.237 |
| Energy | 57 | 1 | 0.963 | 0.835–1.044 |
| Engineering & Construction | 12 | 1 | 0.194 | 0.174–0.214 |
| Financials | 93 | 2 | 1.806 | 1.634–1.956 |
| Food & Drug Stores | 5 | 0 | 0.079 | 0.072–0.090 |
| Food, Beverages & Tobacco | 26 | 1 | 0.412 | 0.372–0.457 |
| Health Care | 45 | 0 | 0.846 | 0.764–0.921 |
| Hotels, Restaurants & Leisure | 11 | 0 | 0.172 | 0.154–0.199 |
| Household Products | 8 | 1 | 0.125 | 0.113–0.141 |
| Industrials | 19 | 1 | 0.334 | 0.303–0.371 |
| Materials | 17 | 1 | 0.301 | 0.269–0.332 |
| Media | 10 | 0 | 0.162 | 0.146–0.178 |
| Motor Vehicles & Parts | 9 | 0 | 0.162 | 0.148–0.181 |
| Retailing | 44 | 2 | 0.719 | 0.648–0.803 |
| Technology | 52 | 0 | 1.401 | 1.016–1.535 |
| Telecommunications | 7 | 0 | 0.113 | 0.101–0.126 |
| Transportation | 17 | 3 | 0.269 | 0.243–0.303 |
| Wholesalers | 21 | 1 | 0.342 | 0.305–0.377 |

Sector ranges describe the grouped final procedure; its point prediction currently coincides with the selected R1 fit. Classification totals reconcile to the common 498-company roster. Company values are comparative HQ scores for this fixed roster, not relocation or offer-acceptance probabilities.

## Donor explanation and support

The following weights describe the **diagnostic** widest prespecified kernel (regional rank 20, company rank 150). Since selected alpha is zero, these weights do not contribute to the reported final benchmark. Bandwidths are inapplicable to that selected estimate; this explanation convention was frozen before fitting.

| Metro | Kernel weight | Distance |
| --- | --- | --- |
| Phoenix–Mesa–Chandler, AZ | 0.0327 | 0.643 |
| Dallas–Fort Worth–Arlington, TX | 0.0319 | 0.693 |
| Denver–Aurora–Centennial, CO | 0.0316 | 0.712 |
| Tampa–St. Petersburg–Clearwater, FL | 0.0291 | 0.858 |
| Charlotte–Concord–Gastonia, NC–SC | 0.0285 | 0.892 |
| Orlando–Kissimmee–Sanford, FL | 0.0285 | 0.893 |
| Houston–Pasadena–The Woodlands, TX | 0.0284 | 0.897 |
| Austin–Round Rock–San Marcos, TX | 0.0265 | 1.001 |
| Miami–Fort Lauderdale–West Palm Beach, FL | 0.0264 | 1.007 |
| Portland–Vancouver–Hillsboro, OR–WA | 0.0263 | 1.011 |

This diagnostic kernel has 44.18 effective regional donors and at least 401.25 effective company donors. The product is weight concentration, not independent sample size. Positive-support counts/mass, largest and top-five weights, bandwidth fallbacks and numerical underflow are retained in [support.csv](reports/support.csv), with [sector summaries](reports/support_by_sector.csv). The broad weights explain why nominal neighbor rank must not be read as a hard group size.

[atlanta_donor_companies.csv](reports/atlanta_donor_companies.csv) retains all 498 × 498 company comparison weights, mixed-distance components and ranks. [atlanta_top_donor_rows.csv](reports/atlanta_top_donor_rows.csv) retains 20 pair weights per query, training labels, positive numerator contributions and omitted mass. Those top 20 omit 99.72%–99.79% of diagnostic pair weight, so they are an explanation excerpt. All metros remain donors with their numerical kernel weights; no outlier was deleted from the primary run. Similarity weights are not feature importance or causal contributions.

## Prespecified stability

All **67 variants** were recorded: four final New York removals, 49 individual-metro removals, five block omissions and nine bandwidth pairs. An additional ten fixed-settings outer fits evaluate New York influence on the same 48 non-New-York test metros using original focus weights.

Removing one donor metro and refitting the grouped final global/distance components produced Atlanta expectations from **8.315 to 9.971**. The largest absolute change was 0.859 HQs. Every resulting Atlanta residual remains positive. Removing New York changed R1/grouped Atlanta expectations by +0.147 to 9.320; its effect is through the global component because alpha=0. [sensitivities.csv](reports/sensitivities.csv) separates the global, fixed-metric direct-label and remaining scaling/bandwidth/support effects.

| Procedure on same 48 test metros | Original focus MAE | Refit without New York | Difference |
| --- | --- | --- | --- |
| FOCUS_GLOBAL | 4.002 | 3.982 | -0.019 |
| GROUPED | 4.101 | 4.123 | +0.023 |

All five block omissions and nine width substitutions leave the final expectation unchanged because alpha is zero. They cannot establish a grouping benefit. Diagnostic top-10 metro overlap ranges from 6 to 10 across block omissions; ranks and company/sector changes are saved for every variant. Atlanta's nearest-donor distance and diagnostic bandwidth are both below their cross-fitted 95th percentiles; these are descriptive support checks with fold-varying selected bandwidths, not extrapolation guarantees.

## Verification and limits

All **114 artifact/numerical checks** and **36 data acceptance checks** passed. Verification independently reconstructs regional/company distances, kernel fixtures, scoring, count/sector reconciliation, donor normalization and pair weights, checks label/fold preservation and train/query separation, reloads final artifacts to reproduce Atlanta probabilities, and confirms unchanged consumed-source hashes. The final run performed 100 distinct global fits with 0 fitting failures, one CPU thread and the exact saved R1 Python/package versions. See [RUN_GUIDE.md](RUN_GUIDE.md), [run metadata](reports/run_metadata.json), [acceptance results](reports/artifact_validation_checks.csv) and [artifact inventory](reports/output_manifest.csv).

An initial export attempt stopped on a pandas index/column ambiguity before opening Atlanta assessment labels. A verification attempt then exposed a donor-CBSA parsing issue. Both implementation issues were fixed; the unchanged search was rerun from preparation, along with export dtype cleanup. No candidates or unfavorable validation rows were omitted, and no search choices changed after results. The protocol's eight preparation documents remain unchanged as the original design record.

The experiment provides no evidence to replace R1 with grouping under this specification. Future evidence should come from untouched periods or additional comparable regions with a frozen outcome/coverage contract. Overlapping companies and donor groups do not add independent economies. Regional structure can reflect historical corporate choices. This study does not identify incentive effects, municipal program performance, future moves, ordinary offices or local jobs.
