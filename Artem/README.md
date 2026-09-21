# Artem - Business Competitiveness Workspace

This folder contains Artem's attributable work for the Invest Atlanta Business Competitiveness track.

## Project question

Where is Atlanta lagging in attracting and retaining major businesses, and which incentives or place-based interventions should Invest Atlanta consider?

## What is currently available

- 2025 Atlanta business-license records: business location and industry signals.
- Historical Invest Atlanta development records: incentives, investment, jobs, and industry.
- 2025 tax parcels: property, valuation, zoning, neighborhood, and NPU attributes.
- Publicly owned properties: potential sites and place-based characteristics.

## Fortune 100 presence screen

The reusable Fortune 100 Atlanta-presence dataset lives in [`data/`](data/README.md).

- [`fortune_100_atlanta_presence_2025.csv`](data/fortune_100_atlanta_presence_2025.csv) has one row per company and a four-bucket presence classification.
- [`verified_location_sources.csv`](data/verified_location_sources.csv) stores direct company-source checks completed so far.

Use `has_atlanta_office` for City of Atlanta findings. Keep `has_atlanta_metro_office` separate: those companies are regional context, not automatically within Invest Atlanta's formal jurisdiction.

## Current limitation

The provided files do not yet include the BLS industry-growth/loss series or comparable-region incentive data named in the project brief. They are needed to make defensible claims about Atlanta's competitiveness relative to peer metros.

## First analysis direction

Create an industry-by-place opportunity map that identifies Atlanta areas with:

1. a concentration of relevant businesses;
2. evidence of prior investment or job creation;
3. suitable commercial parcels or publicly owned sites; and
4. a clear gap in available support.

This can become the Atlanta-side evidence base before adding peer-metro and BLS comparisons.
