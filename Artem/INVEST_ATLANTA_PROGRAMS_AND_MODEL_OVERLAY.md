# Invest Atlanta Programs and Model Actionability Overlay

**Status (November 5, 2026):** This is a policy-screening aid built from the
current public-model experiment. It is not an estimate that a program caused
business entry, and it is not a funding formula.

## Why program offerings are not XGBoost features

Invest Atlanta programs have the same value for every observation in an
Atlanta-only row: Atlanta has the program; other metros do not. A feature that
does not vary across the model's metro-year observations cannot help XGBoost
learn why one metro has a different business-entry rate from another. Adding a
program name or subjective program score to the training table would produce a
misleading result.

Instead, the work has two separate pieces:

1. **Cross-metro XGBoost:** identifies metro conditions associated with future
   Census employer-establishment entry.
2. **Actionability overlay:** connects those conditions to existing City tools,
   using an explicit 0-3 program-alignment judgment.

The model outcome is broad employer-establishment entry, not Fortune-company
office or headquarters location. The latter still needs a source-verified
company-site dataset.

## Current verified tools

| Tool | What it can support | Boundary for this project |
| --- | --- | --- |
| [Economic Opportunity Fund](https://www.investatlanta.com/site-selectors/resources/bonds-loans-grants-incentives) | Project-specific assistance for acquisition, construction, equipment, infrastructure, leasehold improvements, parking, relocation costs, and workforce training. Eligibility considers job retention/creation, financial strength, and investment. | A discretionary project tool, not a universal tax reduction. |
| [Industrial Revenue Bonds](https://www.investatlanta.com/site-selectors/resources/bonds-loans-grants-incentives) | Long-term financing for eligible manufacturing facilities; published minimum is $2 million and maximum is $10 million. | A manufacturing/facility tool, not an office-attraction tool. |
| [Lease Purchase Bonds](https://www.investatlanta.com/site-selectors/resources/bonds-loans-grants-incentives) | A 10-year property-assessment ramp for qualifying real and personal property; suggested minimum is $10 million. | Project-specific and requires a job creation/retention plan. |
| [Georgia Opportunity Zone job tax credit](https://www.investatlanta.com/site-selectors/resources/bonds-loans-grants-incentives) | A stated $3,500 per new employee credit against state corporate-income-tax liability for five years in eligible locations. | This is a **state** credit targeted to eligible areas, not a Citywide Invest Atlanta tax-rate change. |
| [Tax Allocation District financing](https://www.investatlanta.com/developers/opportunities-incentives/tax-allocation-district-financing) | Bonds financed by future property-tax increments for infrastructure and other improvements in designated districts. | A place-based redevelopment tool, not a direct company-income-tax break. |
| [Medium/large business assistance](https://www.investatlanta.com/businesses/medium-large-businesses/business-assistance) | Finance and relocation/expansion assistance, tax-incentive navigation, workforce training/services, and site selection. | The page describes assistance categories, not a published uniform dollar benefit. |
| [New and Emerging Technology Business Tax Waiver](https://www.investatlanta.com/businesses/startups-creatives/new-and-emerging-technology-business-tax-waiver) | Waives specified occupation taxes and administrative fees for up to three years for qualifying recent high-tech businesses with less than $1 million in revenue. | This is for qualifying small/new businesses, not a Fortune-company headquarters incentive. |

## Re-run: does a program-aligned XGBoost feature set work better?

The test uses the existing public panel: 581 metro-year observations across 97
MSAs. Each annual prediction is made using only earlier years; 2020-2023 are
held-out test years, for 388 out-of-time predictions. Both specifications use
the same conservative XGBoost settings.

| Feature set | Inputs | Held-out MAE, entry-rate percentage points | Result |
| --- | --- | ---: | --- |
| Full public context | Workforce scale/growth, wages, establishment density, industry mix, tax context, regional price level, and house-price growth | **0.979** | Better predictive model. |
| Invest Atlanta-aligned screen | Establishment density, employment growth, weekly wage, manufacturing, information, and professional-services shares | 1.193 | Worse by 0.214 percentage points (about 22%). |

The narrower, program-aligned feature screen should therefore **not replace**
the full context model. Its value is interpretability for the policy discussion,
not superior forecasting.

## What the full public model relied on most

The model uses held-out permutation importance. The value is the average
increase in entry-rate prediction error when that factor is randomly shuffled;
it does not show a positive/negative direction or a causal effect.

| Factor | Error increase when shuffled | What it means for policy discussion |
| --- | ---: | --- |
| Existing establishments per 100 jobs | 0.167 pp | Strongest factor; use it to investigate commercial-district, site-readiness, and local-firm-growth conditions. |
| State corporate-income-tax rate | 0.128 pp | Important context but mostly outside City control; use state credits and project tools to compete at the margin. |
| Health-sector share | 0.085 pp | Industry structure context; not a direct policy lever. |
| Employment growth | 0.074 pp | Strong policy-adjacent target for job creation/retention and workforce tools. |
| Manufacturing share | 0.059 pp | A plausible fit for Industrial Revenue Bonds and site/equipment support. |

The full ranking is in
`Artem/data/business_entry_models/invest_atl_policy_screen/permutation_importance.csv`.

## Actionability overlay

The overlay multiplies a nonnegative held-out importance value by a documented
program-alignment score: 0 = no direct City tool, 1 = indirect/limited, 2 =
partial, 3 = direct. It deliberately ranks factors that are both predictive in
this experiment and closer to an existing City tool.

This is **not** an XGBoost weight. It should be used to decide what to research
or pilot first, then evaluated with project-level outcomes such as jobs,
payroll, investment, site type, and a City-versus-MSA location flag.

| Highest initial research/pilot priorities | Rationale |
| --- | --- |
| Existing business density | Strongest observed predictive signal and a plausible connection to commercial-district, site, and local-business interventions. |
| Employment growth | Directly matches job creation/retention and workforce support. |
| Manufacturing presence | Direct match with Industrial Revenue Bonds and eligible facility investment. |
| State tax context | Strong observed context signal, but low City control; package state credits and local project tools instead of treating it as a City lever. |

The reproducible overlay table is
`Artem/data/business_entry_models/invest_atl_policy_screen/actionability_overlay.csv`.

## Next decision-ready step

For a large-company/HQ question, create a firm-project panel with verified
company identity, headquarters/office/site type, address or ZIP/ZCTA, decision
date, jobs, investment, and incentive participation. Then test whether a
specific tool changes outcomes relative to comparable eligible but unsupported
projects. That is the design capable of evaluating incentives; the current
metro model is not.
