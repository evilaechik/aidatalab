#!/usr/bin/env python3
"""Assign exported ArcGIS/Data Axle locations to a target MSA roster locally.

Data Axle Excel exports often redact street numbers.  This utility therefore
does *not* pretend to recover an exact address or geocode a vendor record.
It matches the reported city/state to the Census Gazetteer place centroid and
tests that public point against Census CBSA polygons.  The output explicitly
records ``city_place_centroid_within_cbsa`` as its assignment method.

This is a candidate-location tool, not an office verification tool.  A retail
store, kiosk, warehouse, branch, and office may all occur in the inputs.

Inputs remain local.  Outputs containing licensed locations must be written
outside this repository; the script enforces that guardrail.

Public geographic references required (same vintage):
  * Census 2023 national place Gazetteer ZIP
  * Census TIGER/Line 2023 CBSA ZIP

Example:
  python Artem/scripts/assign_data_axle_locations_to_msas.py \
    --locations-csv /safe/local/arcgis_data_axle_standardized_locations.csv \
    --place-gazetteer /safe/local/2023_Gaz_place_national.zip \
    --cbsa-shapefile /safe/local/tl_2023_us_cbsa.zip \
    --metro-crosswalk Artem/data/big_business_presence/metro_county_crosswalk_2023.csv \
    --output-dir /safe/local/city_msa_assignment
"""

from __future__ import annotations

import argparse
import csv
import io
import re
import struct
import tempfile
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterator

import pandas as pd


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[2]


def reject_repo_output(path: Path) -> None:
    """Avoid accidentally saving licensed data under the Git checkout."""
    resolved = path.expanduser().resolve()
    try:
        resolved.relative_to(REPO_ROOT)
    except ValueError:
        return
    raise ValueError(
        f"Output directory must be outside the repository: {resolved}\n"
        f"Repository: {REPO_ROOT}"
    )


def normalize_text(value: object) -> str:
    text = "" if pd.isna(value) else str(value)
    text = text.lower().replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def normalize_gazetteer_place_name(value: object) -> str:
    """Remove only the legal place designator appended by the Gazetteer."""
    text = normalize_text(value)
    for suffix in (
        " census designated place",
        " metropolitan government",
        " urban county",
        " municipality",
        " borough",
        " village",
        " town",
        " city",
        " cdp",
        " balance",
    ):
        if text.endswith(suffix):
            return text[: -len(suffix)].strip()
    return text


def read_gazetteer(path: Path) -> pd.DataFrame:
    """Read a Census place Gazetteer TSV from its ZIP without persisting it."""
    with zipfile.ZipFile(path) as archive:
        members = [name for name in archive.namelist() if name.lower().endswith(".txt")]
        if len(members) != 1:
            raise ValueError(f"Expected one Gazetteer .txt in {path}; found {members}")
        with archive.open(members[0]) as raw:
            places = pd.read_csv(raw, sep="\t", dtype=str)
    places.columns = [str(column).strip() for column in places.columns]

    required = {"USPS", "NAME", "FUNCSTAT", "ALAND", "INTPTLAT", "INTPTLONG"}
    missing = required - set(places.columns)
    if missing:
        raise ValueError(f"Gazetteer is missing columns: {sorted(missing)}")

    places["state"] = places["USPS"].str.strip().str.upper()
    places["city_key"] = places["NAME"].map(normalize_gazetteer_place_name)
    places["area_sq_m"] = pd.to_numeric(places["ALAND"], errors="coerce").fillna(0)
    places["latitude"] = pd.to_numeric(places["INTPTLAT"], errors="coerce")
    places["longitude"] = pd.to_numeric(places["INTPTLONG"], errors="coerce")
    return places[["state", "city_key", "NAME", "FUNCSTAT", "area_sq_m", "latitude", "longitude"]]


def parse_dbf_records(path: Path) -> Iterator[dict[str, str]]:
    """Minimal DBF reader for the attributes paired with a shapefile."""
    with path.open("rb") as handle:
        header = handle.read(32)
        if len(header) != 32:
            raise ValueError(f"Invalid DBF header: {path}")
        record_count = struct.unpack("<I", header[4:8])[0]
        header_length = struct.unpack("<H", header[8:10])[0]
        record_length = struct.unpack("<H", header[10:12])[0]

        fields: list[tuple[str, int]] = []
        while handle.tell() < header_length:
            descriptor = handle.read(32)
            if not descriptor or descriptor[:1] == b"\r":
                break
            name = descriptor[:11].split(b"\x00", 1)[0].decode("latin-1").strip()
            fields.append((name, descriptor[16]))

        handle.seek(header_length)
        for _ in range(record_count):
            record = handle.read(record_length)
            if len(record) != record_length:
                break
            if record[:1] == b"*":
                continue
            position = 1
            values: dict[str, str] = {}
            for name, length in fields:
                values[name] = record[position : position + length].decode("latin-1").strip()
                position += length
            yield values


