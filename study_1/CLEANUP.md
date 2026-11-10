# Study 1 cleanup — November 10, 2026

The cleanup keeps the completed expanded HQ reference (R0), latest regional feature comparison (R1), their supervised tables, fitted models, predictions, tuning/selection records and source evidence. The original 98-firm execution outputs are retired. Essential original design, feature definitions, source and collection-method documents remain as explicitly labeled historical records.

## Source dependencies and removal of the top-level data folder

`data/` was removed after preserving these four files for every one of the 50 metros under `study_1/source_data/<metro>_data/`:

| File | Count | Dependency |
| --- | ---: | --- |
| `cbp_employment_2023.csv` | 50 | CBP employment, establishments, payroll and the management-sector employment share used by R1 |
| `bds_metro_2023.csv` | 50 | Business dynamics, including R1 establishment entry/exit rates |
| `qcew_annual_2023_2025.csv` | 50 | Comparable linked private employment, establishments, pay and location quotients |
| `download_manifest.csv` | 50 | Original download metadata and payload hashes |

All 200 relocated files retain their original bytes. The three linked source registries now point to these locations. [build_linked_msa.py](scripts/build_linked_msa.py) reads and validates them; [build_feature_refinement.py](scripts/build_feature_refinement.py) selects the three added regional features from the resulting linked indicators. No top-level `data/` or external `Artem` input is needed for offline reproduction.

The other 407 data files were removed: seven unused filenames in each metro folder (`bea_county_gdp_2023_2024.csv`, `cbp_establishments_2023.csv`, `data_dictionary.json`, `economic_census_2022_detail.csv.gz`, `economic_census_2022_sectors.csv`, `fortune500_headquarters_2025.csv`, `state_corporate_tax_2026.csv`) and 57 older Markdown files. Original download manifests still describe their historical collections; the pipeline only reads the three retained payload rows.

## Original-study retirement

Removed the parent `tables/`, `config/`, `models/`, `reports/`, `study_1.sqlite`, legacy office-positive archive, obsolete original result/handoff/run/validation/coverage guides, `build_hq_2025.py`, `verify_training.py`, `collect_expanded_500.py` and `requirements-collection.txt`.

Ten compact inputs formerly in those directories remain in [expanded_500/reference_inputs](expanded_500/reference_inputs/): original company source checks and coverage decisions, original company cohort and audit labels, development fold table, two feature specifications, training plan, model metrics and Atlanta summary. These are required by the expanded builder/validator or the original-versus-expanded comparison; the old fitted models, probability grids and database are not needed.

The unchanged [train_hq_2025.py](scripts/train_hq_2025.py) supplies the shared fitting functions; use the expanded/refinement entry points. Installed training dependencies remain available in `.training_runtime/`; 3,822 regenerable bytecode caches (about 83 MiB) were removed. Preparation requirements now include `openpyxl==3.1.5`.

## Integrity and reproducibility

[cleanup_manifest.json](provenance/cleanup_manifest.json) records exact original/new hashes, relocated destinations and deliberate retirements. Historical snapshots, frozen input manifests, fitted models, predictions and selection records are not rewritten to pretend the new layout existed at fitting time. [study_integrity.py](scripts/study_integrity.py) checks the original bytes or the specific recorded transition; unrecorded changes fail. Retired paths must remain absent and relocated payloads must match their original hashes.

Current report manifests describe the updated documentation, source registry paths and validation reports. Regenerated R1 validation reports are recorded separately from immutable migration inputs because the verifiers recompute them; preparing a new run may change its input/check count. Saved model metrics and selection are unchanged. Follow [README.md](README.md) for preparation order and saved-run validation; builders should only be run when intentionally preparing a new execution.

## Verification after cleanup

- Expanded dataset: 94/94 acceptance checks.
- Linked data: 452/452 checks, including all relocated source hashes and original manifests.
- Saved R0 models: 70/70 artifact checks, including prediction reloads.
- Saved latest R1 run: 54 preparation checks and 148 full-run checks.
- An isolated copy rebuilt all three preparation stages, fitted the latest R1 models and passed artifact verification twice. It selected R1 company logistic regression again. The working study was not refitted.
- Integrity probes reject corrupted moved sources, unrecorded script edits and reintroduced retired files. Current guide links resolve; the captured handoff retains its original historical link text.

Builders now preserve equivalent SQLite databases and the completed analysis-plan record, so offline reproduction does not alter those frozen records when the logical data is identical.

## Public-repository preparation

The existing root, Shane and Study 1 ignore rules were preserved. The root policy now also excludes raw downloads, private/business-license exports, raw geospatial files, installed dependencies, credentials and generated files. Source-archive documentation and citation metadata remain eligible for Git; normalized training tables, fitted models and result reports remain available.

The two run guides now use portable Python 3.12 virtual-environment commands. The geospatial notebook's 12 saved output sets and execution counts were cleared, and 19 generated cache/preview/metadata files were removed. Raw datasets, license workbooks and the installed training environment remain on disk.

905 newly ignored paths were removed from Git's current index. This includes paths already deleted by the prior cleanup. All 287 existing regular files and the local dependency symlink in that set were retained unchanged. Existing Git commits and LFS history were not rewritten. See [public repository notes](PUBLIC_REPOSITORY.md) for excluded-input requirements before a full rebuild or validation from a public clone.
