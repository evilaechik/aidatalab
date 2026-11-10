#!/usr/bin/env python3
"""Offline finalization and validation of the full-500 HQ training extension.

No network, imputation, training, or original-study table mutations.
"""
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

import company_hq_extension
import study_integrity

BASE = Path(__file__).resolve().parents[1]
DEFAULT = BASE / "expanded_500"
DATE = "2026-11-09"
STRATA = ["company_broad_industry", "revenue_band", "ownership_listing_type_2025"]
COPIED_TABLES = ["metro_economic_inputs_2024", "metro_sector_inputs", "metro_occupation_inputs_2024",
                 "fixed_geography_employment_growth", "economic_source_registry", "metro_features_2024",
                 "feature_dictionary", "msa_split_assignments", "additional_hq_context"]
KEYS = {"company_cohort_500": ["company_id"], "company_identity_matches": ["company_id"],
        "sec_identity_candidates": ["company_id"], "sec_source_checks": ["company_id"],
        "firm_source_checks": ["company_id"], "firm_coverage_and_omissions": ["company_id"],
        "cohort_strata": STRATA, "cohort_coverage_summary": STRATA,
        "company_msa_hq_labels_2025": ["company_id", "cbsa"],
        "metro_sector_hq_counts_2025": ["cbsa", "company_broad_industry"],
        "additional_hq_context": ["company_id", "cbsa"],
        "metro_sector_inputs": ["cbsa", "industry_proxy"],
        "metro_occupation_inputs_2024": ["cbsa", "soc"], "feature_dictionary": ["feature_name"],
        **company_hq_extension.KEYS}
for name in ["metro_economic_inputs_2024", "fixed_geography_employment_growth", "metro_features_2024",
             "msa_split_assignments", "metro_hq_targets_2025", "training_aggregate_2025",
             "training_development_2025", "training_atlanta_2025"]:
    KEYS[name] = ["cbsa"]


def read(root, name):
    return pd.read_csv(root / "tables" / f"{name}.csv", dtype={"company_id": str, "cbsa": str, "publisher_hq_cbsa": str})


def read_reference(root, name):
    return pd.read_csv(root / "reference_inputs" / f"{name}.csv", dtype={"company_id": str, "cbsa": str, "publisher_hq_cbsa": str})


