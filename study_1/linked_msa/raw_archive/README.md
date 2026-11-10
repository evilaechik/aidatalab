# Raw archive and source evidence

Source URLs and detailed factual notes are retained here, outside the six analytical tables.

For training use, follow the [current handoff](../TRAINING_HANDOFF.md). Evidence IDs, access dates, retrieval success and coverage flags are audit fields, excluded from predictors. The proposed regional additions retain their source-program units and geography qualifications; source availability does not establish a valid office-absence label.

| File | Purpose |
| --- | --- |
| `source_registry.csv` | Unified source IDs, URLs and local normalized-input references |
| `company_source_registry.csv` | One initial review route per company; annual filing date and source fiscal period where available |
| `collection_attempts.csv` | All 500 company-level screening attempts, availability and incompleteness |
| `reviewed_office_facts.csv` | Reviewed, paraphrased factual assertions with locality, role categories, source URL/line, period and any explicit local quantities |
| `evidence_index.csv` | Analytical evidence IDs mapped to source IDs, URLs, row selectors and retained facts |
| `regional_source_registry.csv` | The 150 reused regional CSVs, their original download routes/dates, transformations and hashes |
| `inherited_economic_source_registry.csv` | Primary-source lineage for the unchanged economic predictors and general levels |
| `geography_source_registry.csv`, `additional_source_definitions.csv` | Geography sources and program definitions, including the QCEW disclosure exception for establishment counts |
| `reviewed_place_cbsa_crosswalk.csv` | Reviewed locality-to-CBSA assignments, ambiguity and method notes |
| `2023_Gaz_place_national.zip`, `2023_Gaz_cousubs_national.zip` | Census representative-point payloads used for locality assignments |
| `current_sec_address_candidates.json` | Inherited current SEC business addresses for discovery only; not accepted as office-function evidence |
| `evidence_qualifications.csv` | Explicit interpretation conflicts, including Block's no-designated-HQ statement |
| `unassigned_location_candidates.csv` | A grouped-use lead not promoted to a site-specific office/function assertion |

The screening protocol selected the retained 2025 annual-filing route where available (465 firms), otherwise the pre-existing official supplemental route (35). It sought the Properties section using indexed primary-source text, equally across industries. All 500 attempts were recorded; 460 returned text and 394 returned a recognized Properties heading. Headings/text availability do not mean a complete filing or office directory was reviewed. Thirty-five fallback routes include private-company and other sources that may not have such a section.

Direct SEC Archives downloads returned HTTP 403, including a retried direct request. Accessible indexed filings were used instead. Source lines are locators in the indexed rendering, not permanent official paragraph IDs. The archive retains normalized facts and original source routes, rather than redistributing full corporate prose. A page failing to return text was not counted as evidence of absence.

Filing dates, fiscal periods and discovery dates are separate. Source fiscal periods annotate the new location facts; they do not prove continuous occupancy or make the data a dated office census. Current SEC metadata retrieved for the earlier expansion remains discovery-only. The 2023/2024 economic payloads were reused from the documented workspace downloads; this run does not claim fresh remote acquisition of those figures.

Gazetteer exact name/state matches use Census place or county-subdivision representative points intersected with the same full-resolution 2023 CBSA geography used by the earlier study. The crosswalk stores its source/method. Studio City is treated as Los Angeles and Elkhorn as Omaha; Nashville uses the consolidated-place entry. Burbank's city entry follows the filing's Los Angeles-area context. Ambiguous/unmatched places remain unresolved rather than being assigned to the nearest metro. The CBSA payload hash/source route is recorded in the geography registry.

`evidence_qualifications.csv` and the source/crosswalk CSVs are retained collection inputs. The offline builder regenerates the analytical tables without repeating web searches. Detailed collection limitations and interpretation are documented in the parent schema and results files.

The 150 regional CSVs and their 50 original download manifests are now under `study_1/source_data/`. The original manifests also describe files retired from the old general-purpose data collection; only their three retained payload rows are required by this pipeline. The [cleanup record](../../CLEANUP.md) documents all source dependencies and retirements.
