# Employment-Normalized Corporate-Anchor Model and Invest Atlanta Realism Overlay

Updated: 2026-11-19

## Why this sensitivity test exists

The original corporate-anchor outcome is a **count**. Large metros naturally
have more workers and more large-company locations, so metro employment was
the dominant model association. That answers a scale question, but it is not
the right view if the project wants to ask which metros host more documented
corporate anchors **relative to their workforce**.

This test therefore changes both sides of the model:

1. It measures documented corporate anchors per 100,000 QCEW jobs; and
2. It removes log QCEW employment from the explanatory feature set.

This does not claim that workforce size is unimportant. It prevents size from
automatically overwhelming every other cross-metro relationship.

## Two normalization methods

| Version | Formula | Why it is included |
| --- | --- | --- |
| Simple workforce rate | `documented anchors / 2022 QCEW jobs × 100,000` | The clearest size-adjusted comparison. |
| Empirical-Bayes (EB) workforce rate | `(anchors + national rate × 429,920 jobs) / (QCEW jobs + 429,920 jobs) × 100,000` | Shrinks unusually high or low rates in small metros toward the national rate. The 429,920-job smoothing exposure is the median workforce of the 97 usable MSAs and is chosen without using the anchor outcome. |

The numerator remains the prior documented corporate-anchor measure: complete
Fortune 2025 listed global HQs plus direct-company-source verified
regional/divisional/subsidiary HQ parent-company × MSA pairs. Its regional
component is not a complete office census.

## Model design

- **Cohort:** 97 top-100 MSAs with a 2022 QCEW workforce row.
- **Features:** wage, establishment density, industry shares, prior employment
  growth, tax context, regional prices, and house-price growth.
- **Removed feature:** `log_qcew_employment`.
- **Evaluation:** five outer held-out folds; Optuna tunes the XGBoost model
  only inside each outer training fold (25 trials). Mean baseline and a fixed,
  strongly regularized XGBoost model are retained.
- **Target transformation:** `log1p(rate)` during fitting, transformed back to
  anchors per 100,000 jobs for scoring.

## Results

MAE/RMSE units are documented corporate anchors per 100,000 QCEW jobs. Lower
is better.

| Normalization | Model | Held-out MAE | Held-out RMSE | Held-out R² |
| --- | --- | ---: | ---: | ---: |
| Simple rate | Mean baseline | 0.326 | 0.405 | -0.032 |
| Simple rate | Fixed XGBoost | 0.271 | 0.365 | **0.164** |
| Simple rate | Nested XGBoost | **0.269** | 0.368 | 0.150 |
| EB-smoothed rate | Mean baseline | 0.171 | 0.228 | -0.001 |
| EB-smoothed rate | Fixed XGBoost | **0.151** | **0.214** | **0.121** |
| EB-smoothed rate | Nested XGBoost | 0.156 | 0.217 | 0.089 |

The simple rate is the primary normalized sensitivity result because its
nested XGBoost reduces MAE by about **17.5%** relative to its mean baseline.
The EB version is more conservative about small metros but produces a weaker
relative improvement. Neither result is strong enough to support a causal
incentive recommendation.

Atlanta has 18 documented corporate anchors, 2,514,345 QCEW jobs, a simple
rate of **0.716 anchors per 100,000 jobs**, and an EB-smoothed rate of
**0.693**.

## What remains after removing employment scale

For the simple rate, held-out permutation importance is:

| Factor | Increase in held-out MAE when shuffled |
| --- | ---: |
| Average weekly wage | 0.0499 |
| Establishments per 100 jobs | 0.0146 |
| Finance-sector employment share | 0.0050 |

All remaining factors have an error increase below 0.002. This is an
association screen, not a finding that raising wages or changing the industry
mix causes corporate-anchor attraction.

## Invest Atlanta realism score

The realism score is a **separate policy overlay**, not a model feature.
Invest Atlanta programs do not vary across the comparison metros; adding an
Atlanta-only program score into XGBoost would not identify a credible
cross-metro effect.

For every model factor, the overlay scores:

- **City control (50%)** — can the City/Invest Atlanta directly affect it?
- **Current program fit (30%)** — is there a named current tool that can
  plausibly support it?
- **Geographic reach (20%)** — is that tool citywide, or limited to targeted
  districts/eligible sites?

Each component is scored 0–3 from public program descriptions, then combined
to a 0–100 realism score. `Actionable signal priority` multiplies the factor's
share of nonnegative held-out importance by that realism score. It is a way to
choose what to investigate or pilot first—not a likelihood of success, dollar
award recommendation, or causal model result.

| Factor | Predictive-signal share | Invest Atlanta realism | Actionable-signal priority |
| --- | ---: | ---: | ---: |
| Average weekly wage (context only) | 68.9% | 0.0 | 0.0 |
| Existing business density | 20.1% | 83.3 | 16.7 |
| Finance-sector employment share | 6.9% | 46.7 | 3.2 |

This reframes the policy story: wages have the strongest remaining statistical
association but receive a **zero realism score** because Invest Atlanta does
not set private-sector wages. Business density is the more realistic
place-based lever through site, construction, district, and redevelopment
tools. Employment growth and manufacturing each score 100 for program fit, but
they show no positive independent signal in this small normalized model, so
they should not be elevated merely because a tool exists.

The relevant current tools are published by Invest Atlanta. The Economic
Opportunity Fund is a project-specific fund that can support acquisition or
construction of land, buildings and equipment, infrastructure, leasehold
improvements, relocation, and workforce training. Lease Purchase Bonds hold
title to qualifying real and personal property for ten years under a published
property-assessment ramp; their suggested minimum is $10 million. This is the
closest listed property-tax mechanism, but approval is project-specific and
requires a job creation/retention plan. [Invest Atlanta’s current incentive
inventory](https://www.investatlanta.com/site-selectors/resources/bonds-loans-grants-incentives)

Tax Allocation Districts are another realistic **site/development** tool only
within a designated district: they direct future property-tax increments to
redevelopment investments such as infrastructure and commercial spaces. They
are not a universal corporate-income-tax subsidy. [Invest Atlanta TAD
overview](https://www.investatlanta.com/about-us/tax-allocation-districts)

## Files

- `data/big_business_presence/fortune500_employment_normalized_corporate_anchor_outcome_2026.csv`
- `data/big_business_presence/fortune500_employment_normalized_anchor_xgb_2026/simple_rate/`
- `data/big_business_presence/fortune500_employment_normalized_anchor_xgb_2026/empirical_bayes_rate/`
- `data/big_business_presence/invest_atl_corporate_anchor_realism_overlay_2026.csv`
- `scripts/build_fortune500_employment_normalized_anchor_outcome.py`
- `scripts/build_invest_atl_corporate_anchor_realism_overlay.py`

## Guardrails

1. The regional/divisional component is source-verified public evidence, but
   no public process has established it as a complete national census.
2. The target combines a 2025 global-HQ listing with regional/divisional
   evidence collected through 2026, so this is a cross-sectional diagnostic,
   not a time-stamped attraction or retention event study.
3. The realism score is intentionally outside the model. A valid incentive
   evaluation requires a project-level panel with company, address, dates,
   jobs, investment, eligibility, award, and a comparable unsupported group.
