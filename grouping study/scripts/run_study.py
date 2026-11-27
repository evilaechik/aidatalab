"""Run the frozen nested study, final predictions, and fixed sensitivities."""
import json
import platform
import sys
import time
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_info, threadpool_limits

from common import (ATL, BLOCKS, FAMILIES, GRID, R1, REPO, ROOT, SEED, TARGET, best,
                    blend, distances, employment, fit_global, focus, kernel, local,
                    losses, metrics, ordered, predict_global, read, save, sha,
                    unique_views, weighted_quantile, write_json)


class Study:
    def __init__(self):
        self.spec = json.loads((ROOT / "config/execution_contract.json").read_text())["regression"]
        self.dev = ordered(read(ROOT / "tables/development.csv"))
        self.atl = ordered(read(ROOT / "tables/atlanta_predictors.csv"))
        self.reference = read(R1 / "reports/training/r1/oof_company_probabilities.csv").query("model == 'B_logistic'")
        self.fits, self.fit_log, self.tuning, self.audits, self.splits = {}, [], [], [], []
        self.outer_settings, self.predictions, self.final, self.support_rows = {}, [], {}, []

    def fit(self, train, c, context):
        key = (tuple(sorted(train.cbsa.unique())), c)
        if key not in self.fits:
            started = time.perf_counter()
            try:
                self.fits[key] = fit_global(train, self.spec, c)
                self.fit_log.append(dict(context=context, C=c, training_metros=len(key[0]),
                                         status="ok", error="", seconds=time.perf_counter()-started))
            except Exception as error:
                self.fit_log.append(dict(context=context, C=c, training_metros=len(key[0]), status="failed", error=repr(error)))
                save("fit_attempts", self.fit_log)
                raise
        return self.fits[key]

    def state(self, train, query, context, blocks=BLOCKS):
        s = distances(train, query, blocks)
        self.audits += [dict(context=context, **r) for r in s["audit"]]
        self.splits.append(dict(context=context, donor_metros=";".join(s["tm"].index),
                                query_metros=";".join(s["qm"].index), training_rows=len(train), query_rows=len(query)))
        return s

    def tune(self, train, context):
        pooled = [[] for _ in GRID]
        for inner in sorted(train.validation_fold.unique()):
            tr = train[train.validation_fold != inner]
            val = ordered(train[train.validation_fold == inner])
            name = f"{context}/inner_{int(inner)}"
            s = self.state(tr, val, name)
            w = focus(tr, val, self.atl)
            y = val[TARGET].to_numpy().reshape(-1, 498)
            gp = {c: predict_global(self.fit(tr, c, name), val, self.spec) for c in [.01, .1, 1.]}
            loc = {(m, k): local(s, m, k) for m in [5, 10, 20] for k in [25, 75, 150]}
            for i, params in enumerate(GRID):
                p, effective = (gp[params["C"]], np.zeros_like(y)) if not params["alpha"] else blend(gp[params["C"]], loc[params["k_m"], params["k_c"]], params["alpha"])
                score = metrics(y, p, w)
                fallback = int((effective == 0).sum()) if params["alpha"] else 0
                self.tuning.append(dict(context=context, split=name, candidate=i, **params, **score,
                                        fallback_rows=fallback, rows=len(val), selected_focus=False, selected_grouped=False, status="ok"))
                pooled[i].append((y, p, w, fallback))
        rows = []
        for i, pieces in enumerate(pooled):
            y, p, w = [np.concatenate([piece[j] for piece in pieces]) for j in range(3)]
            rows.append(dict(context=context, split="pooled", candidate=i, **GRID[i], **metrics(y, p, w),
                             fallback_rows=sum(piece[3] for piece in pieces), rows=y.size, status="ok"))
        grouped = best(rows)
        global_only = best([r for r in rows if r["alpha"] == 0])
        for r in rows:
            r.update(selected_focus=r["candidate"] == global_only["candidate"], selected_grouped=r["candidate"] == grouped["candidate"])
        self.tuning += rows
        return {"FOCUS_GLOBAL": {k: global_only[k] for k in ["C", "alpha", "k_m", "k_c"]},
                "GROUPED": {k: grouped[k] for k in ["C", "alpha", "k_m", "k_c"]}}

    def predict(self, train, query, params, context, state=None, model=None):
        model = self.fit(train, params["C"], context) if model is None else model
        g = predict_global(model, query, self.spec)
        s = self.state(train, query, context) if state is None else state
        # Alpha-zero has no selected bandwidth; widest grid weights explain support only.
        loc = local(s, params["k_m"] or 20, params["k_c"] or 150)
        p, effective = blend(g, loc, params["alpha"])
        return dict(p=p, global_p=g, effective=effective, loc=loc, state=s, model=model, params=params, train=train)

    def outer(self):
        for fold in range(5):
            train, val = self.dev[self.dev.validation_fold != fold], ordered(self.dev[self.dev.validation_fold == fold])
            settings = self.tune(train, f"outer_{fold}")
            self.outer_settings[str(fold)] = settings
            w = focus(train, val, self.atl)
            s = self.state(train, val, f"outer_{fold}/refit")
            for method in FAMILIES:
                if method == "EMP":
                    p, result = employment(train, val), None
                elif method == "R1_GLOBAL":
                    p = val[["company_id", "cbsa"]].merge(self.reference, on=["company_id", "cbsa"], validate="one_to_one", sort=False).probability.to_numpy().reshape(-1, 498)
                    result = None
                else:
                    result = self.predict(train, val, settings[method], f"outer_{fold}/{method}", s)
                    p = result["p"]
                rows = val[["company_id", "cbsa", "company_broad_industry", TARGET]].rename(columns={TARGET: "observed"}).copy()
                rows["method"], rows["fold"], rows["probability"] = method, fold, p.ravel()
                rows["raw_focus_weight"] = np.repeat(w, 498)
                rows["requested_alpha"] = settings[method]["alpha"] if method in settings else 0
                rows["effective_alpha"] = result["effective"].ravel() if result else 0
                rows["fallback"] = (rows.requested_alpha > 0) & (rows.effective_alpha == 0)
                if method == "GROUPED":
                    self.support_rows.append(support(result, f"outer_{fold}"))
                    loc = result["loc"]
                    rows["neff_metro"] = np.repeat(loc["b"]["neff"], 498)
                    rows["neff_company"] = np.tile(loc["a"]["neff"], len(w))
                    rows["nearest_metro_distance"] = np.repeat(loc["b"]["nearest"], 498)
                    rows["metro_bandwidth"] = np.repeat(loc["b"]["h"], 498)
                    rows["global_probability"] = result["global_p"].ravel()
                    rows["local_probability"] = loc["p"].ravel()
                self.predictions.append(rows)
            print(f"Completed outer fold {fold}: {settings}", flush=True)
        oof = pd.concat(self.predictions, ignore_index=True)
        weights = oof.drop_duplicates("cbsa").set_index("cbsa").raw_focus_weight
        oof["focus_weight"] = oof.raw_focus_weight/weights.sum()
        save("oof_company_probabilities", oof)
        write_json(ROOT / "config/outer_settings.json", self.outer_settings)
        return oof


