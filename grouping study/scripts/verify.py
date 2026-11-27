"""Independently check kernels, saved predictions, score calculations, and provenance."""
import argparse
import json
import math
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from common import (ATL, FAMILIES, R1, REPO, ROOT, TARGET, blend, distances,
                    employment, kernel, local, ordered, predict_global, read,
                    save, sha, standardized, write_json)


def main(fixture_only=False):
    checks = []
    def check(name, value):
        checks.append(dict(check=name, passed=bool(value)))
        if not value:
            save("artifact_validation_checks", checks)
            raise AssertionError(name)

    # Tiny fixtures use scalar arithmetic separate from the production distance code.
    train = pd.DataFrame(dict(x=[1., 3., np.nan], constant=[7., 7., 7.]))
    query = pd.DataFrame(dict(x=[5.], constant=[7.]))
    z, q, audit = standardized(train, query, ["x", "constant"])
    check("fixture_training_median_population_scale", np.allclose(z[:, 0], [-math.sqrt(1.5), math.sqrt(1.5), 0]) and np.isclose(q[0, 0], 3/math.sqrt(2/3)))
    check("fixture_constant_column", (z[:, 1] == 0).all() and audit[1]["scale"] == 1 and audit[1]["constant"])
    try:
        standardized(pd.DataFrame(dict(x=[np.nan])), query, ["x"])
        rejected = False
    except ValueError:
        rejected = True
    check("fixture_reject_all_missing", rejected)
    d2 = np.array([[0., 1., 1., 4.]])
    expected = np.array([math.exp(-d/2) for d in d2[0]])
    expected /= sum(expected)
    result = kernel(d2, 2)
    check("fixture_rank_tie_normalization", np.allclose(result["w"][0], expected) and list(result["order"][0]) == [0, 1, 2, 3] and result["h"][0] == 1)
    check("fixture_zero_bandwidth_positive_fallback", kernel(d2, 1)["fallback"][0] and kernel(d2, 1)["h"][0] == 1)
    all_zero = kernel(np.zeros((1, 4)), 2)
    check("fixture_all_identical_distances", all_zero["h"][0] == 1 and np.allclose(all_zero["w"], .25))
    check("fixture_underflow_logged", kernel(np.array([[0., 1., 1e9]]), 2)["underflow"][0] == 1)
    b, a = [.25, .75], [.2, .3, .5]
    y = [[1, 0, 0], [0, 1, 1]]
    scalar = sum(b[m]*a[c]*y[m][c] for m in range(2) for c in range(3))
    check("fixture_factorized_probability", np.isclose(scalar, np.array(b) @ np.array(y) @ np.array(a)) and np.isclose(scalar, .65))
    global_p = np.array([[.1, .2]])
    loc = dict(p=np.array([[.4, .6]]), supported=np.array([[True, False]]))
    p, eff = blend(global_p, loc, .5)
    check("fixture_support_fallback_and_blend", np.allclose(p, [[.25, .2]]) and np.allclose(eff, [[.5, 0]]))
    check("fixture_alpha_zero_identity", np.array_equal(blend(global_p, loc, 0)[0], global_p))
    if fixture_only:
        save("fixture_checks", checks)
        print(f"Passed {len(checks)} independent fixture checks.")
        return
    manifest = read(ROOT / "config/input_manifest.csv")
    check("all_consumed_input_and_code_hashes_unchanged", all(sha(REPO / r.path) == r.sha256 for r in manifest.itertuples()))
    contract = json.loads((ROOT / "config/execution_contract.json").read_text())
    check("84_unique_candidates", len(contract["grid"]) == len({tuple(sorted(p.items())) for p in contract["grid"]}) == 84)
    dev = ordered(read(ROOT / "tables/development.csv"))
    atl = ordered(read(ROOT / "tables/atlanta_predictors.csv"))
    check("atlanta_predictors_have_no_labels", TARGET not in atl and "observed" not in atl and "validation_fold" not in atl)
    split = read(ROOT / "reports/split_audit.csv")
    check("all_query_metros_excluded_from_donors", all(set(r.donor_metros.split(";")).isdisjoint(r.query_metros.split(";")) and ATL not in r.donor_metros.split(";") for r in split.itertuples()))
    for r in split[split.context.str.contains("/inner_")].itertuples():
        outer = r.context.split("/")[0]
        donor_ids = set(r.donor_metros.split(";"))
        if outer.startswith("outer_"):
            excluded = int(outer.split("_")[1])
            check(f"{r.context}_outer_fold_excluded", not donor_ids & set(dev.loc[dev.validation_fold == excluded, "cbsa"]))
    audit = read(ROOT / "reports/transform_audit.csv")
    lookup = split.drop_duplicates("context").set_index("context")
    check("distance_scalers_use_unique_entities", all(r.fitted_entities == (len(lookup.loc[r.context].donor_metros.split(";")) if r.entity == "metro" else 498) for r in audit.itertuples()))
    oof = read(ROOT / "reports/oof_company_probabilities.csv")
    counts = read(ROOT / "reports/oof_metro_predictions.csv")
    comparison = read(ROOT / "reports/model_comparison.csv").set_index("method")
    check("complete_oof_grid_and_unique_keys", len(oof) == 4*24402 and not oof.duplicated(["method", "cbsa", "company_id"]).any())
    check("probabilities_finite_bounded", np.isfinite(oof.probability).all() and oof.probability.between(0, 1).all())
    joined = oof.merge(dev[["company_id", "cbsa", TARGET, "validation_fold"]], on=["company_id", "cbsa"], validate="many_to_one")
    check("oof_original_labels_folds", (joined.observed == joined[TARGET]).all() and (joined.fold == joined.validation_fold).all())
    reference = read(R1 / "reports/training/r1/oof_company_probabilities.csv").query("model == 'B_logistic'")
    ref = oof[oof.method == "R1_GLOBAL"].merge(reference, on=["company_id", "cbsa"], validate="one_to_one", suffixes=("", "_original"))
    check("R1_reference_probabilities_exact", np.array_equal(ref.probability, ref.probability_original))
    grouped = oof[oof.method == "GROUPED"]
    expected_alpha = np.where((grouped.neff_metro < 10) | (grouped.neff_company < 25), 0, grouped.requested_alpha)
    check("outer_support_rule_exact", np.array_equal(expected_alpha, grouped.effective_alpha))
    check("outer_blend_identity", np.allclose(grouped.probability, (1-grouped.effective_alpha)*grouped.global_probability+grouped.effective_alpha*grouped.local_probability, atol=1e-15))
    check("common_focus_weights_all_methods", (oof.groupby("cbsa").raw_focus_weight.nunique() == 1).all())
    for method in FAMILIES:
        f = oof[oof.method == method].sort_values(["cbsa", "company_id"])
        y, p = f.observed.to_numpy().reshape(49, 498), f.probability.to_numpy().reshape(49, 498)
        w = f.raw_focus_weight.to_numpy().reshape(49, 498)[:, 0]
        yc, pc = y.sum(axis=1), p.sum(axis=1)
        saved = counts[counts.method == method].sort_values("cbsa")
        check(f"{method}_company_count_reconciliation", np.allclose(pc, saved.expected, atol=1e-12) and np.array_equal(yc, saved.observed))
        pp = np.clip(p, 1e-12, 1-1e-12)
        deviance = np.array([2*(t*math.log(t/s) - t+s) if t else 2*s for t, s in zip(yc, pc)])
        independently = dict(mae=abs(yc-pc), rmse=(yc-pc)**2, poisson_deviance=deviance,
                             log_loss=(-(y*np.log(pp)+(1-y)*np.log(1-pp))).mean(axis=1), brier=((y-p)**2).mean(axis=1))
        for scope, weights in [("focus", w), ("all", np.ones(49))]:
            for metric, values in independently.items():
                score = np.average(values, weights=weights)
                score = math.sqrt(score) if metric == "rmse" else score
                check(f"{method}_{scope}_{metric}_independent", np.isclose(score, comparison.loc[method, f"{scope}_{metric}"], atol=1e-12))
    final = read(ROOT / "reports/atlanta_company_predictions.csv")
    assessment = read(ROOT / "reports/atlanta_assessment.csv").set_index("method")
    for method in FAMILIES:
        artifact = joblib.load(ROOT / "models" / f"{method}.joblib")
        if method == "EMP":
            p = employment(artifact["train"], atl)
        else:
            gp = predict_global(artifact["model"], atl, artifact["spec"])
            state = distances(artifact["train"], atl)
            params = artifact["params"]
            loc = local(state, params["k_m"] or 20, params["k_c"] or 150)
            p, _ = blend(gp, loc, params["alpha"])
            check(f"{method}_saved_distance_state_reproduces", np.allclose(state["dm"], artifact["state"]["dm"], atol=1e-15) and np.allclose(state["dc"], artifact["state"]["dc"], atol=1e-15))
        original = final[final.method == method].sort_values("company_id")
        check(f"{method}_reload_498_atlanta_predictions", len(original) == 498 and np.allclose(p.ravel(), original.probability, atol=1e-14))
        check(f"{method}_atlanta_count_reconciliation", np.isclose(original.probability.sum(), assessment.loc[method, "expected"], atol=1e-12))
        old = counts[counts.method == method].sort_values("residual", key=lambda x: abs(x))
        radius = old.iloc[np.searchsorted(old.raw_focus_weight.cumsum()/old.raw_focus_weight.sum(), .9)].residual
        check(f"{method}_heuristic_band_independent", np.isclose(abs(radius), assessment.loc[method, "heuristic_radius"]))
    donors = read(ROOT / "reports/atlanta_donor_metros.csv")
    firms = read(ROOT / "reports/atlanta_donor_companies.csv")
    top = read(ROOT / "reports/atlanta_top_donor_rows.csv")
    artifact = joblib.load(ROOT / "models/GROUPED.joblib")
    state = artifact["state"]
    check("saved_donor_kernel_normalization", np.isclose(donors.weight.sum(), 1) and np.allclose(firms.groupby("query_company_id").weight.sum(), 1))
    d = np.zeros_like(state["dm"])
    for fields in contract["regional_blocks"].values():
        tr, qu = state["tm"][fields].to_numpy(float), state["qm"][fields].to_numpy(float)
        med = np.nanmedian(tr, axis=0)
        tr, qu = np.where(np.isnan(tr), med, tr), np.where(np.isnan(qu), med, qu)
        mean, scale = tr.mean(axis=0), tr.std(axis=0)
        scale[scale == 0] = 1
        d += (((qu[:, None, :]-mean)/scale-(tr[None, :, :]-mean)/scale)**2).mean(axis=2)/5
    check("final_regional_block_distances_independent", np.allclose(d, state["dm"], atol=1e-14))
    tr = state["tc"][["log_company_revenue", "log_company_workforce"]].to_numpy(float)
    qu = state["qc"][["log_company_revenue", "log_company_workforce"]].to_numpy(float)
    dc = .4*(((qu[:, None, :]-tr.mean(axis=0))/tr.std(axis=0)-(tr[None, :, :]-tr.mean(axis=0))/tr.std(axis=0))**2).mean(axis=2)
    for field, weight in [("company_broad_industry", .5), ("ownership_listing_type_2025", .1)]:
        dc += weight*(state["qc"][field].to_numpy()[:, None] != state["tc"][field].to_numpy()[None, :])
    check("final_company_mixed_distances_independent", np.allclose(dc, state["dc"], atol=1e-14))
    loc = artifact["loc"]
    manual_p = donors.set_index("cbsa").loc[state["tm"].index].weight.to_numpy() @ state["y"] @ loc["a"]["w"].T
    check("final_local_probability_independent_saved_weights", np.allclose(manual_p, loc["p"][0], atol=1e-15))
    regional_neff = 1/sum(float(v)**2 for v in loc["b"]["w"][0])
    company_neff = np.array([1/sum(float(v)**2 for v in row) for row in loc["a"]["w"]])
    final_support = read(ROOT / "reports/support.csv").query("context == 'final'").sort_values("company_id")
    check("effective_donor_and_pair_statistics_independent", np.allclose(final_support.neff_metro, regional_neff) and np.allclose(final_support.neff_company, company_neff) and np.allclose(final_support.formal_neff_pairs, regional_neff*company_neff))
    check("top20_rows_and_omitted_mass", (top.groupby("query_company_id").size() == 20).all() and np.allclose(top.groupby("query_company_id").weight.sum()+top.groupby("query_company_id").omitted_weight_mass.first(), 1))
    dmap = donors.set_index("cbsa").weight
    amap = firms.set_index(["query_company_id", "donor_company_id"]).weight
    check("top_pair_weights_factorize", all(np.isclose(r.weight, dmap[r.donor_cbsa]*amap[r.query_company_id, r.donor_company_id], atol=1e-16) for r in top.itertuples()))
    sectors = read(ROOT / "reports/atlanta_sector_predictions.csv")
    check("sector_totals_reconcile", all(np.isclose(g.expected.sum(), assessment.loc[m, "expected"]) and g.observed.sum() == 15 for m, g in sectors.groupby("method")))
    sensitivity = read(ROOT / "reports/sensitivities.csv")
    check("all_fixed_sensitivities_present", len(sensitivity) == 67 and sensitivity.variant.str.startswith("leave_out_").sum() == 49 and sensitivity.variant.str.startswith("drop_").sum() == 5 and sensitivity.variant.str.startswith("bandwidth_").sum() == 9)
    ny = read(ROOT / "reports/new_york_outer_influence.csv")
    check("New_York_refit_same_48_test_metros", len(ny) == 96 and ny.groupby("method").cbsa.nunique().eq(48).all() and "35620" not in set(ny.cbsa))
    tuning = read(ROOT / "reports/tuning_scores.csv")
    check("complete_6_context_84_candidate_pooled_search", len(tuning[tuning.split == "pooled"]) == 6*84 and (tuning.status == "ok").all())
    frozen = json.loads((ROOT / "config/selection_frozen.json").read_text())
    settings = json.loads((ROOT / "config/final_settings.json").read_text())
    meta = json.loads((ROOT / "reports/run_metadata.json").read_text())
    check("selection_frozen_before_atlanta_assessment", not frozen["atlanta_labels_loaded_for_assessment"] and not settings["atlanta_labels_loaded_for_assessment"] and datetime.fromisoformat(settings["frozen_at_utc"]) < datetime.fromisoformat(meta["assessment_labels_loaded_at_utc"]))
    check("all_source_hashes_still_unchanged", all(sha(REPO / r.path) == r.sha256 for r in manifest.itertuples()))
    save("artifact_validation_checks", checks)
    write_json(ROOT / "reports/artifact_validation.json", dict(passed=all(c["passed"] for c in checks), check_count=len(checks)))
    print(f"Passed {len(checks)} artifact and independent numerical checks.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture-only", action="store_true")
    with threadpool_limits(limits=1):
        main(parser.parse_args().fixture_only)
