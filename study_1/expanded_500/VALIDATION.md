# Expanded data acceptance

All **94 automated acceptance checks pass**. [validation_summary.json](reports/validation_summary.json)
and [validation_checks.csv](reports/validation_checks.csv) are authoritative.
They validate dataset consistency and reproducibility, not predictive performance
or independent source accuracy. Expanded modeling is now complete; all
**70 training-artifact checks pass** in the separate
[artifact-validation report](reports/training/artifact_validation.json).
See [TRAINING_RUN.md](TRAINING_RUN.md) and [FINAL_RESULTS.md](FINAL_RESULTS.md).
The data summary retains its collection-stage status; current model-run status
is recorded separately in `reports/training/run_metadata.json`.

Checks cover:

- 500 unique stable roster IDs, all 73 strata and 21 sectors; unit census weights.
- 498 eligible firms and the same two excluded unknowns.
- All 500 publisher point assignments, one documented full-TIGER fallback,
  explicit name/rank/industry reconciliation and source routes for every firm.
- 25,000 audit cells: 435 ones, 24,465 zeros and 100 nulls.
- 24,900 supervised pairs with identical company rosters in every metro;
  development/Atlanta splits of 24,402/498 and 49/1 aggregate rows.
- Reconciliation of binary, aggregate, sector and co-HQ-sensitivity counts.
- The unchanged 31/39 predictor allowlists, complete primary company fields,
  and exactly four unique regional gaps repeated across 498 firms.
- Existing whole-MSA folds, no Atlanta development fold, and predictor separation.
- All original 5,000 audit labels, overlapping primary company values and
  inherited regional files preserved; retired original outputs recorded by hash in the [cleanup manifest](../provenance/cleanup_manifest.json).
- Retained input hashes, unique keys, SQLite integrity and matching CSV/SQL values.

Recheck offline from the repository root:

```sh
python study_1/scripts/build_expanded_500.py --validate-only
```

Use the same NumPy/pandas environment as the original study. See
[TRAINING_HANDOFF.md](TRAINING_HANDOFF.md) for the separate model-validation
requirements and [SOURCES.md](SOURCES.md) for actual source-check scope.
