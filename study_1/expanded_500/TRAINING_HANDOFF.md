# Expanded-500 training handoff

**Current follow-up — November 10, 2026:** use the [linked-data training handoff](../linked_msa/TRAINING_HANDOFF.md) for the next regional-feature experiment. It retains these HQ targets, roster, splits and model families, specifies the new three-feature candidate bundle, and prohibits training on incomplete office labels. The executed instructions below reproduce the frozen 31/39-input reference; the existing trainer does not automatically ingest the new linked tables.

Data finalized November 9, 2026. **Both tracks have now been trained and evaluated**;
see [FINAL_RESULTS.md](FINAL_RESULTS.md) and [TRAINING_RUN.md](TRAINING_RUN.md).
The fitting instructions below describe the executed design. Use this directory as the
dataset root. Do not substitute the parent directory's original 100-firm inputs.

| Track | Full | Development | Atlanta assessment | Predictor specification |
| --- | --- | --- | --- | --- |
| Metro aggregate | [50 rows](tables/training_aggregate_2025.csv) | [49 rows](tables/training_development_2025.csv) | [1 row](tables/training_atlanta_2025.csv) | [31 numeric factors](config/feature_spec.json) |
| Company–metro HQ | [24,900 rows](tables/training_company_metro_hq_2025.csv) | [24,402 rows](tables/training_company_hq_development_2025.csv) | [498 rows](tables/training_company_hq_atlanta_2025.csv) | [39 primary inputs](config/company_hq_feature_spec.json) |

The covered denominator is **498**, including 63 outside-frame HQ firms. The
25,000-cell audit grid is not a supervised table: it contains the two exclusions'
100 unknown outcomes. Never impute those labels or convert them to zeros.

```python
from pathlib import Path
import json
import pandas as pd

root = Path("study_1/expanded_500")
spec_a = json.loads((root / "config/feature_spec.json").read_text())
spec_b = json.loads((root / "config/company_hq_feature_spec.json").read_text())
dev_a = pd.read_csv(root / "tables/training_development_2025.csv", dtype={"cbsa": str})
dev_b = pd.read_csv(root / "tables/training_company_hq_development_2025.csv",
                    dtype={"cbsa": str, "company_id": str})
X_a, y_a = dev_a[spec_a["primary_predictors"]], dev_a[spec_a["target"]]
X_b, y_b = dev_b[spec_b["primary_predictors"]], dev_b[spec_b["target"]]
assert X_a.shape == (49, 31) and X_b.shape == (24402, 39)
assert "12060" not in set(dev_a.cbsa) | set(dev_b.cbsa)
```

## Preserve the original experiment's choices

Use the same employment-proportional and mean-count baselines, regularized
Poisson/logistic models, conservative count/binary XGBoost, and preset
main-effects ablations. The copied [training plan](config/training_plan.json)
preserves the original small grids, seed and selection rule. Fit preprocessing
inside training folds; retain natural binary prevalence. All company rows for a
metro share its existing outer fold. Atlanta remains excluded from fitting,
tuning, preprocessing, calibration and model selection.

The original [trainer](../scripts/train_hq_2025.py) and verifier freeze the
98-firm experiment. The new [expanded trainer](../scripts/train_expanded_500.py)
and [artifact verifier](../scripts/verify_expanded_training.py) adapt the
acceptance-validator entry point, row counts, probability denominator, reporting
and outcome checks to [training_contract.json](config/training_contract.json).
The full-500 study's expectations must be learned again; do not multiply the
old model's predictions by five or overwrite the old results.

Compare equally weighted held-out metro count MAE, RMSE and Poisson deviance.
For B, sum all 498 probabilities without thresholding; the shared employment
baseline probability is the training-fold expected count divided by 498.
Also report log loss, Brier score and calibration. Cluster uncertainty by metro
and account for repeated companies. There are still only 49 development metro
environments despite the larger company table. Optional assets, profit margin
and revenue growth remain optional rather than primary predictors.

Freeze development model selection before the expanded Atlanta assessment.
This is a follow-up to an already inspected metro, not a fresh analyst-blind
test. A larger absolute MAE can reflect larger counts; compare improvements over
the baseline within this dataset rather than directly interpreting its MAE
against the original small-cohort MAE.

## Schema and formats

Keys, training filenames, targets, predictor names, column order and normalized
table structure follow the original schema. Necessary population-size name
changes are explicit in [collection_config.json](config/collection_config.json):

- `company_cohort_100.csv` becomes `company_cohort_500.csv`, with the same columns.
- `selected100_count_lower_bound` / `selected100_count_upper_bound` become
  `selected500_count_lower_bound` / `selected500_count_upper_bound`.
- `unreviewed_publisher_count_100` becomes `unreviewed_publisher_count_500`.

These diagnostic fields remain excluded from X. `sampled_company_n=500` records
the roster size even though the expanded collection is an attempted census.
Stable `company_id` uses unique list position; displayed ranks need not be unique.
All CSVs are UTF-8, CBSA identifiers are five-character strings, numeric nulls
are empty, and SQL nulls are NULL. [table_schemas.json](config/table_schemas.json)
declares each table's columns, types, keys and null counts. The equivalent SQLite
database is `study_1_expanded_500.sqlite`.

Source metadata, coverage flags, geographic identifiers and observed HQ/sector
counts are audit fields, never additional predictors. The labels concern one
publisher-selected reported HQ point per firm, not every office, local jobs or
an independently verified year-end occupancy census.
