#!/usr/bin/env python3
"""Verify expanded artifacts, unchanged methods/folds, reconciliation and model reloads."""
import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_poisson_deviance, root_mean_squared_error
import study_integrity

ROOT = Path(__file__).resolve().parents[1] / "expanded_500"
OUT = ROOT / "reports/training"
checks = []


def check(name, condition):
    if not bool(condition):
        raise AssertionError(name)
    checks.append(name)


def read(name):
    return pd.read_csv(OUT / f"{name}.csv", dtype={"cbsa": str, "company_id": str})


def main():
    contract = json.loads((ROOT / "config/training_contract.json").read_text())
    n = contract["eligible_company_n"]
    dev_labels = pd.read_csv(ROOT / "tables/training_company_hq_development_2025.csv")
    counts, pairs = read("oof_metro_predictions"), read("oof_company_probabilities")
    atlanta, ap = read("atlanta_assessment"), read("atlanta_company_probabilities")
    development = pd.read_csv(ROOT / "tables/training_development_2025.csv", dtype={"cbsa": str})
    expected_folds = development.set_index("cbsa").validation_fold
    frozen = json.loads((OUT / "selection_frozen.json").read_text())
    metadata = json.loads((OUT / "run_metadata.json").read_text())
    for name, fingerprint in {**frozen["input_sha256"], **metadata["atlanta_assessment_sha256"]}.items():
        check(f"input unchanged: {name}", study_integrity.historical_match(ROOT / name, fingerprint))
    check("selection record unchanged", hashlib.sha256((OUT / "selection_frozen.json").read_bytes()).hexdigest() == metadata["frozen_selection_sha256"])
    check("all development predictions exclude Atlanta", "12060" not in set(counts.cbsa) | set(pairs.cbsa))
    check("one OOF record per model and metro", not counts.duplicated(["model", "cbsa"]).any())
    check("49 OOF metros per model", counts.groupby("model").size().eq(49).all())
    check(f"{n} known companies per model and held-out metro", pairs.groupby(["model", "cbsa"]).size().eq(n).all())
    check("same supplied outer folds", counts.fold.eq(counts.cbsa.map(expected_folds)).all())
    check("whole-MSA company folds", pairs.fold.eq(pairs.cbsa.map(expected_folds)).all())
    original = ROOT / 'reference_inputs'
    original_folds = pd.read_csv(original / "training_development_2025.csv", dtype={"cbsa": str}).set_index("cbsa").validation_fold.sort_index()
    check("same outer folds as original experiment", expected_folds.sort_index().equals(original_folds))
    plan = json.loads((ROOT / "config/training_plan.json").read_text())
    check("same grids seed and selection rule", plan == json.loads((original / "training_plan.json").read_text()))
    check("six distinct company probability entries", pairs.model.nunique() == 6)
    check("ten benchmark entries", counts.model.nunique() == 10)
    check("complete company OOF grid", len(pairs) == 6 * n * 49 and not pairs.duplicated(["model", "cbsa", "company_id"]).any())
    check("all assessment predictions use Atlanta", atlanta.cbsa.eq("12060").all() and ap.cbsa.eq("12060").all())
    check("no excluded firm trained", not pairs.company_id.isin(["f2025_401", "f2025_407"]).any())
    check("natural dev event count", pairs.groupby("model")["observed"].sum().eq(dev_labels.reported_hq_presence.sum()).all())
    check("probabilities valid without clipping", pairs.probability.between(0, 1, inclusive="neither").all())
    for prediction_rows, probability_rows, scope in [(counts, pairs, "oof"), (atlanta, ap, "atlanta")]:
        summed = probability_rows.groupby(["model", "cbsa"])[["observed", "probability"]].sum().sort_index()
        expected = prediction_rows[prediction_rows.track.eq("B")].set_index(["model", "cbsa"]).sort_index()
        check(f"{scope} company probabilities reproduce metro counts", np.allclose(summed.probability, expected.expected, rtol=1e-7))
        check(f"{scope} binary labels reproduce observed counts", np.allclose(summed.observed, expected.observed))
        for method in ["employment", "mean"]:
            baseline_a = prediction_rows[prediction_rows.model.eq(f"A_{method}")].set_index("cbsa").expected.sort_index()
            baseline_b = prediction_rows[prediction_rows.model.eq(f"B_{method}")].set_index("cbsa").expected.sort_index()
            check(f"{scope} shared {method} baseline equals", np.allclose(baseline_a, baseline_b, rtol=1e-12))
    metrics = read("model_comparison").set_index("model")
    for key, group in counts.groupby("model"):
        independent = [mean_absolute_error(group.observed, group.expected),
                       root_mean_squared_error(group.observed, group.expected),
                       mean_poisson_deviance(group.observed, group.expected)]
        check(f"{key}: independent metric recomputation", np.allclose(independent, metrics.loc[key, ["mae", "rmse", "poisson_deviance"]].astype(float), rtol=1e-10))
    ranking = sorted(plan["primary_model_order"], key=lambda key: (round(float(metrics.loc[key, "mae"]), 12), round(float(metrics.loc[key, "rmse"]), 12), plan["primary_model_order"].index(key)))
    check("selection follows frozen development rule", frozen["ranking"] == ranking and frozen["selected_model"] == ranking[0])
    check("selection record predates modeled Atlanta assessment", frozen["atlanta_loaded_for_model_assessment"] is False)
    for key in ["A_poisson", "A_xgboost", "B_logistic", "B_xgboost", "B_logistic_main", "B_xgboost_main"]:
        outer_training_metros = 49 - counts[(counts.model.eq(key)) & counts.fold.eq(0)].shape[0]
        check(f"{key}: outer settings recorded", all(f"outer_{i}_{key}" in frozen["outer_params"] for i in range(5)) and outer_training_metros in [39, 40])
    for model_path in sorted((ROOT / "models").glob("*.joblib")):
        key = model_path.stem
        artifact = joblib.load(model_path)
        track = artifact["track"]
        name = "training_atlanta_2025" if track == "A" else "training_company_hq_atlanta_2025"
        frame = pd.read_csv(ROOT / "tables" / f"{name}.csv", dtype={"cbsa": str, "company_id": str})
        pipeline = artifact["pipeline"]
        feature_names = list(pipeline.named_steps["preprocess"].feature_names_in_)
        check(f"{key}: serialized feature contract", feature_names == artifact["features"])
        if track == "B":
            prediction = pipeline.predict_proba(frame[feature_names])[:, 1]
            reference = ap[ap.model.eq(key)].set_index("company_id").loc[frame.company_id].probability
        else:
            prediction = pipeline.predict(frame[feature_names])
            reference = atlanta[atlanta.model.eq(key)].expected
        check(f"{key}: model reload reproduces assessment", np.allclose(prediction, reference, rtol=1e-7))
        if "xgboost" not in key:
            table = "training_development_2025" if track == "A" else "training_company_hq_development_2025"
            training = pd.read_csv(ROOT / "tables" / f"{table}.csv")
            transform = pipeline.named_steps["preprocess"]
            numeric = transform.transformers_[0][2]
            imputer = transform.named_transformers_["numeric"].named_steps["simpleimputer"]
            check(f"{key}: fitted imputation uses development only", np.allclose(imputer.statistics_, training[numeric].median(), equal_nan=True))
    check("Atlanta assessed on one common outcome", atlanta.observed.eq(15).all() and ap.groupby("model")["observed"].sum().eq(15).all())
    result = {"validation": "PASS", "checks_passed": len(checks), "checks": checks}
    (OUT / "artifact_validation.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"PASS: {len(checks)} training-artifact checks")


if __name__ == "__main__":
    main()
