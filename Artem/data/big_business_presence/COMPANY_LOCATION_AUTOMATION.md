# Company-location automation and MSA assignment

## What this resource does

`../../scripts/geocode_company_locations_to_msas.py` takes an authorized
company-location export, maps rows to the 2025 Fortune 500, geocodes the street
addresses through the U.S. Census Geocoder, and assigns each matched county to
one of the selected MSAs using the official 2023 Census delineation table.

This solves the geography step consistently for every city. It produces a
candidate-presence table for all selected MSAs, rather than asking a researcher
to decide whether Alpharetta, Marietta, or Sandy Springs should count as Metro
Atlanta each time.

## What it does not claim

There is no free, authoritative national database that lists every Fortune 500
corporate office and reliably distinguishes it from every retail store,
distribution center, dealership, franchise, or remote employee. Public maps,
OpenStreetMap, company location pages, SEC filings, and search results are each
incomplete for a different reason.

Therefore the automated output has three **candidate** classes:

| Candidate class | Meaning | May count in final score? |
| --- | --- | ---: |
| `candidate_qualifying_office` | The source location type or NAICS indicates an office/HQ/administrative/R&D/sales-type site. | No, until direct evidence is reviewed. |
| `candidate_retail_or_distribution_only` | The source suggests a store, warehouse, distribution center, plant, or comparable non-office site. | No. |
| `candidate_unknown_function` | The source supplies a location but not enough functional detail. | No. |

Only a direct company source or a clearly documented source classification can
turn a candidate into `qualifying_hq`, `qualifying_office`, or a completed
non-qualifying outcome in the score audit.

## Best source for a national branch list

The appropriate scalable input is a licensed establishment directory such as
**Data Axle Reference Solutions / U.S. Businesses**, if Emory provides access.
It is designed for location-level business searching and can provide business
address, geographic, industry, and employment-related fields. A Data Axle or
similar licensed export should remain outside this Git repository unless its
license explicitly permits redistribution.

OpenStreetMap may be used to discover extra candidate locations, but should not
be treated as a complete national office directory. Its public services also
have rate/usage policies, so it is not the right way to send 100,000
company-by-metro searches.

## Required input schema

Use `location_import_template.csv` as the column structure. The required fields
are an immutable location ID, company name, and street/city/state/ZIP address.
`location_type`, `naics_code`, and `source_url` improve the candidate
classification but do not replace human verification.

If the location vendor uses a parent-company ID or name different from the
Fortune entity, create a separate alias file with:

```text
source_company_name,fortune_slug
```

This keeps entity-resolution decisions visible and reversible.

## Run

1. Keep the licensed location export outside the repository.
2. Run the main Fortune/MSA build first. It creates `msa_roster.csv` and
   `metro_county_crosswalk_2023.csv` for the selected 200 MSAs.
3. Run the geocoder with an external output directory:

```bash
python3 Artem/scripts/geocode_company_locations_to_msas.py \
  --input-csv /external/fortune500_locations.csv \
  --output-dir /external/fortune500_msa_results \
  --source-name "Data Axle Reference Solutions"
```

The Census batch service allows up to 10,000 addresses per batch. The script
defaults to 5,000 and pauses between requests. It preserves every match failure
and never silently treats it as outside a metro.

## Score workflow after automation

```text
Authorized location list → Census county/MSA assignment → candidate class
                                                      ↓
                                          direct source / function review
                                                      ↓
                            verified F500 HQ or office count by MSA / 500
```

The location list can rapidly identify where a company has *some* footprint.
The review step ensures that the published metric remains an office/HQ score,
not a store-count score.
