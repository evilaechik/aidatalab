# Business competitiveness: expanded metro machine-learning experiment

## What changed

This expands the earlier nine-metro screen to **31 metropolitan areas and 290 counties**. It retains Atlanta, Austin, Charlotte, Dallas, Denver, Houston, Nashville, Raleigh, and Miami, and adds Baltimore, Boston, Chicago, Cincinnati, Columbus (Ohio), Indianapolis, Kansas City, Los Angeles, Minneapolis, New York, Orlando, Philadelphia, Phoenix, Pittsburgh, Portland (Oregon), Salt Lake City, San Antonio, San Diego, San Francisco, Seattle, Tampa, and Washington, DC.

These are **metropolitan statistical areas**, not city government boundaries. The additional places were chosen to increase geographic and economic diversity, not because all 22 are equally relevant competitors to Atlanta. Use the original peer group separately for the Invest Atlanta policy discussion.

## Data and model outcome

- **Data source:** public BLS QCEW fourth-quarter county industry slices for 2018–2025, summed to metros using the Census Bureau's 2023 county-based CBSA definitions. The raw national files for 2021–2025 were already in the project; this run adds 2018–2020 and extracts all 31 metros from them.
- **Outcome:** growth in private employment from December of year *t* to December of year *t+1*. Employment growth is a regional performance proxy, not a direct measure of company attraction, retention, City of Atlanta outcomes, or incentive effectiveness.
- **Features:** previous employment growth, Q4 average weekly wage, establishments per 100 jobs, and shares of employment in manufacturing, information, finance, professional services, health, and hospitality. Predictors are measured before the outcome, but QCEW is published with a lag, so this is a retrospective exercise rather than a real-time forecast test.
- **Rows:** 186 metro-year observations with outcomes from 2020 through 2025. A recent-history sensitivity test uses the same metros and 93 observations, with outcomes from 2023 through 2025.
- **Comparisons:** random forest, XGBoost, CatBoost, and ridge regression against two simple baselines: the training-set mean and the metro's previous growth rate. Algorithms and hyperparameters are fixed in advance, not tuned on the test data.
- **Forward-year tests:** predict all 31 metros in 2024 using earlier outcome years, and repeat for 2025. This yields 62 held-out predictions per model, but only two independent test years and substantial shared national shocks. A separate leave-one-metro-out test assesses geographic transfer; it includes contemporaneous years from other metros and is **not** an independent future forecast.

## Recent actual growth for context

These are observed **December 2024 to December 2025** changes, not predictions:

| Metro | Private jobs, December 2025 | Growth |
| --- | ---: | ---: |
| Austin | 1,127,630 | +3.46% |
| Raleigh | 656,262 | +2.95% |
| Columbus, Ohio | 953,895 | +2.20% |
| Charlotte | 1,207,533 | +1.30% |
| Dallas | 3,636,715 | +1.10% |
| Atlanta | 2,558,481 | +0.10% |
| Denver | 1,387,826 | −0.25% |
| Seattle | 1,789,440 | −1.35% |

The full 31-metro data, including all years, is in `data/expanded_metro_models/metro_year_qcew_2018_2025.csv`. These comparisons do not tell us how many jobs were attracted or retained by the city proper.

## Model experiment: history matters

Mean absolute error (MAE) is the average gap between predicted and observed growth, in **percentage points**. Lower is better. Both columns use the same 31 metros and the same held-out outcome years, 2024 and 2025.

| Model | Longer history: 2018–2025 inputs | Recent history: 2021–2025 inputs |
| --- | ---: | ---: |
| Training-set mean | 0.84 | 0.99 |
| Previous growth | 0.99 | 0.99 |
| Ridge regression | 2.03 | 0.83 |
| Random forest | 2.71 | 0.79 |
| XGBoost | 2.88 | 0.80 |
| CatBoost | 2.42 | 0.77 |

With longer history, **every modeled approach performs worse than both simple baselines** on these held-out years. With the recent window, CatBoost has the lowest average error, but the difference from random forest and XGBoost is small, and pooled held-out R² is still negative. The longer window includes pandemic-era shocks; those years may affect the fit, but this comparison alone does not prove the reason for the deterioration.

