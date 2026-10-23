# External-factor entry model: no prior entry-rate feature

## Purpose

This is the first model aimed at the project’s explanatory question: *what workforce and industry conditions are associated with future employer-establishment entry?*

It explicitly excludes prior-year BDS establishment-entry rate and every other BDS business-dynamism rate. That prevents the model from merely learning that a metro that had many openings last year may have many again this year.

## Current public inputs

The model uses BLS Quarterly Census of Employment and Wages (QCEW) inputs from the preceding year for the 100-MSA roster:

- total employment and employment growth;
- average weekly wage;
- establishments per 100 jobs;
- employment shares in manufacturing, information, finance, professional services, health, and hospitality.
- an employment-weighted state top statutory corporate-income-tax rate, with a separate flag for exposure to a gross-receipts-tax state.
- BEA all-items regional price parity, a cross-metro price-level index (United States = 100).
- FHFA year-over-year fourth-quarter house-price-index growth. For markets with metropolitan divisions, including Atlanta, the division growth rates are combined with same-year QCEW employment weights.

The outcome remains the following year’s Census BDS employer-establishment entry rate. The expanded model has 581 usable metro-years across 97 MSAs, with rolling future-year tests for 2020–2023 (388 predictions).

## Result

| Model | Held-out entry-rate MAE |
| --- | ---: |
| XGBoost with external workforce, industry, tax, housing, and price-level factors | **0.979 pp** |
| Historical mean-rate baseline | 1.628 pp |

This is encouraging evidence that workforce and industry structure contain information beyond a no-information baseline. It is still an exploratory predictive result, not proof that a factor causes business openings. It also should not be compared as a replacement for the momentum model: that model has access to prior business-entry information, while this one intentionally does not.

## External-factor importance

| Prior-year factor | Increase in held-out error when shuffled |
| --- | ---: |
| Establishments per 100 jobs | 0.167 pp |
| Employment-weighted corporate-income-tax rate | 0.128 pp |
| Health-sector employment share | 0.085 pp |
| QCEW employment growth | 0.074 pp |
| Manufacturing employment share | 0.059 pp |
| Metro employment scale | 0.037 pp |
| Regional price parity | 0.028 pp |
| House-price growth | 0.025 pp |

These values show predictive association only. For example, a positive importance for health-sector share does not mean that raising the health-sector share would cause the listed improvement in business entry.

## Data quality boundaries

- Three Connecticut MSAs are excluded from this historical QCEW model because the 2023 Census delineation uses Connecticut planning-region FIPS codes that do not exist in older QCEW files. Providence has a 2017 gap and Washington, DC has a 2015 gap. The model never fills these gaps with zeros; see `qcew_coverage_issues.csv`.
- Industry disclosures are withheld for some county-sector combinations. Those values remain missing and are imputed within each training fold; they are not treated as zero employment.
- Geography is metro-wide. The results are not evidence about the City of Atlanta boundary.
- Regional price parity is an all-items price-level measure, while the FHFA feature is a change in a repeat-sales house-price index. Neither measures office vacancy or commercial rent directly.

## Next data layers

These are the right additions, but they need careful geographic matching rather than quick proxies:

1. **Transit:** use Federal Transit Administration National Transit Database service supply or Census ACS public-transit commute share. NTD agencies must be mapped to MSAs; ACS measures usage, not pure availability.
2. **Office market:** use office vacancy and asking-rent data for a smaller set of matched peer markets. No free, standardized 100-MSA office-vacancy history is available from an authoritative public source, so we should not substitute residential building permits and call it office availability.
3. **Labor-market slack:** add BLS LAUS metro unemployment and labor-force measures. These must be joined by official BLS metro IDs and dated before the entry outcome.
4. **Incentives/project outcomes:** construct a firm-project panel with dates, jobs, industry, facility type, and City-versus-metro address. That is needed for causal policy analysis and major-company attraction specifically.

## Reproduce

Run `python3 Artem/scripts/external_factor_qcew_xgboost.py`.

Outputs are in `Artem/data/business_entry_models/external_qcew_factors/`.
