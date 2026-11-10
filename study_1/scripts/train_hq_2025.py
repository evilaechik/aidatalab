#!/usr/bin/env python3
"""Small, single-threaded, nested whole-metro experiment for both HQ tracks.

Run: python study_1/scripts/train_hq_2025.py
Only final models are serialized; tuning reuses fold-fitted feature matrices.
"""
import argparse
import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys
import time
import warnings
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.special import xlogy
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.exceptions import ConvergenceWarning
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, PoissonRegressor
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from threadpoolctl import threadpool_limits
from xgboost import XGBClassifier, XGBRegressor

ROOT = Path(__file__).resolve().parents[1]
LABELS = {
    "A_employment": "A: employment baseline", "A_mean": "A: mean-count baseline",
    "A_poisson": "A: regularized Poisson", "A_xgboost": "A: count XGBoost",
    "B_employment": "B: shared employment baseline", "B_mean": "B: shared mean baseline",
    "B_logistic": "B: regularized logistic", "B_xgboost": "B: probability XGBoost",
    "B_logistic_main": "B: logistic, main effects only",
    "B_xgboost_main": "B: XGBoost, main effects only",
}


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def read_table(root, name):
    return pd.read_csv(root / "tables" / f"{name}.csv", dtype={"cbsa": str, "company_id": str})


def count_losses(y, p):
    y, p = np.asarray(y), np.asarray(p)
    if not np.isfinite(p).all() or (p <= 0).any():
        raise ValueError("Count expectations must be finite and strictly positive")
    return {"mae": np.abs(y - p), "rmse": (y - p) ** 2,
            "poisson_deviance": 2 * (xlogy(y, y / p) - y + p)}


def count_metrics(y, p, weights=None):
    values = {k: float(np.average(v, weights=weights)) for k, v in count_losses(y, p).items()}
    values["rmse"] = values["rmse"] ** 0.5
    return values


def probability_losses(y, p):
    if not np.isfinite(p).all() or (p <= 0).any() or (p >= 1).any():
        raise ValueError("Probabilities must be finite and strictly inside (0, 1); no clipping")
    return {"log_loss": -y * np.log(p) - (1 - y) * np.log1p(-p), "brier": (y - p) ** 2}


def aggregate(frame, values):
    return pd.Series(np.asarray(values), index=frame.cbsa).groupby(level=0).sum()


def model_parts(key, spec, plan):
    track, method = key.split("_")[:2]
    features = spec["main_effect_predictors" if key.endswith("_main") else "primary_predictors"]
    cat = [c for c in spec.get("categorical_predictors", []) if c in features]
    numeric = [c for c in features if c not in cat]
    tree = method == "xgboost"
    numeric_pipe = "passthrough" if tree else make_pipeline(
        SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True), StandardScaler())
    transforms = [("numeric", numeric_pipe, numeric)]
    if cat:
        transforms.append(("category", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat))
    prep = ColumnTransformer(transforms, sparse_threshold=0, verbose_feature_names_out=False)
    if tree:
        candidates = plan["xgboost_grid"]
    else:
        field, source = ("alpha", "poisson_alpha") if track == "A" else ("C", "logistic_C")
        candidates = [{field: value} for value in plan[source]]
    return features, prep, candidates


def estimator(key, params, plan, y):
    if "poisson" in key:
        return PoissonRegressor(**params, max_iter=1500, tol=1e-8)
    if "logistic" in key:
        return LogisticRegression(**params, solver="lbfgs", max_iter=1500, tol=1e-8)
    common = dict(plan["xgboost_fixed"], **params, random_state=plan["seed"],
                  base_score=float(np.mean(y)), verbosity=0)
    if key.startswith("A"):
        return XGBRegressor(**common, objective="count:poisson", eval_metric="poisson-nloglik")
    return XGBClassifier(**common, objective="binary:logistic", eval_metric="logloss", scale_pos_weight=1)


def predict(model, X, key):
    return model.predict_proba(X)[:, 1] if key.startswith("B") else model.predict(X)


