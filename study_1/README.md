# Study 1 — expanded HQ benchmark

The latest completed study is the November 10, 2026 [regional feature comparison](feature_refinement/README.md). Read its [final results](feature_refinement/FINAL_RESULTS.md), [run guide](feature_refinement/TRAINING_RUN.md) and [validation](feature_refinement/VALIDATION.md).

The selected R1 company logistic model has held-out metro-count MAE 3.564, versus 4.113 for its R0 counterpart and 4.016 for employment. Atlanta has 15 observed HQs against an expectation of 9.17; this does not identify an overall HQ deficit. See the results for uncertainty and limitations.

| Location | Purpose |
| --- | --- |
| `feature_refinement/` | Latest R0/R1 comparison, 34/42-input training tables, fitted R1 models and results |
| `expanded_500/` | Frozen R0 reference: 500 roster firms, 498 eligible firms, 50 metros; models and predictions reused by R1 |
| `expanded_500/reference_inputs/` | Ten compact original-study inputs needed for source checks, fixed methods and historical metric comparisons |
| `linked_msa/` | Linked regional indicators, source lineage and partial office/function evidence |
| `source_data/` | Required CBP, QCEW, BDS payloads and original manifests for all 50 metros |
| `scripts/` | Offline builders, trainers, artifact verifiers and migration integrity checks |
| `provenance/cleanup_manifest.json` | Exact hashes for approved file relocations, retirements and code/documentation changes |
| `.training_runtime/` | Ignored installed training dependencies; retained for local execution |

## Run or verify

Use Python 3.12. Portable setup inside Study 1:

```sh
python3.12 -m venv study_1/.venv
study_1/.venv/bin/python -m pip install -r study_1/requirements.txt -r study_1/requirements-training.txt
```

To inspect the saved study without rebuilding or refitting:

```sh
python study_1/scripts/build_expanded_500.py --validate-only
python study_1/scripts/build_linked_msa.py --validate-only
python study_1/scripts/verify_expanded_training.py
python study_1/scripts/verify_feature_refinement.py
```

The validators write their acceptance reports. Use the configured Python environment described in the [run guide](feature_refinement/TRAINING_RUN.md).

The complete offline preparation order is expanded HQ tables, linked indicators, then feature-refinement tables:

```sh
python study_1/scripts/build_expanded_500.py
python study_1/scripts/build_linked_msa.py
python study_1/scripts/build_feature_refinement.py
python study_1/scripts/verify_feature_refinement.py --data-only
```

Rebuilding updates preparation manifests; run the documented training stage before checking newly built tables against a new selection record. Existing saved models are verified using their original frozen manifests and the recorded cleanup transitions. [train_expanded_500.py](scripts/train_expanded_500.py) reproduces R0; [train_feature_refinement.py](scripts/train_feature_refinement.py) fits R1 and reuses the saved R0 artifacts.

The shared [train_hq_2025.py](scripts/train_hq_2025.py) remains a library of frozen fitting functions. Use the expanded/refinement runners as entry points; its old 98-firm entry point is retired.

## Methods and sources

The [feature catalog](STUDY_1_FEATURE_CATALOG.md), [original design record](STUDY_1_METRO_BENCHMARK_PLAN.md), [collection protocol](COLLECTION_PROTOCOL.md), [source guide](SOURCES.md) and [linked schema](linked_msa/SCHEMA.md) retain the essential design, definitions and evidence. The original design documents describe the initial sample; current cohort sizes and input contracts are in the expanded/refinement directories.

The [cleanup record](CLEANUP.md) documents the removed legacy experiment and the source dependencies formerly under the top-level `data/` folder. All expanded/refinement model files, supervised tables, predictions and selection records were preserved. Office-presence labels remain incomplete; office classifiers, weighted scoring and bespoke tech/healthcare outcomes remain deferred.

For public sharing, raw payloads and installed environments are excluded from Git while their local copies remain. See [public repository notes](PUBLIC_REPOSITORY.md) for the source bundle required by a full rebuild and validation, and the distinction between current ignore rules and existing Git history.
