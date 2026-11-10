# Validation and readiness for the training handoff

Updated November 10, 2026. The current linked-data validator passes **452 checks**. The initial collection passed 449; three added checks audit the explicitly authorized Markdown revisions. [validation_summary.json](reports/validation_summary.json) and [validation_checks.csv](reports/validation_checks.csv) are the current results. Structural acceptance is separate from scientific comparability and model performance.

## What is accepted

The checks verify all six tables' keys and available joins, unique evidence/source IDs, company/metro identity, CSV/SQLite consistency and absence of source URLs in the analytical tables. They preserve unknown office outcomes, suppressed employment/wages, disclosed QCEW establishments, original predictor values, 498 eligible HQ points, 435 in-frame positives and Atlanta's 15. Hash checks cover all 150 reused regional inputs and their original manifests.

The original [collection-time snapshot](config/prior_study_snapshot.csv) and [documentation revision ledger](config/documentation_revisions.csv) remain intact. The [cleanup record](../CLEANUP.md) supplements them with exact retirements, source relocations and code/documentation edits. The validator rejects unrecorded differences and checks original bytes at the new source paths. Expanded/refinement models, predictions, labels and fold contracts remain unchanged.

## Gates before the next model run

1. Run both existing data validators. Verify that the original supervised keys, labels, roster, old features and fold assignments are unchanged after the proposed additions are joined.
2. Check the exact three selectors in [TRAINING_HANDOFF.md](TRAINING_HANDOFF.md): one row per MSA, correct periods and sector/SOC codes, share versus percent units, and original source flags. The current selectors each have 50 numeric values; completeness alone does not settle geography.
3. Resolve or explicitly handle the candidates' source-native geographic qualifications against the fixed frame. Preserve the same evaluation metros. Save geography and null-treatment decisions before fitting.
4. Create a separate versioned training contract, feature allowlists, input hashes and split-specific matrices. Expected R1 predictors are 34 for A and 42 for B if the full bundle passes. No derived R1 matrices or trained R1 models exist at this handoff.
5. Keep source/coverage metadata, observed office functions, local jobs/space and scorecard outcomes outside X. Do not convert the office grid's unknowns to negative labels.
6. Use unchanged whole-MSA nested validation, the small existing model grids, fold-fitted preprocessing and development-only selection. Save OOF predictions and paired R1–R0 comparisons before the final Atlanta assessment.

Readiness remains split: the original expanded HQ experiment is reproducible; the next regional-feature experiment requires the preparation above; broader office-presence models, weighted scores and sector-specific outcomes remain deferred. Passing these checks cannot certify office completeness, causal attribution or a policy effect.

## Commands

Run from the repository root with the existing NumPy/pandas environment:

```sh
python study_1/scripts/build_expanded_500.py --validate-only
python study_1/scripts/build_linked_msa.py --validate-only
```

These validate current data and write acceptance reports; they do not fit models. Preserve completed-run artifacts. Use a new feature-refinement runner/verifier rather than editing the frozen trainers or their input-size contracts. Portable model-environment setup is documented in the [completed expanded training guide](../expanded_500/TRAINING_RUN.md).
