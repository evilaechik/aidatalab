# Current Study 1 status

November 10, 2026 — the new regional-feature training handoff has been executed. Start with [feature_refinement/FINAL_RESULTS.md](feature_refinement/FINAL_RESULTS.md) and its [run index](feature_refinement/README.md).

The selected model is **R1 company logistic regression**: held-out metro-count MAE **3.564**, versus **4.113** for the previous logistic model and **4.016** for employment. Its Atlanta expectation is **9.17** against **15** observed, inside the heuristic 90% error band of **1.32–17.02**. There is no overall HQ deficit against the selected benchmark. The improvement over the old logistic model is clearer than the advantage over employment under the fixed-prediction uncertainty analysis.

| Location | Role |
| --- | --- |
| `feature_refinement/` | Completed R0/R1 comparison, new joined training tables, models, validation and detailed results |
| `expanded_500/` | Unchanged completed 498-firm HQ reference run |
| `linked_msa/` | General regional indicators and partial company-location/function evidence |
| `source_data/` | Retained CBP/QCEW/BDS inputs and original manifests, relocated from the removed top-level `data/` folder |
| `expanded_500/reference_inputs/` | Compact original source checks, labels, folds, feature specifications and comparison metrics |
| `scripts/` | Shared builders, lean training runners and artifact validators |
| `.training_runtime/` | Ignored local training environment, kept within Study 1 |

The captured handoff and earlier status documents remain records of their respective stages. The new run takes precedence for the completed feature-refinement result. Its 54 preparation checks and 148 full-run checks pass; the latter includes preparation checks. New fitting/reporting took approximately 54 seconds with one CPU thread, reusing the frozen R0 run.

Office-presence labels remain incomplete. Weighted scoring, broader-outcome benchmarks and bespoke tech/healthcare outcome work remain deferred, as specified in the handoff. The November 10 cleanup retired the old parent 98-firm outputs and obsolete tooling. Expanded/refinement supervised tables, fitted models, predictions and selection records remain unchanged; see [CLEANUP.md](CLEANUP.md).
