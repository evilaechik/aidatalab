# Completed-run validation

The prepared data pass **54 checks**. The complete saved-run validation passes **148 checks**, including the preparation checks; these are not two independent sets to add together. See [data_validation.json](reports/data_validation.json), [artifact_validation.json](reports/artifact_validation.json) and their detailed CSVs.

The original expanded-data and linked-data validators passed 94 and 452 checks before this run. The 206-file historical snapshot remains unchanged as an audit record. Validators now check original fingerprints together with the exact relocations, retirements and edits recorded in [cleanup_manifest.json](../provenance/cleanup_manifest.json). Expanded/refinement supervised tables, labels, folds, fitted models, predictions and frozen selection records retain their original bytes. Retired historical files must remain absent; relocated inputs must retain their original hashes.

## Data checks

- Official geography evidence, all 50 CBP county membership comparisons and the documented BDS 2023 geography vintage.
- Exactly three additions, with 50 finite values, preserved fraction/percent units and explicit source lineage.
- One-to-one/many-to-one joins, unchanged original columns/keys/labels, 498 firms in every metro and the original whole-MSA folds.
- Training/assessment row counts and 34/42/38 input contracts; excluded firms remain excluded and Atlanta remains reserved.
- Frozen source/configuration/script hashes or exact documented cleanup transitions; unchanged tuning grids, seed and outcome definition.

## Model and result checks

- R0 source selection/input hashes, exact package-version match and unchanged reused artifacts.
- Twenty R0/R1 method entries across 49 held-out metros; six complete R1 probability grids, with valid probabilities and 498 firms per metro.
- Company probabilities sum to the saved metro expectations and observed counts; both shared baselines reconcile across feature sets and tracks.
- MAE, RMSE and Poisson deviance independently recomputed using the saved predictions.
- The selected model follows the frozen MAE/RMSE/reference/model-order rule. Selection is recorded before the new modeled Atlanta assessment.
- All 36 outer/final fits completed, exact feature allowlists were used, final regression imputation matches development-only values, and all 12 R0/R1 saved pipelines reproduce the Atlanta assessment when reloaded.
- Paired R1–R0 error differences recomputed from matched metro predictions.

No convergence failure, failed model variant or discarded metro occurred. The six final new pipelines use the original nested tuning implementation; 525 inner candidate fits and 36 outer/final fits ran with one thread. The fitting/reporting timer was approximately 54 seconds.

Passing these checks establishes computational consistency, not causal identification or complete office coverage. The primary logistic model improves over the previous logistic benchmark, while its advantage over employment remains uncertain under the paired fixed-prediction bootstrap. The intervals omit refitting/selection uncertainty and are not adjusted for all model comparisons. Atlanta's prediction-error band is heuristic.

The captured pre-run handoff and frozen training configuration remain unchanged. [FINAL_RESULTS.md](FINAL_RESULTS.md) adds interpretation of the saved metrics after fitting and validation; no extra model was fitted to produce that interpretation. Output hashes are listed in [output_manifest.csv](reports/output_manifest.csv).
