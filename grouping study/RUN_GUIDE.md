# Run and inspect the grouping study

The completed findings are in [FINAL_RESULTS.md](FINAL_RESULTS.md). The eight original protocol documents retain their preparation-stage wording and bytes. This guide describes the implemented run.

## Organization

| Folder | Contents |
| --- | --- |
| `config/` | Frozen execution contract, source hashes, outer settings, family selection and final settings. |
| `tables/` | Unique company/metro profiles, supplied splits, development rows, predictor-only Atlanta rows and separate Atlanta labels. |
| `scripts/` | Shared math, preparation, fitting/sensitivities, independent verification and report generation. |
| `models/` | Four final serialized artifacts with pipelines, allowed features, parameters, donor state and training views. |
| `reports/` | Flat CSV tuning/prediction/support/sensitivity tables, verification results, metadata and artifact inventory. |

All new work stays here. Study 1 and Artem inputs remain read-only. The scripts never access `private/`, restricted workbooks, licensed location rows or ordinary-office labels. Company IDs and all CBSA fields must be read as strings. `common.read()` preserves them and uses round-trip float parsing. CSVs retain original probability precision; Markdown displays rounded values.

## Environment and entry points

Use Python 3.12 with the exact versions in [the contract](config/execution_contract.json) and `study_1/requirements-training.txt`. This execution used Python 3.12.14 from the bundled runtime and the existing pinned `study_1/.training_runtime` packages, without dependency installation or upgrades. Do not load the joblib files in an incompatible environment.

From the repository root, these are the local commands used:

```sh
GROUPING_PYTHON=/Users/shanelarkin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
export PYTHONPATH=study_1/.training_runtime
export PYTHONDONTWRITEBYTECODE=1
"$GROUPING_PYTHON" "grouping study/scripts/verify.py" --fixture-only
"$GROUPING_PYTHON" "grouping study/scripts/prepare.py"
"$GROUPING_PYTHON" "grouping study/scripts/run_study.py"
"$GROUPING_PYTHON" "grouping study/scripts/verify.py"
"$GROUPING_PYTHON" "grouping study/scripts/report_results.py"
```

On another machine, use an active Python 3.12 environment with the pinned requirements and omit the local package-path override. Preparation rejects version mismatches. Fitting and verification enforce one CPU thread. No network access is needed with the normalized source tables and pinned packages present.

Preparation and fitting overwrite **this folder's** derived outputs. Preserve a completed run elsewhere before intentionally rerunning. Do not run any inherited training or collection entry point. `verify.py` reads the saved run and rewrites only its own verification reports here. `report_results.py` regenerates the narrative, sector support table and inventory from verified results.

## Reading the tables

- Start with `model_comparison.csv` and `atlanta_assessment.csv`; the selected family is frozen in `config/selection_frozen.json`.
- Company prediction keys are `(method, company_id, cbsa)`. Metro prediction keys are `(method, cbsa)`. Each method covers the same 498 companies.
- Tuning rows contain inner-split diagnostics and a `pooled` row per candidate/context. Only pooled rows select parameters. `selected_focus` and `selected_grouped` identify each procedure's selection.
- `raw_focus_weight` comes from that query's training-only regional transform. `focus_weight` is normalized once across all 49 outer metros, identically for every method.
- `support.csv` keys are `(context, company_id, cbsa)`. Effective pair size is a weight-concentration statistic, not independent observations. A selected alpha of zero differs from a positive alpha suppressed by the support gate.
- Alpha-zero fits have no selected neighbor ranks. Their donor explanations use the frozen widest grid pair, rank 20/150, solely for diagnostics. The final report states whether those weights contribute to predictions.
- Final support and leave-one-metro ranges in the company prediction table apply only to GROUPED rows. Other procedures have blanks in those columns. Ranges are prediction-instability summaries, not confidence intervals.
- All 67 final sensitivity cases retain company and sector predictions. The New York outer influence table compares the same 48 test metros, retains original focus weights and refits training components without retuning.
- `fit_attempts.csv` records actual distinct fitted models, including failures. Identical training-geography/C fits are cached across contexts; `split_audit.csv` and `transform_audit.csv` record each prediction context separately.
- `output_manifest.csv` hashes every delivered file except itself and counts CSV data rows. It includes protocol, code, models, checks and results. `config/input_manifest.csv` separately records every consumed upstream/protocol/code input before fitting.

Joblib artifacts contain the final pipeline, feature specification, fixed settings, donor rows and normalized distance/kernel state. Reload verification recomputes predictions from the pipeline and donor rows. The stored training target is never a predictor. Atlanta labels are loaded for modeled assessment only after the final family/settings freezes and label-free prediction export.

Bootstrap intervals use frozen paired predictions and omit refitting/selection uncertainty. Atlanta error bands use weighted absolute held-out residuals and are heuristic. A positive Atlanta observed-minus-expected value indicates more reported HQs than the point benchmark. It is not an office gap, recruitment target or causal policy effect.
