# Public repository contents and local inputs

The repository keeps source code, requirements, essential methods, normalized training tables, dictionaries, fitted models, results, citation metadata and integrity manifests. Personal interpreter paths have been replaced with portable Python 3.12 virtual-environment commands.

## Inputs intentionally excluded from Git

The root `.gitignore` excludes installed environments, raw download folders, source payloads, private institutional exports, business-license files and raw geospatial datasets. These exclusions do not delete the local files.

For Study 1, a complete offline rebuild and full validation require these excluded inputs at their existing relative paths:

- `source_data/`: the CBP, QCEW and BDS CSVs plus original download manifests for all 50 metros (200 files).
- `feature_refinement/raw_archive/`: the official OMB geography workbook, CBP county reference text and two BDS release-note PDFs.
- `linked_msa/raw_archive/`: retained collection attempts, reviewed office facts and place crosswalk, source candidates and original geography payloads. Documentation, source registries, evidence index and qualification metadata remain eligible for Git.

Preserve original bytes when restoring an input bundle. The input manifests, source registries and `provenance/cleanup_manifest.json` record the expected hashes. Public readers can inspect the saved normalized tables and result reports without these downloads. Full validators deliberately require the original evidence instead of silently skipping missing inputs. Redistribution of source bundles should be reviewed separately from publishing code and results.

The private business-license, revenue/employee, tax-parcel and investment workbooks under the older export/private folders are not Study 1 dependencies. They remain local and excluded from Git. This study's offline pipeline does not need those files.

## Portable environment

From the repository root:

```sh
python3.12 -m venv study_1/.venv
study_1/.venv/bin/python -m pip install -r study_1/requirements.txt -r study_1/requirements-training.txt
```

After restoring required source inputs, use [README.md](README.md) for the saved-run validation commands and full preparation order. Installed environments, raw inputs and database journal files should remain ignored; normalized tables, saved model pipelines and frozen selection records should remain available.

## Git history

Ignore rules govern future additions. Previously tracked raw/private files must also be removed from the index to stop including them in the next commit; their local copies can remain. Existing commit history and existing Git LFS objects are not rewritten by this cleanup. Publishing this repository's existing history requires a separate review of historical sensitive records. A newly curated public repository can start from approved current files without copying the existing `.git` directory.
