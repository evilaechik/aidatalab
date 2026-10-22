#!/usr/bin/env python3
"""Expand the nine-metro experiment using the same public QCEW inputs."""
from pathlib import Path

import numpy as np
import pandas as pd
from catboost import CatBoostRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.pipeline import make_pipeline

import nine_metro_models as base

ARTEM = Path(__file__).resolve().parents[1]
OUT = ARTEM / "data" / "expanded_metro_models"
base.OUT = OUT
base.RAW = ARTEM / "data" / "nine_metro_models" / "raw_qcew_industry_slices"
base.YEARS = range(2018, 2026)
base.METRO_OUTPUT_NAME = "metro_year_qcew_2018_2025.csv"
base.METROS = {
    **base.METROS,
    "12580": "Baltimore", "14460": "Boston", "16980": "Chicago",
    "17140": "Cincinnati", "18140": "Columbus OH", "26900": "Indianapolis",
    "28140": "Kansas City", "31080": "Los Angeles", "33460": "Minneapolis",
    "35620": "New York", "36740": "Orlando", "37980": "Philadelphia",
    "38060": "Phoenix", "38300": "Pittsburgh", "38900": "Portland OR",
    "41620": "Salt Lake City", "41700": "San Antonio", "41740": "San Diego",
    "41860": "San Francisco", "42660": "Seattle", "45300": "Tampa",
    "47900": "Washington DC",
}


def additional_models(panel, output):
    """Use identical training and evaluation splits as the original experiment."""
    X, y = panel[base.FEATURES], panel.target_growth
    time = [(np.flatnonzero(panel.target_year < yr), np.flatnonzero(panel.target_year == yr), str(yr)) for yr in (2024, 2025)]
    metro = [(tr, te, str(panel.iloc[te].metro.iloc[0])) for tr, te in LeaveOneGroupOut().split(X, y, panel.metro)]
    rows, imp = [], []
    for evaluation, folds in (("forward_year", time), ("leave_one_metro_out", metro)):
        for train, test, label in folds:
            estimator = make_pipeline(SimpleImputer(strategy="median", keep_empty_features=True), CatBoostRegressor(iterations=150, depth=3, learning_rate=0.04, l2_leaf_reg=5, random_seed=42, verbose=False, thread_count=1, allow_writing_files=False))
            estimator.fit(X.iloc[train], y.iloc[train])
            for name, predicted in (("catboost", estimator.predict(X.iloc[test])), ("previous_growth_baseline", X.iloc[test].prior_employment_growth.to_numpy())):
                for position, prediction in zip(test, predicted):
                    row = panel.iloc[position]
                    rows.append({"evaluation": evaluation, "held_out": label, "model": name, "metro": row.metro, "target_year": row.target_year, "observed_growth": row.target_growth, "predicted_growth": float(prediction)})
            if evaluation == "forward_year":
                loss = mean_absolute_error(y.iloc[test], estimator.predict(X.iloc[test]))
                rng = np.random.default_rng(101)
                for feature in base.FEATURES:
                    changes = []
                    for _ in range(100):
                        shuffled = X.iloc[test].copy()
                        shuffled[feature] = rng.permutation(shuffled[feature].to_numpy())
                        changes.append(100 * (mean_absolute_error(y.iloc[test], estimator.predict(shuffled)) - loss))
                    imp.append({"model": "catboost", "held_out_year": label, "feature": feature, "permutation_delta_mae_pp": float(np.mean(changes)), "permutation_std_pp": float(np.std(changes))})
    predictions = pd.concat([pd.read_csv(output / "held_out_predictions.csv"), pd.DataFrame(rows)], ignore_index=True)
    predictions.to_csv(output / "held_out_predictions.csv", index=False)
    metrics = []
    for (evaluation, name), group in predictions.groupby(["evaluation", "model"]):
        metrics.append({"evaluation": evaluation, "model": name, "n": len(group), "mae_percentage_points": 100 * mean_absolute_error(group.observed_growth, group.predicted_growth), "pooled_r2": r2_score(group.observed_growth, group.predicted_growth)})
    pd.DataFrame(metrics).to_csv(output / "model_comparison.csv", index=False)
    importance = pd.concat([pd.read_csv(output / "heldout_permutation_importance.csv"), pd.DataFrame(imp)], ignore_index=True)
    importance.to_csv(output / "heldout_permutation_importance.csv", index=False)
    return pd.DataFrame(metrics), importance


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    membership = base.counties()
    membership.to_csv(OUT / "metro_counties_2023_census.csv", index=False)
    _, panel = base.build_data(membership)
    base.evaluate(panel)
    metrics, importance = additional_models(panel, OUT)
    print("metros", panel.metro.nunique(), "counties", len(membership), "model rows", len(panel))
    print("Missing values:", panel[base.FEATURES].isna().sum().to_dict())
    print(metrics.to_string(index=False))
    print(importance.groupby(["model", "feature"]).permutation_delta_mae_pp.mean().sort_values(ascending=False).to_string())
    recent = panel[panel.year >= 2022].copy().reset_index(drop=True)
    sensitivity = OUT / "recent_history_sensitivity"
    sensitivity.mkdir(parents=True, exist_ok=True)
    recent.to_csv(sensitivity / "model_panel.csv", index=False)
    base.OUT = sensitivity
    base.evaluate(recent)
    recent_metrics, _ = additional_models(recent, sensitivity)
    print("Recent-history sensitivity: 2021–2025 inputs, outcome years 2023–2025")
    print(recent_metrics.to_string(index=False))


if __name__ == "__main__":
    main()
