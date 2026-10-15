# Public research datasets

This folder contains only public, shareable research artifacts. It does **not** contain restricted Invest Atlanta records, including the separately held business-license file.

## Peer-metro research

- `peer_metro_baseline_2025.csv`: annual QCEW/Bureau of Economic Analysis peer baseline for Atlanta, Austin, and Charlotte.
- `peer_metro_regression/`: Q4 county employment-growth panel, sector trends, and a reproducible exploratory-regression output.
- `peer_metro_decision_tracker_public.csv`: source-linked public announcements of office, headquarters, R&D, manufacturing, and operations decisions. It distinguishes City and metro locations and records announcements rather than treating them as delivered outcomes.

See [`../PUBLIC_DATA_CATALOG.md`](../PUBLIC_DATA_CATALOG.md) for a description of each dataset, its intended use, and limitations.

# Fortune 100 Atlanta presence screen

`fortune_100_atlanta_presence_2025.csv` is a one-row-per-company research screen for the 2025 Fortune 100 list.

## Buckets

| `screening_bucket` | Meaning |
| --- | --- |
| `has_atlanta_office` | A corporate, regional, sales, technology, finance, or administrative office inside City of Atlanta limits. |
| `has_atlanta_metro_office` | The comparable office is in metro Atlanta but outside City of Atlanta, such as Sandy Springs, Alpharetta, Marietta, Kennesaw, Norcross, or Duluth. |
| `store_or_distribution` | The current screen found retail, airport, distribution, processing, or other operational presence but no material local office claim. |
| `no_verified_material_presence` | No material metro corporate, office, retail, or logistics presence was identified during this screen. This is not proof that no employee, agent, vendor, or remote worker exists. |

## Evidence standard

This is a **research screen**, not a final directory. `company_source_checked` means the location was confirmed through a company-owned location/careers/contact page. `screened_source_needed` means the finding should receive a direct official-location citation before it is used as a final published count.

The distinction matters for Invest Atlanta: its formal jurisdiction is City of Atlanta. Metro firms are useful regional context, but should not be reported as City of Atlanta office wins.

## Refresh workflow

1. Start with rows labeled `screened_source_needed`.
2. Add a direct company location, careers, press-release, or filing source.
3. Confirm the municipality from the street address rather than relying on an Atlanta mailing address.
4. Update `evidence_status` to `company_source_checked` and replace the note with the verified address.

## Source basis

- Fortune 500 Companies 2025 dataset (50Pros/Kaggle), used for the rank and company universe.
- Company-owned location and careers pages used for the currently checked rows.