def compare(oof):
    rng = np.random.default_rng(SEED)
    draws = rng.integers(0, 49, (2000, 49))
    rows, counts, boot, per_metro = [], [], {}, {}
    for method in FAMILIES:
        f = oof[oof.method == method].sort_values(["cbsa", "company_id"])
        y, p = f.observed.to_numpy().reshape(-1, 498), f.probability.to_numpy().reshape(-1, 498)
        w = f.raw_focus_weight.to_numpy().reshape(-1, 498)[:, 0]
        loss = losses(y, p)
        boot[method] = {key: (value[draws]*w[draws]).sum(axis=1)/w[draws].sum(axis=1) for key, value in loss.items()}
        boot[method]["rmse"] **= .5
        focus_score, all_score = metrics(y, p, w), metrics(y, p, np.ones(49))
        row = dict(method=method, **{f"focus_{k}": v for k, v in focus_score.items()},
                   **{f"all_{k}": v for k, v in all_score.items()}, effective_validation_metros=w.sum()**2/(w*w).sum(),
                   mean_probability=p.mean(), observed_rate=y.mean(), log_loss_clipped_rows=int(((p < 1e-12) | (p > 1-1e-12)).sum()))
        for key, values in boot[method].items():
            row[f"{key}_ci_low"], row[f"{key}_ci_high"] = np.quantile(values, [.025, .975])
        rows.append(row)
        per_metro[method] = pd.DataFrame(dict(cbsa=sorted(f.cbsa.unique()), observed=y.sum(axis=1), expected=p.sum(axis=1),
                                            raw_focus_weight=w, focus_weight=w/w.sum(), **loss)).assign(method=method)
        counts.append(per_metro[method])
    paired, affected = [], []
    for reference in FAMILIES[:-1]:
        for metric in ["mae", "rmse", "log_loss", "brier", "poisson_deviance"]:
            delta = boot["GROUPED"][metric]-boot[reference][metric]
            a = next(r[f"focus_{metric}"] for r in rows if r["method"] == "GROUPED")
            b = next(r[f"focus_{metric}"] for r in rows if r["method"] == reference)
            lo, hi = np.quantile(delta, [.025, .975])
            paired.append(dict(comparison=f"GROUPED minus {reference}", metric=metric, difference=a-b, ci_low=lo, ci_high=hi,
                               interpretation="fixed-prediction whole-metro percentile interval"))
        a, b = per_metro["GROUPED"], per_metro[reference]
        affected.append(pd.DataFrame(dict(cbsa=a.cbsa, reference=reference, grouped_error=a.mae, reference_error=b.mae,
                                         error_difference=a.mae-b.mae, focus_weight=a.focus_weight)))
    comparison = save("model_comparison", rows)
    save("oof_metro_predictions", pd.concat(counts, ignore_index=True).assign(residual=lambda x: x.observed-x.expected))
    save("paired_comparisons", paired)
    save("paired_metro_errors", pd.concat(affected, ignore_index=True))
    candidates = comparison.to_dict("records")
    for field in ["focus_mae", "focus_log_loss"]:
        minimum = min(r[field] for r in candidates)
        candidates = [r for r in candidates if r[field]-minimum < 1e-10]
    selected = min(candidates, key=lambda r: FAMILIES.index(r["method"]))["method"]
    bins = [0, .005, .01, .02, .05, .1, .2, 1]
    calibrated = oof.assign(probability_bin=pd.cut(oof.probability, bins, include_lowest=True))
    cal = []
    for (method, interval), group in calibrated.groupby(["method", "probability_bin"], observed=False):
        cal.append(dict(method=method, probability_bin=str(interval), rows=len(group),
                        mean_probability=group.probability.mean(), observed_rate=group.observed.mean(),
                        focus_mean_probability=np.average(group.probability, weights=group.raw_focus_weight) if len(group) else np.nan,
                        focus_observed_rate=np.average(group.observed, weights=group.raw_focus_weight) if len(group) else np.nan))
    save("calibration_bins", cal)
    return selected, comparison


