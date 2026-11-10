#!/usr/bin/env python3
"""Run the expanded cohort with the original nested folds, grids and estimators.

Model/preprocessing/tuning/uncertainty functions are imported unchanged from the
frozen original trainer; only the cohort contract, orchestration and report differ.
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
from sklearn.exceptions import ConvergenceWarning
from threadpoolctl import threadpool_limits

import train_hq_2025 as core

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE / "expanded_500"
FITTED = ["A_poisson", "A_xgboost", "B_logistic", "B_xgboost", "B_logistic_main", "B_xgboost_main"]


def compare_original(root, metrics, atlanta):
    old = pd.read_csv(root / "reference_inputs/model_comparison.csv")
    old_atl = pd.read_csv(root / "reference_inputs/atlanta_assessment.csv")
    rows = []
    for study, scores, assessment in [("original_98", old, old_atl), ("expanded_498", metrics, atlanta)]:
        baseline_mae = float(scores.set_index("model").loc["A_employment", "mae"])
        for row in scores.itertuples():
            a = assessment[assessment.model.eq(row.model)].iloc[0]
            rows.append(dict(study=study, model=row.model, mae=row.mae, rmse=row.rmse,
                             mae_improvement_vs_employment_percent=100 * (baseline_mae - row.mae) / baseline_mae,
                             atlanta_observed=a.observed, atlanta_expected=a.expected,
                             atlanta_gap=a.residual, atlanta_gap_percent=100 * a.residual / a.expected))
    pd.DataFrame(rows).to_csv(root / "reports/training/original_vs_expanded.csv", index=False)


def report(root, metrics, atlanta, probability, intervals, winner, elapsed, n):
    observed = int(atlanta.observed.iloc[0])
    scores = metrics.set_index("model")
    paired = pd.read_csv(root / "reports/training/paired_mae_vs_employment.csv").set_index("model")
    selected = atlanta[atlanta.model.eq(winner)].iloc[0]
    ci = intervals[intervals.model.eq(winner) & intervals.scope.eq("metro_fixed_roster") & intervals.metric.eq("mae")].iloc[0]
    lines = ["# Expanded Fortune 500 model results", "", "Run: November 9, 2026.", "",
             f"All 500 roster firms were collected; **{n} covered firms** enter both HQ modeling tracks. "
             "The same 49 development metros, five whole-metro outer folds, nested inner tuning, predictors, seed and restricted grids "
             "were used as in the original experiment. Atlanta stayed out of fitting and model selection.", "",
             "MAE is the average absolute HQ-count error on held-out development metros. RMSE penalizes large errors; "
             "Poisson deviance measures count fit. Lower is better. Counts refer to publisher-selected reported 2025 HQs.", "",
             "## Every model's results", "", f"Atlanta observed **{observed} covered HQs**. "
             "A positive gap means observed exceeds expected; a negative gap means observed is below the benchmark.", "",
             "| Model | OOF MAE | RMSE | Poisson deviance | Atlanta expected | Observed − expected |",
             "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for row in metrics.itertuples():
        a = atlanta[atlanta.model.eq(row.model)].iloc[0]
        lines.append(f"| {core.LABELS[row.model]} | {row.mae:.3f} | {row.rmse:.3f} | {row.poisson_deviance:.3f} | {a.expected:.2f} | {a.residual:+.2f} |")
    meanings = {
        "A_employment": "The size-only reference scales HQ expectations with private employment.",
        "A_mean": "The average-count reference ignores differences between metros.",
        "A_poisson": "Regularized regression uses all 31 regional factors to predict counts directly.",
        "A_xgboost": "Shallow trees test nonlinear regional relationships.",
        "B_employment": f"The same employment expectation is divided over {n} firms and summed back; counts match A exactly.",
        "B_mean": "The common event-rate baseline reproduces the average-count reference.",
        "B_logistic": "Regularized company probabilities use regional factors, company traits and four preset interactions.",
        "B_xgboost": "Shallow trees estimate company probabilities, then sum them into metro counts.",
        "B_logistic_main": "The logistic diagnostic removes the four explicit interactions.",
        "B_xgboost_main": "The XGBoost diagnostic removes explicit interactions; trees can still learn interactions.",
    }
    lines += ["", "The two shared B baselines duplicate A's counts. Main-effects ablations are diagnostic "
              "and were excluded from the unchanged primary selection rule.", ""]
    for row in metrics.itertuples():
        change = row.mae - scores.loc["A_employment", "mae"]
        interpretation = "matches" if abs(change) < 1e-10 else ("improves on" if change < 0 else "has more error than")
        lines.append(f"- **{core.LABELS[row.model]}:** {meanings[row.model]} Its MAE {interpretation} the employment baseline"
                     + ("." if interpretation == "matches" else f" by {abs(change):.3f} HQs per metro."))
    lines += ["", "## Probability quality", "", "| Company model | Log loss | Brier score | Mean probability | Observed rate |",
              "| --- | ---: | ---: | ---: | ---: |"]
    for row in probability.itertuples():
        lines.append(f"| {core.LABELS[row.model]} | {row.log_loss:.5f} | {row.brier:.5f} | {100 * row.mean_probability:.2f}% | {100 * row.observed_rate:.2f}% |")
    lines += ["", "Lower log loss and Brier score are better. Matching average rates alone does not establish "
              "calibration across individual risk levels; bins and diagnostic slopes are saved separately.", "",
              "## Conclusions", "",
              f"- The frozen development rule selects **{core.LABELS[winner]}**: MAE **{scores.loc[winner, 'mae']:.3f}** "
              f"(95% fixed-roster metro-bootstrap interval {ci.lower:.3f}–{ci.upper:.3f}). "
              "This is a development selection score and does not account for selecting the best model.",
              f"- Its Atlanta expectation is **{selected.expected:.2f}** versus **{observed}** observed: "
              f"a gap of **{selected.residual:+.2f} HQs ({100 * selected.residual / selected.expected:+.1f}%)**. "
              f"The heuristic 90% OOF-error band is **{selected.band90_lower:.2f}–{selected.band90_upper:.2f}** HQs."]
    if selected.residual >= 0:
        lines.append("- Atlanta meets or exceeds the selected model's expectation. The expanded cohort does not show an Atlanta total-HQ deficit against that benchmark.")
    elif selected.observed >= selected.band90_lower:
        lines.append("- Atlanta falls below the selected expectation, but remains within its heuristic error band. The shortfall does not establish a clear deficit beyond model error.")
    else:
        lines.append("- Atlanta falls below the selected expectation and its heuristic error band. This is a follow-up signal requiring verification, not a formal significance result or evidence of recruitable missing firms.")
    improvement = 100 * (scores.loc["A_employment", "mae"] - scores.loc[winner, "mae"]) / scores.loc["A_employment", "mae"]
    if winner in ["A_employment", "B_employment"]:
        lines.append("- The added primary-model complexity does not beat the employment baseline on the frozen MAE rule.")
    else:
        delta = paired.loc[winner]
        lines.append(f"- The selected model reduces MAE versus employment by {improvement:.1f}%. "
                     f"The paired MAE difference is {delta.mae_difference_vs_employment:+.3f} "
                     f"(95% fixed-prediction metro-bootstrap interval {delta.lower:+.3f} to {delta.upper:+.3f}). "
                     + ("The interval includes zero, so the apparent gain is uncertain." if delta.lower <= 0 <= delta.upper
                        else "The interval excludes zero under this descriptive fixed-prediction bootstrap; fitting and selection uncertainty remain omitted."))
    best_b = metrics[metrics.model.isin(["B_logistic", "B_xgboost"])].sort_values(["mae", "rmse"]).iloc[0]
    best_a = metrics[metrics.model.str.startswith("A_")].sort_values(["mae", "rmse"]).iloc[0]
    lines.append(f"- Best primary company-model MAE: {best_b.mae:.3f}; best aggregate MAE: {best_a.mae:.3f}. "
                 + ("Company detail improves the point estimate; uncertainty and probability quality still matter." if best_b.mae < best_a.mae
                    else "Company detail does not improve the best aggregate count benchmark on this measure."))
    logistic = scores.loc["B_logistic"]
    logistic_probability = probability.set_index("model").loc["B_logistic"]
    baseline_probability = probability.set_index("model").loc["B_employment"]
    lines.append(f"- Company logistic regression has RMSE {logistic.rmse:.3f} versus employment's {scores.loc['A_employment', 'rmse']:.3f} "
                 f"({100 * (scores.loc['A_employment', 'rmse'] - logistic.rmse) / scores.loc['A_employment', 'rmse']:+.1f}% reduction). "
                 f"Its log loss is {logistic_probability.log_loss:.5f} versus {baseline_probability.log_loss:.5f}, and Brier score "
                 f"{logistic_probability.brier:.5f} versus {baseline_probability.brier:.5f}. "
                 "These secondary point comparisons show where company detail may help; they do not change the MAE-based selection or establish a reliable overall improvement.")
    lines.append(f"- Across all reported specifications, Atlanta expectations range from {atlanta.expected.min():.2f} to {atlanta.expected.max():.2f} "
                 f"against {observed} observed. These are related models using shared data, rather than independent confirmations.")
    for method in ["logistic", "xgboost"]:
        change = scores.loc[f"B_{method}", "mae"] - scores.loc[f"B_{method}_main", "mae"]
        lines.append(f"- Including the preset interactions changes {method} MAE by {change:+.3f} HQs versus main effects alone; negative values favor including them.")
    lines += ["- Compare improvement over the employment baseline within each experiment. Raw errors from the 98-firm and 498-firm studies have different count scales; neither experiment is independent of the other.",
              "- Only 49 development metro environments remain. Bootstrap intervals reuse fixed OOF predictions; the additional crossed company/metro intervals reflect roster composition and omit model refitting and selection uncertainty. Atlanta bands are heuristic prediction-error bands, not confidence intervals for expected counts.",
              "- The two unresolved firms remain excluded. The Pittsburgh co-HQ remains scorecard sensitivity only. These results concern reported HQ points, not ordinary offices, local corporate employment, causal policy effects or potential recruits.",
              "", f"Training and reporting took {elapsed:.1f} seconds. "
              "[Run details](TRAINING_RUN.md), [metrics](reports/training/model_comparison.csv), "
              "[Atlanta assessment](reports/training/atlanta_assessment.csv), "
              "[paired comparisons](reports/training/paired_mae_vs_employment.csv), and "
              "[original versus expanded](reports/training/original_vs_expanded.csv) contain supporting results.", ""]
    (root / "FINAL_RESULTS.md").write_text("\n".join(lines))


def main(root):
    started = time.perf_counter()
    plan = json.loads((root / "config/training_plan.json").read_text())
    contract = json.loads((root / "config/training_contract.json").read_text())
    n = contract["eligible_company_n"]
    original_plan = json.loads((root / "reference_inputs/training_plan.json").read_text())
    assert plan == original_plan, "Expanded plan must retain the original benchmark choices"
    output, models = root / "reports/training", root / "models"
    output.mkdir(exist_ok=True, parents=True)
    models.mkdir(exist_ok=True)
    subprocess.run([sys.executable, str(BASE / "scripts/build_expanded_500.py"), "--root", str(root), "--validate-only"], check=True, stdout=subprocess.DEVNULL)
    specs = {t: json.loads((root / "config" / filename).read_text()) for t, filename in [("A", "feature_spec.json"), ("B", "company_hq_feature_spec.json")]}
    data = {"A": core.read_table(root, "training_development_2025"), "B": core.read_table(root, "training_company_hq_development_2025")}
    assert len(data["A"]) == 49 and len(data["B"]) == contract["company"]["development_rows"] == n * 49
    assert "12060" not in set(data["A"].cbsa) | set(data["B"].cbsa)
    assert data["B"].groupby("cbsa").size().eq(n).all()
    assert data["B"].groupby("cbsa").validation_fold.nunique().eq(1).all()
    assert data["A"].set_index("cbsa").validation_fold.sort_index().equals(data["B"].groupby("cbsa").validation_fold.first().sort_index())
    original_folds = pd.read_csv(root / "reference_inputs/training_development_2025.csv", dtype={"cbsa": str}).set_index("cbsa").validation_fold.sort_index()
    assert data["A"].set_index("cbsa").validation_fold.sort_index().equals(original_folds)
    for track, frame in data.items():
        assert frame[specs[track]["target"]].notna().all()
        assert not set(specs[track]["primary_predictors"]) & set(specs[track]["prohibited_predictors"])
    counts, pairs, tuning, final, params_by_context = [], [], [], {}, {}
    for fold in sorted(data["A"].validation_fold.unique()):
        train_a, test_a = data["A"][data["A"].validation_fold.ne(fold)], data["A"][data["A"].validation_fold.eq(fold)]
        test_b = data["B"][data["B"].validation_fold.eq(fold)]
        for method in ["employment", "mean"]:
            p, _ = core.baseline(train_a, test_a, method)
            core.add_predictions(f"A_{method}", test_a, p, specs["A"]["target"], fold, counts, pairs)
            core.add_predictions(f"B_{method}", test_b, test_b.cbsa.map(dict(zip(test_a.cbsa, p))).to_numpy() / n,
                                 specs["B"]["target"], fold, counts, pairs)
        for key in FITTED:
            frame = data[key[0]]
            train, test = frame[frame.validation_fold.ne(fold)], frame[frame.validation_fold.eq(fold)]
            fit, features, params = core.tune_fit(key, train, specs[key[0]], plan, f"outer_{fold}", tuning)
            core.add_predictions(key, test, core.predict(fit, test[features], key), specs[key[0]]["target"], fold, counts, pairs)
            params_by_context[f"outer_{int(fold)}_{key}"] = params
            print(f"outer {int(fold)} {key}: {params}", flush=True)
    counts, pairs = pd.concat(counts, ignore_index=True), pd.concat(pairs, ignore_index=True)
    assert not counts.duplicated(["model", "cbsa"]).any() and counts.groupby("model").size().eq(49).all()
    assert not pairs.duplicated(["model", "cbsa", "company_id"]).any()
    counts.to_csv(output / "oof_metro_predictions.csv", index=False)
    pairs.to_csv(output / "oof_company_probabilities.csv", index=False)
    metrics = pd.DataFrame([dict(model=key, primary=key in plan["primary_model_order"], **core.count_metrics(g.observed, g.expected)) for key, g in counts.groupby("model", sort=False)])
    metrics["order"] = metrics.model.map({key: i for i, key in enumerate(core.LABELS)})
    metrics = metrics.sort_values("order").drop(columns="order").reset_index(drop=True)
    metrics.to_csv(output / "model_comparison.csv", index=False)
    pd.DataFrame([dict(model=key, fold=int(fold), n_metros=len(g), **core.count_metrics(g.observed, g.expected))
                  for (key, fold), g in counts.groupby(["model", "fold"])]).to_csv(output / "fold_metrics.csv", index=False)
    scores = metrics.set_index("model")
    ranking = sorted(plan["primary_model_order"], key=lambda key: (round(float(scores.loc[key, "mae"]), 12), round(float(scores.loc[key, "rmse"]), 12), plan["primary_model_order"].index(key)))
    winner = ranking[0]
    final_params = {}
    for key in FITTED:
        fit, features, params = core.tune_fit(key, data[key[0]], specs[key[0]], plan, "final_development", tuning)
        final[key], final_params[key] = (fit, features), params
        joblib.dump(dict(pipeline=fit, features=features, params=params, track=key[0]), models / f"{key}.joblib", compress=3)
        if "xgboost" in key:
            fit.named_steps["model"].save_model(models / f"{key}.ubj")
    inputs = ["config/training_plan.json", "config/training_contract.json", "config/feature_spec.json", "config/company_hq_feature_spec.json",
              "tables/training_development_2025.csv", "tables/training_company_hq_development_2025.csv",
              "../scripts/train_expanded_500.py", "../scripts/train_hq_2025.py", "../scripts/build_expanded_500.py", "../requirements-training.txt"]
    core.write_json(output / "selection_frozen.json", dict(frozen_at_utc=datetime.now(timezone.utc).isoformat(), selected_model=winner,
                    ranking=ranking, rule=plan["selection_rule"], final_params=final_params, outer_params=params_by_context,
                    input_sha256={path: hashlib.sha256((root / path).read_bytes()).hexdigest() for path in inputs},
                    atlanta_loaded_for_model_assessment=False))
    print(f"Selection frozen: {winner}. Loading Atlanta assessment files now.", flush=True)
    reserved = {"A": core.read_table(root, "training_atlanta_2025"), "B": core.read_table(root, "training_company_hq_atlanta_2025")}
    assert len(reserved["B"]) == n and len(reserved["A"]) == 1
    final_counts, final_pairs, baselines = [], [], {}
    for method in ["employment", "mean"]:
        p, baselines[method] = core.baseline(data["A"], reserved["A"], method)
        core.add_predictions(f"A_{method}", reserved["A"], p, specs["A"]["target"], "atlanta", final_counts, final_pairs)
        core.add_predictions(f"B_{method}", reserved["B"], np.repeat(p / n, n), specs["B"]["target"], "atlanta", final_counts, final_pairs)
    core.write_json(models / "baselines.json", baselines)
    for key, (fit, features) in final.items():
        frame = reserved[key[0]]
        core.add_predictions(key, frame, core.predict(fit, frame[features], key), specs[key[0]]["target"], "atlanta", final_counts, final_pairs)
    atlanta, ap = pd.concat(final_counts, ignore_index=True), pd.concat(final_pairs, ignore_index=True)
    for index, row in atlanta.iterrows():
        residuals = counts[counts.model.eq(row.model)].residual.abs().to_numpy()
        rank = min(len(residuals), int(np.ceil((len(residuals) + 1) * .9)))
        q = float(np.sort(residuals)[rank - 1])
        atlanta.loc[index, "band90_lower"], atlanta.loc[index, "band90_upper"] = max(0, row.expected - q), row.expected + q
    atlanta.to_csv(output / "atlanta_assessment.csv", index=False)
    ap.to_csv(output / "atlanta_company_probabilities.csv", index=False)
    for method in ["employment", "mean"]:
        a = counts[counts.model.eq(f"A_{method}")].set_index("cbsa").expected.sort_index()
        b = counts[counts.model.eq(f"B_{method}")].set_index("cbsa").expected.sort_index()
        np.testing.assert_allclose(a, b, rtol=1e-12)
    probability = core.calibration(pairs, output)
    intervals = core.uncertainty(counts, pairs, plan, output)
    all_pairs = pd.concat([pairs.assign(assessment="development_oof"), ap.assign(assessment="atlanta")])
    sectors = all_pairs.groupby(["assessment", "model", "company_broad_industry"]).agg(observed=("observed", "sum"), expected=("probability", "sum"), n=("observed", "size")).reset_index()
    sectors["residual"] = sectors.observed - sectors.expected
    sectors.to_csv(output / "sector_diagnostics.csv", index=False)
    card = core.read_table(root, "training_aggregate_2025")
    card["observed_hqs_per_million_private_jobs"] = card.reported_hq_count_2025 / np.exp(card.log_msa_private_employment) * 1e6
    card[["cbsa", "metro_name", "reported_hq_count_2025", "reported_hq_share_2025", "observed_hqs_per_million_private_jobs",
          "selected500_count_lower_bound", "selected500_count_upper_bound", "known_additional_hq_sensitivity_count"]].to_csv(output / "observed_scorecard.csv", index=False)
    pd.DataFrame(tuning).to_csv(output / "tuning_scores.csv", index=False)
    compare_original(root, metrics, atlanta)
    elapsed = time.perf_counter() - started
    metadata = dict(seed=plan["seed"], python=sys.version, platform=platform.platform(), eligible_company_n=n,
                    versions={p: importlib.metadata.version(p) for p in ["numpy", "pandas", "scipy", "scikit-learn", "xgboost", "joblib", "threadpoolctl"]},
                    elapsed_seconds=elapsed, selected_model=winner, data_acceptance_checks=94,
                    oof_metro_rows=len(counts), oof_probability_rows=len(pairs),
                    frozen_selection_sha256=hashlib.sha256((output / "selection_frozen.json").read_bytes()).hexdigest(),
                    atlanta_assessment_sha256={path: hashlib.sha256((root / path).read_bytes()).hexdigest() for path in ["tables/training_atlanta_2025.csv", "tables/training_company_hq_atlanta_2025.csv"]},
                    uncertainty_caveat=plan["uncertainty"], atlanta_band_caveat=plan["atlanta_band"])
    core.write_json(output / "run_metadata.json", metadata)
    report(root, metrics, atlanta, probability, intervals, winner, elapsed, n)
    print(metrics.to_string(index=False), flush=True)
    print(f"Completed in {elapsed:.1f}s; results: {root / 'FINAL_RESULTS.md'}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    warnings.simplefilter("error", ConvergenceWarning)
    with threadpool_limits(limits=1):
        main(args.root.resolve())
