# Fortune 500 Global-HQ Model and Regional-HQ Guardrail

## Executive summary

We now have a public, reproducible Fortune 500 global-HQ benchmark for the
project's 200-MSA comparison roster. It is stronger than the earlier Fortune
100 location-candidate proxy because it has a defined company universe and
real zeroes rather than treating missing location coverage as no presence.

- **Corporate-anchor outcome:** 459 Fortune 500 listed global HQs map into the
  200-MSA roster; 78 metros have at least one.
- **Model result:** nested Poisson XGBoost improves held-out MAE from 5.13 HQs
  for the training-mean baseline to 3.09 HQs, with held-out R² of 0.35.
- **Main association:** metro employment scale is the only consistently strong
  predictive signal. This is a descriptive scale effect, not evidence that a
  policy lever causes HQ attraction.
- **City geography:** 480 listed HQ cities map to 222 official Census place
  jurisdictions, allowing City of Atlanta to remain distinct from Alpharetta,
  Sandy Springs, and other Metro Atlanta places.
- **Tax context:** every HQ row has a 2026 state corporate-tax context, but
  city business, payroll, and property taxes cannot be reduced to one national
  rate or an exact company tax bill without address- and company-specific data.
- **Regional HQs:** the location data produces a useful candidate queue, not
  a completed outcome. Those records remain out of model training until a
  first-party source confirms the office function.

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

Of 500 Fortune companies, 459 map into the 200-MSA roster, 18 map to an MSA
outside the roster, and 23 cannot be safely assigned from their city label.
The selected 200 MSAs contain 78 metros with at least one listed global HQ.

This produces a transparent corporate-anchor benchmark, but it does **not**
measure every office, regional HQ, warehouse, or store.

## City-boundary and tax-jurisdiction layer

The MSA assignment is now paired with a city-jurisdiction table. Fortune's
reported HQ city is matched to a 2023 Census **place**—the Census geography
that represents an incorporated municipality or Census-designated place.

- 480 of 500 listed HQ cities match a Census place, yielding 222 distinct
  matched HQ city jurisdictions.
- Each matched company has a Census place GEOID, official place name, legal/
  statistical area descriptor, and a 2026 top statutory **state** corporate
  income-tax rate.
- The remaining 20 HQ labels are left unassigned at the city level rather than
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
| Training-mean baseline | 5.13 HQs | -0.03 |
| Fixed regularized Poisson XGBoost | 3.28 HQs | 0.33 |
| Nested-Optuna Poisson XGBoost | **3.09 HQs** | **0.35** |

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

Two candidates with an explicit regional/divisional keyword were checked first.
Neither currently supports a verified regional-HQ classification: GM identifies
Detroit as its global HQ and does not establish an Oklahoma City regional HQ;
an HCA Miami job listing indicates East Florida division work but does not
establish a physical regional HQ. They remain unverified candidates.

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
