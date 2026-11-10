# Training handoff — linked-data feature refinement

Updated November 10, 2026. This is the **current handoff for the next study stage**. The completed 98-firm and 498-firm model runs remain historical references. No new model has been trained on the linked collection.

The next question is whether a small amount of additional, consistently collected regional detail improves the **same 2025 HQ benchmark**. The broader company-location/function tables support descriptive review and future outcome construction. They do not yet supply a supervised office-presence outcome.

## Readiness and scope

| Component | Current state | Next use |
| --- | --- | --- |
| Expanded HQ labels, original predictors and saved models | Completed and training-ready | Frozen reference, named R0 below |
| Additional regional indicators | Populated; proposed three-feature bundle specified below | Check geography/units and build separate R1 training matrices before fitting |
| Company locations and functions | 254 new assertions across 112 firms; partial evidence and mixed fiscal-reference periods | Descriptive evidence, coverage review and later label development |
| Office-presence labels | Positives plus unknowns; no verified absence population | No office-presence classifier or office-gap ranking yet |
| MSA scorecard | Unweighted, with lower bounds and coverage fields | Review alongside HQ results; no composite training target |
| Weighted score and parallel broader-outcome models | Deferred | Define separately after reviewing the feature-refinement results |

Keep the full 500-company roster and all 50 MSAs. HQ supervision still uses the same **498 eligible firms**, including 63 outside-frame HQs. Preserve 435 in-frame HQ positives and Atlanta's 15. The two existing HQ exclusions stay unknown everywhere. Block's new no-designated-HQ disclosure qualifies broader-presence evidence; it does not silently revise this frozen publisher-selected-point outcome.

Bespoke technology/healthcare collection and new sector-specific models remain deferred. The four existing company–metro interactions stay in R0/R1 for comparability; the existing main-effects ablations expose their contribution. No new industry-specific interaction is introduced.

## Authoritative inputs and table roles

Use `study_1/expanded_500` for the company master, HQ labels, economic reference tables and split assignments. Use `study_1/linked_msa` for the additional indicators, location evidence and descriptive scorecard. Do not substitute the parent study's 98-firm training tables.

| Input | Key / selection | Role |
| --- | --- | --- |
| `../expanded_500/tables/company_cohort_500.csv` | `company_id` | Fixed company identity and attributes |
| `../expanded_500/tables/training_aggregate_2025.csv` | `cbsa` | 50-row aggregate HQ reference |
| `../expanded_500/tables/training_company_metro_hq_2025.csv` | `company_id, cbsa` | 24,900 known-label HQ pairs |
| `../expanded_500/tables/msa_split_assignments.csv` | `cbsa` | Existing 49 development metros, five folds and reserved Atlanta |
| [metro_indicators](tables/metro_indicators.csv) | `cbsa, metric_id, reference_period, sector_code, soc_code` | Long-format predictors/candidates; filter before widening |
| [company_locations](tables/company_locations.csv) | `location_id` | Reported points/locality groups and scoped local measurements; descriptive |
| [location_functions](tables/location_functions.csv) | `function_observation_id`; join `location_id` | Role evidence and source-reference dates; descriptive |
| [company_msa_coverage](tables/company_msa_coverage.csv) | `company_id, cbsa, reference_year` | Presence/unknown and screening audit; not an HQ training matrix |
| [metric_dictionary](tables/metric_dictionary.csv) | `metric_id` | Definition, unit, scope, missingness and analytical role |
| [msa_scorecard](tables/msa_scorecard.csv) | `cbsa` | Outcomes/diagnostics, excluded from X |

The six linked tables contain 32,400 / 753 / 834 / 50,000 / 119 / 50 rows respectively. These are table records, not independent regional observations. Only 49 development metro environments are available. The 119 dictionary rows are not a 119-predictor allowlist.

The exact schemas and date rules are in [SCHEMA.md](SCHEMA.md). Source URLs and detailed evidence remain in [raw_archive](raw_archive/README.md); source IDs may accompany audit exports but never enter X. Empty numeric CSV cells are null, not zero. Read keys/codes as strings and preserve blank sector/SOC codes explicitly.

## Next comparison: R0 versus R1

R0 is the unchanged expanded-cohort reference: 31 regional inputs in Track A and 39 raw inputs in Track B. R1 appends the following **three general regional features as one fixed bundle**, giving 34 inputs in A and 42 in B. B retains the same four company fields and four preset interactions. Its R1 main-effects-only diagnostic has 38 raw inputs. One-hot encoding changes fitted matrix width, not these collected-input counts.

