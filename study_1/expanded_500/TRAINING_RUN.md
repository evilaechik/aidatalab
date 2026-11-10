# Completed expanded-cohort training

November 9, 2026. Both tracks, shared employment/mean baselines, and the two
main-effects company-model ablations have been trained and evaluated. Read
[FINAL_RESULTS.md](FINAL_RESULTS.md) for each model's results and interpretation.

## Reproduce

Use the same Python 3.12 environment and pinned requirements as the original run:

```sh
study_1/.venv/bin/python study_1/scripts/train_expanded_500.py
study_1/.venv/bin/python study_1/scripts/verify_expanded_training.py
```

If that environment does not exist, create it from the repository root:

```sh
python3.12 -m venv study_1/.venv
study_1/.venv/bin/python -m pip install -r study_1/requirements.txt -r study_1/requirements-training.txt
LOKY_MAX_CPU_COUNT=1 study_1/.venv/bin/python study_1/scripts/train_expanded_500.py
```

Replace the last script path with `study_1/scripts/verify_expanded_training.py`
to verify this run. Raw payloads and local environments are excluded from Git;
restore the source bundle described in [publication notes](../PUBLIC_REPOSITORY.md) for full rebuild/validation.
[requirements-training.txt](../requirements-training.txt)
provides the portable environment definition; actual versions are recorded in
[run_metadata.json](reports/training/run_metadata.json).

## What stayed the same

The expanded trainer imports the original preprocessing, estimators, nested
tuning, prediction aggregation, calibration diagnostics and uncertainty functions
directly from the frozen original trainer. The shared fitting script remains unchanged; compact original comparison inputs remain in `reference_inputs/` while redundant execution artifacts are retired. The expanded orchestration uses the new 498-firm
contract, the expanded acceptance validator, and population-appropriate reports.

- The same 49 development metros and five outer folds, with 10/10/10/10/9 metros.
- Inner tuning holds out each remaining supplied fold; final tuning uses all
  five development folds. No random company-row splits.
- The same 31 regional inputs, 39 company-track primary inputs and 35-input
  company-model main-effects ablations. No new predictors or financial sensitivities.
- The same three Poisson alpha values, three logistic C values and four shallow
  XGBoost depth/tree-count combinations, penalties, learning rate and seed.
- Training-fold regression imputation, missing flags and scaling; training-fold
  category encoding; native XGBoost numeric null handling; one CPU thread.
- Natural event prevalence, no class rebalancing, no probability thresholding or
  per-company geographic normalization, and no post-hoc probability calibration.
- Primary selection by OOF metro-count MAE, then RMSE, then declared order.
  Main-effects ablations remain diagnostic. Secondary metrics do not change selection.

The 24,402 development pairs contain 420 HQ positives and the same 498 firms in
each metro. Baseline company probabilities divide the fold-fitted expected count
by 498, and all B metro expectations sum the same 498 company probabilities.

## Atlanta assessment and uncertainty

After OOF comparison and final development-only tuning/fitting, the selected
model and parameters were saved to
[selection_frozen.json](reports/training/selection_frozen.json). Only then were
Atlanta's 1 aggregate/498 company rows loaded for modeled assessment. The data
acceptance validator may inspect Atlanta for QC, as allowed by the original
handoff. Atlanta has already been inspected in earlier research, so this follow-up
is not a fresh analyst-blind test. No model or interpretation was selected to
produce a deficit.

Two thousand seeded bootstrap replicates resample whole metros for count metrics
and paired MAE differences. Additional B intervals independently resample shared
company and metro clusters. These intervals use fixed OOF predictions; they omit
refitting, tuning and winner-selection uncertainty. They are descriptive rather
than formal significance guarantees or new-company validation.

Atlanta bands use the 45th ordered absolute OOF residual among the 49 metros,
adding/subtracting it from the final expectation and truncating the lower end at
zero. These are heuristic 90% prediction-error bands, not confidence intervals for
the expected count and not formal conformal coverage guarantees.

## Saved results and checks

All outputs are separate from the original run:

- `reports/training/model_comparison.csv`, `fold_metrics.csv`: count benchmarks.
- `oof_metro_predictions.csv`: 490 model/metro held-out counts and residuals.
- `oof_company_probabilities.csv`: 146,412 model/company/metro held-out probabilities.
- `probability_comparison.csv`, `calibration_bins.csv`: probability scores and
  calibration diagnostics; diagnostic slopes never alter predictions.
- `uncertainty.csv`, `paired_mae_vs_employment.csv`: declared cluster intervals.
- `atlanta_assessment.csv`, `atlanta_company_probabilities.csv`: final assessment.
- `original_vs_expanded.csv`: both experiments' metrics, percentage MAE improvement
  relative to their own employment baselines, and Atlanta observed/expected gaps.
- `observed_scorecard.csv`, `sector_diagnostics.csv`: descriptive breakdowns.
- `tuning_scores.csv`, `selection_frozen.json`, `run_metadata.json`: audit trail,
  package versions, seeds, final/outer settings and input/code hashes.
- `models/*.joblib`, `models/*.ubj`, `models/baselines.json`: final fitted pipelines,
  native tree learners and baseline rates. The joblib pipelines retain encoding
  and other preprocessing required for predictions.
- [artifact_validation.json](reports/training/artifact_validation.json): all
  **70 artifact checks pass**, including independent metric recomputation,
  original fold/grid equality, probability/count reconciliation, no excluded
  firms, development-only imputation, selection-rule checks and model reloads.

The 94-check data acceptance summary and collection configuration retain the
collection-stage status; they are not current model-run status records.
`reports/training/run_metadata.json` and `config/training_status.json` describe
this completed run. The source training contract remains the immutable input
record captured in the frozen selection hashes.

More firms improve coverage but do not add independent metro environments. These
remain retrospective reported-HQ benchmarks with two unresolved exclusions,
four unique regional input gaps and no causal policy interpretation. Consult
[SOURCES.md](SOURCES.md) for the source-check limitations and
[the original method references](../feature_refinement/TRAINING_RUN.md).
