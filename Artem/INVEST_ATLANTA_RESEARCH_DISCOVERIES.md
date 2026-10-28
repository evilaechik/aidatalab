# Invest Atlanta Research Discoveries and Decision Log

**Status:** research design and data-quality record. This is not a final
policy recommendation or a final model.

## 1. Research question

The project is addressing:

> Where is Atlanta lagging in business attraction, expansion, and retention
> relative to comparable metros, what conditions are associated with those
> gaps, and which City/Invest Atlanta actions are credible candidates to test?

The question has three separate outcomes that should not be blended into one
score:

| Outcome | Definition needed for the final study |
| --- | --- |
| Attraction | A new qualifying office, HQ, R&D, or operating site opens in the study geography. |
| Expansion | A qualifying existing employer adds jobs, payroll, floor space, or a new local function. |
| Retention | A qualifying employer remains and maintains a defined employment or operations baseline. |

The current company-location experiment is not a measure of all three. At
best, it is an imperfect cross-sectional proxy for large-company location
presence.

## 2. Geography: City of Atlanta and Metro Atlanta are different questions

Nicole’s point is important: an Alpharetta office can create Metro Atlanta
jobs, spending, and housing demand, but it does not automatically deliver the
same tax base, downtown activity, or place-based benefit as a City of Atlanta
office.

The project should carry two explicit geography fields:

| Geography | Proper use |
| --- | --- |
| **City of Atlanta** | The core Invest Atlanta outcome: office location, jobs, sites, incentives, tax base, and access within the City. |
| **Metro Atlanta MSA** | Labor market, talent draw, housing, commuting, airport, and regional business ecosystem context. |

Do not count a suburban office as a City office. Instead, use later labor-shed
and commute analysis to test whether a suburban job center produces material
City benefit or competes with it.

All metro analysis uses official Census MSAs/CBSA boundaries. A multi-state
MSA must either include its whole geography or be excluded from a state-scoped
comparison; it cannot be partially assigned to one state for convenience.

## 3. Comparison cohorts built

| Cohort | Definition | Intended use | Important limitation |
| --- | --- | --- | --- |
| National Top 100 | 100 MSAs ranked by 2023 Census BDS employer establishments | Broad benchmark | The available company-location export has systematic geographic gaps; do not use its previous model as a national result. |
| Green-map Southern/Sunbelt 100 | 100 largest eligible MSAs wholly inside AL, AR, CO, DE, FL, GA, KS, KY, LA, MD, MS, MO, NM, NC, OK, SC, TN, TX, and VA | Atlanta-facing regional peer screen | It is a project-defined scope, not the official Census South or a universally accepted Sunbelt definition. |

The two rosters overlap in 43 MSAs. They are not independent samples.

## 4. Data available now

### Public metro tables