def support(result, context):
    loc, s = result["loc"], result["state"]
    rows = []
    for j, metro in enumerate(s["qm"].index):
        b = loc["b"]["w"][j]
        for i, company in enumerate(s["qc"].index):
            a = loc["a"]["w"][i]
            pairs = np.outer(np.sort(b)[-5:], np.sort(a)[-5:]).ravel()
            reason = ";".join(x for x, bad in [("regional_support_below_10", loc["b"]["neff"][j] < 10), ("company_support_below_25", loc["a"]["neff"][i] < 25)] if bad)
            rows.append(dict(context=context, cbsa=metro, company_id=company, requested_alpha=result["params"]["alpha"],
                             effective_alpha=result["effective"][j, i], fallback_reason=reason,
                             neff_metro=loc["b"]["neff"][j], neff_company=loc["a"]["neff"][i],
                             formal_neff_pairs=loc["b"]["neff"][j]*loc["a"]["neff"][i],
                             max_metro_weight=b.max(), max_company_weight=a.max(), max_pair_weight=b.max()*a.max(),
                             top5_metro_mass=np.sort(b)[-5:].sum(), top5_company_mass=np.sort(a)[-5:].sum(), top5_pair_mass=np.sort(pairs)[-5:].sum(),
                             positive_weight_mass=loc["p"][j, i], positive_firms=int(((s["y"].sum(axis=0)>0) & (a>0)).sum()),
                             positive_metros=int(((s["y"] @ a > 0) & (b>0)).sum()),
                             nearest_metro_distance=loc["b"]["nearest"][j], metro_bandwidth=loc["b"]["h"][j],
                             nearest_company_distance=loc["a"]["nearest"][i], company_bandwidth=loc["a"]["h"][i],
                             metro_bandwidth_fallback=loc["b"]["fallback"][j], company_bandwidth_fallback=loc["a"]["fallback"][i],
                             metro_underflow=loc["b"]["underflow"][j], company_underflow=loc["a"]["underflow"][i]))
    return pd.DataFrame(rows)


