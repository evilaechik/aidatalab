#!/usr/bin/env python3
"""Prepare the three-feature HQ comparison offline; no fitting or network calls."""
import hashlib
import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import study_integrity

STUDY = Path(__file__).resolve().parents[1]
ROOT = STUDY / 'feature_refinement'
BASE = STUDY / 'expanded_500'
LINKED = STUDY / 'linked_msa'
ADDITIONS = {
    'cbp_management_employment_share_2023': ('cbp_employment_share', '55', 'fraction'),
    'bds_establishment_entry_rate_2023': ('bds_estabs_entry_rate', '00', 'percent'),
    'bds_establishment_exit_rate_2023': ('bds_estabs_exit_rate', '00', 'percent'),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def table(root, name):
    return pd.read_csv(root / 'tables' / (name + '.csv'), dtype={'cbsa': str, 'company_id': str})


def build():
    for name in ['config', 'tables', 'reports', 'models', 'raw_archive']:
        (ROOT / name).mkdir(exist_ok=True, parents=True)
    frame = pd.read_csv(BASE / 'config/metro_frame.csv', dtype=str)
    # Compare actual county membership, not just matching metro titles/codes.
    official = pd.read_excel(ROOT / 'raw_archive/omb_cbsa_counties_july_2023.xlsx', header=2, dtype=str)
    official['county_fips'] = official['FIPS State Code'].str.zfill(2) + official['FIPS County Code'].str.zfill(3)
    official = official.rename(columns={'CBSA Code': 'cbsa'})
    cbp = pd.read_csv(ROOT / 'raw_archive/cbp_msa_county_reference_2022_2023.txt', dtype=str, encoding='cp1252')
    cbp['county_fips'] = cbp.fipstate + cbp.fipscty
    audits, crosswalk = [], []
    for cbsa in frame.cbsa:
        expected = set(official.loc[official.cbsa.eq(cbsa), 'county_fips'])
        source = cbp[cbp.msa.eq(cbsa)]
        actual = set(source.loc[source.fipscty.ne('999'), 'county_fips'])
        statewide = source[source.fipscty.eq('999')]
        assert expected and actual == expected, (cbsa, actual ^ expected)
        # Providence's extra 44999 code is statewide, not an extra county.
        # Every county in that state must belong to the metro for acceptance.
        for state in statewide.fipstate:
            all_state = set(official.loc[official['FIPS State Code'].eq(state), 'county_fips'])
            assert all_state and all_state <= expected, (cbsa, state)
        note = 'physical_counties_match; statewide code covers a state wholly inside this MSA' if len(statewide) else 'county_membership_exact_match'
        for program, evidence in [('CBP_2023', 'GEO_CBP_REFERENCE'), ('BDS_2023', 'GEO_BDS_2023_RELEASE;GEO_BDS_2022_RELEASE')]:
            audits.append(dict(cbsa=cbsa, program=program, frame_vintage='OMB July 2023', accepted=1,
                               decision=note if program.startswith('CBP') else 'official_release_documents_TIGER2023_and_prior_July2023_adoption',
                               frame_county_n=len(expected), evidence_ids=evidence))
        crosswalk.extend(dict(cbsa=cbsa, county_fips=fips) for fips in sorted(expected))
    pd.DataFrame(audits).to_csv(ROOT / 'reports/geography_audit.csv', index=False)
    pd.DataFrame(crosswalk).to_csv(ROOT / 'tables/frame_county_membership_2023.csv', index=False)
    sources = [
        ('GEO_CBP_REFERENCE', 'cbp_msa_county_reference_2022_2023.txt', 'https://www2.census.gov/programs-surveys/cbp/technical-documentation/reference/metro-area-geography-reference/msa_county_reference22.txt', 'Official 2022-2023 CBP county-to-MSA reference; physical counties compared with frame'),
        ('GEO_OMB_2023', 'omb_cbsa_counties_july_2023.xlsx', 'https://www2.census.gov/programs-surveys/metro-micro/geographies/reference-files/2023/delineation-files/list1_2023.xlsx', 'Reused official July 2023 delineation payload from existing workspace'),
        ('GEO_BDS_2023_RELEASE', 'bds2023-release-note.pdf', 'https://www2.census.gov/programs-surveys/bds/updates/bds2023-release-note.pdf', '2023 BDS extends vintage-consistent geography across US; specifies TIGER/Line 2023'),
        ('GEO_BDS_2022_RELEASE', 'bds2022-release-note.pdf', 'https://www2.census.gov/programs-surveys/bds/updates/bds2022-release-note.pdf', '2022 BDS adopts July 2023 MSA delineations and new Connecticut county-equivalents'),
    ]
    pd.DataFrame([dict(source_id=s, file=f, source_url=u, factual_note=n, sha256=sha(ROOT / 'raw_archive' / f), review_date='2026-11-10')
                  for s, f, u, n in sources]).to_csv(ROOT / 'raw_archive/geography_source_registry.csv', index=False)
    ind = pd.read_csv(LINKED / 'tables/metro_indicators.csv', dtype=str, keep_default_na=False)
    lineage, columns, dictionary = [], [], []
    for feature, (metric, sector, unit) in ADDITIONS.items():
        rows = ind[(ind.metric_id == metric) & (ind.reference_period == '2023') & (ind.sector_code == sector) & (ind.soc_code == '')].copy()
        assert len(rows) == 50 and rows.cbsa.is_unique and set(rows.cbsa) == set(frame.cbsa)
        values = pd.to_numeric(rows.value, errors='raise')
        assert values.notna().all() and np.isfinite(values).all()
        assert values.between(0, 1 if unit == 'fraction' else 100).all()
        columns.append(pd.Series(values.to_numpy(), index=rows.cbsa, name=feature))
        for r in rows.itertuples():
            lineage.append(dict(cbsa=r.cbsa, feature=feature, metric_id=metric, reference_period='2023', sector_code=sector, soc_code='',
                                value=float(r.value), unit=unit, source_evidence_id=r.evidence_id, source_value_status=r.value_status,
                                geography_decision='accepted_documented_July2023_frame'))
        dictionary.append(dict(feature_name=feature, metric_id=metric, sector_code=sector, reference_period='2023', unit=unit,
                               transform='Identity; preserve fraction/percent units; fold-fitted scaling for regression',
                               scope='Whole-metro published industry/economy measure; not allocated to named firms'))
    extra = pd.concat(columns, axis=1).rename_axis('cbsa').reset_index()
    extra.to_csv(ROOT / 'tables/metro_refinement_features_2023.csv', index=False, float_format='%.12g')
    pd.DataFrame(lineage).to_csv(ROOT / 'tables/refinement_feature_lineage.csv', index=False, float_format='%.12g')
    pd.DataFrame(dictionary).to_csv(ROOT / 'tables/refinement_feature_dictionary.csv', index=False)
    names = ['training_aggregate_2025', 'training_development_2025', 'training_atlanta_2025',
             'training_company_metro_hq_2025', 'training_company_hq_development_2025', 'training_company_hq_atlanta_2025']
    for name in names:
        old = table(BASE, name)
        new = old.merge(extra, on='cbsa', how='left', sort=False, validate='many_to_one' if 'company_id' in old else 'one_to_one')
        assert len(new) == len(old)
        pd.testing.assert_frame_equal(old, new[old.columns])
        new.to_csv(ROOT / 'tables' / (name + '.csv'), index=False, float_format='%.12g')
    shutil.copyfile(BASE / 'tables/msa_split_assignments.csv', ROOT / 'tables/msa_split_assignments.csv')
    specs = {}
    for track, filename in [('A', 'feature_spec.json'), ('B', 'company_hq_feature_spec.json')]:
        old = json.loads((BASE / 'config' / filename).read_text())
        keys = ['target', 'primary_predictors', 'main_effect_predictors', 'categorical_predictors', 'prohibited_predictors']
        spec = {k:old[k] for k in keys if k in old}
        spec['primary_predictors'] = old['primary_predictors'] + list(ADDITIONS)
        if track == 'B':spec['main_effect_predictors'] = old['main_effect_predictors'] + list(ADDITIONS)
        spec.update(feature_set='R1', regional_predictor_n=34, added_predictors=list(ADDITIONS))
        save_json(ROOT / 'config' / filename, spec);specs[track] = spec
    original_plan = json.loads((BASE / 'config/training_plan.json').read_text())
    save_json(ROOT / 'config/training_plan.json', original_plan)
    save_json(ROOT / 'config/training_contract.json', dict(version=1, created='2026-11-10', eligible_company_n=498, roster_n=500,
               target_scope='Frozen 2025 publisher-selected HQ point; no office presence outcome', new_features=list(ADDITIONS),
               tracks={'A':dict(rows=50, development_rows=49, assessment_rows=1, predictors=34),
                       'B':dict(rows=24900, development_rows=24402, assessment_rows=498, predictors=42, main_effect_predictors=38)},
               reference='R0 expanded_500 unchanged artifacts; verify hashes before reuse',
               selection_rule='OOF count MAE, RMSE, R0 before R1 for remaining ties, then original model order; main-only diagnostic',
               geography_gate='passed: official county membership and BDS geography-vintage documentation',
               office_models=False, weighted_score=False, bespoke_tech_health_outcomes=False))
    paths = [p for folder in ['config', 'tables', 'raw_archive'] for p in sorted((ROOT / folder).rglob('*'))
             if p.is_file() and p.name != 'input_manifest.csv']
    paths += [STUDY / 'scripts' / p for p in ['build_feature_refinement.py', 'train_feature_refinement.py', 'verify_feature_refinement.py', 'train_hq_2025.py', 'study_integrity.py']]
    pd.DataFrame([dict(path=str(p.relative_to(STUDY)), sha256=sha(p)) for p in paths if p.exists()]).to_csv(ROOT / 'config/input_manifest.csv', index=False)
    print('Prepared 34/42-input tables; all 50 MSAs pass the geography gate.', flush=True)


if __name__ == '__main__':
    build()
