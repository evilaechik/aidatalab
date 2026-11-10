# Study 1: reported-HQ metro benchmark

Historical design/method record for the initial sample. The current completed study uses 498 eligible firms and three additional regional features; use the [current run index](README.md) and [feature-refinement contract](feature_refinement/config/training_contract.json). Original methodological choices and collection dates below remain documented.

**Follow-up stage — November 10, 2026:** the [current handoff](linked_msa/TRAINING_HANDOFF.md) specifies a limited feature-refinement comparison against the completed expanded-500 HQ benchmark. The [linked collection](linked_msa/README.md) adds general regional indicators and partial company-function evidence. Office-presence models, weighted scoring and bespoke tech/healthcare outcomes remain deferred. The design below records the original experiment and is retained for reproducibility.

Version 2.1 · November 9, 2026 · Supersedes the November 7 office-inventory design
for this initial training handoff, following the user's revised collection scope.

Execution update, November 9: both tracks have been trained under this design.
See [FINAL_RESULTS.md](feature_refinement/FINAL_RESULTS.md) and [TRAINING_RUN.md](feature_refinement/TRAINING_RUN.md).

## Research question

How does Atlanta's reported-HQ count in a broad, fixed Fortune-company sample
compare with other MSAs, and does its difference persist after adjustment for
regional scale, workforce, sector mix, growth, prices, and income?

Run two parallel tracks on the same covered cohort and reported-HQ target.
Each has an aggregate scorecard/baseline, a simple regularized regression, and
a conservative XGBoost challenger. One predicts metro counts directly; the other
predicts company–metro probabilities and sums them into expected metro counts.
The models must demonstrate useful performance on held-out development MSAs
before their Atlanta residual is interpreted.
A residual is a descriptive difference from a learned expectation, not an
estimate of missing firms that Atlanta could recruit or a causal policy effect.

## Two tracks, one benchmark target

| | Track A: metro aggregate | Track B: company–metro HQ |
| --- | --- | --- |
| Aim | Establish a transparent regional-conditions benchmark for total HQ concentration | Test whether company traits and company–metro relationships improve that benchmark or explain company-type patterns |
| Response | Metro HQ count | Binary company–metro HQ label |
| Baseline | Observed scorecard; employment-proportional and mean-count expectations | Same aggregate baseline and sector breakdowns; baseline count divided by 98 gives per-company probabilities |
| Simple regression | L2-regularized Poisson | L2-regularized logistic |
| Conservative ML | Shallow XGBoost count model | Shallow XGBoost probability classifier |
| Benchmark construction | Predict expected count directly | Sum probabilities across the same 98 covered firms |

The aggregate track is the reference against which additional detail must earn
its complexity. The detailed track retains company-level heterogeneity that an
overall metro count obscures. These are three method families per track, with a
shared baseline; they are not six unrelated data collections or six completed
model fits. Both concern reported HQs, not a general office-network inventory.

## Frozen scope

| Decision | Specification |
| --- | --- |
| Population frame | Fixed Fortune 500 2025 edition; stable unique list-position IDs |
| Selected cohort | 100 firms, stratified across 21 sectors, three revenue/list-position bands, and publisher listing categories |
| Covered analysis cohort | 98 firms; two source-role conflicts excluded under a common rule across every MSA |
| Target | Count of publisher-selected reported 2025 HQ points in an MSA |
| HQ unit | One publisher-selected point per eligible firm; known additional HQs are separate sensitivity context |
| Geography | Existing 50 MSAs, July 2023 OMB/Census CBSA membership |
| Economic reference | 2024, except explicit lagged 2023 sector shares; revised source vintages retained |
| Model units | Track A: 50 MSA rows. Track B: 98 companies × 50 MSAs = 4,900 labeled company–MSA rows; the same 50 metro economic profiles |
| Holdout | Atlanta CBSA 12060; remaining 49 MSAs have fixed, outcome-independent five-fold assignments |
| Outputs | Both tracks’ full/development/assessment tables, separate predictor allowlists, label audit, coverage/omissions, source links, schemas, SQLite, validation |
| Outside scope | Comprehensive office presence, subsidiary network, office functions beyond HQ, local jobs, municipal Atlanta, causal inference |

The ranking edition, fiscal reference, publication date, access date, and HQ
snapshot are different concepts. Do not relabel the financial columns as FY2025
or the HQ labels as verified year-end occupancy. Historical roster members remain
in the publisher snapshot through subsequent acquisitions/name changes; this is
not a list of independent operating companies at year-end.