def donor_tables(result):
    loc, s = result["loc"], result["state"]
    b, aw = loc["b"]["w"][0], loc["a"]["w"]
    mt = pd.DataFrame(dict(cbsa=s["tm"].index, metro_name=s["tm"].metro_name.to_numpy(), distance=np.sqrt(s["dm"][0]), weight=b))
    mt["rank"] = mt.distance.rank(method="first").astype(int)
    for block, d2 in s["blocks"].items():
        mt[f"{block}_squared_distance"] = d2[0]
    mt["weighted_positive_mass"] = b*s["y"].sum(axis=1)
    mt["bandwidth_role"] = "selected" if result["params"]["alpha"] else "diagnostic_only_km20_kc150"
    save("atlanta_donor_metros", mt.sort_values(["distance", "cbsa"]))
    companies, top_rows = [], []
    for i, company in enumerate(s["qc"].index):
        a = aw[i]
        ranks = np.empty(len(a), int)
        ranks[loc["a"]["order"][i]] = np.arange(1, len(a)+1)
        same_industry = s["tc"].company_broad_industry.to_numpy() == s["qc"].iloc[i].company_broad_industry
        same_listing = s["tc"].ownership_listing_type_2025.to_numpy() == s["qc"].iloc[i].ownership_listing_type_2025
        companies.append(pd.DataFrame(dict(query_company_id=company, donor_company_id=s["tc"].index,
                                            distance=np.sqrt(s["dc"][i]), weight=a, rank=ranks,
                                            same_industry=same_industry, same_listing=same_listing,
                                            numeric_component=s["dc"][i]-.5*(~same_industry)-.1*(~same_listing),
                                            industry_component=.5*(~same_industry), listing_component=.1*(~same_listing))))
        pair = np.outer(b, a)
        # Stable flatten order is CBSA, then company ID.
        indices = np.argsort(-pair.ravel(), kind="stable")[:20]
        omitted = 1-pair.ravel()[indices].sum()
        for rank, index in enumerate(indices, 1):
            m, f = np.unravel_index(index, pair.shape)
            top_rows.append(dict(query_company_id=company, rank=rank, donor_cbsa=s["tm"].index[m],
                                 donor_company_id=s["tc"].index[f], weight=pair[m, f], training_hq_label=s["y"][m, f],
                                 weighted_positive_contribution=pair[m, f]*s["y"][m, f], omitted_weight_mass=omitted))
    save("atlanta_donor_companies", pd.concat(companies, ignore_index=True))
    save("atlanta_top_donor_rows", top_rows)


