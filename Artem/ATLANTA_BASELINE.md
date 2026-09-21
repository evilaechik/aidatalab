# Atlanta Business Competitiveness: Initial Baseline

Date: 2026-09-20

This is an initial inventory and descriptive baseline. It is not a claim that a license equals a new business, a business closure, or a measure of competitiveness against another metro.

## 1. Business-license signal

The 2025 license file contains 17,623 usable rows. After excluding coordinate values outside a plausible Atlanta-area bounding box, 17,221 records remain. These represent 14,430 distinct company names and 522 NAICS codes.

The largest industry groups in the spatially plausible records are:

| Industry | Records |
| --- | ---: |
| Full-service restaurants | 1,648 |
| Management consulting | 1,067 |
| Other business service centers | 810 |
| Beauty salons | 655 |
| Real-estate agents and brokers | 562 |
| Lessors of residential buildings | 508 |

The data is concentrated in a small set of Neighborhood Planning Units (NPUs): B (3,510 records), E (2,833), M (2,331), D (993), and F (961). It flags 2,740 records as located in a disinvested neighborhood.

## 2. Historical Invest Atlanta project signal

The historical development workbook contains 919 project records after removing one repeated header row. The principal project types are State Opportunity Zone (408), BA (247), BRE (218), and I+E (43). Abbreviations need a data dictionary before they appear in a public result.

Reported project totals are substantial but unevenly populated:

| Measure | Populated projects | Reported total |
| --- | ---: | ---: |
| IA investment | 167 | $32.4M |
| Leveraged capital investment | 519 | $7.89B |
| Total capital investment/project cost | 584 | $7.91B |
| Total economic output | 581 | $33.37B |
| New full-time jobs | 755 | 54,441 |
| Retained full-time jobs | 873 | 12,021 |
| Expansion jobs | 239 | 18,887 |

These totals span multiple years and programs. They should not be added to license counts or treated as current-year outcomes.

## 3. Site and parcel signal

The tax-parcel dataset supplies 171,029 mapped 2025 parcels. It has parcel identifiers, address, property classification, assessed/appraised values, zoning, NPU, neighborhood, and geometry.

The publicly owned-property dataset supplies 5,210 mapped records. It contains owner/agency, address, valuation, land use, acreage, zoning, vacancy-related fields, transit proximity, Opportunity Zone indicators, and other site-screening attributes. It may contain multiple joined records per parcel, so `PARCELID` must be assessed for duplicates before counting sites.

## 4. What we can responsibly answer now

1. Where are business and industry concentrations within Atlanta?
2. Which locations pair industry presence with parcel/site characteristics that may support expansion or relocation?
3. Where has Invest Atlanta historically supported capital investment or jobs, subject to cleaned program definitions?

## 5. What cannot be answered yet

The project brief asks where Atlanta is lagging in attraction and retention, and which peer-region incentives should be adopted. That requires external comparison data that is not in the repository:

- industry employment and establishment trends for Atlanta and peer metros;
- peer-metro incentive policy and award data;
- major relocation, retention, and lost-deal data; and
- commercial availability, rents, and absorption.

## 6. Recommended next deliverable

Build an **Atlanta Industry-Site Opportunity Map**: choose a small number of target industries, map their business concentration by NPU/council district, and layer viable commercial/public sites and prior project outcomes. Add peer-metro trends afterward to turn it into a competitiveness recommendation rather than only a local descriptive map.

