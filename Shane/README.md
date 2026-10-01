# Shane research files and proposed Git commit

This is a reviewable commit draft. No commit, push, release upload, or new download has been performed. The `.gitignore` implements the proposed selection below; it does not delete local files.

## Proposed commit

Title: `Add research context and compact public data; exclude source archives`

Body:

```text
Document the Atlanta business attraction and retention research and collected
data sources. Include ACS public metro tables for 2019/2024 and the combined
May 2025 OEWS table with supporting definitions and provenance.

Keep national source downloads, duplicate exports, and private Invest Atlanta
files out of Git. Document future download and preparation scripts so teammates
can reproduce the larger local inputs.
```

### Include in Git

Paths below are relative to `Shane/`. Sizes are approximate decimal units.

| Files | Size | Why include |
| --- | ---: | --- |
| `.gitignore` and this `README.md` | A few KB | Sharing rules, proposed commit, and teammate workflow |
| `research_context.md` | 8.4 KB | Research question, scope, and analysis sequence |
| `data/data_summary.md` | 11.7 KB | Sources, uses, reference periods, and interpretation caveats |
| `data/download_manifest.csv` | 15.7 KB | Source URLs, retrieval methods, sizes, and checksums for the 69 public data/support files; no private workbook entry |
| `data/acs/ACSDP5Y{2019,2024}.{DP02,DP03}-Data.csv` | 6.42 MB total | Four public metro tables for resident workforce and socioeconomic comparisons |
| Corresponding ACS `-Column-Metadata.csv` and `-Table-Notes.txt` files | 0.34 MB total | Variable labels and methodological notes needed to interpret the tables |
| `data/oews/oews_may2025_selected_metros.csv` | 2.15 MB | One combined occupation/wage table covering Atlanta and nine candidate peer metros |
| `data/oews/datatype_definitions.json`, `footnote_definitions.json`, and `selected_metros_sources.json` | 7.0 KB total | Measure definitions, suppression/top-code footnotes, and exact public-table requests |
| `data/warn/SOURCE_README.md` | 36.9 KB | Upstream coverage, schema, and attribution documentation |

The proposed existing data/documentation files total approximately 8.98 MB, plus this README and the ignore rules. There are 22 proposed files including this README. Small size alone is not sufficient: this selection favors reusable tables and the information needed to interpret and reproduce them.

The ACS and OEWS inputs are explanatory data, not a complete benchmarking panel. The initial industry and firm-size analysis still requires local QCEW, CBP, and BDS inputs. No harmonized peer/industry panel has been created yet.

### Exclude from Git but preserve locally

| Files | Reason | Future sharing route |
| --- | --- | --- |
| `data/qcew/*.zip` (about 842 MB) | Large national source archives | Download script; an exact release snapshot if useful |
| `data/bds/*.csv` (about 346 MB) | Large national historical tables | Download script; create smaller documented metro/year extracts |
| `data/cbp/*.zip` (about 63 MB) | Source archives readily fetched from Census | Download script |
| `data/acs/*.zip` | Duplicate the extracted tables included in Git | Local source backup; no second copy needed in Git |
| `data/oews/*_raw.json` and individual metro CSVs | Duplicate the combined table's underlying information | Local provenance backup; recovery script if needed |
| `data/warn/warn_notices.csv` and `coverage.json` | Supporting later investigation; upstream feed changes over time | Download both from a pinned upstream revision |
| `data/nc_grants/*` | Small but mainly needed for the later incentive-comparison phase | Download script; add a cleaned analysis table later if needed |
| `data/real_estate/*.pdf` | Small reports requiring table extraction; later explanatory evidence | Source links/manual download or script where permitted; share documented extracted metrics later |

These public source files are local **for now**, not necessarily local forever. They can be shared as authorized release attachments later. No release has been created, and source access does not itself establish redistribution rights.

### Keep entirely outside the shared public data package

`data/Invest_ATL_private/`, including `Business_License_2025_Geo_Deidentified.xlsx`, remains excluded in full. Deidentification does not establish permission to publish it. Do not include it in download scripts, manifests, release ZIPs, or public derived datasets. Share only through a separately authorized private transfer if the group has permission. Historical private-folder paths are also excluded by `.gitignore`.

## Future scripts to add

These are proposed tasks, not implemented commands.

1. **`scripts/download_public_data.py`:** Fetch the QCEW 2015–2025 archives, CBP 2015–2023 archives, and both 2023 BDS tables using manifest URLs. Allow dataset selection so members do not need to download everything. Download to temporary files, verify checksums and ZIP integrity, then move into the expected local folders; skip verified existing files and report failures clearly. Add NC grant files and report downloads where the source permits automated access.
2. **`scripts/download_warn.py`:** Retrieve notices, coverage, and source documentation from one pinned upstream commit. Record that revision and keep the original collection's checksums so everyone can reproduce the same snapshot rather than silently fetching a newer feed.
3. **`scripts/prepare_benchmark_panel.py`:** Filter QCEW, CBP, and BDS to the agreed metros, industries, and common 2015–2023 window. Preserve disclosure flags, check geographic/industry revisions, and produce smaller inputs. Peer selection and harmonization rules must be agreed before this script is written.
4. **`scripts/rebuild_oews.py`:** Reissue the ten requests in `selected_metros_sources.json`, retain raw responses locally, and recreate the combined CSV with the same value/footnote handling. Service availability and exact reproducibility must be checked. The committed CSV already lets teammates use this snapshot without fetching it again.
5. **ACS recovery instructions:** Keep the public-export steps and source links; the selected tables are already included in Git. An optional API-based downloader would be a separate workflow with a user-supplied key, never a committed key. Public browser exports can remain the manual fallback.
6. **`scripts/verify_data.py`:** Check selected local files against `download_manifest.csv`, distinguishing missing optional source files from required analysis inputs. Files absent from a teammate's clone are expected because the manifest inventories the complete collected snapshot, not just Git contents.

A release-download script can be added once actual release URLs exist. Do not invent release URLs or treat the manifest's browser-table links as direct downloadable files.

## Teammate workflow

Clone the repository to obtain code, context, documentation, ACS, and OEWS. Use paths relative to the repository rather than another member's home directory. Until the proposed scripts or release attachments exist, obtain the remaining public files from the documented sources or an agreed transfer and place them in the ignored folders. Keep original source downloads unchanged and write transformed outputs separately.

For an offline transfer, send only the agreed public dataset folders and manifest in a versioned archive. Do not ZIP the entire `Shane/data` directory because it contains the private workbook. Existing ZIP archives usually gain little from being compressed again.

## Preview before committing

From the repository root, this read-only command previews the files Git would add under Shane:

```sh
git add --dry-run -- Shane/
```

After reviewing the selection, a future commit could use:

```sh
git add -- Shane/
git diff --cached --stat
git commit -m "Add research context and compact public data; exclude source archives"
```

Review the complete staged set before committing; these commands do not exclude changes already staged elsewhere in the repository. A push would be a separate action.