## Sampling before HQ results

The operational 500-ID sampling frame is retained in
[population_sampling_frame.csv](expanded_500/config/population_sampling_frame.csv).
Strata are sector × list-position third (1–167, 168–334, 335–500) × publisher
listing category. Give each of 73 nonempty strata one seat; allocate the remaining
27 seats sequentially to the largest N/(n+1), breaking ties in sorted stratum
order. Draw the lowest SHA256 hashes within each stratum using the frozen literal
seed `study1-hq2025-20251108` and each company ID. The seed is a fixed string,
not the collection date. The final cohort was fixed before inspecting its HQ outcomes.

The draw contains 35/33/32 firms by position band and 88 publisher-public,
9 unknown/private/other, and 3 mutual cases. Publisher listing category is not a
complete independently verified legal ownership taxonomy. Six firms overlap the
old pilot; no old pilot firm or Atlanta outcome was forced into the new sample.
The two coverage exclusions are not replaced based on HQ locations.

[Stratum counts](expanded_500/tables/cohort_strata.csv), selected-firm inclusion probabilities,
and inverse design weights document the design. Primary outcomes are unweighted
covered-cohort counts. Design weights may inform sensitivity analysis; exclusions
and singleton strata prevent an automatic claim of unbiased full-500 estimation.
All 21 sectors remain after exclusions. Sector diversity is not evidence of
diversity of observed office functions: this handoff observes HQs only.

## Collection and labels

Use the public Fortune 2025 location map as a consistent publisher listing.
Match identities, including explicit alias review, and assign reported coordinates
to Census July 2023 CBSA polygons. Exact street matching is not required.
Try an official filing, directory, or company listing route for every firm.
Supplemental source discovery is logged, not presented as independent verification
of all 100 addresses or as exhaustive office enumeration.

Retain publisher-selected HQ locations when secondary sources identify additional
co-HQs. Flag material function/identity conflicts as unknown coverage outliers;
do not manufacture geographic corrections. See [omissions](expanded_500/OMISSIONS_AND_COVERAGE.md).
For each of 98 covered firms, label its selected HQ MSA 1 and all other frame
MSAs 0. Twelve covered HQ points are outside the frame, so those firms contribute
zero to every selected metro. For two excluded firms, all 50 labels remain null.

Zero counts for a metro are valid for this selected-point, covered-cohort target.
They are not evidence that the metro has no Fortune-company offices or HQs outside
the selected sample. Keep the denominator 98 everywhere. Export lower/upper counts
for the full selected 100 when the two unknown firms are considered; do not silently
add either excluded publisher point back as truth.

## Track A: metro aggregate approach

Aim: explain and benchmark total sampled-company HQ concentration using regional
conditions. Use 31 metro predictors and predict the count directly. This is the
transparent reference for determining whether company-level detail adds value.

### Analysis sequence and validation

1. Describe raw counts, count shares, employment-normalized counts, cohort mix,
   exclusions, unknown bounds, and a known-additional-HQ sensitivity.
2. Fit an employment-proportional baseline and a training-fold mean-count baseline.
3. Fit penalized Poisson regression on the broad 31-feature matrix. An explicitly
   validated ridge/log1p variant is a sensitivity, not a silent target change.
4. Fit conservative Poisson-objective XGBoost on the same feature allowlist, using
   shallow trees, strong penalties, a small predeclared search, and development-only tuning.
5. Compare identical held-out development MSAs using MAE, RMSE, and Poisson deviance.
   Use nested tuning or fixed hyperparameters; do not tune on outer validation predictions.
6. Freeze the approach, train using the 49 development metros, and assess Atlanta once.
   Repeat any sensitivity under predeclared rules; do not select the best Atlanta story.

Fit imputation, missing indicators, scaling, and feature selection inside each
training fold. XGBoost can retain native nulls. Do not fit transformations on all
50 metros. HQ counts, geography IDs, coverage information, and resident-company
financial/sector aggregates are prohibited predictors. Those aggregates depend
on the outcome. The company-MSA audit table does not create 5,000 independent
regional environments.

The original 13 proposed comparison markets remain context only: Atlanta,
Dallas, Houston, Miami, Denver, Phoenix, Minneapolis, Tampa, Charlotte, Austin,
Nashville, Raleigh, and Columbus OH. They do not restrict the 50-MSA training
frame. Raleigh excludes Durham; Columbus GA is not Columbus OH; Austin MN is
not Austin TX. No outcome-based peer reselection was performed.

