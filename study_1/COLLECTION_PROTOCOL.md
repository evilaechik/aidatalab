# Collection and preparation protocol — two HQ tracks

Historical design/method record for the initial sample. The current completed study uses 498 eligible firms and three additional regional features; use the [current run index](README.md) and [feature-refinement contract](feature_refinement/config/training_contract.json). Original methodological choices and collection dates below remain documented.

**Scope update — November 10, 2026:** the protocol below records the original 100-firm collection. The later [linked-data protocol](linked_msa/config/collection_protocol.json), [schema](linked_msa/SCHEMA.md) and [raw-archive guide](linked_msa/raw_archive/README.md) cover the new all-industry regional and partial office/function collection. The [current training handoff](linked_msa/TRAINING_HANDOFF.md) specifies how that collection may enter the next HQ comparison; unknown office presence stays unknown.

Updated November 9, 2026 · The sampling design and collection were frozen November 8.

Both tracks use the same 2025 publisher-selected HQ points, fixed selected cohort,
50-MSA frame and economic inputs. The November 9 company–metro extension only
reorganized retained data. No broader office collection or new external financial
collection was needed. [The study plan](STUDY_1_METRO_BENCHMARK_PLAN.md) describes
the two aims and method families; [the handoff](expanded_500/TRAINING_HANDOFF.md) governs training.

## Population, geography and dates

Preserve the fixed Fortune 500 2025 roster identities and 100-firm draw across
73 sector × list-position-band × publisher-listing strata. Keep the complete
selected roster in the coverage ledger and the same 98 eligible firms in both
tracks. Do not replace exclusions based on favorable HQ outcomes. Historical
roster identities remain fixed through later corporate actions and name changes;
those events do not establish physical office closure.

Use the existing 50 MSAs and July 2023 OMB/Census CBSA membership. Match publisher
coordinates to CBSA polygons, not mailing-city strings; retain out-of-frame
CBSA codes and micropolitan areas rather than assigning a nearby selected MSA.
Exact street verification is not required under the relaxed evidence policy.

HQ labels are 2025 publisher-reported, not independently verified December 31
occupancy. Collection access date is November 8, 2026. Financials are primarily
FY2024; economic predictors are chiefly 2024 with lagged 2023 sector shares and
explicit later revision/release vintages. These dates must not be relabeled as
one common financial year or as information all available in 2025.

## Evidence and coverage

Use the public Fortune 2025 map as the consistent primary listing. Match company
identities, including the seven reviewed aliases. An official company/SEC source
route was searched for every selected firm; preserve the query, URL, scope and
access date. Finding a source does not mean its full contents or every office
were independently audited. No independent human verification is claimed.

Keep material HQ-role conflicts unknown after bounded source checks. Lululemon
and Autoliv remain excluded in every MSA. Keep known co-HQs as separate sensitivity
context; Kraft Heinz's publisher-selected Chicago point remains primary while
its additional Pittsburgh HQ is recorded separately. See
[OMISSIONS_AND_COVERAGE.md](expanded_500/OMISSIONS_AND_COVERAGE.md).

## Labels and denominators

- `reported_hq_presence=1`: eligible firm's selected HQ point is in this CBSA.
- `reported_hq_presence=0`: that point is elsewhere, including outside the frame.
- Empty numeric CSV field / SQL NULL: unresolved HQ-role coverage; excluded
  everywhere, not an imputed zero.
- No general-office absence is established by directory omission, exclusion,
  a failed search, or a selected-HQ zero.

The audit grid contains 5,000 cells: 86 positives, 4,814 zeros and 100 nulls.
The covered 98 firms include 12 with resolved HQs outside the frame. They contribute
zero to each selected MSA while remaining in every common denominator. Metro
counts sum known labels; divide by 98 for covered-cohort shares, not 86 or 500.

Selected-100 bounds are the covered count through that count + 2 in each metro.
These are marginal bounds, not simultaneously attainable upper counts everywhere.
The raw 100-point publisher tally includes known role conflicts and is diagnostic
only. No default full-500 extrapolation or exhaustive co-HQ census is claimed.

## Two preparation contracts

| Contract | Metro aggregate track | Company–metro HQ track |
| --- | --- | --- |
| Rows and response | 50 MSA count rows | 4,900 known company–MSA binary labels |
| Features | 31 metro predictors | Same 31 plus 4 company fields and 4 preset interactions |
| Development / Atlanta | 49 / 1 | 4,802 / 98 |
| Predictor specification | [Metro allowlist](expanded_500/reference_inputs/feature_spec.json) | [Company–metro allowlist](expanded_500/reference_inputs/company_hq_feature_spec.json) |
| Models planned | Shared baseline, regularized Poisson, conservative count XGBoost | Shared baseline, regularized logistic, conservative probability XGBoost |

The same whole-MSA folds govern both tracks. Track B sums company probabilities
into comparable metro counts; no probability threshold is applied. Use specified
company traits only in Track B. HQ location, known outside-frame status, IDs,
coverage, source metadata and target-derived resident-company aggregates remain
excluded from predictors in both tracks.

## Missing data and fitting boundaries

Retain source flags, ACS uncertainty, geography qualifications and source vintages.
Use consistent CBP 2023 sector shares rather than combining suppressed QCEW 2024
values with complete alternatives. Four unique regional predictor cells remain
null; they repeat as 392 cells in Track B. Primary company fields are complete.

The collection stage performs no global imputation, scaling, encoding, calibration
or model fitting. The completed [training run](feature_refinement/TRAINING_RUN.md) fits permitted
preprocessing and models within development training data only.
Fit these operations and any tuning/selection inside development training folds.
Never impute unknown outcomes. Reserve all Atlanta rows from those operations
and from track/model selection. Labels were visible for data QC; no analyst-blind
holdout is claimed. Keep natural event prevalence in the binary track unless a
separately declared correction/calibration procedure justifies another choice.

## Formats, retention and reproduction

Use UTF-8 CSV, snake_case columns, stable company IDs, five-character CBSA strings,
ISO dates and numeric values without thousands separators. Null numeric fields
remain empty/SQL NULL. [Table schemas](expanded_500/config/table_schemas.json) declare keys and
types; SQLite supplies the same normalized and derived tables.

Raw HTML/TXT/PDF/ZIP payloads and obsolete bulk reports were removed after validation.
Keep [source links](SOURCES.md), compact ledgers, normalized inputs, flags, hashes,
rebuild code and current validation reports. Offline rebuilding reproduces tables
from those inputs; it does not re-verify live sources or recover removed responses.

The unused current-2026 office-positive archive was retired during cleanup; it supplied
neither 2025 HQ labels nor supported office negatives. General-office expansion
would require a new collection scope and coverage policy. Keep all study files
and eventual model artifacts inside `study_1`.
