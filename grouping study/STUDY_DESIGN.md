# Study design and similarity specification

Protocol version 1.0 · November 25, 2026 · **Defaults to freeze before implementation results.**

## Scope and units

The focal geography is the Atlanta MSA, CBSA `12060`, not municipal Atlanta. Preserve the 50-MSA July 2023 frame, fixed 2025 Fortune roster, 498 covered HQ firms, two excluded firms, and supplied five development folds. Use the 49 non-Atlanta metros as the donor/validation universe. No new location collection or geographic redefinition is required for the initial HQ run.

Each supervised observation is a company–metro pair. Its binary outcome indicates the firm's one publisher-selected reported HQ point, not every co-HQ or ordinary office. Predictions remain company-level probabilities; summing the same 498 probabilities produces the comparable expected HQ count.

The groups are **overlapping, query-specific neighborhoods**. They are not random groups, fixed K-means partitions, geographic zones, or groups defined using HQ counts. The same donor can support multiple Atlanta companies. IDs are join/tie-break keys, never predictive attributes.

## Prespecified questions

1. Does company-and-metro similarity improve predictive performance near Atlanta relative to the existing global model and an otherwise identical global model tuned for Atlanta-like validation metros?
2. Is the resulting Atlanta assessment stable across reasonable neighbor widths and the predefined sensitivity checks?
3. Are the effective donor populations and their HQ-positive support large enough to justify the local component?

Office outcomes, incentive optimization, new-company generalization, future relocation prediction, and causal effects are not primary questions.

## Regional distance: five balanced blocks

Use these exact existing R1 columns for distance construction. There are 15 columns, grouped into five dimensions. These are a similarity representation, not a replacement of the global regression's 42-input contract.

| Block | Exact columns | Rationale |
| --- | --- | --- |
| Size | `log_msa_private_employment` | One scale measure; avoid giving size separate votes through GDP and population. |
| Workforce capabilities | `bachelors_plus_share_2024`, `soc_business_financial_jobs_per_1000`, `soc_computer_math_jobs_per_1000` | Resident education and two relevant occupational stocks. |
| Industry structure | `cbp_manufacturing_share_2023`, `cbp_retail_share_2023`, `cbp_transport_warehousing_share_2023`, `cbp_information_share_2023`, `cbp_finance_insurance_share_2023`, `cbp_professional_technical_share_2023`, `cbp_health_social_share_2023` | Preserve the original broad-sector coverage as one block rather than cherry-picking Atlanta's HQ sectors. |
| Cost context | `log_median_gross_rent`, `regional_price_parity_2024` | Residential rent and general prices; neither is commercial office rent. |
| Business dynamics | `bds_establishment_entry_rate_2023`, `bds_establishment_exit_rate_2023` | General regional turnover, not named-company arrivals/departures. |

Deliberately exclude the added corporate-management employment share from the distance representation because it can partly describe existing corporate concentration. It remains an allowed R1 regression predictor for a faithful reference comparison, with its endogeneity caveat. The full regression also retains its other inherited features; the experiment changes locality, not the frozen outcome or reference inputs.

Fit median imputation and z-score scaling on **unique training metros**, not on repeated company rows or all 50 metros. Means and standard deviations use the training population convention (`ddof=0`, as in `StandardScaler`). A constant column has scale 1. All-missing distance columns are a data-contract failure. Retain an audit of imputation and constant columns; do not add missingness flags to the distance metric.

For standardized vectors, define squared regional distance:

`D_metro(q,m)^2 = mean over the 5 blocks [mean over columns in that block (z_q - z_m)^2]`.

Thus each block has weight 1/5 regardless of column count. Shares are correlated and are not five independent experiments; block balancing reduces mechanical duplication but does not guarantee a uniquely correct metric. Do not whiten, use PCA, or learn a distance metric in the primary run.

## Company distance

Fit the two numeric company transforms on the distinct eligible training companies. Use inherited `log_company_revenue` and `log_company_workforce`; do not log them again. Company rows are repeated across metros but count once when estimating company scaling.

`D_company(c,f)^2 = 0.4 * mean(z_log_revenue_difference^2, z_log_workforce_difference^2) + 0.5 * I(broad_industry differs) + 0.1 * I(listing_type differs)`.

