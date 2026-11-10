# Fortune 500 Global-HQ Model and Regional-HQ Guardrail

## Executive summary

We now have a public, reproducible Fortune 500 global-HQ benchmark for the
project's 200-MSA comparison roster. It is stronger than the earlier Fortune
100 location-candidate proxy because it has a defined company universe and
real zeroes rather than treating missing location coverage as no presence.

- **Corporate-anchor outcome:** 463 Fortune 500 listed global HQs map into the
  200-MSA roster; 79 metros have at least one.
- **Model result:** nested Poisson XGBoost improves held-out MAE from 5.07 HQs
  for the training-mean baseline to 2.67 HQs, with held-out R² of 0.42.
- **Main association:** metro employment scale is the only consistently strong
  predictive signal. This is a descriptive scale effect, not evidence that a
  policy lever causes HQ attraction.
- **City geography:** 483 listed HQ cities map to 223 official Census place
  jurisdictions, allowing City of Atlanta to remain distinct from Alpharetta,
  Sandy Springs, and other Metro Atlanta places.
- **Tax context:** every HQ row has a 2026 state corporate-tax context, but
  city business, payroll, and property taxes cannot be reduced to one national
  rate or an exact company tax bill without address- and company-specific data.
- **Regional HQs:** the verified file now contains 18 additional
  regional/divisional/business-unit HQ or base sites, three co-located
  global-and-regional HQ records, and 17 verified division offices. It is
  still not a complete national outcome and remains out of model training.

## What changed

The project now has a complete public **Fortune 500 global-headquarters**
outcome for the 200-MSA roster. This replaces the earlier incomplete Fortune
100 commercial-location proxy as the primary corporate-location modeling
outcome.

This is deliberately a global-HQ model. A branch, a local office, or a Data
Axle `Headquarters` category is not automatically a regional headquarters.
Regional/divisional HQs remain a separate evidence-review stream.

## Data construction

- Source universe: Fortune's 2025 Fortune 500 ranking, including its listed
  headquarters city and state.
- Geography: headquarters city is matched to a Census 2023 place centroid and
  assigned when that centroid falls within the project's 2023 CBSA polygon.
- Outcome: distinct Fortune 500 companies with a Fortune-listed **global HQ**
  in each MSA. A missing count is a real zero, not an unobserved location.

Of 500 Fortune companies, 463 map into the 200-MSA roster, 18 map to an MSA
outside the roster, and 19 cannot be safely assigned from their city label.
The selected 200 MSAs contain 79 metros with at least one listed global HQ.

This produces a transparent corporate-anchor benchmark, but it does **not**
measure every office, regional HQ, warehouse, or store.

## City-boundary and tax-jurisdiction layer

The MSA assignment is now paired with a city-jurisdiction table. Fortune's
reported HQ city is matched to a 2023 Census **place**—the Census geography
that represents an incorporated municipality or Census-designated place.

- 483 of 500 listed HQ cities match a Census place, yielding 223 distinct
  matched HQ city jurisdictions.
- Each matched company has a Census place GEOID, official place name, legal/
  statistical area descriptor, and a 2026 top statutory **state** corporate
  income-tax rate.
- The remaining 17 HQ labels are left unassigned at the city level rather than
  being forced into a municipality.

The current city assignment is accurate to the **Fortune-listed city**, not an
exact street parcel. It is sufficient to distinguish Atlanta from Alpharetta,
Sandy Springs, or other Metro Atlanta jurisdictions; it is not sufficient to
calculate an actual company tax bill. Exact local tax analysis needs a street
address, Census Geocoder place lookup, county/municipal property-tax
jurisdiction, assessed value, incentive agreement, and the company's tax base
and apportionment information.

Municipal business-license/occupation taxes, local payroll or income taxes,
and property-tax millage are therefore separate review fields. There is no
single standardized nationwide public table that turns them into one
comparable city “corporate tax rate.”

## Model check

The model uses 97 top-100 MSAs with complete 2022 public factor rows and
evaluates predictions in five stratified held-out folds. The target is the
2025 Fortune-listed global-HQ count, so the exercise is cross-sectional and
associational—not a causal estimate of incentives.

| Model | Held-out MAE | Held-out R² |
| --- | ---: | ---: |
| Training-mean baseline | 5.07 HQs | -0.02 |
| Fixed regularized Poisson XGBoost | 2.90 HQs | **0.42** |
| Nested-Optuna Poisson XGBoost | **2.67 HQs** | **0.42** |

Metro employment scale is the dominant held-out association. Average weekly
wage is a distant and unstable second signal; the remaining tested variables,
including the corporate-tax proxy, do not show stable independent importance
in this sample. Do not translate this into a tax-incentive claim.

## Regional-HQ workstream

The external Fortune 100/Data Axle candidate queue is now linked to the
current Fortune 500 universe:

- 164 candidate company-MSA rows link to 47 current Fortune 500 companies.
- 28 rows from 11 source-company labels require entity review or no longer map
  to the current Fortune 500 list.
- All candidate rows remain `excluded_until_company_source_verifies_function`.

Data Axle category labels are not used as proof of HQ function. Instead, a
separate public seed list records only sites with a company-owned source:

