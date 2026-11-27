# Background and reasoning

Protocol version 1.0 · November 25, 2026 · **Design record; no grouping results exist.**

## Research context

The wider Invest Atlanta question concerns business attraction, expansion, retention, and possible local interventions. A metro's current headquarters stock is a narrower descriptive outcome. It is neither a series of new corporate arrivals nor a direct measure of City of Atlanta projects, ordinary offices, local corporate jobs, or program effectiveness.

Study 1 currently benchmarks publisher-selected reported 2025 Fortune 500 HQ points. Its expanded cohort has 498 eligible firms and 50 metros. The company track predicts one firm's HQ presence in a metro and sums the probabilities to an expected metro count. See the [current study index](../study_1/README.md).

The latest completed R1 result selects regularized company logistic regression: held-out count MAE 3.564, versus 4.113 for the earlier logistic model and 4.016 for the employment baseline. Atlanta has 15 observed HQs against 9.17 expected. The approximate prediction-error band is 1.32–17.02. The improvement versus the earlier logistic model is clearer than the advantage over employment; these are fixed-prediction uncertainty comparisons, not independent replications. [Completed results](../study_1/feature_refinement/FINAL_RESULTS.md).

Observed minus expected is positive in that comparison. It does not indicate an Atlanta shortfall. The large uncertainty also prevents treating the positive gap as established exceptional performance or as a number of recruitable companies.

## How the conversation developed

1. **Numerical-scale concern.** Employment and GDP have larger numeric values than shares and rates. This can distort distance methods and regularization if untreated. Inspection showed that Study 1 already logs major scale variables and standardizes numeric regression inputs inside training folds. XGBoost is generally insensitive to simple changes of predictor units. Repeating ordinary scaling is therefore not the central new experiment.
2. **Economic comparability.** A national cross-section may combine very different economies. A model that predicts total HQ counts well might rely on size without providing a useful comparison for Atlanta. The proposed response is to define comparable observations using a small, justified set of economic dimensions.
3. **Extreme markets.** New York may be a poor comparison for a particular Atlanta company, but it is a valid observation. It should receive influence according to input similarity, rather than be deleted because its result is inconvenient. The saved R1 logistic predictions have New York at 62 observed versus about 52.38 expected. Omitting that case from scoring alone changes MAE from 3.564 to about 3.438; this is not a refitting or influence test.
4. **Atlanta becomes the focal estimand.** The user expressly accepts reduced accuracy or exclusion of irrelevant comparison markets if that improves the Atlanta assessment. Equal accuracy across all metros is not required. Validation must therefore emphasize Atlanta-like economies, while disclosing performance and support elsewhere as diagnostics.
5. **Keep individual companies.** The user wants HQ/office outputs with company traits and metro statistics as inputs. The unit remains company × metro. Grouping creates overlapping sets of comparable input rows, not only aggregate metro averages.
6. **Avoid overly small groups.** Strict clusters discard useful information and can leave very few HQ positives. Soft similarity weights and a blend with the global company model are the primary implementation defaults.
7. **Separate feasibility from prediction.** Size and industrial history can remain predictive context even when they are poor direct policy levers. Incentive applicability belongs in a transparent assessment of actual interventions, not in weights chosen to manufacture actionable-looking predictors.

## The resulting question

> For the fixed Fortune-company roster, does an input-defined neighborhood of similar companies in economically comparable metros improve the HQ benchmark that we can credibly transfer to Atlanta?

For example, an Atlanta assessment row for a large financial company can draw more heavily on similar companies in comparable regional economies. Its own HQ location is not used to decide who is similar. An unseen company or a new future location decision is a different prediction task.

This is an Atlanta-focused retrospective benchmark, not a causal matching study or a model of the next relocation. Atlanta outcomes have already been discussed, so no analyst-blind discovery claim is possible. Atlanta covariates may define the target population without using its labels for fitting or selection.

## What existing work supports—and does not support

- **Nearest-neighbor methods:** established methods predict from nearby observations in an explicitly defined feature space. This supports the proposed mechanism, not an assertion that it will outperform regression in this small HQ sample. [Official guide](https://scikit-learn.org/stable/modules/neighbors.html).
- **Urban economics:** Duranton and Puga document and model functional specialization, including concentration of headquarters and business services in larger cities. This motivates retaining scale and economic structure as context while distinguishing HQs from other functions. It does not provide Atlanta-specific incentive effects. [Research paper](https://diegopuga.org/papers/sec2func.pdf).
- **Matching and inference:** Abadie and Imbens study causal matching estimators under additional identifying assumptions. Finding similar observations alone does not meet those assumptions. Our grouping estimator is predictive, not their treatment-effect estimator. [Research paper](https://economics.mit.edu/sites/default/files/publications/LARGE%20SAMPLE%20PROPERTIES%20OF%20MATCHING%20ESTIMATORS.pdf).
- **Current project studies:** Study 1 supplies the company–metro labels, regularized reference model, and whole-metro folds, but has not run this grouping study. Artem's actionability overlay supplies a cautionary precedent for separating predictive fit from program alignment; it modeled business entry, not the present HQ outcome. [Overlay](../artem/INVEST_ATLANTA_PROGRAMS_AND_MODEL_OVERLAY.md).

No claim is made that these sources implement the exact proposed combination. The neighborhood dimensions, kernel, blend, and validation weighting below are new protocol choices requiring testing.

## What success would look like

Success would be better supported, stable predictions in Atlanta-like held-out metros, together with understandable comparison weights for Atlanta companies. It is not defined as finding an Atlanta deficit, removing New York, increasing the apparent importance of actionable variables, or proving an incentive works.

If there are too few comparable economies, locality worsens performance, or reasonable dimensions materially change the Atlanta story, the correct result is to retain the stronger reference or report that the local benchmark is inconclusive. More company rows cannot overcome the limited number of distinct regional environments.
