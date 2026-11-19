#!/usr/bin/env python3
"""Translate size-adjusted model signals into an Invest Atlanta realism overlay.

This is deliberately not an XGBoost input. Invest Atlanta's programs exist in
Atlanta, not across all comparison MSAs, so inserting a city-only program score
into a cross-metro model would not identify a credible effect. The overlay
instead ranks which observed associations are both predictive and plausibly
addressable by a current Invest Atlanta tool.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ARTEM = Path(__file__).resolve().parents[1]
INPUT = (
    ARTEM / "data" / "big_business_presence" / "fortune500_employment_normalized_anchor_xgb_2026"
    / "simple_rate" / "anchor_density_rate_xgb_permutation_importance.csv"
)
OUTPUT = ARTEM / "data" / "big_business_presence" / "invest_atl_corporate_anchor_realism_overlay_2026.csv"
BONDS = "https://www.investatlanta.com/site-selectors/resources/bonds-loans-grants-incentives"
TADS = "https://www.investatlanta.com/about-us/tax-allocation-districts"


# Scales: 0 = none, 1 = indirect/limited, 2 = partial or targeted, 3 = direct.
# Scores describe the published tool inventory as of 2026-11-19, not funding
# availability, eligibility approval, or expected project impact.
PROGRAM_MAP = {
    "qcew_employment_growth": ("Employment growth", 3, 3, 3, "Economic Opportunity Fund; medium/large-business assistance", BONDS),
    "avg_weekly_wage": ("Average weekly wage", 0, 0, 0, "No direct City wage-setting tool; retain as labor-market context only", BONDS),
    "establishments_per_100_jobs": ("Existing business density", 2, 3, 3, "Economic Opportunity Fund; Lease Purchase Bonds; Tax Allocation District financing in eligible districts", BONDS),
    "share_manufacturing": ("Manufacturing employment share", 3, 3, 3, "Industrial Revenue Bonds; Economic Opportunity Fund", BONDS),
    "share_information": ("Information-sector employment share", 1, 1, 3, "Business assistance and site-selection support", BONDS),
    "share_finance": ("Finance-sector employment share", 1, 1, 3, "Business assistance and site-selection support", BONDS),
    "share_professional": ("Professional-services employment share", 1, 1, 3, "Business assistance and site-selection support", BONDS),
    "share_health": ("Health-sector employment share", 1, 1, 2, "501(c)(3) bonds and project-specific assistance", BONDS),
    "share_hospitality": ("Hospitality-sector employment share", 1, 1, 2, "Business assistance and commercial-district investment", BONDS),
    "employment_weighted_corporate_tax_rate": ("State corporate-tax context", 0, 2, 1, "Georgia Opportunity Zone credit navigation; project-specific assistance", BONDS),
    "employment_share_in_gross_receipts_tax_states": ("Gross-receipts-tax-state exposure", 0, 0, 0, "No direct Invest Atlanta tool", BONDS),
    "regional_price_parity": ("Regional price level", 1, 2, 2, "Tax Allocation District financing and place-based redevelopment", TADS),
    "fhfa_hpi_yoy_growth": ("House-price growth", 1, 2, 2, "Tax Allocation District financing and place-based redevelopment", TADS),
}


def main() -> None:
    importance = pd.read_csv(INPUT)
    expected = set(PROGRAM_MAP)
    observed = set(importance["feature"])
    if expected != observed:
        raise ValueError(f"Program mapping mismatch: {sorted(expected.symmetric_difference(observed))}")

    mapping = pd.DataFrame(
        [
            {
                "feature": feature,
                "plain_factor": values[0],
                "city_control_0_to_3": values[1],
                "current_program_fit_0_to_3": values[2],
                "geographic_reach_0_to_3": values[3],
                "current_tool": values[4],
                "source_url": values[5],
            }
            for feature, values in PROGRAM_MAP.items()
        ]
    )
    overlay = importance.merge(mapping, on="feature", how="inner", validate="one_to_one")
    overlay["positive_held_out_mae_increase"] = overlay["held_out_mae_increase"].clip(lower=0)
    total_positive = overlay["positive_held_out_mae_increase"].sum()
    overlay["predictive_signal_share_pct"] = (
        100 * overlay["positive_held_out_mae_increase"] / total_positive if total_positive else 0
    )
    overlay["invest_atl_realism_score_0_to_100"] = (
        100
        * (
            0.50 * overlay["city_control_0_to_3"]
            + 0.30 * overlay["current_program_fit_0_to_3"]
            + 0.20 * overlay["geographic_reach_0_to_3"]
        )
        / 3
    )
    overlay["actionable_signal_priority_0_to_100"] = (
        overlay["predictive_signal_share_pct"] * overlay["invest_atl_realism_score_0_to_100"] / 100
    )
    overlay["not_an_xgboost_feature"] = True
    overlay["interpretation"] = (
        "Screening overlay only. The realism score combines City control (50%), current program fit (30%), "
        "and geographic reach (20%). Actionable-signal priority combines this score with held-out predictive "
        "importance. It is not a causal effect, probability, funding formula, or XGBoost input."
    )
    columns = [
        "feature", "plain_factor", "held_out_mae_increase", "predictive_signal_share_pct",
        "city_control_0_to_3", "current_program_fit_0_to_3", "geographic_reach_0_to_3",
        "invest_atl_realism_score_0_to_100", "actionable_signal_priority_0_to_100",
        "current_tool", "source_url", "not_an_xgboost_feature", "interpretation",
    ]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    overlay[columns].sort_values(
        "actionable_signal_priority_0_to_100", ascending=False
    ).to_csv(OUTPUT, index=False)
    print(overlay[columns].sort_values("actionable_signal_priority_0_to_100", ascending=False).to_string(index=False))


if __name__ == "__main__":
    main()
