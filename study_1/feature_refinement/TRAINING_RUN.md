# Reproduce the regional feature comparison

Run from the repository root with Python 3.12 and the pinned [training requirements](../requirements-training.txt). The offline builder also needs `openpyxl==3.1.5` to read the archived official geography workbook; this dependency is now pinned in [preparation requirements](../requirements.txt). No network request or company-location collection occurs during preparation or training.

```sh
python study_1/scripts/build_feature_refinement.py
python study_1/scripts/verify_feature_refinement.py --data-only
python study_1/scripts/train_feature_refinement.py
python study_1/scripts/verify_feature_refinement.py
```

The first two commands prepare/check the inputs. Training writes a fresh R1 run to this directory; do not run it merely to inspect saved results. Verification reloads models and recomputes metrics without refitting. The shared fitting implementation remains unchanged; the standalone 98-firm workflow is retired.

For a portable environment, run the following from the repository root:

```sh
python3.12 -m venv study_1/.venv
study_1/.venv/bin/python -m pip install -r study_1/requirements.txt -r study_1/requirements-training.txt
LOKY_MAX_CPU_COUNT=1 \
study_1/.venv/bin/python study_1/scripts/train_feature_refinement.py
```

Use `study_1/.venv/bin/python study_1/scripts/verify_feature_refinement.py` for the full verifier. Existing local dependencies under `.training_runtime/` are retained but excluded from Git. The per-run metadata and environment freeze record the actual versions. Raw inputs are also excluded from Git; restore the inputs listed in [publication notes](../PUBLIC_REPOSITORY.md) before rebuilding or running the full validation chain.

## Methods and efficiency

R0 predictions/models are reused only after checking the original frozen input/selection hashes and package versions. R1 fits the same six variants: aggregate Poisson/XGBoost, company logistic/XGBoost, and the two company main-effects diagnostics. The employment/mean-count baselines are fitted on each outer training set and checked against R0.

The shared core caches each inner fold's training-only preprocessing across hyperparameter candidates. There is one CPU thread, no larger grid, no additional feature search and no redundant R0 retraining. Five outer folds plus final development fitting produce 36 retained outer/final fits and 525 inner candidate fits. Only the six final R1 pipelines are serialized.

Regression imputation, missing indicators, scaling and company category encoding are fitted within training folds. XGBoost retains native numeric-null handling. Natural event prevalence is preserved. All 498 company probabilities are summed per metro without thresholding or per-company geographic normalization.

Primary selection uses equal-metro OOF count MAE, then RMSE, then R0 for remaining feature-set ties, then the original model order. Main-effects-only variants are diagnostic. The selection record is written before loading the new Atlanta assessment tables for modeled prediction. Atlanta has previously been inspected and is not an analyst-blind test.

Uncertainty uses 2,000 seeded whole-metro draws and the existing crossed company/metro sensitivity. Paired R1–R0 MAE uses the same metros in each draw. These fixed-prediction intervals omit model-refitting, hyperparameter-selection and winner-selection uncertainty. The Atlanta band remains a heuristic prediction-error band.

## Geography and scope

The official CBP 2022–2023 county-to-MSA reference matches the July 2023 frame's physical counties in all 50 metros. Providence's additional `44999` is a statewide reporting code: all Rhode Island counties already belong to this metro. BDS release documentation establishes July 2023 MSA adoption and the 2023 vintage-consistent geography. The audit records the evidence and decisions rather than claiming that company addresses or economic microdata were independently re-geocoded.

Shares remain fractions and BDS rates remain percent units. No source year, ownership population, outcome definition or evaluation metro was substituted. The office/function tables and evidence-coverage flags are not model predictors or supervised office outcomes. Additional co-HQs and Block's role conflict do not revise the frozen selected-point HQ target.

## Cleanup provenance

Source payloads now live under `study_1/source_data/`. The builders and verifiers recognize only the exact before/after hashes and relocations recorded in [cleanup_manifest.json](../provenance/cleanup_manifest.json). Original frozen run manifests and selection records remain unchanged; this record documents source-layout and orchestration changes rather than pretending they were present at fitting time.