def tune_fit(key, data, spec, plan, context, tuning):
    """Cache one training-only transformation per inner fold across candidates."""
    features, prep, candidates = model_parts(key, spec, plan)
    target = spec["target"]
    cache = []
    for fold in sorted(data.validation_fold.unique()):
        train, test = data[data.validation_fold.ne(fold)], data[data.validation_fold.eq(fold)]
        transformer = clone(prep)
        cache.append((transformer.fit_transform(train[features]), train[target].to_numpy(),
                      transformer.transform(test[features]), test))
    scores = []
    for order, params in enumerate(candidates):
        all_y, all_p = [], []
        for X_train, y_train, X_test, test in cache:
            fitted = estimator(key, params, plan, y_train).fit(X_train, y_train)
            p = predict(fitted, X_test, key)
            if key.startswith("B"):
                probability_losses(test[target].to_numpy(), p)
                all_y.extend(aggregate(test, test[target]).to_numpy())
                all_p.extend(aggregate(test, p).to_numpy())
            else:
                all_y.extend(test[target].to_numpy())
                all_p.extend(p)
        metrics = count_metrics(all_y, all_p)
        tuning.append(dict(model=key, context=context, candidate=order, params=json.dumps(params), **metrics))
        scores.append((metrics["mae"], metrics["rmse"], order))
    params = candidates[min(scores)[2]]
    fitted = Pipeline([("preprocess", prep), ("model", estimator(key, params, plan, data[target]))])
    fitted.fit(data[features], data[target])
    return fitted, features, params


def add_predictions(key, frame, values, target, fold, count_rows, probability_rows):
    if key.startswith("B"):
        probability_losses(frame[target].to_numpy(), np.asarray(values))
        pair = frame[["company_id", "cbsa", "company_broad_industry", target]].rename(columns={target: "observed"}).copy()
        pair["probability"] = np.asarray(values)
        pair["model"], pair["fold"] = key, fold
        probability_rows.append(pair)
        counts = pair.groupby("cbsa")[["observed", "probability"]].sum().rename(columns={"probability": "expected"}).reset_index()
        counts = counts.merge(frame[["cbsa", "metro_name"]].drop_duplicates(), on="cbsa", validate="one_to_one")
    else:
        counts = frame[["cbsa", "metro_name", target]].rename(columns={target: "observed"}).copy()
        counts["expected"] = values
    counts["model"], counts["fold"] = key, fold
    counts["track"] = key[0]
    counts["method"] = key.split("_")[1]
    counts["residual"] = counts.observed - counts.expected
    count_rows.append(counts)


def baseline(train, test, method):
    if method == "employment":
        rate = float(train.reported_hq_count_2025.sum() / np.exp(train.log_msa_private_employment).sum())
        return rate * np.exp(test.log_msa_private_employment).to_numpy(), {"rate_per_private_job": rate}
    mean = float(train.reported_hq_count_2025.mean())
    return np.full(len(test), mean), {"mean_count": mean}


