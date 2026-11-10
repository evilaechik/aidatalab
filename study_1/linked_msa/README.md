# Linked MSA and company-function collection

Collected November 10, 2026. The six planned tables are populated for the existing **500-company roster and 50-MSA frame**. The regional indicator collection is complete for the defined source extracts, with unavailable values retained. The company-office collection is a documented first source-screening pass, **not a complete national office census**.

**Training handoff:** [TRAINING_HANDOFF.md](TRAINING_HANDOFF.md) now specifies the next limited HQ feature-refinement comparison, exact candidate selectors, shared folds/models, leakage exclusions and deliverables. The three proposed additions need geography QA and separate training matrices/configuration before fitting. Office outcomes remain descriptive; weighted scoring and sector-specific outcome models remain deferred.

| Analytical table | Rows | Contents |
| --- | ---: | --- |
| [metro_indicators](tables/metro_indicators.csv) | 32,400 | Existing 31 predictors, their general economic levels, broad industry detail, business dynamics and general occupations |
| [company_locations](tables/company_locations.csv) | 753 | 500 inherited publisher points and 253 additional company/locality groups |
| [location_functions](tables/location_functions.csv) | 834 | 498 inherited reported HQ roles and 336 newly documented function observations |
| [company_msa_coverage](tables/company_msa_coverage.csv) | 50,000 | 500 companies × 50 MSAs × two source-reference years; positives and unresolved coverage |
| [metric_dictionary](tables/metric_dictionary.csv) | 119 | Definitions, units, calculation rules and permitted analytical roles; these are not 119 selected predictors |
| [msa_scorecard](tables/msa_scorecard.csv) | 50 | Unweighted HQ, documented function and corporate-management indicators with explicit dates and coverage |

[linked_msa.sqlite](linked_msa.sqlite) contains the six tables and small reference copies of company IDs and the metro frame. The existing full company master, economic files, split assignments and fitted models are reused without modification.

The additional collection covers headquarters and co-HQs, divisional management, R&D, engineering, internal finance/shared services, administration/back-office work, corporate sales/client services and offices with unspecified functions. Broad sector detail is collected consistently across industries. Bespoke technology/healthcare extensions remain deferred.

**Coverage:** all 500 firms received the same initial source-screening protocol; 460 returned indexed source text. Review retained **254 factual location assertions across 112 firms**, yielding 253 locality groups. Eight groups have unresolved metro assignments. One locality has explicit employment and 23 have explicit office area; undisclosed quantities remain null. Neither locality groups nor functional-role observations are physical-office counts.

Source URLs and detailed evidence live only in [raw_archive](raw_archive/README.md). Analytical tables contain source/evidence IDs. Read [COLLECTION_RESULTS.md](COLLECTION_RESULTS.md) for interpretation and [SCHEMA.md](SCHEMA.md) for joins and limitations.

The frozen HQ experiment remains unchanged: **435 in-frame HQ positives, including Atlanta's 15**. A newly identified HQ-role conflict is flagged for the broader study without revising that earlier benchmark. The scorecard has no weighted score and the incomplete office labels are not ready for a presence-classification model.

Offline rebuild, from the repository root using the existing NumPy/pandas environment:

```sh
python study_1/scripts/build_linked_msa.py
python study_1/scripts/build_linked_msa.py --validate-only
```

All **452 current acceptance checks** pass, including the documentation-revision audit; the collection baseline had 449 checks. Detailed results are in [validation_checks.csv](reports/validation_checks.csv) and [VALIDATION.md](VALIDATION.md). No model fitting or new train/test split occurs in this builder.