## Track B: company–metro HQ approach

Aim: examine whether different company types have different regional HQ patterns,
then aggregate their predicted probabilities into the same metro-count benchmark.
This is a detailed HQ extension, not a collection of ordinary offices.

The full table has 4,900 known company–MSA labels: 98 firms × 50 metros. The same
whole-MSA split gives 4,802 development rows and 98 Atlanta assessment rows. Keep
both excluded firms in the separate 5,000-row audit grid with null labels. The 12
firms with resolved HQs outside the frame remain in the common 98-firm roster.

Join the 31 metro features to company revenue, workforce, broad sector, and
publisher listing category. Four frozen sector–ecosystem interactions represent
technology/computer workforce, financials/finance employment, health care/health
employment, and industrial-sector/manufacturing employment hypotheses. The full
39-column primary input specification is in
[company_hq_feature_spec.json](expanded_500/reference_inputs/company_hq_feature_spec.json). Assets,
profit margin, and revenue growth remain optional sensitivities. Company
financials are company-wide, not local office employment. Do not join HQ
location, known inside-frame status, or source/coverage metadata into X.

1. Use the same observed aggregate scorecard and employment-proportional/mean-count
   baselines as Track A. Express baseline expected count/98 as each firm's
   probability; the summed result is identical to the metro baseline. Flag any
   probability outside [0,1] rather than silently clipping it.
2. Fit L2-regularized binary logistic regression on the primary inputs; compare
   main effects alone with the small frozen interaction block under development-only rules.
3. Fit conservative shallow XGBoost with binary probability objective and the
   same input allowlist. Keep actual event prevalence; do not automatically
   rebalance the 4,814 negatives against 86 positives.
4. Sum probabilities over all 98 covered firms in each held-out metro. Do not
   threshold them into 0/1 predictions. Evaluate metro count errors alongside
   log loss, Brier score, and probability calibration.

Fit encoders, imputation, scaling, tuning and any calibration inside development
training folds. Reuse Track A's whole-MSA outer folds. Same-company observations
across metros are intentionally retained for prediction on this known roster;
new-company transfer would require a separate company-held-out experiment.
Account for company and metro dependence in uncertainty estimates rather than
assuming 4,900 independent observations.

These are marginal binary predictions, not a constrained joint location-choice
model. The frame excludes other possible HQ locations, so do not force each
firm's probabilities to sum to 1 across the 50 metros. Do not normalize using
Atlanta's observed count or a frame total that contains it. Known outside-frame
HQ status is outcome metadata, not a predictor. Keep the scope as the single
publisher-selected HQ point, including the existing co-HQ sensitivity rules.

## Shared decision rule

Exact training files, loading examples, feature contracts and expected training
deliverables are in [TRAINING_HANDOFF.md](expanded_500/TRAINING_HANDOFF.md). Completed data
acceptance and predictive validation are separated in [VALIDATION.md](feature_refinement/VALIDATION.md).

Use held-out development metro counts to compare both tracks and all three model
families. Freeze the reporting/model-selection rule before assessing Atlanta;
never choose a track because its Atlanta gap is more favorable. A detailed model
is useful if it improves transferable count predictions, calibrated probabilities,
or robust company-type diagnostics enough to justify its complexity. Additional
rows alone are not evidence of improvement. Neither track identifies causal effects.

No new external collection is needed for Track B: it reorganizes and transforms
retained inputs. Non-HQ office collection is a separate future study. Both tracks
have completed model fitting and result assessment; outputs remain inside `study_1`.

## Completion and limits

Status as of November 9: both datasets and predictor contracts are prepared.
Training-environment setup, model fitting, out-of-fold performance assessment,
declared uncertainty estimates and the final Atlanta comparison are complete.

Collection is complete for this relaxed, publisher-reported HQ pilot. Four
covariate cells remain null because of source suppression or geography gaps;
fold-specific missing-data handling is a training step, not a reason to invent
measurements. The cohort is much broader than the original 25, but 49 development
metros remain a small macro sample. More features or a complex learner do not
increase that independent sample size. Model uncertainty and baseline performance
must determine whether an adjusted benchmark adds useful information.

A later study of general company presence would require a new, dated, comparable
non-HQ office collection and defensible absence evidence. The current data do not
answer that broader question. Models and expected counts are now available;
causal driver rankings, SHAP results and intervention recommendations were not produced.
