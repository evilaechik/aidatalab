"""Convert held-out XGBoost importance into a transparent actionability overlay.

The overlay is intentionally outside the prediction model. Existing Invest
Atlanta programs are Atlanta-only and therefore cannot vary across metros.
It combines each factor's held-out permutation importance with a documented
0-3 judgment of how directly an existing Invest Atlanta tool could address
the factor. It is a prioritization aid, not a causal estimate or funding rule.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ARTEM = Path(__file__).resolve().parents[1]
INPUT = ARTEM / "data" / "business_entry_models" / "invest_atl_policy_screen" / "permutation_importance.csv"
OUTPUT = ARTEM / "data" / "business_entry_models" / "invest_atl_policy_screen" / "actionability_overlay.csv"

PROGRAM_ALIGNMENT = {
    "establishments_per_100_jobs": {
        "plain_factor": "Existing business density",
        "actionability_score_0_to_3": 2,
        "current_tool": "Tax Allocation District financing; small-business financing; site-selection assistance",
        "reason": "Can support commercial districts, site redevelopment, and local firm investment, but does not directly set metro-wide density.",
    },
    "qcew_employment_growth": {
        "plain_factor": "Employment growth",
        "actionability_score_0_to_3": 3,
        "current_tool": "Economic Opportunity Fund; workforce training and services; business retention and expansion support",
        "reason": "Current tools explicitly consider job creation, retention, expansion, relocation, and workforce support.",
    },
    "share_manufacturing": {
        "plain_factor": "Manufacturing employment share",
        "actionability_score_0_to_3": 3,
        "current_tool": "Industrial Revenue Bonds; Economic Opportunity Fund; site-selection support",
        "reason": "Industrial Revenue Bonds specifically finance eligible manufacturing facilities; this is a direct sector match.",
    },
    "avg_weekly_wage": {
        "plain_factor": "Average weekly wage",
        "actionability_score_0_to_3": 2,
        "current_tool": "Economic Opportunity Fund; workforce training and services",
        "reason": "The current strategic direction prioritizes middle-wage jobs, but the City does not directly set metro wages.",
    },
    "share_information": {
        "plain_factor": "Information-sector employment share",
        "actionability_score_0_to_3": 2,
        "current_tool": "New and Emerging Technology Business Tax Waiver; startup financing; site-selection support",
        "reason": "The tax waiver targets qualifying young firms below $1 million in revenue, so it is not a large-company incentive.",
    },
    "share_professional": {
        "plain_factor": "Professional-services employment share",
        "actionability_score_0_to_3": 1,
        "current_tool": "Business assistance; site-selection assistance",
        "reason": "Programs can support projects in the sector, but there is no sector-specific financial tool in the verified inventory.",
    },
    "employment_weighted_corporate_tax_rate": {
        "plain_factor": "State corporate-income-tax context",
        "actionability_score_0_to_3": 1,
        "current_tool": "Georgia Opportunity Zone job tax credit; project-specific incentives",
        "reason": "Georgia sets the tax rate. Invest Atlanta can package or target incentives but cannot change the statewide rate.",
    },
    "share_health": {
        "plain_factor": "Health-sector employment share",
        "actionability_score_0_to_3": 1,
        "current_tool": "501(c)(3) bonds; project-specific financing",
        "reason": "Applicable mainly to eligible nonprofit facilities and not a broad sector-development lever.",
    },
    "log_qcew_employment": {
        "plain_factor": "Metro employment scale",
        "actionability_score_0_to_3": 0,
        "current_tool": "None directly",
        "reason": "Useful context, but not a City-controlled lever in this model.",
    },
    "regional_price_parity": {
        "plain_factor": "Regional price level",
        "actionability_score_0_to_3": 0,
        "current_tool": "None directly",
        "reason": "A broad metro cost context measure, not an Invest Atlanta program lever.",
    },
    "fhfa_hpi_yoy_growth": {
        "plain_factor": "House-price growth",
        "actionability_score_0_to_3": 1,
        "current_tool": "Tax Allocation District financing; residential housing incentives",
        "reason": "The City can influence project supply and redevelopment, but the variable is not a direct affordability or housing-policy measure.",
    },
    "share_hospitality": {
        "plain_factor": "Hospitality-sector employment share",
        "actionability_score_0_to_3": 1,
        "current_tool": "Business assistance; commercial-district investment",
        "reason": "Potentially related to district investment, but not a targeted large-business attraction tool.",
    },
    "share_finance": {
        "plain_factor": "Finance-sector employment share",
        "actionability_score_0_to_3": 1,
        "current_tool": "Site-selection and business assistance",
        "reason": "No verified finance-specific incentive in the current inventory.",
    },
    "employment_share_in_gross_receipts_tax_states": {
        "plain_factor": "Exposure to a gross-receipts-tax state",
        "actionability_score_0_to_3": 0,
        "current_tool": "None directly",
        "reason": "A state-tax structure measure outside City control.",
    },
}


def main() -> None:
    importance = pd.read_csv(INPUT)
    importance = importance[importance["feature_set"] == "all_public_context"].copy()
    if set(importance["feature"]) != set(PROGRAM_ALIGNMENT):
        missing = set(importance["feature"]).symmetric_difference(PROGRAM_ALIGNMENT)
        raise ValueError(f"Mapping does not match model features: {sorted(missing)}")
    mapping = pd.DataFrame.from_dict(PROGRAM_ALIGNMENT, orient="index").rename_axis("feature").reset_index()
    overlay = importance.merge(mapping, on="feature", how="inner", validate="one_to_one")
    overlay["positive_model_importance_pp"] = overlay["mae_increase_pp"].clip(lower=0)
    overlay["actionability_priority_pp"] = (
        overlay["positive_model_importance_pp"] * overlay["actionability_score_0_to_3"] / 3
    )
    overlay["interpretation"] = (
        "Screening priority only: held-out predictive importance multiplied by a documented program-alignment judgment. "
        "Not a causal effect, funding amount, or model input."
    )
    columns = [
        "feature", "plain_factor", "mae_increase_pp", "actionability_score_0_to_3",
        "actionability_priority_pp", "current_tool", "reason", "interpretation",
    ]
    overlay[columns].sort_values("actionability_priority_pp", ascending=False).to_csv(OUTPUT, index=False)
    print(overlay[columns].sort_values("actionability_priority_pp", ascending=False).to_string(index=False))


if __name__ == "__main__":
    main()