Categorical columns are `company_broad_industry` and `ownership_listing_type_2025`. Compare the documented category strings exactly; no ordering is implied. Company primary fields are expected complete. A novel query category is a mismatch with existing categories, not a numeric code.

This mixed metric balances scale, industry, and publisher listing type. The weights are explicit design judgments. The industry label is broad; listing type is not a verified legal-ownership taxonomy. There is no extra same-company bonus. A donor from the same known firm is allowed and naturally has zero company distance; company ID is not a distance coordinate. This is transfer across metros for a known roster.

## Soft neighborhoods and local probabilities

For query company `c` in query metro `q`, use only donor metros `m` in the current training split and the common 498 donor companies `f`. Exclude **every row** of any validation/query metro from donor labels. An Atlanta row is never a donor.

1. Set `h_m(q)` to the distance to the `k_m`th nearest distinct donor metro, using one-based rank among training metros.
2. Set `h_c(c)` to the distance to the `k_c`th nearest distinct donor company, including the same firm if present.
3. For a zero bandwidth, use the smallest strictly positive distance in the corresponding donor list; if all distances are zero, use 1. Record the fallback. Break ranking ties by string CBSA/company ID.
4. Normalize Gaussian weights separately: `b_m ∝ exp(-D_metro(q,m)^2 / (2*h_m^2))` and `a_f ∝ exp(-D_company(c,f)^2 / (2*h_c^2))`.
5. Pair weights are `w_fm = a_f * b_m`, summing to 1 across the complete donor grid. The local HQ estimate is `p_local(c,q) = sum_f sum_m w_fm * y_fm`.

This is a soft kernel smoother with nearest-neighbor-adaptive bandwidths. `k` is a bandwidth rank, **not** a hard retained-row count. All numerically supported donors may contribute; far donors can contribute negligibly. Use stable exponentiation and record numerical underflow rather than silently turning the procedure into a hard cutoff.

Do not renormalize each firm's probabilities across metros, condition on its known HQ being outside the frame, balance classes, or turn probabilities into binary labels before aggregation. Firms with HQs outside the frame remain legitimate zero rows.

## Borrowing strength from the global model

Let `p_global(c,q)` be R1-style company logistic regression fitted only on the current training split. Primary grouped prediction:

`p_grouped = (1-alpha)*p_global + alpha*p_local`.

Use `alpha` from `{0, 0.25, 0.5, 0.75}`. Zero is an explicit no-locality fallback; a purely local estimate is not eligible as the selected primary model. This preserves some ability to extrapolate beyond peer counts and stabilizes rare outcomes. It does not create independent observations or calibrated probabilities automatically.

The defined factorized row kernel is the first implementation. A separately fitted regression for each of 498 query firms, hard company clusters, new tree searches, local HQ-rate targets, and employment-offset residual models are outside the first run. They would introduce additional choices and are not required to execute this handoff.

## Atlanta-focused evaluation population

The common validation emphasis is defined using regional covariates only. In each fit/evaluation split, fit the regional transform on training metros and define a reference bandwidth from the 10th nearest training metro to Atlanta. For each held-out metro `j`, its raw evaluation weight is:

`v_j = exp(-D_metro(Atlanta,j)^2 / (2*h_focus^2))`.

Normalize weights across the held-out observations being scored. The focus rule uses the full five-block primary distance, always bandwidth rank 10, independent of the model and candidate `k_m`. It may use Atlanta's input covariates, but not its label. For pooled outer predictions, retain each fold's raw weights and normalize once across all 49 metros. Document their fold-specific origin.

Within inner tuning, compute the corresponding weights using each inner-training transform and bandwidth. Never use a scaler fitted on the outer validation metros to calculate inner or outer focus weights. This makes the target population explicit without pretending the test labels are untouched by previous research.

## Interpretation of locality

Outlying economies may receive little influence in Atlanta's estimate; no universal outlier exclusion is required. A group with few effective metros can still be unreliable even if it has thousands of company rows. Treat soft weights as a bias/variance trade-off to test. Keep size as context; do not claim that filtering out large markets reveals incentive effects.

The primary run and its choices are specified in [TRAINING_HANDOFF.md](TRAINING_HANDOFF.md). Support thresholds and uncertainty limits are in [VALIDATION.md](VALIDATION.md).
