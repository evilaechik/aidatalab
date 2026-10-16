# Atlanta, Austin, and Charlotte: deeper public-data analysis

Date: 2026-10-09

## What this analysis can answer

This compares the three **metropolitan areas** using public county-level employment data. It is useful for identifying different growth patterns and testing which characteristics are associated with county employment growth.

It does not directly measure a firm moving into a metro, expanding a local office, or deciding to remain. Those outcomes require announcement, project, lease, permit, and address-level records.

## Q4 private employment trend

| Metro | Q4 2023 | Q4 2024 | Q4 2025 | 2023–24 growth | 2024–25 growth |
| --- | ---: | ---: | ---: | ---: | ---: |
| Atlanta-Sandy Springs-Roswell | 2,542,158 | 2,556,020 | 2,558,481 | +0.55% | +0.10% |
| Austin-Round Rock-San Marcos | 1,085,925 | 1,089,930 | 1,127,630 | +0.37% | +3.46% |
| Charlotte-Concord-Gastonia | 1,187,290 | 1,192,005 | 1,207,533 | +0.40% | +1.30% |

Atlanta has by far the largest private employment base. Its growth slowed sharply in 2025 relative to Austin and Charlotte. This is a signal for deeper work. It does not establish that Atlanta lost attraction or retention decisions because total employment also reflects business cycles, productivity, labor supply, and closures.

## Sector findings, 2024–25

| Metro | Strongest positive signals | Signals to investigate |
| --- | --- | --- |
| Atlanta | Health care and social assistance: +15,163 jobs (+4.25%). Professional/scientific/technical services were essentially flat. | Transportation/warehousing: -23,424 jobs (-12.39%); manufacturing: -3,539 (-2.02%); information: -2,760 (-3.33%); finance/insurance: -2,433 (-1.94%). |
| Austin | Manufacturing: +12,836 (+17.94%); professional/scientific/technical services: +5,738 (+3.83%); health care: +4,789 (+3.57%). | Validate whether manufacturing growth is tied to a small number of facilities before treating it as a metro-wide attraction result. |
| Charlotte | Health care: +5,276 (+4.24%); finance/insurance: +4,592 (+4.63%); professional/scientific/technical services: +2,094 (+2.35%). | Information: -3,038 (-11.65%); manufacturing: -6,527 (-6.00%). |

The full sector table is in `data/peer_metro_regression/metro_sector_q4_trends_2023_2025.csv`.

## Linear-regression screen

### Design

- **Unit of analysis:** County-year.
- **Sample:** 45 counties in the three 2023 Census-defined metros, observed over two changes: 2023–24 and 2024–25. That produces 90 observations.
- **Outcome:** Year-over-year log change in a county's Q4 private employment.
- **Inputs:** prior-year county employment, prior-year average weekly wage, prior-year employment shares in information, finance, professional services, manufacturing, transportation/warehousing, and health care; Austin and Charlotte metro indicators; and a 2025 year indicator.
- **Estimation:** Ordinary least squares with HC3 robust standard errors.

### Result

The model's R-squared is **0.151**. It explains about 15% of the county-level variation in employment growth. That is useful as a screening result, but it leaves most variation unexplained.

The Austin metro indicator is +0.025 log points relative to Atlanta after the model controls for its listed county characteristics. In plain language, the Austin counties in this narrow sample grew about 2.5 percentage points faster per year than comparable Atlanta counties in the model. The Charlotte indicator is near zero after those controls.

Do not present that Austin coefficient as the effect of Austin policy, Texas taxes, or a particular incentive. There are only three metros, so each metro indicator includes all unmeasured characteristics of that metro. State tax cannot be estimated separately because it does not vary inside a metro and is inseparable from the metro indicator.

No industry-share coefficient is strong enough in this small model to establish that a particular sector mix causes faster county growth. This is exactly why the next phase needs direct business-decision data.

The reproducible coefficients, standard errors, and approximation-based p-values are in `data/peer_metro_regression/county_q4_employment_growth_regression.csv`.

## What factors are plausible after this screen

| Factor | Current evidence | Next evidence needed |
| --- | --- | --- |
| Industry clusters | Austin's recent growth is concentrated in manufacturing and professional services. Charlotte's finance employment is growing. Atlanta's health-care base is growing, while logistics employment needs investigation. | Company-level expansion announcements, occupation data, supplier/customer linkages, and industry-specific job postings. |
| Talent and wage structure | The model includes prior average weekly wages and industry mix, but neither isolates a clear relationship in the current sample. | Occupation employment, degree completions, STEM and finance talent supply, and employer statements that cite talent. |
| Sites and real estate | Not measured in the model. This could be especially important for Austin manufacturing and Atlanta's office-location question. | Industrial/office vacancy, asking rent, absorption, site inventory, construction permits, and travel time to sites. |
| Incentives and taxes | Georgia, Texas, and North Carolina have different state tax systems, but the current sample cannot separate tax policy from every other metro difference. | Comparable total-cost scenarios plus incentive awards, eligibility rules, and firm-level project decisions. |
| City capture | All results are metro-wide. They cannot say whether jobs are locating in Atlanta proper or in suburban jurisdictions. | Geocoded office and facility addresses, classified as City of Atlanta, metro suburb, or outside the metro. |

## Recommended next analysis

Build a decision-level table for 2020–2026. Each row should be one announced project, office opening, expansion, retention, closure, or relocation. Capture:

1. Company and NAICS industry.
2. Exact site and City-versus-suburb classification.
3. Decision type: attraction, expansion, retention, closure, or relocation.
4. Announced jobs, capital investment, square feet, and decision date.
5. Cited reason: workforce, cost, site availability, customer access, logistics, incentives, leadership/HQ, or other.
6. Incentive offered and final outcome when public.

That table gives the project a direct outcome measure. It also makes a later regression meaningful: the dependent variable can become a count or value of actual firm decisions rather than broad employment growth.

## Public sources and reproducibility

- BLS Quarterly Census of Employment and Wages, county area slices, fourth quarter 2023–2025: https://www.bls.gov/cew/overview.htm
- Census Bureau, July 2023 metropolitan-area delineation file: https://www.census.gov/geographies/reference-files/time-series/demo/metro-micro/delineation-files.html
- The reproducible script is `scripts/build_peer_metro_regression.py`.
