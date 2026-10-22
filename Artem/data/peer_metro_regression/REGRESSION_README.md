# County Q4 employment-growth regression

## Model

**Outcome:** year-over-year log growth in Q4 private employment for a county.

**Observations:** 90 county-year observations: 45 counties in Atlanta, Austin, and Charlotte, observed for the 2023–24 and 2024–25 changes. County counts are Atlanta 29, Austin 5, and Charlotte 11.

**Predictors:** prior-year Q4 county employment, prior-year average weekly wage, prior-year shares of six industry groups, Austin and Charlotte metro indicators with Atlanta as the reference, and a 2025 year indicator.

**Fit:** R-squared = 0.151; residual degrees of freedom = 78.

## Interpretation rules

- Coefficients use log points. For small values, multiplying a coefficient by 100 approximates a percentage-point change in annual employment growth.
- Industry-share coefficients estimate association after controlling for the other listed predictors. They are not evidence that changing a county's industry mix would cause the same change in growth.
- Metro indicators absorb many unobserved metro differences. State tax cannot be estimated separately in this model because each metro is located in one state and the tax rate does not vary within a metro.
- Approximate p-values use HC3 heteroskedasticity-robust standard errors and a normal approximation. With only 90 observations and two annual changes, treat them as screening evidence rather than a final causal result.

## Data

The model uses BLS QCEW fourth-quarter county files for 2023, 2024, and 2025 and the Census Bureau's July 2023 metropolitan-area delineation file. It uses private ownership totals and six NAICS-sector employment shares.