def parse_polygon_records(path: Path) -> Iterator[tuple[tuple[float, float, float, float], list[list[tuple[float, float]]]]]:
    """Yield bounding boxes and polygon rings from a Polygon shapefile."""
    with path.open("rb") as handle:
        header = handle.read(100)
        if len(header) != 100:
            raise ValueError(f"Invalid shapefile header: {path}")
        while True:
            record_header = handle.read(8)
            if not record_header:
                return
            if len(record_header) != 8:
                raise ValueError(f"Truncated shapefile record header: {path}")
            _, content_words = struct.unpack(">2i", record_header)
            content = handle.read(content_words * 2)
            if len(content) < 4:
                yield ((0, 0, 0, 0), [])
                continue
            shape_type = struct.unpack("<i", content[:4])[0]
            if shape_type == 0:
                yield ((0, 0, 0, 0), [])
                continue
            if shape_type not in {5, 15, 25}:
                raise ValueError(f"Expected Polygon shape, found shape type {shape_type}")
            xmin, ymin, xmax, ymax = struct.unpack("<4d", content[4:36])
            part_count, point_count = struct.unpack("<2i", content[36:44])
            part_indexes = struct.unpack(f"<{part_count}i", content[44 : 44 + 4 * part_count])
            point_offset = 44 + 4 * part_count
            points = [
                struct.unpack("<2d", content[point_offset + 16 * i : point_offset + 16 * (i + 1)])
                for i in range(point_count)
            ]
            rings = [
                points[start : part_indexes[index + 1] if index + 1 < part_count else point_count]
                for index, start in enumerate(part_indexes)
            ]
            yield ((xmin, ymin, xmax, ymax), rings)


def point_in_ring(longitude: float, latitude: float, ring: list[tuple[float, float]]) -> bool:
    """Ray-casting point-in-polygon test for a closed or open ring."""
    contains = False
    if len(ring) < 3:
        return False
    previous_x, previous_y = ring[-1]
    for current_x, current_y in ring:
        crosses = (current_y > latitude) != (previous_y > latitude)
        if crosses:
            intercept = (previous_x - current_x) * (latitude - current_y) / (previous_y - current_y) + current_x
            if longitude < intercept:
                contains = not contains
        previous_x, previous_y = current_x, current_y
    return contains


def point_in_polygon(longitude: float, latitude: float, rings: list[list[tuple[float, float]]]) -> bool:
    """Even-odd handling supports multipart polygons and interior holes."""
    return sum(point_in_ring(longitude, latitude, ring) for ring in rings) % 2 == 1


def load_target_cbsa_polygons(shapefile_zip: Path, target_cbsa: set[str]) -> dict[str, dict[str, object]]:
    """Read only target CBSA polygons, retaining code and public geometry."""
    with tempfile.TemporaryDirectory(prefix="cbsa_shape_") as temporary:
        temporary_path = Path(temporary)
        with zipfile.ZipFile(shapefile_zip) as archive:
            archive.extractall(temporary_path)
        dbf = next(temporary_path.glob("*.dbf"), None)
        shp = next(temporary_path.glob("*.shp"), None)
        if dbf is None or shp is None:
            raise ValueError("CBSA ZIP must contain a .dbf and .shp")
        attributes = list(parse_dbf_records(dbf))
        shapes = list(parse_polygon_records(shp))

    if len(attributes) != len(shapes):
        raise ValueError("CBSA attribute and geometry record counts do not match")

    polygons: dict[str, dict[str, object]] = {}
    for attributes_row, (bbox, rings) in zip(attributes, shapes, strict=True):
        cbsa = attributes_row.get("CBSAFP", "")
        if cbsa in target_cbsa and rings:
            polygons[cbsa] = {"bbox": bbox, "rings": rings, "census_name": attributes_row.get("NAME", "")}
    missing = target_cbsa - set(polygons)
    if missing:
        raise ValueError(f"CBSA polygons missing for target codes: {sorted(missing)[:10]}")
    return polygons


