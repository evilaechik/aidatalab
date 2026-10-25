# Fortune 100 National-Export Coverage Audit

## Decision

**Do not use the earlier U.S. Top-100 MSA XGBoost run as a national result.**
The missing metros are not a boundary-assignment problem: the licensed source
export contains zero raw rows assigned to each of them. Filling those cells
with zero or a guessed office count would make the model less defensible.

## What was checked

For every missing Top-100 MSA, the audit checked the full local Data Axle
export before site-type screening, the city-to-MSA assignment table, and the
candidate-score table. All 17 have:

- zero raw records assigned to the target MSA;
- zero pre-screen Fortune-company candidate records in the target MSA; and
- no score-table row.

The issue is therefore upstream of the MSA boundaries and warehouse/retail
screen.

## Metro-by-metro status

| Missing MSA | Export coverage diagnosis | Correct action |
| --- | --- | --- |
| Los Angeles-Long Beach-Anaheim, CA | California has zero raw matched-Fortune records in the supplied export. | Fresh MSA-scoped export for all Fortune companies. |
| San Francisco-Oakland-Fremont, CA | California has zero raw matched-Fortune records in the supplied export. | Fresh MSA-scoped export for all Fortune companies. |
| San Diego-Chula Vista-Carlsbad, CA | California has zero raw matched-Fortune records in the supplied export. | Fresh MSA-scoped export for all Fortune companies. |
| Riverside-San Bernardino-Ontario, CA | California has zero raw matched-Fortune records in the supplied export. | Fresh MSA-scoped export for all Fortune companies. |
| Sacramento-Roseville-Folsom, CA | California has zero raw matched-Fortune records in the supplied export. | Fresh MSA-scoped export for all Fortune companies. |
| San Jose-Sunnyvale-Santa Clara, CA | California has zero raw matched-Fortune records in the supplied export. | Fresh MSA-scoped export for all Fortune companies. |
| Oxnard-Thousand Oaks-Ventura, CA | California has zero raw matched-Fortune records in the supplied export. | Fresh MSA-scoped export for all Fortune companies. |
| Fresno, CA | California has zero raw matched-Fortune records in the supplied export. | Fresh MSA-scoped export for all Fortune companies. |
| Santa Rosa-Petaluma, CA | California has zero raw matched-Fortune records in the supplied export. | Fresh MSA-scoped export for all Fortune companies. |
| Bakersfield-Delano, CA | California has zero raw matched-Fortune records in the supplied export. | Fresh MSA-scoped export for all Fortune companies. |
| Seattle-Tacoma-Bellevue, WA | Washington has zero raw matched-Fortune records in the supplied export. | Fresh MSA-scoped export for all Fortune companies. |
| Spokane-Spokane Valley, WA | Washington has zero raw matched-Fortune records in the supplied export. | Fresh MSA-scoped export for all Fortune companies. |
| Portland-Vancouver-Hillsboro, OR-WA | Oregon has zero raw matched-Fortune records in the supplied export. | Fresh MSA-scoped export for all Fortune companies. |
| Urban Honolulu, HI | Hawaii has zero raw matched-Fortune records in the supplied export. | Fresh MSA-scoped export for all Fortune companies. |
| Boise City, ID | Idaho has one raw matched-Fortune record, but none in this MSA. | Fresh Boise-MSA-scoped export; do not infer zero. |
| El Paso, TX | Texas has many raw matched-Fortune records, but none in this MSA. | Fresh El Paso-MSA-scoped export; do not infer zero. |
| Reno, NV | Nevada has a small number of raw matched-Fortune records, but none in this MSA. | Fresh Reno-MSA-scoped export; do not infer zero. |

## Additional data-quality findings

1. The export maps to **86 distinct current Fortune 100 companies**, not the
   complete 100-company universe.
2. Several searches use names that are not unique company identifiers. The
   returned data can include unrelated businesses sharing a word in the
   company name. A query label alone is not sufficient evidence that a record
   belongs to that Fortune company.
3. The earlier automated filter removes obvious retail, warehouse, shipping,
   and kiosk locations, but it cannot correct a wrong company identity or a
   geographically incomplete export.

## Repair protocol

For each of the 17 MSAs—and then for every MSA used in the final model:

1. Query the full current Fortune 100 company universe **within that MSA**;
   do not use a nationwide top-result export.
2. Retain only records where the Data Axle business, headquarters, corporate
   parent, or verified brand field matches a pre-defined company alias table.
3. Code the site type: office/HQ/R&D, manufacturing, warehouse/logistics,
   retail, or unknown.
4. Create a zero score only when the completed MSA-scoped query returns no
   identity-verified eligible office/HQ/R&D sites.
5. Have a person review the unknown and high-impact records before any score
   enters a model.

Until that repair is complete, use the public metro-factor tables for
descriptive benchmarking only and keep the licensed location data outside the
repository. A narrower source-covered model-mechanics sensitivity is recorded
in `Artem/SOURCE_COVERED_METRO_DIAGNOSTIC.md`; it is not a national finding or
a policy model.