- 18 additional verified HQ/base site records across 13 Fortune 500 companies
  and 16 company-MSA pairs,
  including Amazon HQ2 in Arlington; JPMorgan Chase regional HQs in Washington
  and Columbus; Cigna in Plano; Comcast division/regional headquarters in
  Metro Atlanta; HCA's East Florida divisional base in Fort Lauderdale;
  Kroger's Atlanta Division HQ in Alpharetta; Lockheed Martin business-unit
  HQs in Denver and DFW; PepsiCo's Frito-Lay North America HQ in Plano; RTX
  business HQs in Charlotte and East Hartford; Boeing Defense, Space &
  Security in St. Louis; Centene's East Coast HQ in Charlotte; General
  Dynamics' Gulfstream HQ in Savannah; and Merck's U.S. Human Health Division
  HQ in Upper Gwynedd, Pennsylvania.
- Three HQ records (Kenvue, JLL, and Rockwell Automation) are separately kept
  because their global and regional/North America HQs are co-located in the
  same MSA. They document corporate structure but do **not** increase a
  company-MSA presence score.
- 17 Kroger **division office** addresses are separately retained as verified
  operating footprint, not promoted to regional HQs.
- 37 of the 38 records map to the 200-MSA roster. Dillons in Hutchinson,
  Kansas is explicitly retained as outside that roster rather than treated as
  a zero or discarded.

The files are
`data/big_business_presence/fortune500_verified_regional_divisional_sites_2026.csv`
and `data/big_business_presence/fortune500_verified_regional_divisional_sites_summary_2026.csv`.
Every HQ/base row is flagged for one additional currentness review before it
can become a training label. This protects the model from silently treating an
older source or a division-office location as a current regional HQ.

### Company-by-company public-filing discovery pass

To avoid relying only on location directories, a second reproducible pass
searches official SEC 10-K text for regional/divisional/business-unit HQ
language and matches unambiguous issuers to the 2025 Fortune 500 universe. The
first scan found 19 leads across 16 Fortune 500 companies. These are not added
to the verified-site table until a current company source confirms the site
function and location.

The lead file is
`data/big_business_presence/fortune500_public_filing_regional_hq_discovery_leads_2026.csv`;
the matching summary is
`data/big_business_presence/fortune500_public_filing_regional_hq_discovery_summary_2026.csv`.
The companion script, `scripts/discover_fortune500_regional_hq_sec_leads.py`,
can be re-run to extend the scan. It stores only a short public filing context
and source link—not downloaded filings or licensed location data.

## Recommended use in the project

1. Use the complete Fortune 500 global-HQ model for an initial benchmark of
   corporate-anchor concentration.
2. Describe regional-HQ results as a separate, source-verified dataset under
   construction—not as model labels yet.
3. After a licensed Data Axle/D&B export covers the Fortune 500 consistently,
   assign locations to MSAs, screen out retail/distribution sites, and verify
   regional/divisional HQ function with a first-party source. Only then test a
   regional-HQ or weighted corporate-footprint outcome.

## Sources

- [Fortune 500 ranking](https://fortune.com/ranking/fortune500/2025/)
- [Census 2023 geographic reference files](https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.2023.html)
- [Census Geocoder documentation](https://www.census.gov/programs-surveys/geography/technical-documentation/complete-technical-documentation/census-geocoder.html)
- [2026 state corporate-income-tax rates](https://taxfoundation.org/data/all/state/state-corporate-income-tax-rates-brackets/)
- [GM current U.S. operations](https://www.gm.com/company/us-operations)
- [HCA Miami division-related listing](https://careers.hcahealthcare.com/jobs/18008320-regional-coding-operations-manager-wfh)
- [Amazon HQ2 opening](https://www.aboutamazon.com/news/amazon-offices/amazon-opens-offices-at-hq2-in-arlington-va)
- [JPMorgan Chase Mid-Atlantic headquarters](https://www.jpmorganchase.com/newsroom/press-releases/2022/opens-new-regional-headquarters)
- [JPMorgan Chase Ohio regional headquarters](https://www.jpmorganchase.com/newsroom/press-releases/2023/ohio-headquarters-renovation)
- [Cigna regional headquarters in Plano](https://newsroom.cigna.com/keith-barnes-named-market-president-for-cignas-commercial-business-in-north-texas-and-oklahoma)
- [Comcast Central Division headquarters](https://corporate.comcast.com/stories/local/georgia/comcast-connects-atlanta)
- [HCA East Florida Division](https://investor.hcahealthcare.com/news/news-details/2019/HCA-Healthcare-Appoints-Charles-Gressle-as-East-Florida-Division-President/default.aspx)
- [Kroger division office directory](https://www.thekrogerco.com/contact-us/our-divisions)
- [Lockheed Martin domestic headquarters facilities](https://www.lockheedmartin.com/content/dam/lockheed-martin/careers/how-we-hire/Interview%20Guide%202-25.pdf)
- [PepsiCo Frito-Lay North America headquarters](https://www.pepsico.com/newsroom/press-releases/2009/pepsicos-frito-lay-north-america-headquarters-achieves-leed-gold-certification)
- [RTX corporate and business headquarters](https://www.rtx.com/locations)
- [Boeing Defense, Space & Security headquarters](https://www.boeing.com/content/theboeingcompany/us/en/features/2026/02/boeing-defense-space-and-security-headquarters-returns-to-st-louis.html)
- [Centene East Coast headquarters](https://investors.centene.com/2021-06-21-Centene-Dedicates-New-East-Coast-Headquarters-In-Charlotte)
- [Gulfstream headquarters](https://investorrelations.gd.com/news/press-release-details/2019/Gulfstream-Opens-Gulfstream-East-Campus-At-Company-Headquarters/default.aspx)
- [Merck Upper Gwynedd division headquarters](https://www.merck.com/research/rd-locations/)
- [SEC EDGAR full-text search](https://efts.sec.gov/LATEST/search-index)
