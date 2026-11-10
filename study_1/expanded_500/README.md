# Study 1 — expanded Fortune 500 HQ data

**Completed follow-up — November 10, 2026:** the [feature-refinement results](../feature_refinement/FINAL_RESULTS.md) compare three added regional features against this completed HQ benchmark. New regional indicators and partial location/function evidence are documented in the [linked schema](../linked_msa/SCHEMA.md). This directory's training inputs, fitted models and completed results remain the frozen reference.

Finalized November 9, 2026. **All 500 roster identities collected; 498 firms
eligible. Expanded models have now been trained and evaluated.** Read
[FINAL_RESULTS.md](FINAL_RESULTS.md) and [TRAINING_RUN.md](TRAINING_RUN.md). The redundant parent 98-firm experiment has been retired; compact source checks, original labels, feature specifications, folds and summary metrics remain under `reference_inputs/` for reproducibility.

This is the same 2025 publisher-selected HQ study, expanded from a stratified
sample to an attempted census. The same 50 metros, 31 regional factors, four
company characteristics, four preset interactions and whole-MSA folds are retained.
The two existing HQ-role exclusions remain unknown everywhere.

| Contract | Metro aggregate | Company–metro HQ |
| --- | ---: | ---: |
| Full supervised rows | 50 | 24,900 |
| Development rows | 49 | 24,402 |
| Reserved Atlanta rows | 1 | 498 |
| Primary input columns | 31 | 39 |
| Known HQ positives in the frame | 435 | 435 |

The covered roster includes 63 firms whose resolved HQs are outside the selected
50 metros. They remain in the common denominator of 498, contributing zeros to
the narrow selected-point target. The audit grid has 25,000 cells: 435 positive,
24,465 zero and 100 unknown. A zero does not mean absence of ordinary offices.

The regional predictors are copied byte-for-byte from the original study, with
the same four missing cells. Those gaps repeat as 1,992 company–metro numeric
nulls. Primary company fields are complete. Optional revenue growth remains
missing where unpublished; no imputation, encoding or scaling has been fitted.

The expanded Atlanta observed count is 15 publisher-selected HQs. This is a
descriptive count, not a new model expectation or evidence of a deficit.

Training results are saved separately under `reports/training` and `models`.
All 70 training-artifact checks pass. For the dataset, start with
[TRAINING_HANDOFF.md](TRAINING_HANDOFF.md), the
[machine-readable training contract](config/training_contract.json),
[SOURCES.md](SOURCES.md), and [OMISSIONS_AND_COVERAGE.md](OMISSIONS_AND_COVERAGE.md).
All **94 data acceptance checks pass**; see [VALIDATION.md](VALIDATION.md).

## Rebuild offline

From the repository root, with the documented NumPy/pandas environment:

```sh
python study_1/scripts/build_expanded_500.py
python study_1/scripts/build_expanded_500.py --validate-only
```

The offline builder starts from compact retained normalized tables and citations;
no removed raw payload or network request is needed. The shared company-feature
helper now derives roster sizes dynamically while preserving its original
98-firm output contract. The original model-training script remains frozen to
that earlier experiment. [train_expanded_500.py](../scripts/train_expanded_500.py)
uses the expanded contract and reuses the original fitting functions.

The offline builder is self-contained: normalized economic inputs already live in `tables/`, and inherited company checks/method references live in `reference_inputs/`. It no longer reads the removed parent tables/configuration. Historical hashes are retained; exact cleanup transitions are checked against the [migration record](../CLEANUP.md).