The recent CatBoost's error was 0.76 points for 2024 and 0.78 for 2025. Atlanta's actual 2025 growth was +0.10%; that model predicted +0.61%. These are retrospective test predictions, not forecasts made at the time. The same 2024–2025 test years are being used to compare models and history windows, so the apparent best result is selection-biased. A future, untouched test period is still needed.

The longer-history leave-one-metro-out test looks better for the random forest (MAE 2.04 points versus 2.94 for the training-mean baseline), but it permits training on other metros in the held-out metro's same year. Shared national shocks can make this easier than predicting a future year. Do not use it as evidence of reliable forward forecasting.

## Qualitative interpretation of feature importance

We calculate held-out **permutation importance** by shuffling an input within each held-out year and measuring the change in error. It is model-specific, not a coefficient, does not give the direction of effect, and is not a causal policy weight. Correlated features and missing values can obscure or distort ranks.

For CatBoost in the recent-history run, finance employment share, information employment share, and manufacturing share each increased average MAE by roughly 0.01–0.02 percentage points when shuffled. These are small relative to the model's 0.77-point MAE. They suggest cluster composition is worth investigating in case studies, **not** that finance, information, or manufacturing caused growth. The information signal was 0.029 points in the 2024 test but only 0.001 in 2025, illustrating instability. The longer-history random forest ranks information higher, but that model performs badly out of sample; its ranking should not be used for decisions.

These signals do not tell Kelly which incentives to recommend. A financial-services share, for example, could reflect existing firms, specialized workers, prior investments, or other conditions not captured in the model. Test possible mechanisms with company decisions, workforce data, site costs, and policy evidence.

## Missingness and limits

BLS suppresses some county-industry observations for confidentiality. If any constituent county has suppressed employment for a sector, the corresponding metro-sector share is left missing; it is median-imputed **inside each training fold**, not filled with zero. Out of 186 rows, professional share is missing 89 times, health 71, hospitality 57, information 55, finance 30, and manufacturing 29. Missingness is therefore a serious limit on the weights and on comparisons across metros with different numbers of counties.

Other important conditions—effective tax burden, housing, skilled-worker availability, office rents, transit, land availability, and incentives—are not in these models. A two-year test, purposeful metro selection, geographic and temporal correlation, and post-hoc model comparison all limit generalization. The source data includes no restricted Invest Atlanta files.

## Recommended next work

1. Collect comparable years of metro workforce, housing, site/office cost, transit, and incentive data. Track release dates to prevent look-ahead leakage and compare coverage before fitting models.
2. Add a direct business-outcome dataset: new-to-market company projects, expansions, closures, or establishment births and deaths. Distinguish announced from delivered jobs and City Atlanta from its suburbs.
3. Use longer-term data and a pre-registered rolling-origin evaluation, reserving a new period not used to choose the model. Compare recent-window and longer-window models and report results by year and by the original nine peer metros.
4. Pair any model signal with qualitative evidence, including company announcements, interviews, policy eligibility, and case studies. Do not interpret importance as causal or turn it directly into incentive weights.

## Sources and reproduction

- [BLS QCEW open data slices](https://www.bls.gov/cew/additional-resources/open-data/csv-data-slices.htm); [BLS guidance for aggregating counties and handling disclosures](https://www.bls.gov/cew/publications/factsheets/aggregating-msa-microsa-and-csa-data-from-county-data.htm).
- [Census 2023 metro delineations](https://www.census.gov/geographies/reference-files/time-series/demo/metro-micro/delineation-files.html).
- [Scikit-learn guidance on permutation importance](https://scikit-learn.org/stable/modules/permutation_importance.html).

Run `PYTHONDONTWRITEBYTECODE=1 python3 Artem/scripts/expanded_metro_models.py` from the repository root. The expanded CSV outputs and README are in `data/expanded_metro_models/`. The script reuses the national source slices in `data/nine_metro_models/raw_qcew_industry_slices/`; the Census workbook is in `data/peer_metro_regression/raw_inputs/`. Python dependencies include pandas, numpy, openpyxl, scikit-learn, XGBoost, and CatBoost.