| New output column | Exact `metro_indicators` selector | Value and interpretation |
| --- | --- | --- |
| `cbp_management_employment_share_2023` | `metric_id=cbp_employment_share`, `reference_period=2023`, `sector_code=55`, `soc_code` blank | Published sector employment / total CBP employment; fraction. Broad corporate-management activity across industries, including holding companies. |
| `bds_establishment_entry_rate_2023` | `metric_id=bds_estabs_entry_rate`, `reference_period=2023`, `sector_code=00`, `soc_code` blank | Published all-industry establishment entry rate; percent, not a named-company relocation rate. |
| `bds_establishment_exit_rate_2023` | `metric_id=bds_estabs_exit_rate`, `reference_period=2023`, `sector_code=00`, `soc_code` blank | Published all-industry establishment exit rate; percent, not a corporate-office closure rate. |

Each selector currently returns exactly 50 numeric values. All three retain `native_program_cbsa_not_independently_rebuilt` geography status. **Numeric completeness does not finish geography validation.** Before fitting, check each program's boundary vintage/membership against the fixed frame and record the result. Resolve a mismatch using comparable geography, or leave the incompatible values null under a documented rule. If a feature cannot be made meaningful under that rule, omit it from the entire proposed bundle and record a revised allowlist before fitting. Keep the same metro evaluation population; do not quietly drop difficult metros or substitute other years/programs.

This is a specified next experiment, not an implemented/fitted feature specification. Collection-time `selected_for_new_model=0` flags remain accurate. The future runner must write a versioned configuration containing the final selectors, units, null/geography decisions, input hashes and exact allowlists before fitting. Do not load every numeric indicator, all broad sectors, sparse local jobs/space or evidence-coverage flags into a learner. No additional feature search or new interactions are part of this default comparison.

Construct R1 by widening only these selectors to one row per CBSA, joining them one-to-one to A and many-to-one to B. Start with the existing split-specific training files. Require unchanged keys, rows, labels, folds, old predictor values and company roster in every metro. A minimal extraction pattern, run from the repository root:

```python
from pathlib import Path
import pandas as pd

root = Path("study_1")
ind = pd.read_csv(root / "linked_msa/tables/metro_indicators.csv",
                  dtype=str, keep_default_na=False)
choices = {
    "cbp_management_employment_share_2023": ("cbp_employment_share", "55"),
    "bds_establishment_entry_rate_2023": ("bds_estabs_entry_rate", "00"),
    "bds_establishment_exit_rate_2023": ("bds_estabs_exit_rate", "00"),
}
series = []
for name, (metric, sector) in choices.items():
    rows = ind.loc[(ind.metric_id == metric) &
                   (ind.reference_period == "2023") &
                   (ind.sector_code == sector) & (ind.soc_code == "")]
    assert len(rows) == 50 and rows.cbsa.is_unique
    series.append(pd.to_numeric(rows.set_index("cbsa").value,
                                errors="raise").rename(name))
extra = pd.concat(series, axis=1).reset_index()
dev = pd.read_csv(root / "expanded_500/tables/training_development_2025.csv",
                  dtype={"cbsa": str})
joined = dev.merge(extra, on="cbsa", how="left", validate="one_to_one")
assert len(joined) == 49 and "12060" not in set(joined.cbsa)
```

This example checks extraction/join cardinality. Apply the documented geography decision before treating `extra` as eligible X. Source-derived deterministic calculations may be prepared without target information; all learned transformations stay within training folds.

## Preserve the benchmarking design

- Track A: fold-fitted employment-proportional and mean-count baselines, L2-regularized Poisson regression and shallow count XGBoost. Target: `reported_hq_count_2025`.
- Track B: the same baselines, L2-regularized logistic regression and shallow binary XGBoost. Target: `reported_hq_presence`. Preserve the main-effects diagnostics for comparability.
- Reuse the supplied whole-MSA outer folds: 10/10/10/10/9 development metros. Inner tuning leaves out each remaining supplied fold. Every company row for one metro stays together. No random row split.
- Reuse [the frozen training plan](../expanded_500/config/training_plan.json): seed 20261109; Poisson alpha 10/1/0.1; logistic C 0.01/0.1/1; XGBoost depths 1/2 and 100/250 trees with the existing penalties, learning rate and one-thread setting. Do not expand the search because more indicators exist.
- Fit regression imputation, missing flags, scaling and B category encoding on training folds only. Retain XGBoost's existing native numeric-null handling and fold-fitted category encoding. Keep natural prevalence, no rebalancing and no post-hoc probability calibration.
- Estimate the employment baseline rate on training metros only. B baseline probability is expected count / **498**. Sum all 498 company probabilities per held-out metro without thresholding or per-company normalization across metros. Do not force totals to observed counts.
- Compare equal-MSA OOF count MAE first, RMSE second, then the declared order. Keep the existing model order within each feature set and prefer R0 for an exact remaining tie. Shared A/B baselines are the same predictions, not independent evidence. Main-effects variants remain diagnostic.

