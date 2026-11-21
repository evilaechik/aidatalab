#!/usr/bin/env python3
"""Create static, presentation-ready figures for the corporate-anchor model.

The figures use the employment-normalized sensitivity model so metro scale is
not an explanatory feature. They are intentionally static Matplotlib exports
for slides and Markdown, not an interactive visualization.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ARTEM = Path(__file__).resolve().parents[1]
DATA = ARTEM / "data" / "big_business_presence"
SIMPLE = DATA / "fortune500_employment_normalized_anchor_xgb_2026" / "simple_rate"
EB = DATA / "fortune500_employment_normalized_anchor_xgb_2026" / "empirical_bayes_rate"
OUT = ARTEM / "figures" / "corporate_anchor_model"

NAVY = "#003B70"
BLUE = "#2C7FB8"
TEAL = "#0F766E"
ORANGE = "#E87817"
GRAY = "#6B7280"
LIGHT_GRAY = "#E5E7EB"
RED = "#B42318"

MODEL_LABELS = {
    "training_mean_baseline": "Mean baseline",
    "fixed_regularized_squared_error_xgboost": "Fixed XGBoost",
    "nested_optuna_squared_error_xgboost": "Nested XGBoost",
}
MODEL_ORDER = list(MODEL_LABELS)


def save_figure(figure: plt.Figure, stem: str) -> None:
    """Write slide-ready PNG and vector SVG versions of one figure."""
    figure.savefig(OUT / f"{stem}.png", dpi=220, bbox_inches="tight", facecolor="white")
    figure.savefig(OUT / f"{stem}.svg", bbox_inches="tight", facecolor="white")
    plt.close(figure)


def load_metrics(path: Path) -> pd.DataFrame:
    metrics = pd.read_csv(path)
    metrics["model_order"] = metrics["model"].map({name: index for index, name in enumerate(MODEL_ORDER)})
    return metrics.sort_values("model_order")


def performance_figure(simple: pd.DataFrame, eb: pd.DataFrame) -> None:
    """Compare out-of-fold MAE across the two normalization checks."""
    merged = simple[["model", "mae_outcome"]].merge(
        eb[["model", "mae_outcome"]], on="model", suffixes=("_simple", "_eb")
    )
    merged["label"] = merged["model"].map(MODEL_LABELS)
    merged["order"] = merged["model"].map({name: index for index, name in enumerate(MODEL_ORDER)})
    merged = merged.sort_values("order")

    figure, axis = plt.subplots(figsize=(10.5, 6.2))
    positions = np.arange(len(merged))
    width = 0.34
    simple_bars = axis.bar(
        positions - width / 2,
        merged["mae_outcome_simple"],
        width,
        label="Simple workforce rate",
        color=NAVY,
    )
    eb_bars = axis.bar(
        positions + width / 2,
        merged["mae_outcome_eb"],
        width,
        label="EB-smoothed workforce rate",
        color=TEAL,
    )
    for bar in [*simple_bars, *eb_bars]:
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.009,
            f"{bar.get_height():.3f}",
            ha="center",
            va="bottom",
            fontsize=10,
        )
    axis.set_xticks(positions, merged["label"])
    axis.set_ylabel("Held-out mean absolute error\n(anchors per 100,000 QCEW jobs)")
    axis.set_ylim(0, max(merged[["mae_outcome_simple", "mae_outcome_eb"]].max()) * 1.25)
    figure.suptitle("Size-adjusted model performance", x=0.125, ha="left", fontsize=17, fontweight="bold", color=NAVY)
    figure.text(
        0.125,
        0.91,
        "Lower is better. Each result is evaluated across 97 held-out MSAs; workforce size is excluded as a feature.",
        fontsize=10,
        color=GRAY,
    )
    axis.grid(axis="y", color=LIGHT_GRAY, linewidth=0.8)
    axis.set_axisbelow(True)
    axis.spines[["top", "right"]].set_visible(False)
    axis.legend(frameon=False, loc="upper right")
    figure.tight_layout(rect=(0, 0, 1, 0.88))
    save_figure(figure, "01_size_adjusted_model_performance")


def prediction_figure() -> None:
    """Show outer-fold actual-versus-predicted simple workforce rates."""
    predictions = pd.read_csv(SIMPLE / "anchor_density_rate_xgb_outer_fold_predictions.csv")
    predictions = predictions.loc[predictions["model"].eq("nested_optuna_squared_error_xgboost")].copy()
    atlanta = predictions.loc[predictions["msa"].eq(12060)].iloc[0]
    extent = max(predictions[["actual_outcome_count", "predicted_outcome_count"]].max()) * 1.08

    figure, axis = plt.subplots(figsize=(8.8, 7.2))
    axis.scatter(
        predictions["actual_outcome_count"],
        predictions["predicted_outcome_count"],
        s=46,
        color=BLUE,
        alpha=0.74,
        edgecolor="white",
        linewidth=0.5,
    )
    axis.scatter(
        atlanta["actual_outcome_count"],
        atlanta["predicted_outcome_count"],
        s=95,
        color=ORANGE,
        edgecolor="white",
        linewidth=1.2,
        zorder=3,
    )
    axis.annotate(
        "Atlanta",
        xy=(atlanta["actual_outcome_count"], atlanta["predicted_outcome_count"]),
        xytext=(9, 12),
        textcoords="offset points",
        fontsize=11,
        fontweight="bold",
        color=ORANGE,
    )
    axis.plot([0, extent], [0, extent], linestyle="--", color=GRAY, linewidth=1.2, label="Perfect prediction")
    axis.set_xlim(0, extent)
    axis.set_ylim(0, extent)
    axis.set_aspect("equal", adjustable="box")
    axis.set_xlabel("Actual documented anchors per 100,000 QCEW jobs")
    axis.set_ylabel("Held-out XGBoost prediction")
    figure.suptitle("Held-out predictions: normalized corporate-anchor rate", x=0.125, ha="left", fontsize=16, fontweight="bold", color=NAVY)
    figure.text(
        0.125,
        0.91,
        "Nested XGBoost; Atlanta is 0.716 actual versus 0.443 predicted. This is a diagnostic, not a forecast.",
        fontsize=9.5,
        color=GRAY,
    )
    axis.grid(color=LIGHT_GRAY, linewidth=0.8)
    axis.set_axisbelow(True)
    axis.spines[["top", "right"]].set_visible(False)
    axis.legend(frameon=False, loc="upper left")
    figure.tight_layout(rect=(0, 0, 1, 0.88))
    save_figure(figure, "02_held_out_prediction_check")


def importance_figure() -> None:
    """Show all positive held-out permutation signals with uncertainty bars."""
    importance = pd.read_csv(SIMPLE / "anchor_density_rate_xgb_permutation_importance.csv")
    labels = {
        "avg_weekly_wage": "Average weekly wage (context only)",
        "establishments_per_100_jobs": "Existing business density",
        "share_finance": "Finance-sector employment share",
        "share_health": "Health-sector employment share",
        "share_hospitality": "Hospitality-sector employment share",
        "regional_price_parity": "Regional price level",
    }
    importance = importance.loc[importance["feature"].isin(labels)].copy()
    importance["label"] = importance["feature"].map(labels)
    importance = importance.sort_values("held_out_mae_increase")
    colors = [GRAY if feature == "avg_weekly_wage" else BLUE for feature in importance["feature"]]
    positions = np.arange(len(importance))

    figure, axis = plt.subplots(figsize=(10.6, 6.2))
    axis.barh(
        positions,
        importance["held_out_mae_increase"],
        xerr=importance["permutation_std"],
        color=colors,
        error_kw={"ecolor": "#374151", "capsize": 3, "linewidth": 1},
    )
    axis.set_yticks(positions, importance["label"])
    for position, row in enumerate(importance.itertuples(index=False)):
        axis.text(
            row.held_out_mae_increase + row.permutation_std + 0.0014,
            position,
            f"{row.held_out_mae_increase:.4f}",
            va="center",
            fontsize=9.5,
        )
    axis.set_xlabel("Increase in held-out MAE when the factor is shuffled")
    figure.suptitle("Model signals after removing workforce size", x=0.125, ha="left", fontsize=16, fontweight="bold", color=NAVY)
    figure.text(
        0.125,
        0.91,
        "Higher means the factor helped prediction more. Error bars show variation across 150 held-out shuffles; association only.",
        fontsize=9.5,
        color=GRAY,
    )
    axis.grid(axis="x", color=LIGHT_GRAY, linewidth=0.8)
    axis.set_axisbelow(True)
    axis.spines[["top", "right"]].set_visible(False)
    figure.tight_layout(rect=(0, 0, 1, 0.88))
    save_figure(figure, "03_held_out_factor_signal")


def policy_figure() -> None:
    """Separate predictive signal from City program realism."""
    overlay = pd.read_csv(DATA / "invest_atl_corporate_anchor_realism_overlay_2026.csv")
    select = [
        "avg_weekly_wage",
        "establishments_per_100_jobs",
        "share_finance",
        "share_health",
        "share_hospitality",
        "regional_price_parity",
    ]
    overlay = overlay.set_index("feature").loc[select].reset_index()
    overlay = overlay.sort_values("actionable_signal_priority_0_to_100")
    labels = overlay["plain_factor"].where(
        overlay["feature"].ne("avg_weekly_wage"), "Average weekly wage (context only)"
    )
    positions = np.arange(len(overlay))

    figure, (left, right) = plt.subplots(ncols=2, figsize=(13.2, 6.3), sharey=True, gridspec_kw={"width_ratios": [1.08, 1]})
    left.barh(positions, overlay["predictive_signal_share_pct"], color=[GRAY if value == 0 else BLUE for value in overlay["invest_atl_realism_score_0_to_100"]])
    left.set_yticks(positions, labels)
    left.set_xlabel("Share of nonnegative predictive signal (%)")
    left.set_title("Statistical signal", loc="left", fontsize=13, fontweight="bold", color=NAVY)
    left.grid(axis="x", color=LIGHT_GRAY, linewidth=0.8)
    left.set_axisbelow(True)
    left.spines[["top", "right"]].set_visible(False)

    right.barh(positions, overlay["actionable_signal_priority_0_to_100"], color=TEAL)
    right.set_xlabel("Signal × Invest Atlanta realism")
    right.set_title("Actionable screening priority", loc="left", fontsize=13, fontweight="bold", color=NAVY)
    right.grid(axis="x", color=LIGHT_GRAY, linewidth=0.8)
    right.set_axisbelow(True)
    right.spines[["top", "right"]].set_visible(False)
    for position, row in enumerate(overlay.itertuples(index=False)):
        right.text(
            row.actionable_signal_priority_0_to_100 + 0.35,
            position,
            f"{row.actionable_signal_priority_0_to_100:.1f}",
            va="center",
            fontsize=9.5,
        )
    figure.suptitle("Policy screening: prioritize actionable signals, not just strong correlations", x=0.08, ha="left", fontsize=16, fontweight="bold", color=NAVY)
    figure.text(
        0.08,
        0.02,
        "Wages are retained as labor-market context but receive zero policy realism because Invest Atlanta does not set private-sector wages.\n"
        "Business density is the leading actionable screen; relevant tools include project-specific site, construction, leasehold, and redevelopment support.",
        fontsize=9.5,
        color=GRAY,
    )
    figure.tight_layout(rect=(0, 0.10, 1, 0.93))
    save_figure(figure, "04_policy_realism_screen")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    simple = load_metrics(SIMPLE / "anchor_density_rate_xgb_metrics.csv")
    eb = load_metrics(EB / "anchor_density_eb_xgb_metrics.csv")
    performance_figure(simple, eb)
    prediction_figure()
    importance_figure()
    policy_figure()
    print(f"Wrote four Matplotlib figures to {OUT}")


if __name__ == "__main__":
    main()
