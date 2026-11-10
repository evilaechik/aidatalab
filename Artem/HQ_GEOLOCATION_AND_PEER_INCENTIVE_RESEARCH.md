# Geocoded Regional Headquarters Data and Peer Incentive Research

**Status (November 5, 2026):** Research design and policy inventory. No
licensed location data was downloaded into this repository.

## Bottom line

A ZIP/ZCTA or census-tract headquarters study is feasible, but the reliable
unit is a **verified company site**, not a search result or a ZIP code alone.

The practical source for current locations is the licensed Esri Business
Locations dataset supplied by Data Axle. It includes business name, physical
address, geographic coordinates, NAICS classifications, a direct headquarters
name, a business category (Branch, Headquarters, Independent, or Kiosk), and
location-confidence information. See [Esri ArcGIS Places documentation](https://doc.arcgis.com/en/esri-demographics/latest/arcgis-places/data-axle.htm)
and the [2025 methodology statement](https://www.esri.com/content/dam/esri_content_doc/dbl/us/j9940_methodology_stmt_business_locations_sum_jun2025_final.pdf).

It can identify an observed location as a **headquarters** or **branch**. It
does **not** reliably identify the narrower organizational label “regional
headquarters.” A regional HQ usually appears as a branch in a business-location
file. That label must be verified against the company’s website, press release,
SEC filing, or a credible local announcement.

## Recommended data design

| Study element | Recommended choice | Why |
| --- | --- | --- |
| Company universe | Current Fortune 500 parent-company list plus an alias table | Prevents false matches from generic business names. |
| Candidate locations | Licensed Esri/Data Axle Business Locations | Provides names, addresses, parent/HQ fields, branch/HQ category, coordinates, NAICS, and geocoding confidence. |
| Geography | Geocode the physical address, then spatially join to Census tract, ZCTA, City boundary, and MSA boundary | A postal ZIP alone is not a stable research boundary; a ZCTA/tract is reproducible. |
| Regional-HQ status | Company-source verification of “regional HQ,” “Southeast HQ,” operating hub, or comparable wording | The business listing’s Branch flag alone does not establish the function. |
| Site type | Office, HQ, regional HQ, R&D, manufacturing, logistics, retail, or unknown | Keeps warehouses/stores from inflating an office/HQ outcome. |
| Spatial reliability | Retain location-confidence field; require high/very-high confidence for automated spatial scoring and manually review lower-confidence records | Some listed locations can be placed only at ZIP or city centroids. |

### Build procedure

1. Query licensed locations MSA by MSA for every Fortune parent and its aliases.
2. Match exact corporate parent or exact business name; retain the source’s
   Branch/Headquarters category and coordinates.
3. Exclude retail, warehouse/distribution, shipping/mailing, and kiosk records
   from an office/HQ outcome, while preserving them as a separate site type.
4. Spatially join the coordinates to the official MSA, City of Atlanta, ZCTA,
   and census-tract boundaries.
5. Verify all observed Headquarters records and high-impact Branch records
   against company sources. Assign `regional_hq_verified = yes/no/unknown`.
6. Publish only aggregate counts and reproducible data definitions. Keep raw
   licensed records and coordinates outside GitHub.

### What to measure

Do not train one metric to stand in for attraction, expansion, and retention.

| Outcome | Example definition |
| --- | --- |
| HQ attraction | A company establishes a verified principal, divisional, or regional HQ in the City/MSA after the study start date. |
| HQ expansion | An existing qualifying HQ adds verified jobs, floor space, or a new function. |
| HQ retention | A qualifying HQ remains in place and maintains a defined employment or operations baseline. |
| Local siting | Among companies already choosing an MSA, the tract/ZCTA selected for a qualifying site. |

The first three need a dated, longitudinal company-site file. The fourth is a
cross-sectional location-choice question and can use current point locations.

## A better historical option: NETS

If the team can obtain a license, the National Establishment Time Series
(NETS) database is the stronger choice for a dated site panel. USDA’s
description says NETS includes business name, address, CBSA codes, latitude and
longitude, links to parent and headquarters, the number of establishments
reporting to a headquarters, ownership changes, and establishment type
(single-location, headquarters, or branch). [USDA NETS documentation](https://www.ers.usda.gov/topics/food-markets-prices/food-prices-expenditures-and-establishments/using-proprietary-data)

NETS still does not make “regional HQ” a clean universal category. It can,
however, show address changes and opening/closing history that a current
Business Locations snapshot cannot.

## Access note for Emory

Emory provides ArcGIS Online and ArcGIS Pro access through its institutional
organization. That confirms access to the ArcGIS environment, but **does not
by itself confirm** that an account has credits/permissions to export the
national Business Locations dataset. Confirm availability and permitted export
terms with GIS at Emory before querying. [GIS at Emory](https://gis.ecds.emory.edu/)

## Peer-city policy patterns worth studying

The comparison below uses current government or official economic-development
sources. It is a policy-design inventory, not evidence that any policy caused
a relocation.

| Peer | Current tool | Design lesson for Atlanta |
| --- | --- | --- |
| [Austin](https://www.austintexas.gov/economic-development/programs/business-incentives) | Business Expansion Program and Chapter 380 agreements; Austin publishes executed agreements, payments, and compliance material. | Create a public project-level incentive ledger with commitments, payments, and compliance outcomes. |
| [Charlotte](https://www.charlottenc.gov/Growth-and-Development/Economic-Development/Business-Recruitment-and-Expansion) | Business Investment Grants reimburse 50%-90% of incremental net-new property tax for 3-10 years; projects must be competitive and awards are discretionary. | Use a performance-based reimbursement tied to demonstrable competition, investment, jobs, wages, and a defined term. |
| [Dallas](https://dallasecodev.org/628/Business-Development-Negotiated-Incentiv) | Negotiated tax abatements, grants, or loans can require job creation/retention, capital investment, living wages, and public-purpose criteria. | Make wage, job-quality, investment, retention, and clawback/compliance conditions explicit. |
| [Nashville](https://www.nashville.gov/departments/mayor/economic-opportunity/growth-incentives) | Job grants, PILOT agreements, and TIF; recruitment grants target large job creation and wage thresholds. | Separate firm incentives from redevelopment finance and publish a historical project list. |
| [Raleigh](https://raleighnc.gov/grants-funding-and-relief/services/business-investment-grant) | Business Investment Grants are performance-based and tied to jobs plus new taxable investment; corporate, divisional, and regional HQs are explicitly eligible growth clusters. | Explicitly define which HQ types qualify and tie awards to jobs, taxable investment, and demonstrated competition. |
| [Miami-Dade](https://www.miamidade.gov/business/library/forms/reip-application-2024.pdf) | Relocation and Expansion Incentive Program requires new-to-market/expanding companies, at least 50 new jobs within five years, a qualifying office lease/expansion, living-wage compliance, and a higher new-job wage threshold. | Use a clear office-space, net-new-job, wage, and annual-reporting standard for office/HQ incentives. |
| [Houston](https://preflight.houstontx.gov/opportunityzones/leveragingfunds.html) | Chapter 312 tax abatements and Chapter 380 performance-based property/sales-tax incentives, sometimes paired with Opportunity Zone financing. | Consider a transparent menu of place-based tools but distinguish local tools from state/federal tax programs. |
| [Denver](https://denvergov.org/Government/Agencies-Departments-Offices/Agencies-Departments-Offices-Directory/Economic-Development-Opportunity/Choose-Denver) | Tailored business support, workforce help, and a Global Landing Pad for international firms; public evidence found here does not show a single standard large-employer rebate like Charlotte’s BIG. | Not every competitor needs a uniform cash incentive: concierge, workforce, permitting, and international-entry services can be a separate competitive strategy. |

## Suggested policy rubric

Use the peer review to score each current or proposed Invest Atlanta tool,
instead of ranking cities by the largest advertised subsidy.

| Criterion | What to record |
| --- | --- |
| Target | Industry, company size, site type, City geography, and whether HQ/regional HQ is eligible. |
| Trigger | Net new jobs, retained jobs, wage, capital investment, lease/floor-space, or site remediation. |
| Benefit | Grant, tax reimbursement, loan, bond, infrastructure support, permit help, or workforce service. |
| Performance safeguards | Contract, timing, reporting, verification, clawback, and recapture rules. |
| Public value | Tax-base effect, job quality, workforce access, local hiring, transit access, neighborhood benefit, and displacement risk. |
| Evidence | Project-level award, actual payment, jobs/investment delivered, and a comparable unassisted-project benchmark where possible. |

## Recommended next move

Build the geocoded company-site table first, with a City-versus-MSA flag and a
separate regional-HQ verification field. Then use the peer-policy rubric to
compare what Atlanta can offer for each site type. A company-location model
should use verified sites as the outcome; the policy rubric should be a separate
decision tool, not an XGBoost feature.