Report paired **R1 minus R0** MAE for each fitted model and improvement over the shared employment baseline. Negative paired error differences favor R1. Report fold/per-metro differences, not just a single pooled score. B additionally reports log loss, Brier score and calibration. A lower secondary metric alone does not change the MAE-based primary selection.

Use 2,000 seeded whole-metro bootstrap replicates for fixed-roster count comparisons. For company-model sensitivity, retain the existing crossed company/metro resampling. State that fixed-OOF intervals omit refitting, tuning and winner-selection uncertainty. Reuse the existing heuristic Atlanta prediction-error band with its limitations; do not call it a causal confidence interval or formal conformal guarantee.

Keep every Atlanta row out of fitting, tuning, preprocessing, calibration and model/feature selection. Freeze development comparison and final settings before generating the new Atlanta assessment. Atlanta has already been viewed in prior work; this follow-up is not analyst-blind. Choose no feature, model, score weight or interpretation to create a deficit.

## Leakage and outcome limits

Exclude HQ addresses/CBSA, inside-frame status, resident-company aggregates, observed HQ/sector counts, office/function presence, scorecard counts, local measured jobs/space, source IDs and evidence/coverage status from X. The location/function data were collected around reported company activity and do not supply independent baseline exposures. Do not convert office unknowns to negatives, sample them as controls or fit a positive-versus-unobserved classifier as a presence benchmark.

The two office-reference years are fiscal-period annotations, not a balanced occupancy panel. Do not pool them as interchangeable 2025 labels or difference them into openings/closures. Locality groups are not physical sites; function categories overlap. Do not add them into a total-office count. Detailed functions remain descriptive until their dates, geography and ascertainment are comparable across the roster.

Any later NAICS 55 outcome benchmark needs its own dated target, baseline, exposure, predictor list and validation contract. Remove predictors that mechanically reproduce that target, including the new management share/count and their numerator/denominator reconstruction where applicable. Whole-economy sector activity must not be allocated to individual Fortune firms. Weighted scoring and tech/healthcare outcome work remain separate later stages, with no weights chosen from Atlanta residuals.

Coefficients and SHAP values describe model associations. Correlated features, residual confounding and measurement/coverage differences prevent them from establishing that changing a factor would attract firms. Predictive gains would improve the benchmark; explanations of firm decisions still need separately verified events and research designs.

## Implementation and deliverables

Use a small new runner that reuses the existing fitting/preprocessing functions. Preserve the frozen trainers, old model files and old reports. Save the new experiment under a separate proposed directory, **`study_1/feature_refinement/`**; it is not created or trained by this documentation update.

Before fitting, create there a training contract, A/B feature specifications, geography/units decisions, input/split hashes and split-specific wide tables. Expected shapes are A: 50/49/1 rows with 34 predictors, and B: 24,900/24,402/498 rows with 42 predictors, if all three additions pass the gate. Use a new verifier aware of the revised column counts; the old hard-coded acceptance contracts remain unchanged. R0 saved predictions may be reused only after verifying identical targets, keys, folds, feature values, methods and hashes; otherwise reproduce R0 into the new directory.

Save per-model/per-fold metrics, OOF metro counts, B company probabilities, calibration, paired R1–R0 and baseline comparisons, uncertainty, frozen development selection, final Atlanta assessment, fitted pipelines and versions/seeds/runtime/hash metadata. Report every attempted specification, including failures. Finish with a concise `FINAL_RESULTS.md` stating each model's results, what they mean, whether extra detail helped, whether an Atlanta gap persists within uncertainty, and remaining limitations. Coverage and causal uncertainty remain separate from model-performance uncertainty.

## Preflight and current status

From the repository root, using the existing NumPy/pandas environment:

```sh
python study_1/scripts/build_expanded_500.py --validate-only
python study_1/scripts/build_linked_msa.py --validate-only
```

These commands validate existing inputs and do not train R1. The expanded trainer currently reproduces R0 only; running it does not automatically consume the new indicators. See [VALIDATION.md](VALIDATION.md) for acceptance gates, [SCHEMA.md](SCHEMA.md) for joins and [the completed expanded run](../expanded_500/TRAINING_RUN.md) for portable training-environment instructions.
