#!/usr/bin/env python3
"""Create employment-normalized Fortune corporate-anchor outcomes for the top 100 MSAs.

Raw corporate-anchor counts are expected to rise with metro scale. This builder
creates two descriptive alternatives using the same direct-source documented
corporate-anchor count: a simple count per 100,000 QCEW jobs and an
employment-only empirical-Bayes version that shrinks small-metro rates toward
the national rate. Neither converts the incomplete regional-HQ research stream
into a complete office census.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
import pandas as pd


ARTEM = Path(__file__).resolve().parents[1]
ANCHORS = ARTEM / "data" / "big_business_presence" / "fortune500_documented_corporate_anchor_msa_outcome_2026.csv"
ROSTER = ARTEM / "data" / "business_entry_models" / "top100_xgboost" / "top_100_msa_roster.csv"
FACTORS = ARTEM / "data" / "business_entry_models" / "external_qcew_factors" / "external_factor_model_panel.csv"
OUTPUT = ARTEM / "data" / "big_business_presence" / "fortune500_employment_normalized_corporate_anchor_outcome_2026.csv"


def code(series: pd.Series) -> pd.Series:
    return series.astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--anchors", type=Path, default=ANCHORS)
    parser.add_argument("--roster", type=Path, default=ROSTER)
    parser.add_argument("--factors", type=Path, default=FACTORS)
    parser.add_argument("--factor-year", type=int, default=2022)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    for path in [args.anchors, args.roster, args.factors]:
        if not path.is_file():
            raise FileNotFoundError(path)

    anchors = pd.read_csv(args.anchors, dtype={"msa_cbsa": str})
    anchors["msa"] = code(anchors["msa_cbsa"])
    roster = pd.read_csv(args.roster, dtype={"msa": str})
    roster["msa"] = code(roster["msa"])
    factors = pd.read_csv(args.factors, dtype={"msa": str})
    factors["msa"] = code(factors["msa"])
    factors = factors[pd.to_numeric(factors["year"], errors="coerce").eq(args.factor_year)].copy()
    if factors["msa"].duplicated().any():
        raise ValueError(f"Factor data has duplicate MSA rows for {args.factor_year}.")

    result = roster.merge(
        anchors[["msa", "documented_corporate_anchor_count"]], on="msa", how="left", validate="one_to_one"
    ).merge(
        factors[["msa", "qcew_employment"]], on="msa", how="left", validate="one_to_one"
    )
    result["msa_cbsa"] = result["msa"]
    result["documented_corporate_anchor_count"] = pd.to_numeric(
        result["documented_corporate_anchor_count"], errors="coerce"
    )
    result["qcew_employment"] = pd.to_numeric(result["qcew_employment"], errors="coerce")
    eligible = result["documented_corporate_anchor_count"].notna() & result["qcew_employment"].gt(0)
    result["employment_normalization_status"] = np.where(
        eligible, "usable_2022_qcew_exposure", "factor_exposure_missing"
    )
    result["documented_anchors_per_100k_qcew_jobs"] = np.where(
        eligible,
        result["documented_corporate_anchor_count"] / result["qcew_employment"] * 100_000,
        np.nan,
    )

    # The smoothing exposure is the cohort's median workforce, determined
    # without looking at the anchor outcome. It prevents a single documented
    # site in a small metro from dominating a rate comparison.
    smoothing_jobs = float(result.loc[eligible, "qcew_employment"].median())
    national_rate_per_job = float(
        result.loc[eligible, "documented_corporate_anchor_count"].sum()
        / result.loc[eligible, "qcew_employment"].sum()
    )
    result["eb_smoothing_jobs"] = smoothing_jobs
    result["national_anchor_rate_per_100k_jobs"] = national_rate_per_job * 100_000
    result["eb_documented_anchors_per_100k_qcew_jobs"] = np.where(
        eligible,
        (
            result["documented_corporate_anchor_count"] + national_rate_per_job * smoothing_jobs
        ) / (result["qcew_employment"] + smoothing_jobs) * 100_000,
        np.nan,
    )
    result["outcome_caveat"] = (
        "Global-HQ component is complete; regional/divisional component is direct-source documented evidence, "
        "not a complete regional-HQ census. Employment normalization removes most metro-scale exposure but does not create a causal policy outcome."
    )
    result = result.sort_values("msa")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False, quoting=csv.QUOTE_MINIMAL)
    print(f"Usable employment-normalized rows: {eligible.sum():,}")
    print(f"Median QCEW employment used for EB smoothing: {smoothing_jobs:,.0f}")
    print(f"Output: {args.output.resolve()}")


if __name__ == "__main__":
    main()
