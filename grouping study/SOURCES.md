# Sources and evidence map

Prepared November 25, 2026. External sources below were checked while preparing this protocol. They support methodological reasoning, not results of this unexecuted experiment. Source access date, economic reference year, publication date, and 2025 HQ snapshot are different concepts.

## Local sources of record

| Source | Use and limitation |
| --- | --- |
| [Study 1 index](../study_1/README.md) and [current status](../study_1/CURRENT_STATUS.md) | Identify the completed 498-firm R1 run; older design documents retain original-sample descriptions. |
| [R1 final results](../study_1/feature_refinement/FINAL_RESULTS.md) | MAE 3.564 versus 4.016 employment, Atlanta 15 versus 9.17, uncertainty, and retrospective/causal limits. |
| [R1 run guide](../study_1/feature_refinement/TRAINING_RUN.md) | Whole-metro nested validation, reference reuse, preprocessing, and frozen selection. |
| [Shared fitting code](../study_1/scripts/train_hq_2025.py) | Existing median imputation/standardization, logistic settings, employment baseline, and metric implementation. Its legacy entry point is retired; inspect/reuse functions safely. |
| [R1 orchestration](../study_1/scripts/train_feature_refinement.py) | Imports shared fitting functions, version/hash checks, R1 comparison outputs, and timing. |
| [Feature catalog](../study_1/STUDY_1_FEATURE_CATALOG.md) | Underlying variables and source meanings; historical counts must be read alongside current R1 contracts. |
| [Expanded source guide](../study_1/expanded_500/SOURCES.md) and [omissions](../study_1/expanded_500/OMISSIONS_AND_COVERAGE.md) | Publisher ranking/map, geographic assignments, source discovery, two exclusions, and selected-point target. Not independent verification of every historical office. |
| [Linked collection results](../study_1/linked_msa/COLLECTION_RESULTS.md) and [schema](../study_1/linked_msa/SCHEMA.md) | Partial functions/offices, mixed source-reference periods, unknowns rather than verified office negatives. |
| [Public repository notes](../study_1/PUBLIC_REPOSITORY.md) and [cleanup record](../study_1/CLEANUP.md) | Required local source bundle, preserved artifacts, and deliberate historical migrations. |
| [Artem global-HQ study](../artem/FORTUNE500_GLOBAL_HQ_MODEL.md) | Broader HQ benchmark; different geography/labels/baselines, so its raw errors cannot rank the current experiment. |
| [Artem actionability overlay](../artem/INVEST_ATLANTA_PROGRAMS_AND_MODEL_OVERLAY.md) | Separate program-alignment precedent. Its narrower business-entry feature screen had MAE 1.193 versus 0.979 for full context; not a HQ result or causal program evaluation. |

The New York scoring-only calculation discussed in the chat was derived from the saved R1 `B_logistic` rows in `study_1/feature_refinement/reports/training/oof_metro_predictions.csv`. It omitted one fixed error from the score without refitting. Do not cite it as an estimated training influence or a grouping result.

## External primary and official references

1. **Scikit-learn, nearest-neighbor methods.** [Official guide](https://scikit-learn.org/stable/modules/neighbors.html) and [neighbor regression API](https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KNeighborsRegressor.html). Establish prediction from similar observations and distance weighting. The present two-part adaptive kernel/blend is specified by this protocol, not an off-the-shelf estimator claimed by that guide.
2. **Scikit-learn, scaling.** [Importance of feature scaling](https://scikit-learn.org/stable/auto_examples/preprocessing/plot_scaling_importance.html). Supports standardization for distance-based methods and the relative insensitivity of tree predictions to ordinary predictor rescaling. It does not establish that a variable with greater fitted importance is causal.
3. **Scikit-learn, evaluation.** [Common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html) and [cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html). Support training-only learned transforms and separate tuning/evaluation. Our target-specific focus weights and small-sample support gates are explicit new design choices.
4. **Duranton, Gilles, and Diego Puga (2005), “From sectoral to functional urban specialisation,” Journal of Urban Economics 57(2), 343–370.** [Author-hosted manuscript](https://diegopuga.org/papers/sec2func.pdf). Motivates distinguishing corporate functions and regional economic structure. It does not validate the proposed Atlanta similarity metric.
5. **Abadie, Alberto, and Guido W. Imbens (2006), “Large Sample Properties of Matching Estimators for Average Treatment Effects,” Econometrica 74(1), 235–267.** [Author/institution-hosted paper](https://economics.mit.edu/sites/default/files/publications/LARGE%20SAMPLE%20PROPERTIES%20OF%20MATCHING%20ESTIMATORS.pdf). Provides causal-matching context and assumptions. This protocol is not their treatment-effect estimator; its bootstrap is a qualified frozen-prediction summary, not an assertion of valid matching-estimator inference.
6. **U.S. Census Bureau, metropolitan-area glossary.** [Official definitions](https://www.census.gov/programs-surveys/metro-micro/about/glossary.html). MSAs reflect commuting-based integration. Economic peer grouping does not redefine their boundaries or permit reassigning metro statistics to arbitrary sites.
7. **HM Treasury (2024), Multi-Criteria Decision Analysis guidance.** [Official guidance](https://www.gov.uk/government/publications/green-book-supplementary-guidance-multi-criteria-decision-analysis/use-of-multi-criteria-decision-analysis-in-options-appraisal-of-economic-cases). Supports transparent decision criteria and sensitivity analysis of policy trade-offs. It does not justify treating predictive feature importance times feasibility as an intervention-effect estimate or replacing cost-effectiveness analysis.

## Citation and update policy

Future results should cite the exact local input artifacts, source registries, code versions, configuration and these documents. Keep source IDs/URLs in audit metadata rather than predictive features. Describe source revisions or new office collection as a new version, not as evidence that the original snapshot was different.

Do not invent recent applications, claim an independent replication of Study 1, or attribute this exact estimator to the cited research. Reusing the same firms, metros and economic measures creates related follow-ups, not independent confirmations.