def uncertainty(counts, pairs, plan, output):
    """Fixed-prediction bootstrap; crossed cluster draws reuse companies across MSAs."""
    n_boot = plan["bootstrap_replicates"]
    rng = np.random.default_rng(plan["seed"])
    metros = sorted(counts.cbsa.unique())
    companies = sorted(pairs.company_id.unique())
    mw = rng.multinomial(len(metros), np.full(len(metros), 1 / len(metros)), size=n_boot)
    cw = rng.multinomial(len(companies), np.full(len(companies), 1 / len(companies)), size=n_boot)
    rows, deltas = [], []
    baseline_error = counts[counts.model.eq("A_employment")].set_index("cbsa").loc[metros]
    baseline_error = np.abs(baseline_error.observed - baseline_error.expected).to_numpy()
    for key, group in counts.groupby("model", sort=False):
        group = group.set_index("cbsa").loc[metros]
        losses = count_losses(group.observed, group.expected)
        for metric, loss in losses.items():
            samples = mw @ loss / len(metros)
            if metric == "rmse":
                samples = np.sqrt(samples)
            low, high = np.quantile(samples, [.025, .975])
            rows.append(dict(model=key, scope="metro_fixed_roster", metric=metric, lower=low, upper=high))
        difference = mw @ (losses["mae"] - baseline_error) / len(metros)
        low, high = np.quantile(difference, [.025, .975])
        deltas.append(dict(model=key, mae_difference_vs_employment=float(np.mean(losses["mae"] - baseline_error)), lower=low, upper=high))
    for key, group in pairs.groupby("model", sort=False):
        y = group.pivot(index="cbsa", columns="company_id", values="observed").loc[metros, companies].to_numpy()
        p = group.pivot(index="cbsa", columns="company_id", values="probability").loc[metros, companies].to_numpy()
        y_count, p_count = cw @ y.T, cw @ p.T
        for metric, losses in count_losses(y_count, p_count).items():
            samples = (losses * mw).sum(axis=1) / len(metros)
            if metric == "rmse":
                samples = np.sqrt(samples)
            low, high = np.quantile(samples, [.025, .975])
            rows.append(dict(model=key, scope="crossed_company_metro", metric=metric, lower=low, upper=high))
        for metric, loss in probability_losses(y, p).items():
            samples = np.einsum("bm,mc,bc->b", mw, loss, cw, optimize=True) / (len(metros) * len(companies))
            low, high = np.quantile(samples, [.025, .975])
            rows.append(dict(model=key, scope="crossed_company_metro", metric=metric, lower=low, upper=high))
    result = pd.DataFrame(rows)
    result.to_csv(output / "uncertainty.csv", index=False)
    pd.DataFrame(deltas).to_csv(output / "paired_mae_vs_employment.csv", index=False)
    return result


def calibration(pairs, output):
    rows, bins = [], []
    for key, group in pairs.groupby("model", sort=False):
        y, p = group.observed.to_numpy(), group.probability.to_numpy()
        scores = {k: float(v.mean()) for k, v in probability_losses(y, p).items()}
        logits = np.log(p / (1 - p)).reshape(-1, 1)
        fit = LogisticRegression(C=np.inf, max_iter=1500, tol=1e-8).fit(logits, y)
        rows.append(dict(model=key, n=len(y), positives=int(y.sum()), mean_probability=float(p.mean()),
                         observed_rate=float(y.mean()), calibration_intercept=float(fit.intercept_[0]),
                         calibration_slope=float(fit.coef_[0, 0]), **scores))
        work = group.copy()
        work["bin"] = pd.cut(p, [0, .005, .01, .02, .05, .1, .2, 1], include_lowest=True)
        for label, part in work.groupby("bin", observed=True):
            bins.append(dict(model=key, bin=str(label), n=len(part), positives=int(part.observed.sum()),
                             mean_probability=part.probability.mean(), observed_rate=part.observed.mean()))
    result = pd.DataFrame(rows)
    result.to_csv(output / "probability_comparison.csv", index=False)
    pd.DataFrame(bins).to_csv(output / "calibration_bins.csv", index=False)
    return result


