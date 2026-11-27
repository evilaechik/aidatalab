"""Write the checked result narrative, sector support summary, and artifact index."""
import json

import numpy as np

from common import FAMILIES, ROOT, read, save, sha


def table(headers, rows):
    return "\n".join(["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"]*len(headers)) + " |"] +
                     ["| " + " | ".join(str(v) for v in row) + " |" for row in rows])


def main():
    meta = json.loads((ROOT / "reports/run_metadata.json").read_text())
    validation = json.loads((ROOT / "reports/artifact_validation.json").read_text())
    assert validation["passed"]
    score = read(ROOT / "reports/model_comparison.csv").set_index("method")
    assessment = read(ROOT / "reports/atlanta_assessment.csv").set_index("method")
    paired = read(ROOT / "reports/paired_comparisons.csv").query("metric == 'mae'")
    sens = read(ROOT / "reports/sensitivities.csv")
    support = read(ROOT / "reports/support.csv")
    outer_support = support[support.context != "final"]
    target_support = support[support.context == "final"]
    companies = read(ROOT / "tables/companies.csv")
    bysector = target_support.merge(companies[["company_id", "company_broad_industry"]], on="company_id", validate="one_to_one")
    save("support_by_sector", bysector.groupby("company_broad_industry", as_index=False).agg(
        companies=("company_id", "size"), min_neff_company=("neff_company", "min"), median_neff_company=("neff_company", "median"),
        min_neff_metro=("neff_metro", "min"), effective_alpha_min=("effective_alpha", "min"), effective_alpha_max=("effective_alpha", "max")))
    settings = json.loads((ROOT / "config/outer_settings.json").read_text())
    selected = meta["selected_procedure"]
    gparams = meta["final_settings"]["GROUPED"]
    final = read(ROOT / "reports/atlanta_company_predictions.csv")
    sectors = read(ROOT / "reports/atlanta_sector_predictions.csv")
    sector_ranges = read(ROOT / "reports/sector_stability_ranges.csv").set_index("company_broad_industry")
    donors = read(ROOT / "reports/atlanta_donor_metros.csv")
    top_rows = read(ROOT / "reports/atlanta_top_donor_rows.csv")
    ny = read(ROOT / "reports/new_york_outer_influence.csv")
    extrap = read(ROOT / "reports/extrapolation.csv")
    loo = sens[sens.variant.str.startswith("leave_out_")]
    validation_table = table(["Procedure", "Focus MAE (95% interval)", "Focus RMSE", "Focus log loss", "Focus Brier", "All-metro MAE"], [
        [m, f"{r.focus_mae:.3f} ({r.mae_ci_low:.3f}–{r.mae_ci_high:.3f})", f"{r.focus_rmse:.3f}", f"{r.focus_log_loss:.6f}", f"{r.focus_brier:.6f}", f"{r.all_mae:.3f}"] for m, r in score.iterrows()])
    paired_table = table(["Paired count-MAE difference", "Estimate", "95% fixed-prediction interval"], [
        [r.comparison, f"{r.difference:+.3f}", f"{r.ci_low:+.3f} to {r.ci_high:+.3f}"] for r in paired.itertuples()])
    atlanta_table = table(["Procedure", "Observed", "Expected", "Observed − expected", "Heuristic error band", "Requested/effective alpha"], [
        [m, int(r.observed), f"{r.expected:.3f}", f"{r.observed_minus_expected:+.3f}", f"{r.heuristic_low:.3f}–{r.heuristic_high:.3f}", f"{r.requested_alpha:g}/{r.effective_alpha_min:g}–{r.effective_alpha_max:g}"] for m, r in assessment.iterrows()])
    fold_table = table(["Outer fold", "Focus-global C", "Grouped C", "Grouped alpha", "Regional/company rank"], [
        [f, p["FOCUS_GLOBAL"]["C"], p["GROUPED"]["C"], p["GROUPED"]["alpha"], f"{p['GROUPED']['k_m']}/{p['GROUPED']['k_c']}" if p["GROUPED"]["alpha"] else "inapplicable"] for f, p in settings.items()])
    sector_table = table(["Sector", "Companies", "Observed", f"Expected ({selected})", "Grouped leave-one-metro range"], [
        [r.company_broad_industry, r.companies, r.observed, f"{r.expected:.3f}", f"{sector_ranges.loc[r.company_broad_industry, 'leave_one_metro_min']:.3f}–{sector_ranges.loc[r.company_broad_industry, 'leave_one_metro_max']:.3f}"]
        for r in sectors[sectors.method == selected].itertuples()])
    donor_table = table(["Metro", "Kernel weight", "Distance"], [[r.metro_name, f"{r.weight:.4f}", f"{r.distance:.3f}"] for r in donors.head(10).itertuples()])
    ny_rows = []
    for method, rows in ny.groupby("method"):
        old = np.average(rows.original_absolute_error, weights=rows.raw_focus_weight)
        new = np.average(rows.absolute_error, weights=rows.raw_focus_weight)
        ny_rows.append([method, f"{old:.3f}", f"{new:.3f}", f"{new-old:+.3f}"])
    ny_table = table(["Procedure on same 48 test metros", "Original focus MAE", "Refit without New York", "Difference"], ny_rows)
    alpha_zero = sum(p["GROUPED"]["alpha"] == 0 for p in settings.values())
    fallback_rows = ((outer_support.requested_alpha > 0) & (outer_support.effective_alpha == 0)).sum()
    text = f"""# Atlanta company–metro grouping results

Executed November 27, 2026 · Protocol 1.0 · Completed and artifact-verified.

## Result and scope

Retain **{selected}**. The prespecified grouping procedure did not improve the Atlanta-focused benchmark. Its held-out focus MAE was {score.loc['GROUPED', 'focus_mae']:.3f}, compared with {score.loc['FOCUS_GLOBAL', 'focus_mae']:.3f} for focused global tuning and {score.loc['R1_GLOBAL', 'focus_mae']:.3f} for unchanged R1. Final grouping tuning selected **alpha={gparams['alpha']:g}**, so its Atlanta output uses the global regression throughout.

This is a retrospective benchmark of the publisher-selected 2025 Fortune 500 HQ stock in the July 2023 50-MSA frame. It preserves 498 eligible companies, the 63 outside-frame firms, both exclusions, Block's frozen selected point, 420 development positives and Atlanta's 15. Economic inputs retain their inherited 2023–2024 reference periods and units; company financials follow the 2025 publisher edition. Inputs were reused from Study 1, rather than independently recollected. Ordinary-office fitting remains gated by inadequate absence-capable coverage.

## What changed

The implementation adds five equally weighted regional similarity blocks and a mixed company distance, adaptive Gaussian donor weights, a global/local probability blend, and covariate-only Atlanta-focused validation weights. Study 1 already standardized regression inputs. Distances fit unique training metros and companies; regression preprocessing fits training rows only. Companies remain separate until their 498 probabilities are summed. No extra feature search, outcome change or protocol departure was used.

## Held-out validation

{validation_table}

All procedures use the same 49 held-out metros and common fold-derived focus weights. Effective validation support is **{score.effective_validation_metros.iloc[0]:.2f} metros**, above the frozen minimum of 15. The focus kernel remains broad; these are Atlanta-weighted comparisons across related regional environments. Poisson deviance, clipping counts and all-metro probability diagnostics are in [model_comparison.csv](reports/model_comparison.csv). No probability required log-loss clipping.

{paired_table}

Positive differences favor the reference. Grouping's difference from focused global tuning is small and uncertain. Its disadvantage versus R1 has a positive interval under this fixed-prediction calculation. The 2,000 whole-metro bootstrap draws retain each metro's full company roster and focus weight. Their intervals omit refitting, tuning, final-family selection, source error and geographic dependence. Choosing the minimum outer score remains development selection.

## Tuning attribution

{fold_table}

Grouping chose alpha zero in **{alpha_zero}/5 outer folds**. Support fallback affected **{fallback_rows}/{len(outer_support)} outer company–metro predictions**; zero-alpha choices were tuning decisions rather than support failures. Focus-global selected C=0.1 in fold 1 while R1 retained C=0.01 there. The grouped fold-0 change jointly selected a different C and positive local weight; its comparison is the prespecified full procedure, not an isolated fixed-C kernel effect. Final focused global and grouped settings both use C=0.01, with no local component. Stored R1 OOF probabilities remain unchanged on exact company/CBSA keys.

## Atlanta assessment

{atlanta_table}

The selected benchmark expects **{assessment.loc[selected, 'expected']:.2f} HQs**, and observed minus expected is **{assessment.loc[selected, 'observed_minus_expected']:+.2f}**. The positive residual indicates more selected HQs than the point benchmark. It is not an Atlanta shortfall, a count of available recruits, or evidence of exceptional policy performance.

Each error band adds/subtracts the first weighted 90th percentile of the procedure's frozen absolute outer count residuals, truncated to [0,498]. These are heuristic error ranges, without formal Atlanta coverage or confidence-interval interpretation. Equal final point predictions can have different bands because their nested outer procedures differed. Atlanta labels were opened for assessment only after family/settings freeze and label-free final prediction export; prior knowledge of Atlanta's outcome still prevents an analyst-blind claim.

## Companies and sectors

[atlanta_company_predictions.csv](reports/atlanta_company_predictions.csv) contains all 498 company probabilities for each procedure, labels and classifications. Grouped support and leave-one-metro ranges are attached only to GROUPED rows. Those ranges describe fixed-settings instability, not probability confidence. No probabilities were thresholded or renormalized across geography.

{sector_table}

Sector ranges describe the grouped final procedure; its point prediction currently coincides with the selected R1 fit. Classification totals reconcile to the common 498-company roster. Company values are comparative HQ scores for this fixed roster, not relocation or offer-acceptance probabilities.

## Donor explanation and support

The following weights describe the **diagnostic** widest prespecified kernel (regional rank 20, company rank 150). Since selected alpha is zero, these weights do not contribute to the reported final benchmark. Bandwidths are inapplicable to that selected estimate; this explanation convention was frozen before fitting.

{donor_table}

This diagnostic kernel has {target_support.neff_metro.iloc[0]:.2f} effective regional donors and at least {target_support.neff_company.min():.2f} effective company donors. The product is weight concentration, not independent sample size. Positive-support counts/mass, largest and top-five weights, bandwidth fallbacks and numerical underflow are retained in [support.csv](reports/support.csv), with [sector summaries](reports/support_by_sector.csv). The broad weights explain why nominal neighbor rank must not be read as a hard group size.

[atlanta_donor_companies.csv](reports/atlanta_donor_companies.csv) retains all 498 × 498 company comparison weights, mixed-distance components and ranks. [atlanta_top_donor_rows.csv](reports/atlanta_top_donor_rows.csv) retains 20 pair weights per query, training labels, positive numerator contributions and omitted mass. Those top 20 omit {top_rows.groupby('query_company_id').omitted_weight_mass.first().min():.2%}–{top_rows.groupby('query_company_id').omitted_weight_mass.first().max():.2%} of diagnostic pair weight, so they are an explanation excerpt. All metros remain donors with their numerical kernel weights; no outlier was deleted from the primary run. Similarity weights are not feature importance or causal contributions.

## Prespecified stability

All **67 variants** were recorded: four final New York removals, 49 individual-metro removals, five block omissions and nine bandwidth pairs. An additional ten fixed-settings outer fits evaluate New York influence on the same 48 non-New-York test metros using original focus weights.

Removing one donor metro and refitting the grouped final global/distance components produced Atlanta expectations from **{loo.expected.min():.3f} to {loo.expected.max():.3f}**. The largest absolute change was {loo.delta.abs().max():.3f} HQs. Every resulting Atlanta residual remains positive. Removing New York changed R1/grouped Atlanta expectations by {sens.query("variant == 'remove_new_york' and method == 'GROUPED'").delta.iloc[0]:+.3f} to {sens.query("variant == 'remove_new_york' and method == 'GROUPED'").expected.iloc[0]:.3f}; its effect is through the global component because alpha=0. [sensitivities.csv](reports/sensitivities.csv) separates the global, fixed-metric direct-label and remaining scaling/bandwidth/support effects.

{ny_table}

All five block omissions and nine width substitutions leave the final expectation unchanged because alpha is zero. They cannot establish a grouping benefit. Diagnostic top-10 metro overlap ranges from {int(sens[sens.variant.str.startswith('drop_')].top10_overlap.min())} to {int(sens[sens.variant.str.startswith('drop_')].top10_overlap.max())} across block omissions; ranks and company/sector changes are saved for every variant. Atlanta's nearest-donor distance and diagnostic bandwidth are both below their cross-fitted 95th percentiles; these are descriptive support checks with fold-varying selected bandwidths, not extrapolation guarantees.

## Verification and limits

All **{validation['check_count']} artifact/numerical checks** and **{len(read(ROOT / 'reports/data_checks.csv'))} data acceptance checks** passed. Verification independently reconstructs regional/company distances, kernel fixtures, scoring, count/sector reconciliation, donor normalization and pair weights, checks label/fold preservation and train/query separation, reloads final artifacts to reproduce Atlanta probabilities, and confirms unchanged consumed-source hashes. The final run performed {meta['distinct_global_fits']} distinct global fits with {meta['failures']} fitting failures, one CPU thread and the exact saved R1 Python/package versions. See [RUN_GUIDE.md](RUN_GUIDE.md), [run metadata](reports/run_metadata.json), [acceptance results](reports/artifact_validation_checks.csv) and [artifact inventory](reports/output_manifest.csv).

An initial export attempt stopped on a pandas index/column ambiguity before opening Atlanta assessment labels. A verification attempt then exposed a donor-CBSA parsing issue. Both implementation issues were fixed; the unchanged search was rerun from preparation, along with export dtype cleanup. No candidates or unfavorable validation rows were omitted, and no search choices changed after results. The protocol's eight preparation documents remain unchanged as the original design record.

The experiment provides no evidence to replace R1 with grouping under this specification. Future evidence should come from untouched periods or additional comparable regions with a frozen outcome/coverage contract. Overlapping companies and donor groups do not add independent economies. Regional structure can reflect historical corporate choices. This study does not identify incentive effects, municipal program performance, future moves, ordinary offices or local jobs.
"""
    (ROOT / "FINAL_RESULTS.md").write_text(text)
    paths = sorted(p for p in ROOT.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.name != "output_manifest.csv")
    save("output_manifest", [dict(path=str(p.relative_to(ROOT)), bytes=p.stat().st_size, sha256=sha(p),
                                  rows=sum(1 for _ in p.open())-1 if p.suffix == ".csv" else "") for p in paths])
    print("Wrote checked final results, sector support, and artifact inventory.")


if __name__ == "__main__":
    main()
