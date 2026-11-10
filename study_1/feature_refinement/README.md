# Study 1 — regional feature refinement

This run compares the completed expanded-cohort **R0** HQ benchmark with **R1**, which adds three general regional features. It implements the [handoff captured before fitting](config/TRAINING_HANDOFF_INPUT.md). The 500-company roster, 498 eligible HQ firms, 50 MSAs, five development folds and Atlanta assessment are unchanged.

The captured handoff is an immutable verbatim input; its relative links use the original linked-data directory as their base. Some historical targets were retired during cleanup; use the current run guide for execution. For working navigation, open the [original handoff](../linked_msa/TRAINING_HANDOFF.md).

R1 adds CBP 2023 corporate-management employment share and BDS 2023 all-industry establishment entry/exit rates. Track A has 34 inputs; Track B has 42, or 38 in its main-effects diagnostic. These metrics apply across industries. Office/function outcomes remain descriptive; weighted scores and bespoke technology/healthcare outcome models remain deferred.

Start with [FINAL_RESULTS.md](FINAL_RESULTS.md), [TRAINING_RUN.md](TRAINING_RUN.md) and [VALIDATION.md](VALIDATION.md).

| Directory | Contents |
| --- | --- |
| `config/` | Captured handoff, frozen feature lists and training plan, contract and input hashes |
| `tables/` | Three new metro features, dictionary/lineage, county membership, copied folds and six joined full/development/Atlanta training tables |
| `raw_archive/` | Official geography evidence, original payloads, source URLs and review notes |
| `reports/` | Data/artifact validation, geography audit, reference-reuse and output manifests |
| `reports/training/` | Combined R0/R1 metrics, OOF counts, paired comparisons, final selection, Atlanta assessment and run metadata |
| `reports/training/r1/` | New company probabilities, calibration, uncertainty, tuning and sector diagnostics |
| `models/r1/` | Six fitted pipelines, native XGBoost files and baseline rates |

The compact scripts are in the shared `study_1/scripts/` directory: [builder](../scripts/build_feature_refinement.py), [runner](../scripts/train_feature_refinement.py), and [verifier](../scripts/verify_feature_refinement.py). They reuse the frozen core fitting functions. Expanded/refinement tables, model files, predictions and selection records remain unchanged. The redundant original experiment was retired through the [documented cleanup](../CLEANUP.md).

R0's large probability files and fitted models are referenced in place, with hash/version checks and a [reuse manifest](reports/reference_reuse_manifest.csv). They are not duplicated or retrained. The new run's source URLs remain in `raw_archive`; model tables carry evidence IDs and numeric predictors.

The private training runtime is kept under `study_1/.training_runtime/` and ignored by Git. It is an environment, not an analytical deliverable. Model versions and portable setup are documented in the run guide.