def choose_place(candidates: pd.DataFrame) -> tuple[pd.Series | None, str]:
    """Prefer incorporated/active places; report ambiguity instead of hiding it."""
    if candidates.empty:
        return None, "city_not_matched_to_census_place"
    active = candidates[candidates["FUNCSTAT"].eq("A")]
    pool = active if not active.empty else candidates
    chosen = pool.sort_values(["area_sq_m", "NAME"], ascending=[False, True]).iloc[0]
    if len(pool) > 1:
        return chosen, "multiple_city_place_matches_selected_largest"
    return chosen, "exact_city_place_match"


def assign_cbsa(longitude: float, latitude: float, polygons: dict[str, dict[str, object]]) -> str | None:
    for cbsa, polygon in polygons.items():
        xmin, ymin, xmax, ymax = polygon["bbox"]  # type: ignore[misc]
        if xmin <= longitude <= xmax and ymin <= latitude <= ymax:
            if point_in_polygon(longitude, latitude, polygon["rings"]):  # type: ignore[arg-type]
                return cbsa
    return None


def build_assignments(
    locations: pd.DataFrame,
    places: pd.DataFrame,
    polygons: dict[str, dict[str, object]],
    metro_names: dict[str, str],
) -> pd.DataFrame:
    """Attach a transparent city-centroid MSA assignment to each location."""
    frame = locations.copy()
    frame["city"] = frame["city"].fillna("").astype(str).str.strip()
    frame["state"] = frame["state"].fillna("").astype(str).str.strip().str.upper()
    frame["city_key"] = frame["city"].map(normalize_text)

    place_groups = {
        key: group for key, group in places.groupby(["state", "city_key"], sort=False)
    }
    lookup_rows: list[dict[str, object]] = []
    for state, city_key in frame[["state", "city_key"]].drop_duplicates().itertuples(index=False):
        candidates = place_groups.get((state, city_key), pd.DataFrame(columns=places.columns))
        place, status = choose_place(candidates)
        if place is None:
            lookup_rows.append(
                {
                    "state": state,
                    "city_key": city_key,
                    "census_place_name": "",
                    "place_match_status": status,
                    "place_latitude": pd.NA,
                    "place_longitude": pd.NA,
                    "msa_cbsa": "",
                    "msa_name": "",
                    "msa_assignment_method": "unassigned",
                }
            )
            continue
        longitude, latitude = float(place["longitude"]), float(place["latitude"])
        cbsa = assign_cbsa(longitude, latitude, polygons)
        lookup_rows.append(
            {
                "state": state,
                "city_key": city_key,
                "census_place_name": place["NAME"],
                "place_match_status": status,
                "place_latitude": latitude,
                "place_longitude": longitude,
                "msa_cbsa": cbsa or "",
                "msa_name": metro_names.get(cbsa or "", ""),
                "msa_assignment_method": "city_place_centroid_within_cbsa" if cbsa else "outside_target_msa_roster",
            }
        )
    lookup = pd.DataFrame(lookup_rows)
    return frame.merge(lookup, on=["state", "city_key"], how="left").drop(columns=["city_key"])


