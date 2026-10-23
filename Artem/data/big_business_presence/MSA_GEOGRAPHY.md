# MSA geography rule

## Unit of analysis

The score uses **Metropolitan Statistical Areas (MSAs)**, identified by their
five-digit Core Based Statistical Area (CBSA) codes. It does not use city
limits, counties alone, or Combined Statistical Areas (CSAs).

For example, an address in Alpharetta or Marietta belongs to the
Atlanta-Sandy Springs-Roswell MSA (CBSA `12060`), but it is not a City of
Atlanta office. The major-company score is metro-wide; a separate City of
Atlanta analysis must use municipal boundaries and a different field.

## How an address is assigned

1. The Census Geocoder matches a street address and returns its county FIPS
   code.
2. `metro_county_crosswalk_2023.csv` maps that county to the 2023 Census/OMB
   MSA to which it belongs.
3. The company-location record receives that MSA code, or remains unmatched.

MSAs are groups of whole counties. The county crosswalk is therefore the
correct official boundary rule for the score and avoids ambiguous
point-in-polygon behavior near a county border. No coordinate reference system
transformation is needed for this county-code workflow.

## Vintage and source

The project uses the Census Bureau's July 2023 CBSA delineation List 1, the
same vintage used in the public BDS comparison inputs. The Census describes a
CBSA as a core plus adjacent counties connected through social and economic
integration, including commuting ties. The selected roster contains 200 MSAs
ranked by 2023 Census BDS establishments unless the team supplies a custom MSA
roster.

If later analysis needs a map, use the matching 2023 Census TIGER/Line CBSA
shapefile and retain its source vintage. Do not substitute a city polygon for
the MSA score.
