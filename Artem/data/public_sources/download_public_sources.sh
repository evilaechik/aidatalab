#!/usr/bin/env bash
set -euo pipefail

SOURCE_ROOT="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$SOURCE_ROOT/qcew" "$SOURCE_ROOT/lodes" "$SOURCE_ROOT/boundaries" "$SOURCE_ROOT/transit"

# BLS QCEW area slices: all published industries for each core-metro county and Q4 year.
# County FIPS: Fulton 13121, DeKalb 13089, Cobb 13067, Gwinnett 13135, Clayton 13063,
# Forsyth 13117, Henry 13151, Douglas 13097, Rockdale 13247, Cherokee 13057.
for year in 2023 2024 2025; do
  for county in 13121 13089 13067 13135 13063 13117 13151 13097 13247 13057; do
    curl --fail --location --retry 3 --silent --show-error \
      "https://data.bls.gov/cew/data/api/${year}/4/area/${county}.csv" \
      --output "$SOURCE_ROOT/qcew/qcew_${year}_q4_${county}.csv"
  done
done

# Census LEHD LODES 8: 2023 is the latest complete Georgia vintage in the public file directory.
for type in wac rac; do
  file="ga_${type}_S000_JT00_2023.csv.gz"
  curl --fail --location --retry 3 --silent --show-error \
    "https://lehd.ces.census.gov/data/lodes/LODES8/ga/${type}/${file}" \
    --output "$SOURCE_ROOT/lodes/$file"
done
curl --fail --location --retry 3 --silent --show-error \
  "https://lehd.ces.census.gov/data/lodes/LODES8/ga/od/ga_od_main_JT00_2023.csv.gz" \
  --output "$SOURCE_ROOT/lodes/ga_od_main_JT00_2023.csv.gz"

# Census places provide an authoritative city boundary; filter this Georgia layer to Atlanta during analysis.
curl --fail --location --retry 3 --silent --show-error \
  "https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_13_place_500k.zip" \
  --output "$SOURCE_ROOT/boundaries/cb_2024_13_place_500k.zip"

# MARTA publishes a periodically refreshed GTFS feed. Keep the downloaded date in analysis metadata.
curl --fail --location --retry 3 --silent --show-error \
  "https://itsmarta.com/google_transit_feed/google_transit.zip" \
  --output "$SOURCE_ROOT/transit/marta_gtfs.zip"

printf 'Public-source downloads completed in %s\n' "$SOURCE_ROOT"
