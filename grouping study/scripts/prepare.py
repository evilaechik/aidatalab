"""Validate unchanged R1 sources and freeze the grouping execution contract."""
import importlib.metadata
import json
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from common import ATL, BLOCKS, COMPANY, GRID, R1, REPO, ROOT, TARGET, read, save, sha, write_json


def main():
    for name in ["config", "tables", "reports", "models"]:
        (ROOT / name).mkdir(exist_ok=True)
    checks = []

    def check(name, passed):
        checks.append(dict(check=name, passed=bool(passed)))
        if not passed:
            save("data_checks", checks)
            raise ValueError(name)

    protocols = ["Readme", "background", "STUDY_DESIGN", "DATA_CONTRACT", "TRAINING_HANDOFF", "VALIDATION", "REPORTING_AND_INTERPRETATION", "SOURCES"]
    source_paths = [ROOT / f"{name}.md" for name in protocols] + list((ROOT / "scripts").glob("*.py"))
    names = ["training_company_hq_development_2025", "training_company_hq_atlanta_2025", "training_company_metro_hq_2025",
             "training_development_2025", "training_atlanta_2025", "msa_split_assignments"]
    source_paths += [R1 / "tables" / f"{n}.csv" for n in names]
    source_paths += [R1 / "config" / f"{n}.json" for n in ["company_hq_feature_spec", "feature_spec", "training_plan", "input_manifest"] if (R1 / "config" / f"{n}.json").exists()]
    source_paths += [R1 / "config/input_manifest.csv", R1 / "reports/training/r1/oof_company_probabilities.csv",
                     R1 / "reports/training/oof_metro_predictions.csv", R1 / "reports/training/run_metadata.json",
                     R1 / "reports/training/selection_frozen.json", R1 / "models/r1/B_logistic.joblib", R1 / "reports/output_manifest.csv"]
    source_paths += [REPO / "study_1/expanded_500/tables" / f"{n}.csv" for n in ["company_cohort_500", "company_msa_hq_labels_2025", "firm_coverage_and_omissions"]]
    source_paths += [REPO / "study_1" / n for n in ["CLEANUP.md", "PUBLIC_REPOSITORY.md", "provenance/cleanup_manifest.json", "requirements-training.txt", "scripts/company_hq_extension.py", "scripts/train_hq_2025.py"]]
    manifest = save("input_manifest", [dict(path=str(p.relative_to(REPO)), sha256=sha(p), bytes=p.stat().st_size) for p in sorted(set(source_paths))], "config")
    spec = json.loads((R1 / "config/company_hq_feature_spec.json").read_text())
    metadata = json.loads((R1 / "reports/training/run_metadata.json").read_text())
    versions = {name: importlib.metadata.version(name) for name in metadata["versions"]}
    check("python_3_12", sys.version_info[:2] == (3, 12))
    check("exact_R1_package_versions", versions == metadata["versions"])
    original_inputs = read(R1 / "config/input_manifest.csv").set_index("path").sha256
    check("normalized_inputs_match_R1_frozen_training_hashes", all(
        sha(R1 / "tables" / f"{name}.csv") == original_inputs[f"feature_refinement/tables/{name}.csv"] for name in names))
    original_outputs = read(R1 / "reports/output_manifest.csv").set_index("path").sha256
    reference_paths = ["reports/training/r1/oof_company_probabilities.csv", "reports/training/oof_metro_predictions.csv",
                       "reports/training/run_metadata.json", "reports/training/selection_frozen.json", "models/r1/B_logistic.joblib"]
    check("references_match_saved_R1_output_hashes", all(sha(R1 / name) == original_outputs[name] for name in reference_paths))
    data = {n: read(R1 / "tables" / f"{n}.csv") for n in names}
    dev, atl, full = [data[n] for n in names[:3]]
    split = data["msa_split_assignments"]
    roster = read(REPO / "study_1/expanded_500/tables/company_cohort_500.csv")
    audit = read(REPO / "study_1/expanded_500/tables/company_msa_hq_labels_2025.csv")
    coverage = read(REPO / "study_1/expanded_500/tables/firm_coverage_and_omissions.csv")
    eligible = set(coverage.loc[coverage.eligible_primary == 1, "company_id"])
    excluded = set(coverage.loc[coverage.eligible_primary == 0, "company"])
    check("500_roster_and_498_eligible", len(roster) == roster.company_id.nunique() == 500 and len(eligible) == 498)
    check("two_documented_exclusions", excluded == {"Lululemon athletica", "Autoliv"})
    check("matrix_dimensions", len(dev) == 24402 and len(atl) == 498 and len(full) == 24900 and full.cbsa.nunique() == 50)
    check("positive_totals", dev[TARGET].sum() == 420 and atl[TARGET].sum() == 15 and full[TARGET].sum() == 435)
    check("outside_frame_63", ((coverage.eligible_primary == 1) & (coverage.hq_inside_frame == 0)).sum() == 63)
    check("audit_unknowns_preserved", len(audit) == 25000 and audit[TARGET].isna().sum() == 100)
    check("audit_excluded_firms_unknown", audit.loc[~audit.company_id.isin(eligible), TARGET].isna().all())
    check("42_regression_15_distance_inputs", len(spec["primary_predictors"]) == len(set(spec["primary_predictors"])) == 42 and sum(map(len, BLOCKS.values())) == 15)
    check("no_prohibited_features", not set(spec["primary_predictors"]) & set(spec["prohibited_predictors"]))
    for name, frame in [("dev", dev), ("atlanta", atl), ("full", full)]:
        check(f"{name}_unique_keys", not frame.duplicated(["company_id", "cbsa"]).any())
        check(f"{name}_binary_labels", frame[TARGET].isin([0, 1]).all())
        check(f"{name}_complete_roster", all(set(g.company_id) == eligible for _, g in frame.groupby("cbsa")))
    compare = pd.concat([dev, atl]).set_index(["company_id", "cbsa"]).sort_index()
    check("full_source_values_unchanged", compare.equals(full.set_index(["company_id", "cbsa"]).sort_index()))
    joined = full[["company_id", "cbsa", TARGET]].merge(audit, on=["company_id", "cbsa"], validate="one_to_one", suffixes=("", "_audit"))
    check("audit_targets_identical", (joined[TARGET] == joined[TARGET+"_audit"]).all())
    check("reserved_atlanta_and_five_folds", ATL not in set(dev.cbsa) and set(atl.cbsa) == {ATL} and set(dev.validation_fold) == set(range(5)))
    folds = dev[["cbsa", "validation_fold"]].drop_duplicates().merge(split, on="cbsa", validate="one_to_one", suffixes=("", "_source"))
    check("supplied_folds_unchanged", len(folds) == 49 and (folds.validation_fold == folds.validation_fold_source).all())
    regional = json.loads((R1 / "config/feature_spec.json").read_text())["primary_predictors"]
    check("34_regional_inputs", len(regional) == 34)
    check("regional_values_constant_per_metro", (full.groupby("cbsa")[regional].nunique(dropna=False) == 1).all().all())
    check("company_values_constant_across_metros", (full.groupby("company_id")[COMPANY].nunique(dropna=False) == 1).all().all())
    check("primary_company_fields_complete", full[COMPANY].notna().all().all())
    numeric = [f for f in spec["primary_predictors"] if f not in spec["categorical_predictors"]]
    check("no_numeric_infinities", not np.isinf(full[numeric].to_numpy()).any())
    company = dev.drop_duplicates("company_id")[["company_id", "company"]+COMPANY].sort_values("company_id")
    joined = company.merge(roster, on="company_id", validate="one_to_one", suffixes=("", "_roster"))
    check("inherited_company_log_units", np.allclose(joined.log_company_revenue, np.log(joined.company_revenue_usd_millions), atol=1e-9) and np.allclose(joined.log_company_workforce, np.log(joined.company_global_workforce_fortune), atol=1e-9))
    check("documented_category_strings", all((joined[f] == joined[f+"_roster"]).all() for f in COMPANY[2:]))
    ref = read(R1 / "reports/training/r1/oof_company_probabilities.csv").query("model == 'B_logistic'")
    joined = dev[["company_id", "cbsa", TARGET, "validation_fold"]].merge(ref, on=["company_id", "cbsa"], validate="one_to_one")
    check("reference_exact_roster_labels_folds", len(joined) == 24402 and (joined[TARGET] == joined.observed).all() and (joined.validation_fold == joined.fold).all())
    check("reference_probability_bounds", ref.probability.between(0, 1).all())
    check("nested_bandwidth_ranks_feasible", min(dev.loc[~dev.validation_fold.isin([a, b]), "cbsa"].nunique() for a in range(5) for b in range(5) if a != b) >= 20)
    save("companies", company, "tables")
    save("metros", full.drop_duplicates("cbsa")[["cbsa", "metro_name"]+regional].sort_values("cbsa"), "tables")
    save("splits", split, "tables")
    columns = ["company_id", "cbsa", "company", "metro_name"] + spec["primary_predictors"]
    save("development", dev[columns+[TARGET, "validation_fold"]], "tables")
    save("atlanta_predictors", atl[columns], "tables")
    save("atlanta_labels", atl[["company_id", "cbsa", TARGET]], "tables")
    save("data_checks", checks)
    contract = dict(protocol="1.0", frozen_at_utc=datetime.now(timezone.utc).isoformat(), target=TARGET,
                    seed=20261125, threads=1, bootstrap_replicates=2000, python=sys.version, versions=versions,
                    counts=dict(companies=498, development_metros=49, full_metros=50, development_positives=420),
                    regression=spec, regional_blocks=BLOCKS, company_fields=COMPANY,
                    company_weights=dict(numeric=.4, industry=.5, listing=.1), grid=GRID,
                    logistic=dict(solver="lbfgs", penalty="l2", fit_intercept=True, max_iter=1500, tol=1e-8, class_weight=None),
                    distance="unique-training-entity median imputation and population z scores; equal mean of five block MSEs",
                    kernel="normalized exp(-D_squared/(2*h_squared)); kth donor bandwidth, string-ID ties, zero fallback to minimum positive or 1",
                    focus=dict(blocks="primary five blocks", bandwidth_rank=10, weight="exp(-D_squared/(2*h_squared))", normalize="once per pooled split context"),
                    support=dict(metro_min=10, company_min=25, validation_min=15, action="effective alpha=0 if donor support fails"),
                    alpha_zero_explanation="Bandwidths are inapplicable; km=20,kc=150 supply diagnostic donor explanations only, with effective alpha zero",
                    splits="supplied whole-MSA folds; inner training excludes both inner and outer held-out folds; Atlanta covariates only",
                    selection="focus count MAE then company log loss, absolute tie tolerance 1e-10; smaller alpha, larger km, larger kc, smaller C; family order EMP,R1_GLOBAL,FOCUS_GLOBAL,GROUPED",
                    probability_scoring=dict(log_loss_clip=[1e-12, 1-1e-12], original_probabilities_for_counts_and_brier=True),
                    uncertainty="2000 whole-metro paired fixed-prediction draws, seed 20261125; weighted first-reaching 90th absolute-residual quantile for heuristic Atlanta band",
                    sensitivities=["New York removal with refits and original focus weights", "49 leave-one-donor-metro refits", "five block omissions", "nine bandwidth pairs"],
                    input_manifest_sha256=sha(ROOT / "config/input_manifest.csv"), deviations=[])
    write_json(ROOT / "config/execution_contract.json", contract)
    print(f"Prepared {len(checks)} passing checks; frozen 84 grouping candidates.", flush=True)


if __name__ == "__main__":
    main()