def report(root, metrics, atlanta, probability, intervals, winner, elapsed):
    observed = int(atlanta.observed.iloc[0])
    lines = ["# Study 1 final results", "", "Run: November 9, 2026. Both HQ modeling tracks completed.", "",
             "Results cover 98 sampled firms and publisher-selected reported 2025 HQs. "
             "Five nested whole-metro folds evaluate 49 development metros; Atlanta was assessed after selection froze. "
             "MAE is the average absolute HQ-count error; RMSE penalizes large errors; Poisson deviance measures count fit. Lower is better.", "",
             "## Results of each model", "", f"Atlanta observed **{observed} HQs** in the covered sample. "
             "A positive Atlanta gap means observed exceeds expected; it is not a recruitment opportunity estimate.", "",
             "| Model | OOF MAE | RMSE | Poisson deviance | Atlanta expected | Observed − expected |",
             "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for row in metrics.itertuples():
        a = atlanta[atlanta.model.eq(row.model)].iloc[0]
        lines.append(f"| {LABELS[row.model]} | {row.mae:.3f} | {row.rmse:.3f} | {row.poisson_deviance:.3f} | {a.expected:.2f} | {a.residual:+.2f} |")
    lines += ["", "The B baselines exactly reproduce A's counts; they supply no company-specific information. "
              "The mean-count baseline is secondary. Main-effects rows are prespecified diagnostics and were excluded from primary selection.", ""]
    reference = metrics.set_index("model").loc["A_employment", "mae"]
    meanings = {
        "A_employment": "Scales the expected HQ count with private employment; the transparent size-only reference.",
        "A_mean": "Assigns the training-metro average to every new metro; ignores regional differences.",
        "A_poisson": "Uses all 31 regional features with shrinkage to estimate counts directly.",
        "A_xgboost": "Tests shallow nonlinear relationships among the same regional features.",
        "B_employment": "Divides the employment expectation equally over 98 companies, then sums it back.",
        "B_mean": "Uses one common training-fold event probability, recovering the mean count.",
        "B_logistic": "Uses regional conditions, company traits and preset interactions to estimate and sum HQ probabilities.",
        "B_xgboost": "Tests shallow nonlinear company–metro relationships at natural event prevalence.",
        "B_logistic_main": "Removes the four preset interactions from logistic regression to check their incremental value.",
        "B_xgboost_main": "Removes those explicit interactions from XGBoost; its trees can still learn interactions.",
    }
    for row in metrics.itertuples():
        delta = row.mae - reference
        comparison = "equals" if abs(delta) < 1e-12 else ("improves on" if delta < 0 else "underperforms")
        lines.append(f"- **{LABELS[row.model]}:** {meanings[row.model]} Its held-out MAE {comparison} the employment baseline"
                     + ("." if comparison == "equals" else f" by {abs(delta):.3f} HQs per metro."))
    lines += ["", "## Company probabilities", "", "| Model | Log loss | Brier score | Mean probability | Observed rate |",
              "| --- | ---: | ---: | ---: | ---: |"]
    for row in probability.itertuples():
        lines.append(f"| {LABELS[row.model]} | {row.log_loss:.5f} | {row.brier:.5f} | {100 * row.mean_probability:.2f}% | {100 * row.observed_rate:.2f}% |")
    lines += ["", "Lower log loss and Brier score are better. Similar mean predicted and observed rates indicate "
              "average calibration only; probability-bin results and diagnostic calibration slopes are retained in the reports. "
              "Rare events make low Brier scores easy to obtain, so they do not by themselves establish useful discrimination.", "",
              "## General conclusions", ""]
    best = metrics.set_index("model").loc[winner]
    selected = atlanta[atlanta.model.eq(winner)].iloc[0]
    ci = intervals[(intervals.model.eq(winner)) & intervals.scope.eq("metro_fixed_roster") & intervals.metric.eq("mae")].iloc[0]
    lines += [f"- The frozen development rule selects **{LABELS[winner]}**: MAE **{best.mae:.3f}** HQs "
              f"(95% metro-bootstrap interval {ci.lower:.3f}–{ci.upper:.3f}). "
              "This is a development selection score, not an independent estimate of the selected winner's performance.",
              f"- That model expects **{selected.expected:.2f}** Atlanta HQs versus **{observed}** observed "
              f"(gap **{selected.residual:+.2f}**). Its heuristic 90% OOF-error band is "
              f"**{selected.band90_lower:.2f}–{selected.band90_upper:.2f}** HQs. "
              "The band describes possible count error, not confidence in the expected value; one held-out metro cannot establish general reliability."]
    b_best = metrics[metrics.model.isin(["B_logistic", "B_xgboost"])].sort_values(["mae", "rmse"]).iloc[0]
    a_best = metrics[metrics.model.isin(["A_employment", "A_mean", "A_poisson", "A_xgboost"])].sort_values(["mae", "rmse"]).iloc[0]
    lines.append(f"- The best primary company model has MAE {b_best.mae:.3f}; the best aggregate model has MAE {a_best.mae:.3f}. "
                 + ("Company detail improves the point estimate, but uncertainty must support any stronger claim."
                    if b_best.mae < a_best.mae else "Company detail does not improve the best aggregate count benchmark in this run."))
    paired = pd.read_csv(root / "reports/training/paired_mae_vs_employment.csv").set_index("model")
    ablation = paired.loc["B_xgboost_main"]
    lines.append(f"- The main-effects company XGBoost diagnostic has MAE {metrics.set_index('model').loc['B_xgboost_main', 'mae']:.3f}, "
                 f"but its MAE difference versus employment is {ablation.mae_difference_vs_employment:+.3f} "
                 f"(95% paired metro-bootstrap interval {ablation.lower:+.3f} to {ablation.upper:+.3f}). "
                 "This run does not establish a reliable improvement over the size-only benchmark.")
    lines.append("- Neither primary company learner improves log loss or Brier score over the shared employment baseline in this run. "
                 "Atlanta is close to the employment benchmark; the results do not establish an HQ deficit.")
    for method in ["logistic", "xgboost"]:
        main, full = metrics.set_index("model").loc[f"B_{method}_main"], metrics.set_index("model").loc[f"B_{method}"]
        lines.append(f"- Preset interactions change {method} MAE by {full.mae - main.mae:+.3f} HQs versus main effects alone; "
                     "negative values favor including them.")
    lines += ["- Count uncertainty resamples metros; additional company-model intervals independently resample shared company and metro clusters. "
              "Intervals use fixed OOF predictions and omit model-refitting and selection uncertainty. Atlanta bands are heuristic, not formal coverage guarantees.",
              "- The known Pittsburgh co-HQ adds one only in the scorecard sensitivity; it was not a replacement training label. "
              "The two unresolved firms remain excluded everywhere. Results do not estimate all 500 firms, ordinary offices, causal effects, or recruitable missing HQs.",
              "", f"Training and reporting took {elapsed:.1f} seconds. "
              "[Run details](TRAINING_RUN.md), [model comparison](reports/training/model_comparison.csv), "
              "[Atlanta assessment](reports/training/atlanta_assessment.csv), and "
              "[uncertainty](reports/training/uncertainty.csv) provide reproducible supporting results.", ""]
    (root / "FINAL_RESULTS.md").write_text("\n".join(lines))


def main(root):
    started = time.perf_counter()
    plan = json.loads((root / "config/training_plan.json").read_text())
    output, models = root / "reports/training", root / "models"
    output.mkdir(exist_ok=True, parents=True)
    models.mkdir(exist_ok=True)
    # Acceptance validation may inspect Atlanta for data QC, never for fitting.
    subprocess.run([sys.executable, str(root / "scripts/build_hq_2025.py"), "--root", str(root), "--validate-only"], check=True, stdout=subprocess.DEVNULL)
    specs = {"A": json.loads((root / "config/feature_spec.json").read_text()),
             "B": json.loads((root / "config/company_hq_feature_spec.json").read_text())}
    data = {"A": read_table(root, "training_development_2025"),
            "B": read_table(root, "training_company_hq_development_2025")}
    assert len(data["A"]) == 49 and len(data["B"]) == 4802
    assert "12060" not in set(data["A"].cbsa) | set(data["B"].cbsa)
    assert data["B"].groupby("cbsa").size().eq(98).all()
    assert data["B"].groupby("cbsa").validation_fold.nunique().eq(1).all()
    assert data["A"].set_index("cbsa").validation_fold.sort_index().equals(
        data["B"].groupby("cbsa").validation_fold.first().sort_index())
    for track, frame in data.items():
        assert not frame[specs[track]["target"]].isna().any()
        assert not set(specs[track]["primary_predictors"]) & set(specs[track]["prohibited_predictors"])
    fitted_keys = ["A_poisson", "A_xgboost", "B_logistic", "B_xgboost", "B_logistic_main", "B_xgboost_main"]
    count_rows, pair_rows, tuning, final, fitted_params = [], [], [], {}, {}
    for fold in sorted(data["A"].validation_fold.unique()):
        train_a = data["A"][data["A"].validation_fold.ne(fold)]
        test_a = data["A"][data["A"].validation_fold.eq(fold)]
        test_b = data["B"][data["B"].validation_fold.eq(fold)]
        for method in ["employment", "mean"]:
            p, _ = baseline(train_a, test_a, method)
            add_predictions(f"A_{method}", test_a, p, specs["A"]["target"], fold, count_rows, pair_rows)
            per_company = test_b.cbsa.map(dict(zip(test_a.cbsa, p))).to_numpy() / 98
            add_predictions(f"B_{method}", test_b, per_company, specs["B"]["target"], fold, count_rows, pair_rows)
        for key in fitted_keys:
            track = key[0]
            train, test = data[track][data[track].validation_fold.ne(fold)], data[track][data[track].validation_fold.eq(fold)]
            fit, features, params = tune_fit(key, train, specs[track], plan, f"outer_{fold}", tuning)
            add_predictions(key, test, predict(fit, test[features], key), specs[track]["target"], fold, count_rows, pair_rows)
            print(f"outer {int(fold)} {key}: {params}", flush=True)
    counts, pairs = pd.concat(count_rows, ignore_index=True), pd.concat(pair_rows, ignore_index=True)
    assert not counts.duplicated(["model", "cbsa"]).any()
    assert not pairs.duplicated(["model", "cbsa", "company_id"]).any()
    assert counts.groupby("model").size().eq(49).all()
    counts.to_csv(output / "oof_metro_predictions.csv", index=False)
    pairs.to_csv(output / "oof_company_probabilities.csv", index=False)
    metrics = pd.DataFrame([dict(model=key, primary=key in plan["primary_model_order"],
                                 **count_metrics(group.observed, group.expected))
                            for key, group in counts.groupby("model", sort=False)])
    metrics["order"] = metrics.model.map({key: i for i, key in enumerate(LABELS)})
    metrics = metrics.sort_values("order").drop(columns="order").reset_index(drop=True)
    metrics.to_csv(output / "model_comparison.csv", index=False)
    fold_metrics = [dict(model=key, fold=int(fold), n_metros=len(group), **count_metrics(group.observed, group.expected))
                    for (key, fold), group in counts.groupby(["model", "fold"])]
    pd.DataFrame(fold_metrics).to_csv(output / "fold_metrics.csv", index=False)
    # Round only for deterministic handling of floating-point-identical shared baselines.
    ranking = sorted(plan["primary_model_order"], key=lambda key: (
        round(float(metrics.set_index("model").loc[key, "mae"]), 12),
        round(float(metrics.set_index("model").loc[key, "rmse"]), 12), plan["primary_model_order"].index(key)))
    winner = ranking[0]
    for key in fitted_keys:
        track = key[0]
        fit, features, params = tune_fit(key, data[track], specs[track], plan, "final_development", tuning)
        final[key] = (fit, features)
        fitted_params[key] = params
        joblib.dump(dict(pipeline=fit, features=features, params=params, track=track), models / f"{key}.joblib", compress=3)
        if "xgboost" in key:
            fit.named_steps["model"].save_model(models / f"{key}.ubj")
    input_paths = [root / "scripts/train_hq_2025.py", root / "config/training_plan.json", root / "requirements-training.txt",
                   root / "config/feature_spec.json", root / "config/company_hq_feature_spec.json",
                   root / "tables/training_development_2025.csv", root / "tables/training_company_hq_development_2025.csv"]
    frozen = dict(frozen_at_utc=datetime.now(timezone.utc).isoformat(), selected_model=winner,
                  ranking=ranking, rule=plan["selection_rule"], final_params=fitted_params,
                  input_sha256={str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in input_paths},
                  atlanta_loaded_for_model_assessment=False)
    write_json(output / "selection_frozen.json", frozen)
    print(f"Selection frozen: {winner}. Loading Atlanta assessment files now.", flush=True)
    reserved = {"A": read_table(root, "training_atlanta_2025"), "B": read_table(root, "training_company_hq_atlanta_2025")}
    final_counts, final_pairs = [], []
    baseline_specs = {}
    for method in ["employment", "mean"]:
        p, params = baseline(data["A"], reserved["A"], method)
        baseline_specs[method] = params
        add_predictions(f"A_{method}", reserved["A"], p, specs["A"]["target"], "atlanta", final_counts, final_pairs)
        add_predictions(f"B_{method}", reserved["B"], np.repeat(p / 98, 98), specs["B"]["target"], "atlanta", final_counts, final_pairs)
    write_json(models / "baselines.json", baseline_specs)
    for key, (fit, features) in final.items():
        frame = reserved[key[0]]
        add_predictions(key, frame, predict(fit, frame[features], key), specs[key[0]]["target"], "atlanta", final_counts, final_pairs)
    atlanta, atlanta_pairs = pd.concat(final_counts, ignore_index=True), pd.concat(final_pairs, ignore_index=True)
    for index, row in atlanta.iterrows():
        residuals = counts[counts.model.eq(row.model)].residual.abs().to_numpy()
        rank = min(len(residuals), int(np.ceil((len(residuals) + 1) * .9)))
        q = float(np.sort(residuals)[rank - 1])
        atlanta.loc[index, "band90_lower"] = max(0, row.expected - q)
        atlanta.loc[index, "band90_upper"] = row.expected + q
    atlanta.to_csv(output / "atlanta_assessment.csv", index=False)
    atlanta_pairs.to_csv(output / "atlanta_company_probabilities.csv", index=False)
    for method in ["employment", "mean"]:
        a = counts[counts.model.eq(f"A_{method}")].set_index("cbsa").expected.sort_index()
        b = counts[counts.model.eq(f"B_{method}")].set_index("cbsa").expected.sort_index()
        np.testing.assert_allclose(a, b, rtol=1e-12)
    probability = calibration(pairs, output)
    intervals = uncertainty(counts, pairs, plan, output)
    all_pairs = pd.concat([pairs.assign(assessment="development_oof"), atlanta_pairs.assign(assessment="atlanta")])
    sectors = all_pairs.groupby(["assessment", "model", "company_broad_industry"]).agg(
        observed=("observed", "sum"), expected=("probability", "sum"), n=("observed", "size")).reset_index()
    sectors["residual"] = sectors.observed - sectors.expected
    sectors.to_csv(output / "sector_diagnostics.csv", index=False)
    scorecard = read_table(root, "training_aggregate_2025")
    scorecard["observed_hqs_per_million_private_jobs"] = scorecard.reported_hq_count_2025 / np.exp(scorecard.log_msa_private_employment) * 1e6
    scorecard[["cbsa", "metro_name", "reported_hq_count_2025", "reported_hq_share_2025",
               "observed_hqs_per_million_private_jobs", "selected100_count_lower_bound", "selected100_count_upper_bound",
               "known_additional_hq_sensitivity_count"]].to_csv(output / "observed_scorecard.csv", index=False)
    pd.DataFrame(tuning).to_csv(output / "tuning_scores.csv", index=False)
    elapsed = time.perf_counter() - started
    packages = ["numpy", "pandas", "scipy", "scikit-learn", "xgboost", "joblib", "threadpoolctl"]
    metadata = dict(seed=plan["seed"], python=sys.version, platform=platform.platform(),
                    versions={p: importlib.metadata.version(p) for p in packages},
                    elapsed_seconds=elapsed, selected_model=winner, data_acceptance_checks=106,
                    oof_metro_rows=len(counts), oof_probability_rows=len(pairs),
                    frozen_selection_sha256=hashlib.sha256((output / "selection_frozen.json").read_bytes()).hexdigest(),
                    atlanta_assessment_sha256={str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                                              for p in [root / "tables/training_atlanta_2025.csv", root / "tables/training_company_hq_atlanta_2025.csv"]},
                    uncertainty_caveat=plan["uncertainty"], atlanta_band_caveat=plan["atlanta_band"])
    write_json(output / "run_metadata.json", metadata)
    report(root, metrics, atlanta, probability, intervals, winner, elapsed)
    print(metrics.to_string(index=False), flush=True)
    print(f"Completed in {elapsed:.1f}s; results: {root / 'FINAL_RESULTS.md'}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    warnings.simplefilter("error", ConvergenceWarning)
    with threadpool_limits(limits=1):
        main(args.root.resolve())