def sensitivities(study, oof):
    primary = study.final["GROUPED"]
    settings = primary["params"]
    variants, company_rows, sector_rows, ny_outer = [], [], [], []
    base = primary["p"][0]
    def record(name, method, result):
        p = result["p"][0]
        original = study.final[method]["p"][0]
        loc, state = result.get("loc"), result.get("state")
        row = dict(variant=name, method=method, expected=p.sum(), delta=p.sum()-original.sum(),
                   max_company_change=np.max(np.abs(p-original)), fallback_rows=int(((result.get("effective", np.zeros((1, 498))) == 0) & (result.get("params", {}).get("alpha", 0)>0)).sum()))
        if loc:
            ids = state["tm"].index
            top = list(ids[np.argsort(-loc["b"]["w"][0], kind="stable")[:10]])
            old = primary["state"]["tm"].index
            old_top = list(old[np.argsort(-primary["loc"]["b"]["w"][0], kind="stable")[:10]])
            union = set(top) | set(old_top)
            row.update(neff_metro=loc["b"]["neff"][0], min_neff_company=loc["a"]["neff"].min(),
                       top10_metros=";".join(top), top10_overlap=len(set(top)&set(old_top)),
                       top10_mean_rank_change=np.mean([abs((top.index(x)+1 if x in top else 11)-(old_top.index(x)+1 if x in old_top else 11)) for x in union]))
        variants.append(row)
        company_rows.append(study.atl[["company_id", "company_broad_industry"]].assign(variant=name, method=method, probability=p, delta=p-original))
        frame = company_rows[-1].groupby("company_broad_industry", as_index=False)[["probability", "delta"]].sum()
        sector_rows.append(frame.assign(variant=name, method=method))
    no_ny = study.dev[study.dev.cbsa != "35620"]
    for method in FAMILIES:
        if method == "EMP":
            result = dict(p=employment(no_ny, study.atl))
        else:
            params = study.final[method]["params"]
            result = study.predict(no_ny, study.atl, params, f"sensitivity/no_ny/{method}")
        record("remove_new_york", method, result)
        if method == "GROUPED":
            old = primary
            mask = old["state"]["tm"].index != "35620"
            b = old["loc"]["b"]["w"][0, mask]
            b /= b.sum()
            direct_local = b @ old["state"]["y"][mask] @ old["loc"]["a"]["w"].T
            eff = old["effective"][0]
            global_effect = ((1-eff)*(result["global_p"][0]-old["global_p"][0])).sum()
            label_effect = (eff*(direct_local-old["loc"]["p"][0])).sum()
            variants[-1].update(global_component_effect=global_effect, fixed_metric_direct_donor_effect=label_effect,
                                 scaling_bandwidth_support_interaction=variants[-1]["delta"]-global_effect-label_effect)
    for cbsa in sorted(study.dev.cbsa.unique()):
        train = study.dev[study.dev.cbsa != cbsa]
        record(f"leave_out_{cbsa}", "GROUPED", study.predict(train, study.atl, settings, f"sensitivity/leave_out_{cbsa}"))
    for block in BLOCKS:
        s = study.state(study.dev, study.atl, f"sensitivity/drop_{block}", {k: v for k, v in BLOCKS.items() if k != block})
        record(f"drop_{block}_block", "GROUPED", study.predict(study.dev, study.atl, settings, f"sensitivity/drop_{block}", s, primary["model"]))
    for km in [5, 10, 20]:
        for kc in [25, 75, 150]:
            params = dict(settings, k_m=km, k_c=kc)
            record(f"bandwidth_{km}_{kc}", "GROUPED", study.predict(study.dev, study.atl, params, f"sensitivity/bandwidth_{km}_{kc}", primary["state"], primary["model"]))
    for fold in range(5):
        train = study.dev[(study.dev.validation_fold != fold) & (study.dev.cbsa != "35620")]
        val = ordered(study.dev[(study.dev.validation_fold == fold) & (study.dev.cbsa != "35620")])
        for method in ["FOCUS_GLOBAL", "GROUPED"]:
            result = study.predict(train, val, study.outer_settings[str(fold)][method], f"sensitivity/no_ny/outer_{fold}/{method}")
            old = oof[(oof.method == method) & oof.cbsa.isin(val.cbsa)].sort_values(["cbsa", "company_id"])
            y = val[TARGET].to_numpy().reshape(-1, 498)
            ny_outer.append(pd.DataFrame(dict(method=method, fold=fold, cbsa=sorted(val.cbsa.unique()), observed=y.sum(axis=1),
                                               original_expected=old.probability.to_numpy().reshape(-1, 498).sum(axis=1),
                                               expected=result["p"].sum(axis=1), raw_focus_weight=old.raw_focus_weight.to_numpy().reshape(-1, 498)[:, 0])))
    ny = pd.concat(ny_outer, ignore_index=True)
    ny["original_absolute_error"] = abs(ny.observed-ny.original_expected)
    ny["absolute_error"] = abs(ny.observed-ny.expected)
    save("new_york_outer_influence", ny)
    save("sensitivities", variants)
    cp = save("sensitivity_company_predictions", pd.concat(company_rows, ignore_index=True))
    save("sensitivity_sector_predictions", pd.concat(sector_rows, ignore_index=True))
    loo = cp[cp.variant.str.startswith("leave_out_")]
    ranges = loo.groupby("company_id").probability.agg(leave_one_metro_min="min", leave_one_metro_max="max").reset_index()
    save("company_stability_ranges", ranges)
    sectors = loo.groupby(["variant", "company_broad_industry"]).probability.sum().reset_index()
    save("sector_stability_ranges", sectors.groupby("company_broad_industry").probability.agg(leave_one_metro_min="min", leave_one_metro_max="max").reset_index())
    return pd.DataFrame(variants), ranges


