# Business competitiveness: nine-metro modeling brief

## Question and outcome

Can last year's industry mix and local business conditions help predict next year's private-employment growth in the Atlanta metro and eight comparison metros: Austin, Charlotte, Dallas, Denver, Houston, Nashville, Raleigh, and Miami?

This first model measures **year-over-year change in December private-sector employment**, a proxy for regional labor-market performance. It is **not** a direct measure of business attraction, expansion, retention, the City of Atlanta's capture of projects, or the impact of incentives. Job growth combines openings, expansions, closures, departures, and other changes.

## What the data says

| Metro | December 2025 private jobs | December 2024–2025 change |
| --- | ---: | ---: |
| Atlanta | 2,558,481 | +0.10% |
| Austin | 1,127,630 | +3.46% |
| Charlotte | 1,207,533 | +1.30% |
| Dallas | 3,636,715 | +1.10% |
| Denver | 1,387,826 | −0.25% |
| Houston | 2,872,860 | +0.70% |
| Nashville | 980,237 | +0.18% |
| Raleigh | 656,262 | +2.95% |
| Miami | 2,537,789 | +0.62% |

These are metro totals, not counts for the named city governments. Metro memberships are fixed using the 2023 Census delineation and total 96 counties. Atlanta is 29 counties; Austin 5; Charlotte 11; Dallas 11; Denver 10; Houston 10; Nashville 14; Raleigh 3; and Miami 3.

## How the model was tested

- **Data:** BLS QCEW fourth-quarter county totals and industry data, 2021–2025, aggregated to nine fixed metros. The quarter's December employment is used for the outcome.
- **Inputs:** prior employment growth; average weekly wage; establishments per 100 jobs; and employment shares in manufacturing, information, finance, professional services, healthcare, and hospitality.
- **Timing:** each row uses conditions measured in year *t* to predict employment growth from December *t* to December *t+1*. QCEW is released with a lag, so the year-*t* inputs are not available at the start of year *t+1*. The complete modeling panel has 27 metro-year rows, with outcomes in 2023–2025. This is a retrospective proxy exercise, not an operational real-time forecasting test.
- **Forward-year test:** train on earlier outcome years, then predict 2024 and 2025. Each test has nine metros. The 2024 test uses only nine training rows; the 2025 test uses 18. This is the more relevant check for forecasting the future.
- **Second check:** leave one metro out at a time. This tests transfer across metros, but training can include the same calendar year as the held-out metro, so it is not an independent future forecast.
- **Comparisons:** a training-set mean baseline, ridge regression, random forest, and XGBoost. Model settings are fixed, without a hyperparameter search.

### Test results

| Model | Forward-year mean absolute error, percentage points | Forward-year pooled R² | Leave-one-metro-out MAE, percentage points |
| --- | ---: | ---: | ---: |
| Training-set mean | 1.53 | −1.74 | 1.07 |
| Ridge | 1.38 | −1.64 | 0.95 |
| Random forest | 1.30 | −1.33 | 0.90 |
| XGBoost | 1.42 | −1.84 | 0.90 |

The random forest has the lowest forward-test error in this small comparison, but a negative pooled R² means its predictions were worse than an oracle benchmark using the test period's overall mean. That test-period mean would not be known in advance; the practical training-set mean baseline is shown separately. Choosing the best model using these same results also makes its reported performance optimistic. **This is not a reliable forecasting model yet.**

## What the “weights” do and do not tell us

We measured **held-out permutation importance**, not conventional regression coefficients: shuffle one input across the nine held-out metros within each test year, and measure how much average prediction error changes. Positive values mean shuffling made predictions worse on average; zero or negative values do not prove a factor is irrelevant. They give neither a causal effect nor a positive/negative direction of influence. Correlated features and sparse data can distort the ranking.

