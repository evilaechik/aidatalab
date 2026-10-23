#!/usr/bin/env python3
"""Build the Top-100 MSA comparison roster defined by the green-state map.

The study geography is an MSA, not an individual city.  A multi-state MSA is
included only when *all* of its member states are selected on the map.  MSAs
are ranked by their 2023 Census Business Dynamics Statistics employer-
establishment count.

The resulting roster and county crosswalk are public geographic/reference
data.  They contain no Data Axle locations or Invest Atlanta restricted data.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


ARTEM = Path(__file__).resolve().parents[1]
RAW = ARTEM / "data" / "business_entry_models" / "raw_inputs"
BDS_PATH = RAW / "census_bds_2023_msa.csv"
DELINEATION_PATH = RAW / "census_cbsa_delineation_list1_2023.xlsx"
DEFAULT_OUTPUT = ARTEM / "data" / "map_green_state_100"

# Exact green states in the supplied map image, 2026-10-22.
MAP_GREEN_STATES = {
    "Alabama",
    "Arkansas",
    "Colorado",
    "Delaware",
    "Florida",
    "Georgia",
    "Kansas",
    "Kentucky",
    "Louisiana",
    "Maryland",
    "Mississippi",
    "Missouri",
    "New Mexico",
    "North Carolina",
    "Oklahoma",
    "South Carolina",
    "Tennessee",
    "Texas",
    "Virginia",
}


def load_delineation() -> pd.DataFrame:
    if not DELINEATION_PATH.exists():
        raise FileNotFoundError(DELINEATION_PATH)
    data = pd.read_excel(DELINEATION_PATH, header=2)
    data.columns = [str(column).strip() for column in data.columns]
    data["CBSA Code"] = pd.to_numeric(data["CBSA Code"], errors="coerce")
    data = data[
        data["Metropolitan/Micropolitan Statistical Area"].eq("Metropolitan Statistical Area")
    ].dropna(subset=["CBSA Code"]).copy()
    data["CBSA Code"] = data["CBSA Code"].astype(int)
    return data


def members_within_map(states: pd.Series) -> bool:
    return set(states).issubset(MAP_GREEN_STATES)


def build_roster(top_n: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    if not BDS_PATH.exists():
        raise FileNotFoundError(BDS_PATH)
    bds = pd.read_csv(BDS_PATH, usecols=["year", "msa", "estabs"], low_memory=False)
    bds["estabs"] = pd.to_numeric(bds["estabs"], errors="coerce")
    bds = bds[bds["year"].eq(2023)].dropna(subset=["msa", "estabs"]).copy()
    bds["msa"] = bds["msa"].astype(int)

    delineation = load_delineation()
    metadata = (
        delineation.groupby("CBSA Code", as_index=False)
        .agg(
            msa_title=("CBSA Title", "first"),
            member_states=("State Name", lambda values: "; ".join(sorted(set(values)))),
            state_set=("State Name", lambda values: sorted(set(values))),
        )
    )
    metadata = metadata[metadata["state_set"].map(members_within_map)].copy()
    candidates = bds.merge(metadata, left_on="msa", right_on="CBSA Code", how="inner", validate="one_to_one")
    if len(candidates) < top_n:
        raise ValueError(f"Only {len(candidates)} selected-state MSAs available; need {top_n}")
    roster = (
        candidates.nlargest(top_n, "estabs")
        .sort_values("estabs", ascending=False)
        .rename(columns={"estabs": "establishments_2023"})
        [["year", "msa", "establishments_2023", "msa_title", "member_states"]]
        .reset_index(drop=True)
    )
    roster["scope_name"] = "green_map_selected_states"
    roster["selection_method"] = "Top 100 eligible MSAs by 2023 Census BDS employer establishments"
    roster["scope_states"] = "; ".join(sorted(MAP_GREEN_STATES))

    counties = delineation[delineation["CBSA Code"].isin(roster["msa"])].copy()
    counties["county_fips"] = (
        counties["FIPS State Code"].astype(int).astype(str).str.zfill(2)
        + counties["FIPS County Code"].astype(int).astype(str).str.zfill(3)
    )
    crosswalk = counties.rename(
        columns={
            "CBSA Code": "msa_cbsa",
            "Metropolitan Division Code": "division_msa",
            "CBSA Title": "metro_name",
            "State Name": "county_state",
            "County/County Equivalent": "county_name",
            "Central/Outlying County": "county_role",
        }
    )[
        ["county_fips", "msa_cbsa", "division_msa", "metro_name", "county_state", "county_name", "county_role"]
    ].copy()
    crosswalk["msa_cbsa"] = crosswalk["msa_cbsa"].astype(int).astype(str).str.zfill(5)
    crosswalk["division_msa"] = pd.to_numeric(crosswalk["division_msa"], errors="coerce").astype("Int64")
    crosswalk = crosswalk.sort_values(["msa_cbsa", "county_fips"]).reset_index(drop=True)
    return roster, crosswalk


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--top-n", type=int, default=100)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.top_n <= 0:
        raise ValueError("--top-n must be positive")

    roster, crosswalk = build_roster(args.top_n)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    roster.to_csv(args.output_dir / "msa_roster.csv", index=False)
    crosswalk.to_csv(args.output_dir / "metro_county_crosswalk_2023.csv", index=False)
    print(f"Roster: {len(roster)} MSAs, {len(crosswalk)} county rows")
    print(f"Largest MSA: {roster.iloc[0]['msa_title']}")
    print(f"Smallest MSA: {roster.iloc[-1]['msa_title']}")
    print(f"Output: {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
