# Data contract and office-outcome gate

Protocol version 1.0 · November 25, 2026 · **Read existing inputs; derive nothing in the documentation-only stage.**

## Source of truth

Use the latest completed Study 1 R1 tables under `study_1/feature_refinement/`. Preserve their upstream R0 labels and folds. Earlier top-level documents sometimes describe the retired 98-firm sample, and inherited collection contracts can retain stale model-status wording. Current cohort facts and completed results take precedence; do not infer that R0/R1 are untrained from a historical contract string.

| Existing repository path | Role |
| --- | --- |
| `study_1/feature_refinement/tables/training_company_hq_development_2025.csv` | Primary supervised development matrix; 24,402 rows. |
| `study_1/feature_refinement/tables/training_company_hq_atlanta_2025.csv` | 498 Atlanta assessment rows; separate predictors from labels before selection. |
| `study_1/feature_refinement/tables/training_company_metro_hq_2025.csv` | Full 24,900 known-label pairs; audit only when enforcing splits. |
| `study_1/feature_refinement/tables/training_development_2025.csv` | 49 unique regional profiles, targets, and folds. |
| `study_1/feature_refinement/tables/training_atlanta_2025.csv` | Atlanta regional profile and observed aggregate target. |
| `study_1/feature_refinement/tables/msa_split_assignments.csv` | Supplied five whole-MSA development folds and reserved Atlanta. |
| `study_1/feature_refinement/config/company_hq_feature_spec.json` | Authoritative 42-column regression allowlist and two categorical fields. |
| `study_1/feature_refinement/config/feature_spec.json` | 34 regional predictors; use the exact subset specified for distance. |
| `study_1/feature_refinement/config/training_plan.json` | Inherited logistic settings, folds, seed, and reference fitting rules. |
| `study_1/expanded_500/tables/company_cohort_500.csv` | Full roster, identities, company attributes, and out-of-frame context for audit. |
| `study_1/expanded_500/tables/company_msa_hq_labels_2025.csv` | 25,000-cell audit including unknown excluded firms; not the training matrix. |
| `study_1/expanded_500/tables/firm_coverage_and_omissions.csv` | Exclusion and coverage policy. |
| `study_1/feature_refinement/reports/training/r1/oof_company_probabilities.csv` | Existing R1 company probabilities for exact reference comparisons. |
| `study_1/feature_refinement/reports/training/oof_metro_predictions.csv` | R0/R1 count predictions; select `feature_set=R1` and the correct model. |
| `study_1/feature_refinement/models/r1/B_logistic.joblib` | Saved global R1 model for unchanged final-reference prediction only. |

The linked-office evidence lives under `study_1/linked_msa/`; it is not an alternative HQ label source or additional regression input pool.

## Fixed counts and meanings

| Quantity | Expected value |
| --- | ---: |
| Fortune roster | 500 identities |
| Eligible HQ roster | 498 firms |
| Excluded firms | Lululemon and Autoliv; excluded in every metro |
| Metro frame | 50 MSAs |
| Development geography | 49 MSAs, supplied five folds |
| Atlanta CBSA | `12060` |
| Known-label full matrix | 24,900 = 498 × 50 |
| Development matrix | 24,402 = 498 × 49 |
| Atlanta matrix | 498 |
| Full audit cells | 25,000, including 100 unknown excluded-firm cells |
| HQ positives inside the frame | 435 |
| Development positives | 420 |
| Atlanta observed HQs | 15 |
| Covered firms whose selected HQ is outside the frame | 63 |

The target is `reported_hq_presence`, binary 0/1 on supervised rows. The aggregate target is `reported_hq_count_2025`. A zero means the selected publisher HQ point is elsewhere, not that ordinary offices, local employment, or additional HQ functions are absent. Outside-frame firms remain in the common 498 denominator. Preserve Block's point in the frozen target and its separately documented role conflict; do not silently revise historical labels.

## Types, keys, and joins

- Read CBSA, company ID, category strings, and evidence IDs as text. Preserve leading zeros where applicable.
- Company matrix key: `(company_id, cbsa)`; one row per pair. Metro profile key: `cbsa`.
- Every development/assessment metro contains the same eligible company IDs. Regional values are identical across a metro's company rows.
- Use a many-to-one join for regional profiles and company attributes, verifying unchanged cardinality. Never join long indicators by CBSA alone.
- Preserve source percent versus fraction units. Use the inherited log columns without another log transform.
- Numeric CSV blanks are nulls. Fit predictor imputation within training; never impute outcomes. Primary company fields are complete. Source suppression is not zero activity.
- One location/function observation is not necessarily one physical office; function categories overlap. They cannot be summed into an office count.

## Predictor contracts

The global regression uses the existing R1 `primary_predictors` exactly: 34 regional fields, four company characteristics, and four preset interactions, totaling 42 raw columns. Two company fields are categorical; fitted one-hot width can differ by fold. Preserve the interactions rather than adding new industry-specific hypotheses.

Distances use only the 15 regional columns and four company fields explicitly listed in [STUDY_DESIGN.md](STUDY_DESIGN.md). IDs may link records and order ties but do not enter either distance.

Prohibited in prediction and similarity: company/HQ names as learned features, actual HQ address/CBSA, known outside-frame status, HQ/sector counts, observed presence, local company jobs/space, source/evidence IDs, source availability, review completeness, split/fold IDs, scorecard values, and any resident-company aggregate reconstructed from the response. Names may appear in human-readable outputs only.

Do not use restricted business-license, revenue/employee, parcel, or incentive workbooks; licensed Data Axle location rows; or the untracked `private/` directory. The initial study needs none of these.

## Atlanta-label separation

Preparation may check label counts and key consistency, including the already-known count of 15. It must export predictor-only Atlanta inputs for training/tuning functions. Keep Atlanta outcomes in a separate assessment object/file. Selection and all transformations may use Atlanta covariates solely as specified, never Atlanta labels or residuals. Load labels for reporting after the final selection record is written.

## Reference reuse and provenance

At execution start, record hashes of every consumed input, fold file, allowlist, source code helper, reference prediction file, and model artifact, plus these protocol documents. Record package versions and the upstream cleanup/migration evidence. Match reference predictions by company/CBSA/model, not row order.

Reference predictions can be reused only with identical outcomes, eligible roster, folds, source values, and appropriate package compatibility for model reloads. If reproduction is needed, write the result here and disclose the reason; do not overwrite Study 1 or compare mismatched outcomes. Reusing source tables is not fresh independent source verification.

## Ordinary offices: future extension, not a substitute outcome

The retained collection has company-source location/function positives and unknown coverage, with uneven disclosure. It has no completed absence-capable national office audit. Do not convert unknowns to negatives or fit a positive-versus-unobserved classifier and call it presence prediction.

Before office fitting, a separate versioned contract must specify a roster, qualifying office/site functions, physical-site versus company–metro unit, comparable reporting dates, geography, source-review protocol, deduplication, and defensible negative-label coverage across Atlanta and donor metros. Unknowns must remain unknown. Regional/R&D/administrative office outcomes should remain separate from the selected-HQ outcome unless a new target explicitly combines them.

Future collection can concentrate on the input-selected Atlanta peer set rather than every national market, provided the same coverage standard is applied to all included company–metro cells. A deliberate positive-only study is a different design requiring explicit ascertainment assumptions and is not authorized by this HQ contract.

Until that gate is passed, produce no office classifier, office-gap ranking, total-office estimate, or combined HQ/office score. Office evidence may only be described with coverage and date qualifications.
