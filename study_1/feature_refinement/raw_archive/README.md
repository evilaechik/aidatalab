# Geography and source archive

The [source registry](geography_source_registry.csv) contains the official URLs, payload hashes, review date and factual purpose of each retained geography source. The original company/indicator source lineage remains in `study_1/linked_msa/raw_archive/`, referenced by evidence IDs in the new feature-lineage table.

The CBP reference file is used to compare actual constituent county FIPS sets with the archived July 2023 OMB delineation workbook. Statewide pseudo-county rows are reviewed separately, not treated as physical counties. Providence's `44999` row is accepted because the whole state is inside that metro. BDS 2022 release notes document the July 2023 MSA update, and BDS 2023 release notes specify the extension of vintage-consistent TIGER/Line 2023 geography across the United States.

The OMB workbook is reused from the existing workspace collection. The CBP reference and BDS release-note payloads were downloaded for this run. Economic feature values are reused from the linked indicator collection; no fresh economic-value download or historical occupancy census is claimed.

Source URLs are kept here rather than in model tables. `reports/geography_audit.csv` and `tables/refinement_feature_lineage.csv` retain the decisions and evidence IDs needed to trace the three additions.