def save(root, name, frame):
    frame.to_csv(root / "tables" / f"{name}.csv", index=False, float_format="%.12g")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def build(root):
    for folder in ["tables", "config", "reports"]:
        (root / folder).mkdir(exist_ok=True, parents=True)
    # Frozen normalized inputs and compact original checks live in this run.
    # No parent 98-firm experiment or external data folder is required.
    cohort = read(root, "company_cohort_500")
    old_ledger = read_reference(root, "firm_coverage_and_omissions").set_index("company_id")
    old_checks = read_reference(root, "firm_source_checks").set_index("company_id")
    sec = read(root, "sec_source_checks").fillna("").set_index("company_id")
    supplements = pd.read_csv(root / "config/official_company_supplements.csv").fillna("").set_index("company_id")
    checks, ledger = [], []
    frame = pd.read_csv(root / "config/metro_frame.csv", dtype={"cbsa": str})
    for row in cohort.itertuples():
        key = row.company_id
        if key in old_checks.index:
            check_row = dict(old_checks.loc[key], company_id=key)
        elif key in supplements.index:
            s = supplements.loc[key]
            check_row = dict(company_id=key, company=row.company, search_query=s.search_query,
                             directory_or_listing_attempted=1, publisher_listing_found=1,
                             publisher_listing_url=row.publisher_source_url, official_supplementary_source_url=s.source_url,
                             official_source_check_scope=s.scope, access_date=s.access_date)
        else:
            s = sec.loc[key]
            if s.status != "metadata_read":
                raise ValueError(f"No completed supplemental route for {key}: {s.status}")
            check_row = dict(company_id=key, company=row.company,
                             search_query=f"Official SEC identity lookup: {row.company}; {row.publisher_map_name}",
                             directory_or_listing_attempted=1, publisher_listing_found=1,
                             publisher_listing_url=row.publisher_source_url, official_supplementary_source_url=s.source_url,
                             official_source_check_scope="Official submissions metadata read for identity and current business address; 2025 annual filing route retained separately when available. Not independent 2025 HQ-role or full-filing verification.",
                             access_date=DATE)
        checks.append(check_row)
        if key in old_ledger.index:
            policy = dict(old_ledger.loc[key], company_id=key)
            assert str(policy["publisher_hq_cbsa"]) == row.publisher_hq_cbsa
        else:
            inside = int(row.publisher_hq_cbsa in set(frame.cbsa))
            policy = dict(company_id=key, company=row.company, company_broad_industry=row.company_broad_industry,
                          publisher_reported_location=row.publisher_reported_location, publisher_hq_cbsa=row.publisher_hq_cbsa,
                          publisher_hq_msa=row.publisher_hq_msa, official_supplementary_source_url=check_row["official_supplementary_source_url"],
                          eligible_primary=1, coverage_status="reported_hq_msa_resolved", hq_inside_frame=inside,
                          omission_reason="", omission_supports_general_office_absence=0,
                          selected_hq_absence_scope="Selected HQ point elsewhere supports a selected-point zero only",
                          general_office_presence_status="unknown_not_enumerated",
                          other_msa_zero_scope="Publisher-selected HQ point is elsewhere; no claim about offices or additional HQs",
                          known_additional_hq="", policy_note="Fixed 2025 publisher identity/location; later corporate actions do not establish historical physical closure.")
            if not inside:
                policy["policy_note"] += " Reported HQ outside selected 50; zero in each selected MSA, not a coverage exclusion."
        ledger.append(policy)
    checks = pd.DataFrame(checks)[list(pd.read_csv(root / "reference_inputs/firm_source_checks.csv", nrows=0).columns)]
    ledger = pd.DataFrame(ledger)[list(pd.read_csv(root / "reference_inputs/firm_coverage_and_omissions.csv", nrows=0).columns)]
    save(root, "firm_source_checks", checks)
    save(root, "firm_coverage_and_omissions", ledger)
    eligible = ledger[ledger.eligible_primary.eq(1)]
    n, excluded_n = len(eligible), len(cohort) - len(eligible)
    labels = cohort[["company_id"]].merge(frame[["cbsa"]], how="cross").merge(
        ledger[["company_id", "eligible_primary", "publisher_hq_cbsa"]], on="company_id", validate="many_to_one")
    labels["reported_hq_presence"] = np.where(labels.eligible_primary.eq(1), labels.cbsa.eq(labels.publisher_hq_cbsa).astype(int), np.nan)
    labels["label_status"] = np.where(labels.eligible_primary.eq(0), "unknown_excluded_role_conflict",
                                      np.where(labels.reported_hq_presence.eq(1), "reported_hq_present", "reported_selected_hq_elsewhere"))
    labels = labels[["company_id", "cbsa", "reported_hq_presence", "label_status"]]
    save(root, "company_msa_hq_labels_2025", labels)
    target = frame[["cbsa", "metro_name"]].copy()
    target["reported_hq_count_2025"] = target.cbsa.map(eligible.publisher_hq_cbsa.value_counts()).fillna(0).astype(int)
    target["eligible_company_n"], target["sampled_company_n"], target["excluded_unknown_company_n"] = n, 500, excluded_n
    target["reported_hq_share_2025"] = target.reported_hq_count_2025 / n
    target["selected500_count_lower_bound"] = target.reported_hq_count_2025
    target["selected500_count_upper_bound"] = target.reported_hq_count_2025 + excluded_n
    target["unreviewed_publisher_count_500"] = target.cbsa.map(cohort.publisher_hq_cbsa.value_counts()).fillna(0).astype(int)
    additional = read(root, "additional_hq_context").groupby("cbsa").company_id.nunique()
    target["known_additional_hq_sensitivity_count"] = target.reported_hq_count_2025 + target.cbsa.map(additional).fillna(0).astype(int)
    target["target_scope"] = "2025 publisher-selected HQ point; covered Fortune500 cohort; not all offices or all co-HQs"
    save(root, "metro_hq_targets_2025", target)
    sectors = sorted(cohort.company_broad_industry.unique())
    by_sector = frame[["cbsa"]].merge(pd.DataFrame({"company_broad_industry": sectors}), how="cross")
    actual = eligible.groupby(["publisher_hq_cbsa", "company_broad_industry"]).size().rename("reported_hq_count_2025").reset_index().rename(columns={"publisher_hq_cbsa": "cbsa"})
    by_sector = by_sector.merge(actual, on=["cbsa", "company_broad_industry"], how="left").fillna({"reported_hq_count_2025": 0})
    by_sector["reported_hq_count_2025"] = by_sector.reported_hq_count_2025.astype(int)
    by_sector["eligible_sector_company_n"] = by_sector.company_broad_industry.map(eligible.company_broad_industry.value_counts())
    save(root, "metro_sector_hq_counts_2025", by_sector)
    coverage = cohort.merge(ledger[["company_id", "eligible_primary"]], on="company_id").groupby(STRATA).agg(
        selected_n=("company_id", "size"), eligible_n=("eligible_primary", "sum"), population_n=("stratum_population_n", "first")).reset_index()
    coverage["excluded_n"] = coverage.selected_n - coverage.eligible_n
    save(root, "cohort_coverage_summary", coverage)
    metro, splits = read(root, "metro_features_2024"), read(root, "msa_split_assignments")
    aggregate = metro.merge(target.drop(columns="metro_name"), on="cbsa", validate="one_to_one").merge(splits, on="cbsa", validate="one_to_one")
    for name, selected in [("training_aggregate_2025", aggregate), ("training_development_2025", aggregate[aggregate.split_role.eq("development")]),
                            ("training_atlanta_2025", aggregate[aggregate.split_role.eq("atlanta_assessment")])]:
        save(root, name, selected)
    spec = json.loads((root / "reference_inputs/feature_spec.json").read_text())
    spec.update(common_covered_company_n=n, sampled_company_n=500,
                model_grain="One row per MSA; same 50 economic profiles regardless of company-row count",
                inference_scope=f"Covered {n}-firm Fortune 500 2025 roster in fixed50 frame; retrospective reported-HQ benchmark, not all offices or causal effects",
                design_weights="Attempted census: all 500 companies included in roster; unit design weights; coverage exclusions remain explicit",
                prohibited_predictors=[c for c in aggregate if c not in spec["primary_predictors"]])
    json_write(root / "config/feature_spec.json", spec)
    company_spec = company_hq_extension.build(root, cohort, labels, metro, splits)
    company_spec.update(analysis_revision="2026-11-09_full500_extension")
    json_write(root / "config/company_hq_feature_spec.json", company_spec)
    cfg = dict(protocol_version=3, target_year=2025, collection_date=DATE, company_population="Fixed Fortune 500 2025 edition",
               selection="Attempted census of all 500 stable list-position identities; no outcome-based selection",
               cohort_n=500, final_covered_company_n=n, final_coverage_exclusions_n=excluded_n,
               exclusion_ids=ledger.loc[ledger.eligible_primary.eq(0), "company_id"].to_list(), metro_n=50,
               geography="July 2023 CBSA membership; 500k cartographic polygons, full TIGER fallback for one waterfront point",
               raw_retention="No new raw payloads retained in expansion; source URLs, hashes, compact normalized fields and ledgers only",
               primary_predictors_unchanged=True, original_study_preserved=True, model_training_performed=False,
               financial_reference="2025 edition primarily FY2024; archived public ranking response reused",
               temporal_scope="Retrospective: economic vintages and source revisions unchanged; current SEC metadata is supplemental only",
               schema_changes={"company_cohort_100.csv": "company_cohort_500.csv", "selected100_count_lower_bound": "selected500_count_lower_bound",
                               "selected100_count_upper_bound": "selected500_count_upper_bound", "unreviewed_publisher_count_100": "unreviewed_publisher_count_500"})
    json_write(root / "config/collection_config.json", cfg)
    contract = dict(status="data_prepared_models_not_trained", cohort_n=500, eligible_company_n=n, excluded_company_n=excluded_n,
                    metro_n=50, independent_development_metros=49, atlanta_cbsa="12060",
                    aggregate=dict(target="reported_hq_count_2025", full="tables/training_aggregate_2025.csv",
                                   development="tables/training_development_2025.csv", assessment="tables/training_atlanta_2025.csv",
                                   primary_features=31, feature_spec="config/feature_spec.json", development_rows=49, assessment_rows=1),
                    company=dict(target="reported_hq_presence", full="tables/training_company_metro_hq_2025.csv",
                                 development="tables/training_company_hq_development_2025.csv", assessment="tables/training_company_hq_atlanta_2025.csv",
                                 primary_features=39, feature_spec="config/company_hq_feature_spec.json", full_rows=n * 50,
                                 development_rows=n * 49, assessment_rows=n, baseline_probability_denominator=n),
                    missing_policy="Retain numeric nulls; fit imputation/encoding/scaling inside training folds only; never impute outcomes",
                    validation="Same supplied whole-MSA folds as original; Atlanta excluded from fitting, tuning, preprocessing and selection",
                    trainer_note="Original train_hq_2025.py and verify_training.py freeze 98-firm assumptions. Adapt their validation, denominators, report wording and bootstrap roster to this contract before expanded-model training.")
    json_write(root / "config/training_contract.json", contract)
    if not (root / "config/analysis_plan.json").exists():
        json_write(root / "config/analysis_plan.json", dict(analysis_revision="2026-11-09_full500_extension", status=contract["status"],
                   training_contract="config/training_contract.json", model_families_unchanged=True,
                   baseline="Training-fold employment-proportional and mean-count expectations", regression="Poisson A; logistic B",
                   xgboost="Same shallow count/probability specifications", company_interactions="Four existing interactions, plus predeclared main-effects ablations",
                   selected_model=None, model_selection="Development-only count MAE then RMSE; do not select a model to obtain an Atlanta deficit"))
    schemas = {}
    table_frames = {path.stem: read(root, path.stem) for path in sorted((root / "tables").glob("*.csv"))}
    database_unchanged = study_integrity.sqlite_matches(root / "study_1_expanded_500.sqlite", table_frames)
    with sqlite3.connect(root / "study_1_expanded_500.sqlite") as db:
        for path in sorted((root / "tables").glob("*.csv")):
            name, table = path.stem, read(root, path.stem)
            if not database_unchanged:
                table.to_sql(name, db, index=False, if_exists="replace")
            if name in KEYS and not database_unchanged:
                columns = ",".join(f'"{c}"' for c in KEYS[name])
                db.execute(f'CREATE UNIQUE INDEX "key_{name}" ON "{name}" ({columns})')
            schemas[name] = dict(rows=len(table), primary_key=KEYS.get(name, []), columns=[dict(name=c, dtype=str(table[c].dtype), null_n=int(table[c].isna().sum())) for c in table])
        if not database_unchanged:
            db.execute("VACUUM")
    json_write(root / "config/table_schemas.json", schemas)
    inputs = ["company_cohort_500", "cohort_strata", "company_identity_matches", "collection_source_registry", "sec_identity_candidates", "sec_source_checks"] + COPIED_TABLES
    paths = [root / "tables" / f"{name}.csv" for name in inputs] + [root / "config" / name for name in ["official_company_supplements.csv", "sec_identity_overrides.csv", "collection_config.json", "metro_frame.csv", "population_sampling_frame.csv"]]
    pd.DataFrame([dict(path=str(p.relative_to(root)), sha256=sha(p), role="retained_normalized_input_or_configuration") for p in paths]).to_csv(root / "config/input_manifest.csv", index=False)
    return validate(root)


