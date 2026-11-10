# Fortune 500 Regional, Divisional, and Subsidiary HQ Research

Updated: 2026-11-10

## What this measure is for

The project’s **big-business presence** outcome is the number of Fortune 500
companies with a source-verified, non-global-headquarters leadership location
in a metropolitan area. It is intentionally stricter than a count of stores,
warehouses, sales offices, or job postings.

Each company counts at most once per MSA. Multiple verified sites for the same
company in the same MSA are retained as evidence, but form one company–MSA
outcome pair.

## Current public research inventory

The current public, source-verified file contains:

| Measure | Current count |
| --- | ---: |
| Documented sites of every type | 109 |
| Eligible regional/divisional/subsidiary or additional-HQ sites | 85 |
| Eligible company–MSA pairs in the 200-MSA model roster | 77 |
| Fortune 500 companies with an eligible documented site | 49 |
| Eligible sites outside or unassigned in the 200-MSA roster | 2 |
| Fortune 500 companies with SEC discovery leads requiring source review | 29 |

The two outside/unassigned documented sites are ADM's North American
Headquarters in Decatur, Illinois and Berkshire Hathaway's Shaw Industries
Corporate Headquarters in Dalton, Georgia. They remain in the site file for
research completeness but do not silently enter the 200-MSA model.

The large majority of documented sites use direct company or investor-relations
material. One uses a clearly labeled public economic-development headquarters
inventory with company context, and one is a company-hosted report whose
headquarters claim comes from a third-party evaluator. Those exceptions are
explicitly tagged `eligible_after_company_source_confirmation` and
`eligible_after_direct_company_source_confirmation`; neither should enter a
final model score until direct current company confirmation is added.

## Inclusion standard

A site is eligible only when a public source explicitly identifies it as one
of the following:

1. An additional or dual corporate headquarters;
2. A named regional or geographic headquarters;
3. A sector, division, operating-business, or subsidiary headquarters; or
4. A named divisional base with company evidence of an executive operating
   role.

The source must establish both the function and the Fortune 500 parent link.
Company-owned/investor-relations material is preferred. A government record is
used only when it clearly records the specific headquarters and relationship,
and this exception is labelled in the site note.

## Deliberate exclusions

Do **not** count a site merely because it is:

- A retail store, factory, warehouse, distribution center, airport operation,
  or call center;
- A generic office or sales office without an explicit headquarters function;
- A company property whose connection to the Fortune 500 parent is not
  documented; or
- A business-unit headquarters located in the parent company’s global-HQ MSA.

Those locations can still be valuable context. For example, Kroger's division
offices are retained in the site file, but not treated as HQ outcome entries.

## Files

- `data/big_business_presence/fortune500_verified_regional_divisional_sites_2026.csv` — auditable site-level evidence, source links, classification, and MSA assignment.
- `data/big_business_presence/fortune500_verified_regional_divisional_sites_summary_2026.csv` — counts by site class.
- `data/big_business_presence/fortune500_regional_divisional_hq_coverage_tracker_2026.csv` — all 500 companies and their research status.
- `data/big_business_presence/fortune500_public_filing_regional_hq_discovery_leads_2026.csv` — unverified leads from official SEC filing text. These are a research queue, **not** model labels.
- `scripts/build_verified_fortune500_regional_divisional_sites.py` — rebuilds the verified site files and assigns documented locations to MSAs.
- `scripts/build_fortune500_regional_hq_coverage_tracker.py` — rebuilds the 500-company coverage log.
- `scripts/discover_fortune500_regional_hq_sec_leads.py` — re-runs the conservative SEC discovery pass.

## What the coverage tracker means

The tracker is designed to prevent a common research mistake: treating a
company that is not yet found as a company that has no regional headquarters.

| Status | Meaning | Action |
| --- | --- | --- |
| `verified_eligible_regional_or_business_unit_hq` | At least one eligible site has current, public evidence. | Perform one final currentness check before scoring. |
| `verified_nonincremental_or_footprint_only` | A verified site exists but is co-located with the global-HQ MSA or is a lower-tier operating footprint. | Keep as context; do not score it as a new company–MSA pair. |
| `public_filing_lead_needs_current_company_source` | SEC text contains a promising headquarters phrase, but the current function and location remain unproven. | Validate with a current company or investor-relations source. |
| `not_yet_in_public_research_queue` | This scan has not reached a documented lead or verified site. | Search named operating segments, brands, acquisitions, and corporate/investor pages. |

## Important limit

There is no complete public U.S. registry of every Fortune 500 branch or
regional headquarters. Therefore, no honest public-web process can prove that
it has found **every** regional HQ. This project can be comprehensive and
auditable by maintaining the coverage tracker, but it must describe the result
as **source-verified documented regional/divisional/subsidiary HQ presence**,
not as a census of every office.

For a fully enumerated location score, the defensible next source is a licensed
business-location database (for example, Data Axle/Esri), followed by manual
classification of location type. That database should remain outside the public
repository under its license terms.

## Rebuild

```bash
python3 Artem/scripts/build_verified_fortune500_regional_divisional_sites.py \
  --place-gazetteer /path/to/2023_Gaz_place_national.zip \
  --cbsa-shapefile /path/to/tl_2023_us_cbsa.zip

python3 Artem/scripts/build_fortune500_regional_hq_coverage_tracker.py
```

Before using the count as a model label, preserve the geography rule: a source
location must first be assigned to an MSA using its documented city/address,
and then deduplicated to one Fortune-company × MSA pair.