def build_candidate_presence_tables(assigned: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Summarize locations without mislabeling consumer sites as offices."""
    in_target = assigned.loc[assigned["msa_cbsa"].ne("")].copy()
    if in_target.empty:
        return pd.DataFrame(), pd.DataFrame()

    in_target["is_headquarters_category"] = in_target["source_business_category"].eq("Headquarters")
    in_target["is_matched_current_f500"] = in_target["fortune_match_status"].eq("matched")
    in_target["fortune_rank_number"] = pd.to_numeric(in_target["fortune_2025_rank"], errors="coerce")
    in_target["is_matched_current_f100"] = in_target["fortune_rank_number"].le(100)

    company_columns = [
        "msa_cbsa",
        "msa_name",
        "company_name",
        "fortune_2025_company",
        "fortune_2025_rank",
        "fortune_match_status",
    ]
    presence = (
        in_target.groupby(company_columns, dropna=False)
        .agg(
            data_axle_location_rows=("source_record_id", "size"),
            headquarters_category_rows=("is_headquarters_category", "sum"),
            branch_category_rows=("source_business_category", lambda value: value.eq("Branch").sum()),
            kiosk_category_rows=("source_business_category", lambda value: value.eq("Kiosk").sum()),
        )
        .reset_index()
        .sort_values(["msa_cbsa", "company_name"])
    )
    presence["candidate_evidence"] = "Data Axle commercial location; office status requires separate verification"

    score_rows: list[dict[str, object]] = []
    for (cbsa, name), group in in_target.groupby(["msa_cbsa", "msa_name"], dropna=False):
        score_rows.append(
            {
                "msa_cbsa": cbsa,
                "msa_name": name,
                "distinct_query_company_location_candidates": group["company_name"].nunique(),
                "distinct_matched_current_f500_location_candidates": group.loc[
                    group["is_matched_current_f500"], "company_name"
                ].nunique(),
                "distinct_matched_current_f100_location_candidates": group.loc[
                    group["is_matched_current_f100"], "company_name"
                ].nunique(),
                "distinct_companies_with_headquarters_category_location": group.loc[
                    group["is_headquarters_category"], "company_name"
                ].nunique(),
                "location_rows": len(group),
                "score_definition": "Distinct companies with at least one Data Axle commercial location assigned by city-place centroid",
                "not_an_office_score": "True; stores, kiosks, branches, warehouses, and offices can all be included",
            }
        )
    scores = pd.DataFrame(score_rows).sort_values(
        "distinct_matched_current_f500_location_candidates", ascending=False
    )
    return presence, scores


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--locations-csv", required=True, type=Path)
    parser.add_argument("--place-gazetteer", required=True, type=Path)
    parser.add_argument("--cbsa-shapefile", required=True, type=Path)
    parser.add_argument("--metro-crosswalk", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    reject_repo_output(args.output_dir)
    for path in [args.locations_csv, args.place_gazetteer, args.cbsa_shapefile, args.metro_crosswalk]:
        if not path.expanduser().is_file():
            raise FileNotFoundError(path)

    locations = pd.read_csv(args.locations_csv, dtype=str, keep_default_na=False)
    required_location_columns = {"company_name", "city", "state"}
    missing = required_location_columns - set(locations.columns)
    if missing:
        raise ValueError(f"Locations CSV missing columns: {sorted(missing)}")

    crosswalk = pd.read_csv(args.metro_crosswalk, dtype={"msa_cbsa": str})
    target_metros = (
        crosswalk[["msa_cbsa", "metro_name"]]
        .drop_duplicates()
        .assign(msa_cbsa=lambda data: data["msa_cbsa"].str.zfill(5))
    )
    metro_names = dict(target_metros.itertuples(index=False, name=None))
    places = read_gazetteer(args.place_gazetteer)
    polygons = load_target_cbsa_polygons(args.cbsa_shapefile, set(metro_names))
    assigned = build_assignments(locations, places, polygons, metro_names)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    assigned.to_csv(args.output_dir / "data_axle_locations_city_msa_assignment.csv", index=False, quoting=csv.QUOTE_MINIMAL)

    audit = (
        assigned.groupby(["msa_assignment_method", "place_match_status"], dropna=False)
        .size()
        .reset_index(name="location_rows")
        .sort_values("location_rows", ascending=False)
    )
    audit.to_csv(args.output_dir / "data_axle_city_msa_assignment_audit.csv", index=False)

    unmatched = (
        assigned.loc[assigned["msa_cbsa"].eq(""), ["city", "state", "msa_assignment_method", "place_match_status"]]
        .value_counts()
        .rename("location_rows")
        .reset_index()
        .sort_values("location_rows", ascending=False)
    )
    unmatched.to_csv(args.output_dir / "data_axle_unassigned_city_state_audit.csv", index=False)

    presence = (
        assigned.loc[assigned["msa_cbsa"].ne(""), ["msa_cbsa", "msa_name", "company_name"]].drop_duplicates()
    )
    company_presence, scores = build_candidate_presence_tables(assigned)
    company_presence.to_csv(args.output_dir / "data_axle_msa_company_location_candidates.csv", index=False)
    scores.to_csv(args.output_dir / "data_axle_msa_location_candidate_scores.csv", index=False)

    counts = Counter(assigned["msa_assignment_method"])
    print(f"Assigned {len(assigned):,} local records.")
    for method, count in counts.most_common():
        print(f"  {method}: {count:,}")
    print(f"Distinct MSA/company location candidates: {len(presence):,}")
    print(f"Output: {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