| Random-forest input | Mean increase in held-out error when shuffled, percentage points | Qualitative interpretation |
| --- | ---: | --- |
| Finance employment share | +0.0146 | A tentative industry-mix signal. It could represent a financial-services cluster, but cannot distinguish talent, firms, wages, or local policy. |
| Establishments per 100 jobs | +0.0067 | A tentative signal of business-base composition or average establishment size, not a direct measure of new business attraction. |
| Information employment share | +0.0028 | A weak signal potentially related to technology activity; it is not evidence that increasing this share causes growth. |
| Manufacturing employment share | +0.0027 | A weak signal for industrial composition, not a causal effect of manufacturing. |

These changes are tiny compared with the forest's 1.30-point prediction error. They are averages over only two held-out years and should not be presented as stable percentage weights. In particular, **do not select an incentive because one variable ranks first**.

## Missing data and limitations

BLS suppresses employment in some county/industry cells to protect employers. We preserve those values as missing, never as zero. If any component county is suppressed for a metro-sector-year, the metro share is left missing; a median estimated from the training fold is used for that feature. Across the 27 modeling rows, professional-services share is missing in 18, health and hospitality each in 14, information in 9, finance in 7, and manufacturing in 3. This severely limits conclusions about the apparent industry rankings. A county-industry record absent altogether is treated as zero, following BLS guidance; suppression is tracked separately.

**Review of earlier analysis:** the previous `build_peer_metro_regression.py` script did not check `disclosure_code` when constructing sector shares, so it could treat suppressed BLS zero-filled cells as actual zero employment. Its sector-level trends and regression outputs should be revalidated before presentation. The nine-metro model uses a separate suppression-aware pipeline; the total-employment figures are checked for suppression.

The nine metros share only five years of raw data, and their economic cycles are correlated. The model has no direct observations of incentives, tax burden, office rents, sites, transit, workforce availability, company relocation decisions, or City of Atlanta results. It cannot establish why a firm chose a location. Inflation and differences in local industrial composition also complicate interpreting wages. We do not use the restricted Invest Atlanta dataset.

## Work for the team

**Artem:** Validate more years and geographic definitions, test stability with different training windows and seeds, and compare a simple model to the forest on genuinely held-out years. Pursue a company-project or establishment entry/exit outcome where comparable data exists. Do not treat this prototype as a final causal analysis.

**Shane:** Add comparable historical metro data for workforce and educational attainment, housing costs, commercial rents/vacancy where licensing permits, transit/commute access, and business openings/closures. Record geography, years, definitions, availability dates, and sources. The source and output files for this model are in `data/nine_metro_models/`.

**Kelly:** Build a cited inventory of peer-city and state incentives, including eligibility, type, award amount, performance requirements, clawbacks, and effective dates. Treat finance, professional services, and industrial-site support as hypotheses for comparison—not factors proven by the model. Compare policies only after checking whether Atlanta could administer them and whether a project actually used them.

## Sources and reproducibility

- [BLS QCEW data and methodology](https://www.bls.gov/cew/overview.htm), [open data slices](https://www.bls.gov/cew/additional-resources/open-data/csv-data-slices.htm), and [aggregation/disclosure guidance](https://www.bls.gov/cew/publications/factsheets/aggregating-msa-microsa-and-csa-data-from-county-data.htm).
- [Census Bureau 2023 metro delineations](https://www.census.gov/geographies/reference-files/time-series/demo/metro-micro/delineation-files.html).
- [Held-out permutation-importance guidance](https://scikit-learn.org/stable/modules/permutation_importance.html).

All raw QCEW industry slices, the county membership, derived metro panel, model inputs, predictions, metrics, and per-year importance are saved in `data/nine_metro_models/`. Run `python3 Artem/scripts/nine_metro_models.py` from the repository root to reproduce them. The original Census source workbook remains under `data/peer_metro_regression/raw_inputs/`. Libraries required: pandas, numpy, openpyxl, scikit-learn, and xgboost; downloads use curl. This is an initial public-data research prototype, not a finished policy recommendation.