def validate(root):
    checks = []
    def check(name, condition):
        checks.append(dict(check=name, passed=bool(condition)))
        if not condition:
            raise AssertionError(name)
    cohort, ledger, sources = read(root, "company_cohort_500"), read(root, "firm_coverage_and_omissions"), read(root, "firm_source_checks")
    eligible = ledger[ledger.eligible_primary.eq(1)]
    n, excluded = len(eligible), set(ledger.loc[ledger.eligible_primary.eq(0), "company_id"])
    macro, dev, atl = read(root, "training_aggregate_2025"), read(root, "training_development_2025"), read(root, "training_atlanta_2025")
    pairs, dp, ap = read(root, "training_company_metro_hq_2025"), read(root, "training_company_hq_development_2025"), read(root, "training_company_hq_atlanta_2025")
    labels, identity = read(root, "company_msa_hq_labels_2025"), read(root, "company_identity_matches")
    spec_a = json.loads((root / "config/feature_spec.json").read_text())
    spec_b = json.loads((root / "config/company_hq_feature_spec.json").read_text())
    for path in sorted((root / "tables").glob("*.csv")):
        table = read(root, path.stem)
        if path.stem in KEYS:
            check(f"unique_key_{path.stem}", not table.duplicated(KEYS[path.stem]).any())
    check("500_stable_list_position_ids", len(cohort) == cohort.company_id.nunique() == 500 and set(cohort.fortune_2025_list_position) == set(range(1, 501)))
    check("same_500_population_ids", set(cohort.company_id) == set(pd.read_csv(root / "config/population_sampling_frame.csv").company_id))
    check("attempted_census_unit_weights", cohort.inclusion_probability.eq(1).all() and cohort.design_weight.eq(1).all())
    check("all_73_strata_censused", len(read(root, "cohort_strata")) == 73 and read(root, "cohort_strata").population_n.sum() == 500 and read(root, "cohort_strata").sample_n.sum() == 500)
    check("21_sectors_covered", eligible.company_broad_industry.nunique() == cohort.company_broad_industry.nunique() == 21)
    check("same_two_unknown_exclusions", excluded == {"f2025_401", "f2025_407"} and n == 498)
    check("every_company_has_source_route", len(sources) == 500 and sources.publisher_listing_found.eq(1).all() and sources.official_supplementary_source_url.str.startswith("https://").all())
    check("500_unique_publisher_identity_matches", cohort.publisher_map_company_id.nunique() == 500 and len(identity) == 500)
    check("all_identity_revenues_agree", identity.revenue_agrees.all())
    check("rank_errors_explicitly_retained", set(identity.loc[~identity.rank_agrees, "company_id"]) == {"f2025_231", "f2025_499"})
    check("industry_difference_explicitly_retained", set(identity.loc[~identity.industry_agrees, "company_id"]) == {"f2025_136"})
    check("all_500_coordinates_assigned", cohort.publisher_hq_cbsa.notna().all() and identity.cbsa_match_n.eq(1).all())
    check("only_declared_waterfront_fallback", set(identity.loc[identity.cbsa_assignment_method.str.contains("fallback"), "company_id"]) == {"f2025_465"})
    check("no_general_office_absence_inferred", ledger.omission_supports_general_office_absence.eq(0).all())
    check("25000_audit_rows", len(labels) == 25000)
    check("excluded_100_cells_unknown", labels[labels.company_id.isin(excluded)].reported_hq_presence.isna().all() and labels.reported_hq_presence.isna().sum() == 100)
    check("24900_known_supervised_rows", len(pairs) == 24900 and pairs.company_id.nunique() == n and pairs.reported_hq_presence.notna().all())
    check("24402_498_company_split", len(dp) == n * 49 and len(ap) == n and ap.cbsa.eq("12060").all() and "12060" not in set(dp.cbsa))
    check("49_1_macro_split", len(dev) == 49 and len(atl) == 1 and atl.cbsa.eq("12060").all())
    check("same_roster_every_metro", pairs.groupby("cbsa").size().eq(n).all() and pairs.groupby("cbsa").company_id.nunique().eq(n).all())
    joined = pairs.merge(labels, on=["company_id", "cbsa"], validate="one_to_one", suffixes=("_training", "_audit"))
    check("supervised_labels_equal_audit", joined.reported_hq_presence_training.eq(joined.reported_hq_presence_audit).all())
    check("binary_labels", set(pairs.reported_hq_presence) == {0, 1})
    check("435_inframe_63_outside", eligible.hq_inside_frame.sum() == 435 and eligible.hq_inside_frame.eq(0).sum() == 63)
    check("counts_reconcile_to435", labels.reported_hq_presence.sum() == 435 and macro.reported_hq_count_2025.sum() == 435)
    check("every_metro_count_reconciles", np.allclose(macro.reported_hq_count_2025, macro.cbsa.map(pairs.groupby("cbsa").reported_hq_presence.sum())))
    check("constant_498_denominator", macro.eligible_company_n.eq(n).all() and np.allclose(macro.reported_hq_share_2025, macro.reported_hq_count_2025 / n))
    check("selected500_bounds", macro.selected500_count_lower_bound.eq(macro.reported_hq_count_2025).all() and macro.selected500_count_upper_bound.sub(macro.selected500_count_lower_bound).eq(2).all())
    check("known_additional_hq_one_only", macro.known_additional_hq_sensitivity_count.sum() - macro.reported_hq_count_2025.sum() == 1)
    check("sector_counts_reconcile", np.allclose(macro.reported_hq_count_2025, macro.cbsa.map(read(root, "metro_sector_hq_counts_2025").groupby("cbsa").reported_hq_count_2025.sum())))
    check("original_31_allowlist_unchanged", spec_a["primary_predictors"] == json.loads((root / "reference_inputs/feature_spec.json").read_text())["primary_predictors"])
    check("original_39_allowlist_unchanged", spec_b["primary_predictors"] == json.loads((root / "reference_inputs/company_hq_feature_spec.json").read_text())["primary_predictors"])
    check("31_numeric_metro_factors", len(spec_a["primary_predictors"]) == 31 and macro[spec_a["primary_predictors"]].isna().sum().sum() == 4)
    check("39_primary_company_inputs", len(spec_b["primary_predictors"]) == 39 and len(spec_b["numeric_predictors"]) == 37 and len(spec_b["categorical_predictors"]) == 2)
    check("primary_company_attributes_complete", pairs[["log_company_revenue", "log_company_workforce"] + spec_b["categorical_predictors"]].notna().all().all())
    check("four_macro_gaps_repeat_1992_times", pairs[spec_b["numeric_predictors"]].isna().sum().sum() == 4 * n)
    check("no_outcome_id_or_coverage_predictors", not set(spec_b["primary_predictors"]) & set(spec_b["prohibited_predictors"]) and not set(spec_a["primary_predictors"]) & set(spec_a["prohibited_predictors"]))
    check("no_optional_financials_in_primary", not set(spec_b["primary_predictors"]) & set(spec_b["optional_sensitivity_predictors"]))
    check("finite_primary_numeric_values", np.isfinite(pairs[spec_b["numeric_predictors"]].stack().to_numpy()).all())
    inherited = pd.read_csv(root / "config/original_study_snapshot.csv").set_index("path").sha256
    for name in COPIED_TABLES:
        check(f"inherited_bytes_unchanged_{name}", sha(root / "tables" / f"{name}.csv") == inherited[f"tables/{name}.csv"])
    old = read_reference(root, "company_msa_hq_labels_2025").sort_values(["company_id", "cbsa"]).reset_index(drop=True)
    subset = labels[labels.company_id.isin(old.company_id)].sort_values(["company_id", "cbsa"]).reset_index(drop=True)
    check("all_original_5000_audit_labels_preserved", old.equals(subset))
    original_cohort = read_reference(root, "company_cohort_100").set_index("company_id")
    common = cohort.set_index("company_id").loc[original_cohort.index]
    for column in ["company_revenue_usd_millions", "company_global_workforce_fortune", "company_broad_industry", "ownership_listing_type_2025", "publisher_hq_cbsa"]:
        check(f"original_company_values_preserved_{column}", common[column].equals(original_cohort[column]))
    folds = pairs[["cbsa", "split_role", "validation_fold"]].drop_duplicates().sort_values("cbsa").reset_index(drop=True)
    check("whole_metro_folds_shared", folds.equals(read(root, "msa_split_assignments").sort_values("cbsa").reset_index(drop=True)))
    check("five_folds_10_10_10_10_9", sorted(dev.groupby("validation_fold").size()) == [9, 10, 10, 10, 10])
    check("Atlanta_has_no_fold", ap.validation_fold.isna().all() and atl.validation_fold.isna().all())
    check("dynamic_company_spec_counts", spec_b["covered_companies"] == n and spec_b["rows"] == len(pairs) and spec_b["development_rows"] == len(dp) and spec_b["atlanta_assessment_rows"] == len(ap) and spec_b["positive_hq_labels_inside_frame"] == 435)
    for table, target in [(macro, "reported_hq_count_2025"), (pairs, "reported_hq_presence")]:
        check(f"no_imputed_outcomes_{target}", table[target].notna().all())
    manifest = pd.read_csv(root / "config/input_manifest.csv")
    check("normalized_input_hashes_match", all(sha(root / r.path) == r.sha256 for r in manifest.itertuples()))
    original_manifest = pd.read_csv(root / "config/original_study_snapshot.csv")
    check("original_study_data_models_reports_unchanged", all(study_integrity.historical_match(BASE / r.path, r.sha256, allow_removed=True) for r in original_manifest.itertuples()))
    with sqlite3.connect(root / "study_1_expanded_500.sqlite") as db:
        check("sqlite_integrity", db.execute("PRAGMA integrity_check").fetchone()[0] == "ok")
        check("sqlite_same_label_nulls", db.execute("SELECT COUNT(*) FROM company_msa_hq_labels_2025 WHERE reported_hq_presence IS NULL").fetchone()[0] == 100)
        check("sqlite_same_supervised_rows", db.execute("SELECT COUNT(*) FROM training_company_metro_hq_2025").fetchone()[0] == 24900)
        for name in ["training_aggregate_2025", "training_company_metro_hq_2025", "company_cohort_500"]:
            check(f"sqlite_csv_values_{name}", pd.read_sql_query(f'SELECT * FROM "{name}"', db).equals(read(root, name)))
    summary = dict(validation="PASS", checks_passed=len(checks), checks_failed=0, collected_roster=500, eligible_firms=n,
                   excluded_unknown_firms=len(excluded), hqs_inside_frame=435, hqs_outside_frame=63,
                   audit_rows=len(labels), positive_labels=435, zero_labels=int(labels.reported_hq_presence.eq(0).sum()), unknown_labels=100,
                   macro_full_rows=len(macro), macro_development_rows=len(dev), macro_atlanta_rows=len(atl),
                   company_full_rows=len(pairs), company_development_rows=len(dp), company_atlanta_rows=len(ap),
                   metro_predictors=31, company_primary_predictors=39, unique_metro_predictor_gaps=4,
                   repeated_company_numeric_gaps=4 * n, original_study_preserved=True, model_training_performed=False,
                   source_quality="Publisher-reported HQ pilot; supplemental route checks are not independent historical HQ verification")
    save_path = root / "reports/validation_checks.csv"
    pd.DataFrame(checks).to_csv(save_path, index=False)
    json_write(root / "reports/validation_summary.json", summary)
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    validate(args.root) if args.validate_only else build(args.root)
