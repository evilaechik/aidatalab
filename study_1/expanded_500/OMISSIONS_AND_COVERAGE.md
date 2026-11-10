# Expanded roster coverage and exceptions

**Later evidence — November 10, 2026:** the [linked-data schema](../linked_msa/SCHEMA.md) documents partial office/function observations and a new Block HQ-role conflict. Block's publisher point stays in this frozen selected-point benchmark, while the broader study flags that point as contested. The bounded-screen findings below describe the November 9 collection, not the subsequent review. See [the current handoff](../linked_msa/TRAINING_HANDOFF.md) before reusing outcomes or coverage fields.

All 500 companies were collected. The covered training roster is 498: Lululemon
and Autoliv retain their original unresolved HQ-role exclusions. Their 100 audit
cells remain null, and neither company enters any supervised-training metro.
See the [exclusion evidence](#excluded-unknowns).

There are 435 covered selected HQ points in the 50-MSA frame and 63 outside.
Outside-frame firms remain in the denominator and contribute selected-point
zeros to each selected metro. The geographic assignment preserves other MSAs
and micropolitan areas. A zero establishes no absence of offices or co-HQs.

The [500-row policy ledger](tables/firm_coverage_and_omissions.csv) records each
decision. The full-500 per-metro marginal bounds are the covered count through
covered count + 2; their upper endpoints cannot occur simultaneously everywhere.
Kraft Heinz's known additional Pittsburgh HQ remains a sensitivity only, adding
one to that scorecard count. Additional co-HQs were not comprehensively collected.

## Source reconciliation

- All 500 publisher map IDs match the ranking roster one-to-one; the identity
  audit preserves reviewed name changes rather than replacing historical firms.
- Murphy USA has displayed ranking rank 231 and map rank 230. Ingredion has
  displayed ranking rank 498 and map rank 499. Names and revenues support their
  identities; the two source disagreements are recorded without changing the
  primary HQ point or silently altering either source's rank.
- GuideWell's detailed industry description differs between the map and ranking.
  The ranking industry/sector is used consistently for company predictors; both
  source descriptions remain in the identity audit.
- Prologis is the only full-TIGER geography fallback, resolving its San Francisco
  waterfront point under the same July 2023 membership. All original 100 company
  CBSA assignments remain unchanged.
- Later SEC metadata identifies current addresses and filing routes. It does not
  independently establish historical HQ roles, and it did not reinstate the
  original two excluded companies. No additional unresolved role conflict was
  identified by this bounded screen; that is not an exhaustive HQ-role audit.

Four unique regional factor cells remain null: Hartford/Bridgeport growth,
Sacramento management intensity and Las Vegas legal relative wage. They repeat
as 1,992 company–metro numeric nulls. Primary company characteristics are complete;
the optional financial fields remain outside the primary feature allowlist.

The original 100-firm labels and primary company fields are preserved exactly
for overlapping firms. Census inclusion probabilities and design weights are now
one for every roster firm; they do not correct the two coverage exclusions.

## Excluded unknowns

| Firm | What remains unresolved | Supports absence? | Primary treatment |
| --- | --- | --- | --- |
| Lululemon athletica | Publisher point Sumner WA is a distribution location; corporate HQ Vancouver Canada in 2025 filing. Qualifying US HQ role unresolved; exclude coverage outlier rather than infer US absence. [Official source](https://www.sec.gov/Archives/edgar/data/1397187/000139718725000013/lulu-20250202.htm) | No: neither general-office absence nor selected-HQ absence inferred | All 50 labels null; excluded everywhere |
| Autoliv | Publisher point Auburn Hills MI conflicts with principal executive offices Stockholm Sweden in filing issued 2025. US regional HQ role not established in bounded official-source search; exclude coverage outlier. [Official source](https://www.sec.gov/Archives/edgar/data/1034670/000095017025023852/alv-20241231.htm) | No: neither general-office absence nor selected-HQ absence inferred | All 50 labels null; excluded everywhere |

These are coverage outliers, not statistically extreme companies. Additional
bounded official-source searches did not resolve the relevant US HQ role. The
underlying publisher locations remain in the audit record; they are not accepted
as HQ training positives or converted into 50 zeros. No replacement firms were
chosen after seeing HQ outcomes. Both excluded firms are publisher-public cases;
Autoliv is Motor Vehicles & Parts and lululemon Apparel. All 21 sectors remain
represented after exclusion. Compare strata in
[cohort_coverage_summary.csv](tables/cohort_coverage_summary.csv).