def main():
    started = time.perf_counter()
    manifest = read(ROOT / "config/input_manifest.csv")
    assert all(sha(REPO / row.path) == row.sha256 for row in manifest.itertuples())
    study = Study()
    oof = study.outer()
    selected, comparison = compare(oof)
    neff = float(comparison.effective_validation_metros.iloc[0])
    frozen = dict(selected_procedure=selected, frozen_at_utc=datetime.now(timezone.utc).isoformat(),
                  atlanta_labels_loaded_for_assessment=False, effective_validation_metros=neff,
                  validation_support="sufficient_by_prespecified_gate" if neff >= 15 else "insufficient",
                  contract_sha256=sha(ROOT / "config/execution_contract.json"), outer_settings=study.outer_settings,
                  outer_comparison=comparison.to_dict("records"))
    write_json(ROOT / "config/selection_frozen.json", frozen)
    print(f"Frozen selected family: {selected}; effective validation metros {neff:.2f}", flush=True)
    final_settings = study.tune(study.dev, "final")
    inherited = joblib.load(R1 / "models/r1/B_logistic.joblib")
    final_settings["R1_GLOBAL"] = dict(C=inherited["params"]["C"], alpha=0, k_m=0, k_c=0)
    write_json(ROOT / "config/final_settings.json", dict(settings=final_settings, selected_procedure=selected,
               frozen_at_utc=datetime.now(timezone.utc).isoformat(), atlanta_labels_loaded_for_assessment=False))
    final_rows = []
    s = study.state(study.dev, study.atl, "final/refit")
    for method in FAMILIES:
        if method == "EMP":
            result = dict(p=employment(study.dev, study.atl), params=dict(alpha=0), train=study.dev)
        else:
            result = study.predict(study.dev, study.atl, final_settings[method], f"final/{method}", s,
                                   inherited["pipeline"] if method == "R1_GLOBAL" else None)
        study.final[method] = result
        joblib.dump(dict(method=method, **result, spec=study.spec, contract_sha256=frozen["contract_sha256"]), ROOT / "models" / f"{method}.joblib", compress=3)
        rows = study.atl[["company_id", "cbsa", "company", "company_broad_industry"]].copy()
        rows["method"], rows["probability"] = method, result["p"].ravel()
        rows["requested_alpha"] = result["params"]["alpha"]
        rows["effective_alpha"] = result.get("effective", np.zeros((1, 498))).ravel()
        final_rows.append(rows)
    # Save label-free predictions before opening the assessment outcome object.
    predicted = save("atlanta_predictions_before_labels", pd.concat(final_rows, ignore_index=True))
    support_frame = support(study.final["GROUPED"], "final")
    save("support", pd.concat(study.support_rows+[support_frame], ignore_index=True))
    donor_tables(study.final["GROUPED"])
    assessment_loaded = datetime.now(timezone.utc).isoformat()
    labels = read(ROOT / "tables/atlanta_labels.csv").rename(columns={TARGET: "observed"})
    final = predicted.merge(labels, on=["company_id", "cbsa"], validate="many_to_one")
    assessment = []
    counts = read(ROOT / "reports/oof_metro_predictions.csv")
    grouped_oof = oof[oof.method == "GROUPED"].drop_duplicates("cbsa")
    extrapolation = []
    for field, target in [("nearest_metro_distance", support_frame.nearest_metro_distance.iloc[0]), ("metro_bandwidth", support_frame.metro_bandwidth.iloc[0])]:
        threshold = float(grouped_oof[field].quantile(.95))
        extrapolation.append(dict(diagnostic=field, atlanta=target, cross_fitted_95th_percentile=threshold, warning=target > threshold,
                                  qualification="outer-selected bandwidths vary across folds"))
    save("extrapolation", extrapolation)
    for method in FAMILIES:
        old = counts[counts.method == method]
        radius = weighted_quantile(abs(old.residual), old.raw_focus_weight)
        expectation = study.final[method]["p"].sum()
        assessment.append(dict(method=method, selected=method == selected, observed=int(labels.observed.sum()), expected=expectation,
                               observed_minus_expected=labels.observed.sum()-expectation, heuristic_low=max(0, expectation-radius),
                               heuristic_high=min(498, expectation+radius), heuristic_radius=radius,
                               requested_alpha=study.final[method]["params"]["alpha"],
                               effective_alpha_min=study.final[method].get("effective", np.zeros((1, 498))).min(),
                               effective_alpha_max=study.final[method].get("effective", np.zeros((1, 498))).max(),
                               neff_metro=support_frame.neff_metro.iloc[0] if method == "GROUPED" else np.nan,
                               min_neff_company=support_frame.neff_company.min() if method == "GROUPED" else np.nan,
                               support_status="supported_by_frozen_gate" if neff >= 15 else "exploratory_insufficient_validation_support"))
    save("atlanta_assessment", assessment)
    sector = final.groupby(["method", "company_broad_industry"], as_index=False).agg(observed=("observed", "sum"), expected=("probability", "sum"), companies=("company_id", "count"))
    sector["observed_minus_expected"] = sector.observed-sector.expected
    save("atlanta_sector_predictions", sector)
    variants, ranges = sensitivities(study, oof)
    # Support and instability columns describe GROUPED only.
    final = final.merge(ranges.assign(method="GROUPED"), on=["company_id", "method"], how="left", validate="many_to_one")
    final = final.merge(support_frame.drop(columns=["context", "requested_alpha", "effective_alpha"]).assign(method="GROUPED"),
                        on=["company_id", "cbsa", "method"], how="left", validate="many_to_one")
    save("atlanta_company_predictions", final)
    save("tuning_scores", study.tuning)
    save("fit_attempts", study.fit_log)
    save("transform_audit", study.audits)
    save("split_audit", study.splits)
    metadata = dict(completed_at_utc=datetime.now(timezone.utc).isoformat(), assessment_labels_loaded_at_utc=assessment_loaded,
                    elapsed_seconds=time.perf_counter()-started, python=sys.version, platform=platform.platform(),
                    versions=json.loads((ROOT / "config/execution_contract.json").read_text())["versions"], seed=SEED, threads=1,
                    threadpools=threadpool_info(), selected_procedure=selected, final_settings=final_settings,
                    distinct_global_fits=len(study.fits), failures=sum(r["status"] != "ok" for r in study.fit_log),
                    input_manifest_sha256=sha(ROOT / "config/input_manifest.csv"), contract_sha256=frozen["contract_sha256"],
                    selection_sha256=sha(ROOT / "config/selection_frozen.json"), code_hashes={p.name: sha(p) for p in (ROOT / "scripts").glob("*.py")})
    write_json(ROOT / "reports/run_metadata.json", metadata)
    print(f"Finished fitting, reporting, and {len(variants)} sensitivities in {metadata['elapsed_seconds']:.1f}s.", flush=True)


if __name__ == "__main__":
    with threadpool_limits(limits=1):
        main()