| Data source | Measures assembled | Use | Limitation |
| --- | --- | --- | --- |
| [Census BDS](https://www.census.gov/programs-surveys/bds.html) | Employer-establishment counts | Builds metro rosters | A business-dynamics measure, not office presence. |
| [BLS QCEW](https://www.bls.gov/cew/) | Employment, growth, wages, establishments per 100 jobs, sector shares | Structural metro context | Historical association, not a City lever. |
| State corporate-tax archive | Employment-weighted corporate-tax rate and gross-receipts-tax exposure | State business-cost context | State-level policy is not controlled solely by Invest Atlanta. |
| [BEA regional price parities](https://www.bea.gov/data/prices-inflation/regional-price-parities) | Relative price level | Cost context | Does not measure commercial rents or site availability. |
| [FHFA HPI](https://www.fhfa.gov/data/hpi/datasets) | House-price growth | Housing-market context | A price trend is not housing affordability or a City housing policy. |
| [Census BPS](https://www.census.gov/construction/bps/index.html) | Permitted homes per 1,000 jobs; multifamily share | Housing-supply pipeline scorecard | Does not measure office space, affordability, or permitting speed. |
| [IPEDS](https://nces.ed.gov/ipeds/use-the-data) | Business/STEM bachelor’s-or-higher completions per 1,000 jobs | Talent-pipeline scorecard | Counts institution location, not graduate retention or employer-ready availability. |
| [Census CBP](https://www.census.gov/data/datasets/2023/econ/cbp/2023-cbp.html) | Establishments by size band; large-establishment share | Descriptive business ecosystem | Must not predict the Fortune-location outcome because it is outcome-adjacent leakage. |

The housing, talent, and descriptive business-ecosystem tables cover all 100
green-map MSAs and all 100 national-roster MSAs. The data files and builders
are in `Artem/data/...` and `Artem/scripts/...`.

### Restricted data rule

Invest Atlanta’s confidential business-license, revenue, and employee records
must stay outside the repository and must follow the agreement governing their
use. No such raw data should be uploaded to GitHub or used in a public model
output. Licensed Data Axle location inputs and location-level derivatives also
remain outside the repository.

## 5. Company-location outcome: what we discovered

### Desired final outcome

The final large-business score should count distinct Fortune companies with a
**source-verified qualifying site in an MSA**, with a site-type field:

- office / regional office;
- headquarters;
- R&D or engineering;
- manufacturing;
- warehouse / logistics;
- retail / consumer; or
- unknown pending review.

The study must decide which site types count for each operation-specific
question. An office/HQ study should not treat a warehouse like an office.

### Problems found in the supplied Data Axle export

The initial automated score is not suitable as a national Fortune-office
outcome. The audit found:

1. Only **86 distinct current Fortune 100 companies** were represented, not
   the full 100-company universe.
2. Generic text searches can return unrelated businesses with a similar name;
   a search label alone does not prove company identity.
3. The export is geographically incomplete. It has no raw assigned records
   for 17 National Top-100 MSAs, including all listed California, Washington,
   Oregon, and Hawaii cases.
4. A warehouse/retail screen removes obvious non-office sites but cannot fix a
   wrong company identity or a missing regional export.

The 17 missing metros are Los Angeles, San Francisco, San Diego, Riverside,
Sacramento, San Jose, Oxnard, Fresno, Santa Rosa, Bakersfield, Seattle,
Spokane, Portland, Honolulu, Boise, El Paso, and Reno. They are **unknown**,
not zero-office metros.

See `Artem/FORTUNE100_NATIONAL_COVERAGE_AUDIT.md` for the full per-metro
coverage audit and repair protocol.

### Conservative sensitivity screen

A stricter local screen was built for diagnostic purposes only. It requires:

- an exact normalized match in a Data Axle headquarters or corporate-parent
  field; or
- an exact normalized business-name match for a Branch or Headquarters record;
- then exclusion of explicitly retail, warehouse/logistics, shipping/mailing,
  and kiosk sites.

This removes many obvious name-match errors. It still does not turn the export
into verified office data, and a zero from this screen means “no observed
high-confidence candidate,” not “no office.”

## 6. Modeling discoveries

### Validation design used

The exploratory models use five outer held-out MSA folds. Optuna tuning occurs
inside each outer-training fold through three inner folds. Ridge penalties,
scaling, and imputation are fitted only on training folds. SHAP values are
calculated for held-out predictions.

That prevents direct tuning leakage into the test fold. It does **not** remove
selection uncertainty from trying multiple cohorts, feature sets, and model
families in a small cross-section.

### Source-covered sensitivity results

These results are model-mechanics checks on the high-confidence candidate
proxy, not evidence about verified office attraction.

| Scope and context-only model | Usable MSAs | MAE | Held-out R² | Discovery |
| --- | ---: | ---: | ---: | --- |
| Source-covered national-roster subset: tuned XGBoost | 80 | 2.73 | 0.633 | XGBoost outperformed the tested linear models in this subset. |
| Source-covered national-roster subset: OLS | 80 | 3.72 | 0.392 | Linear fit was weaker in this subset. |
| Source-covered national-roster subset: Ridge | 80 | 3.64 | 0.403 | Ridge was also weaker in this subset. |
| Source-covered green-map subset: tuned XGBoost | 99 | 2.71 | 0.492 | Lowest average prediction error in this scope. |
| Source-covered green-map subset: OLS | 99 | 3.04 | 0.528 | Highest held-out R² in this scope. |
| Source-covered green-map subset: Ridge | 99 | 2.97 | 0.513 | Close to both XGBoost and OLS. |

There is no universally best model across the two scopes. The southern model
does not justify forcing XGBoost, OLS, or Ridge as the final model before the
outcome is rebuilt and validation is pre-specified.

### Housing and talent finding

Adding the BPS housing-pipeline proxies and IPEDS talent proxy lowered the
observed held-out scores in these specific runs. This is **not evidence that
housing or graduates do not matter**. It may reflect small-sample variation,
feature correlation, target noise, or iterative model selection.

Keep these variables in the peer scorecard and test them again after the
project has a verified outcome and a pre-specified validation plan.

### SHAP/“weight” finding

XGBoost has no single fixed linear coefficient. Normalized mean-absolute SHAP
shares show which variables a fitted model relied on, not the effect of a
policy change.

In the green-map context-only diagnostic, the largest shares were metro
employment (17.5%), corporate-tax rate (16.8%), house-price growth (13.7%),
finance-sector share (12.0%), and average weekly wage (9.5%). These are
**exploratory hypotheses**, not final policy weights and not incentive-dollar
weights.

## 7. What is safe to say now

1. Atlanta needs separate City and MSA scorecards. Suburban offices should
   contribute to regional context without being counted as City wins.
2. Corporate location analysis must distinguish office/HQ/R&D from
   manufacturing, logistics, retail, and other operations.
3. The first Data Axle-based national score is not usable as a national
   benchmark. Missing metros should never be silently coded as zero.
4. QCEW, BPS, IPEDS, FHFA, BEA, and CBP provide a useful comparable metro
   context layer, but most are context measures or proxies rather than direct
   Invest Atlanta levers.
5. SHAP and regression output can guide investigation only after an outcome is
   credible; they cannot select incentives or establish causality.

## 8. Recommended research workflow

### Phase 1 — build a credible business-presence outcome

1. Create a complete current Fortune company universe and company-alias table.
2. Query the licensed source MSA by MSA, rather than use a nationwide
   top-result export.
3. Verify corporate identity and classify site type.
4. Review unknown and high-impact records manually.
5. Record a zero only after a completed query returns no qualifying site.

### Phase 2 — define the performance measures before modeling

For each geography and operation type, pre-specify attraction, expansion, and
retention measures. Use annual panels where possible rather than a single
cross-section.

### Phase 3 — build two separate evidence products

| Product | Purpose |
| --- | --- |
| Descriptive context model | Compare employment scale, industrial composition, labor costs, housing, talent, price levels, and risks across peers. |
| Invest Atlanta opportunity scorecard | Compare direct or policy-adjacent levers: site readiness, office inventory, permitting reliability, transit/workforce access, university partnerships, incentive design, and small-business support. |

### Phase 4 — validate model claims

1. Pre-specify a small factor set based on the operation type.
2. Use a count model such as penalized Poisson or negative binomial as the
   transparent primary baseline; compare XGBoost as an exploratory nonlinear
   benchmark.
3. Use repeated nested cross-validation and confidence intervals for paired
   performance differences.
4. Keep a final untouched validation cohort or later-year outcome test.
5. Report uncertainty and do not translate model importance into incentive
   amounts.

## 9. High-priority next data additions

| Priority | Data | Why |
| --- | --- | --- |
| 1 | Census LEHD LODES / OnTheMap | Tests the City-versus-suburb labor-shed question directly. |
| 1 | BLS OEWS | Adds office/R&D occupation concentration and occupation-specific wage measures. |
| 1 | ACS / HUD | Adds rent burden, vacancy, degree attainment, commute, transit use, remote work, and broadband. |
| 2 | EPA Smart Location Database and FTA NTD | Adds district access, density, and transit-service measures with a documented geographic crosswalk. |
| 2 | Office-market data and site-readiness inventory | Measures actual office blocks, rents, vacancy, zoning, utilities, and delivery timeline. |
| 2 | Peer incentive policy rubric | Compares eligibility, job/wage thresholds, targeting, clawbacks, and site support instead of raw subsidy totals. |

## 10. Supporting project documents

- `Artem/FORTUNE100_NATIONAL_COVERAGE_AUDIT.md` — exact missing-metro and
  export-quality audit.
- `Artem/SOURCE_COVERED_METRO_DIAGNOSTIC.md` — restricted sensitivity model,
  model comparisons, and exploratory SHAP shares.
- `Artem/ACTIONABLE_METRO_FEATURES.md` — current housing/talent features and
  policy-facing data queue.
- `Artem/EXTERNAL_DATA_CATALOG.md` — external dataset inventory and
  operation-specific site-selection framework.

## Bottom line

The project has built a useful public metro-context foundation and identified
the right policy-facing data gaps. The next critical task is not a more complex
model: it is a complete, source-verified company-presence outcome separated by
City, MSA, company identity, and site type.
