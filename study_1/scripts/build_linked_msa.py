#!/usr/bin/env python3
"""Build six linked descriptive tables offline. No fitting or network calls."""
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
import study_integrity

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'study_1/expanded_500'
OUT = ROOT / 'study_1/linked_msa'
SOURCE_DATA = ROOT / 'study_1/source_data'
RAW = OUT / 'raw_archive'
DATE = '2026-11-10'
FUNCTIONS = {
    'headquarters': 'Reported corporate headquarters or principal executive office; additional co-HQs do not alter the frozen publisher target.',
    'regional_divisional_management': 'Explicit regional, divisional or subsidiary headquarters; not inferred from industry.',
    'research_development': 'Explicit research, R&D or product development at the named locality.',
    'engineering': 'Explicit engineering at the named locality.',
    'finance_shared_services': 'Internal finance, accounting or shared-service work; financial-sector membership alone is insufficient.',
    'administration_back_office': 'Administrative, claims, corporate support, business operations or IT operations; subfunctions remain in archive.',
    'sales_client_services': 'Corporate sales, marketing, consulting or customer service; not retail outlets.',
    'office_function_unspecified': 'Office evidence without a defensible specific function; never imputed from industry.'}
KEYS = {'metro_indicators': ['cbsa','metric_id','reference_period','sector_code','soc_code'],
        'company_locations': ['location_id'], 'location_functions': ['function_observation_id'],
        'company_msa_coverage': ['company_id','cbsa','reference_year'],
        'metric_dictionary': ['metric_id'], 'msa_scorecard': ['cbsa']}


def read(path, **kwargs):
    return pd.read_csv(path, dtype=str, keep_default_na=False, **kwargs)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, allow_nan=False)+'\n')


def number(value, flag=''):
    if str(flag).strip() in {'D','N','S','X','(D)','(NA)'}:
        return np.nan, 'suppressed_or_unavailable'
    try:
        val = float(value)
        return (val, 'published_flagged' if str(flag).strip() else 'published') if np.isfinite(val) else (np.nan,'unavailable')
    except (ValueError, TypeError):
        return np.nan, 'unavailable'


def build():
    for p in [OUT/'tables', OUT/'reports', OUT/'config', RAW]:
        p.mkdir(parents=True, exist_ok=True)
    frame = read(BASE/'config/metro_frame.csv')
    cohort = read(BASE/'tables/company_cohort_500.csv')
    identities = read(BASE/'tables/company_identity_matches.csv').set_index('company_id')
    policy = read(BASE/'tables/firm_coverage_and_omissions.csv').set_index('company_id')
    sectors = cohort.set_index('company_id').company_broad_industry.to_dict()
    metas, evidence, indicators, definitions = [], [], [], {}

    def define(key, definition, unit, program, block, role='descriptive_candidate', formula='Published source value', scope='MSA economy; not Fortune-500-specific'):
        definitions.setdefault(key, dict(metric_id=key, definition=definition, unit=unit, source_program=program,
                                         block=block, analytical_role=role, formula=formula, population_scope=scope,
                                         missing_policy='Keep null; no suppression, absence, site count or job allocation imputation.',
                                         eligible_existing_hq_predictor=int(role=='existing_frozen_predictor'),
                                         selected_for_new_model=0))

    def ev(eid, sid, url, local_path, selector, period, summary=''):
        evidence.append(dict(evidence_id=eid, source_id=sid, source_url=url, local_path=local_path,
                             row_selector=selector, reference_period=period, access_date=DATE, factual_summary=summary))
        return eid

    def indicator(cbsa, key, period, value, status, eid, sector='', soc='', flag='', geography='native_program_cbsa_not_independently_rebuilt'):
        indicators.append(dict(cbsa=cbsa, metric_id=key, reference_period=str(period), reference_year=int(str(period)[:4]),
                               sector_code=sector, soc_code=soc, value=value, value_status=status,
                               source_flag=flag, geography_status=geography, evidence_id=eid))

    # Existing features retain their exact values and original role; new metrics
    # are descriptive candidates, not an automatically enlarged predictor list.
    fd = read(BASE/'tables/feature_dictionary.csv').set_index('feature_name')
    features = read(BASE/'tables/metro_features_2024.csv')
    source_registry = read(BASE/'tables/economic_source_registry.csv')
    for row in features.to_dict('records'):
        for key, d in fd.iterrows():
            if key not in row: continue
            define(key, d.definition, d.unit, d.source_program, d.block, 'existing_frozen_predictor', d.formula)
            period = '2023' if key.startswith('cbp_') else '2024'
            eid = ev(f'EV_FEATURE_{row["cbsa"]}_{key}', 'INHERITED_FEATURES', '', 'study_1/expanded_500/tables/metro_features_2024.csv',
                     f'cbsa={row["cbsa"]};column={key}; source program={d.source_program}', d.reference_period,
                     'Same normalized predictor as frozen HQ experiment. Source routes retained in inherited_economic_source_registry.csv.')
            val,status = number(row[key])
            indicator(row['cbsa'], key, period, val, status, eid, geography='inherited_documented_geography')
    # Human-readable levels and margins of error for the same general factors.
    econ = read(BASE/'tables/metro_economic_inputs_2024.csv')
    for row in econ.to_dict('records'):
        for key in econ.columns:
            if key in fd.index or key in {'cbsa','metro_name','comparison_role','priority_peer','boundary_vintage','economic_reference_year','qcew_ownership'}: continue
            if not any(x in key for x in ['_employment_2024','_establishments_2024','_pay_2024','gdp_2024','population_2024','moe90_2024','income_2024','rent_2024']): continue
            unit = 'persons' if 'population' in key else 'jobs' if 'employment' in key else 'establishments' if 'establishments' in key else 'thousand USD' if 'gdp' in key else 'fraction' if 'share' in key else 'USD per month' if 'rent' in key else 'USD'
            define(key, key.replace('_',' '), unit, 'Inherited general economic input', 'general_metro_levels')
            eid=ev(f'EV_LEVEL_{row["cbsa"]}_{key}', 'INHERITED_ECONOMIC_LEVELS', '', 'study_1/expanded_500/tables/metro_economic_inputs_2024.csv', f'cbsa={row["cbsa"]};column={key}', '2024')
            val,status=number(row[key]);indicator(row['cbsa'],key,'2024',val,status,eid,geography='inherited_documented_geography')
    # Consistent broad-sector detail, all industries equally; no bespoke tech or
    # healthcare occupations/NAICS extensions and no 2025 ownership mismatch.
    sector_names = {}
    for folder in sorted(SOURCE_DATA.glob('*_data')):
        manifest_path=folder/'download_manifest.csv'
        if not manifest_path.exists(): continue
        manifest=read(manifest_path)
        for filename in ['cbp_employment_2023.csv','qcew_annual_2023_2025.csv','bds_metro_2023.csv']:
            path=folder/filename
            if not path.exists(): continue
            data=read(path); cbsa=data.metro_cbsa.iloc[0]
            if cbsa not in set(frame.cbsa): continue
            info=manifest[manifest.file==filename].iloc[0]
            sid='SRC_'+folder.name+'_'+filename.removesuffix('.csv')
            metas.append(dict(source_id=sid, program=info.dataset, local_path=str(path.relative_to(ROOT)),
                              cbsa=cbsa,
                              source_urls=info.source_urls, source_vintage=info.source_vintage,
                              original_access_date=info.verified_date, reused_date=DATE, sha256=sha(path), method=info.method))
            if filename.startswith('cbp_'):
                data=data[(data.EMPSZES=='001')&(data.LFO=='001')]
                total=number(data[data.NAICS2017=='00'].EMP.iloc[0],data[data.NAICS2017=='00'].EMP_F.iloc[0])[0]
                for r in data.to_dict('records'):
                    sector=r['NAICS2017']; sector_names[sector]=r['NAICS2017_LABEL']
                    eid=ev(f'EV_CBP_{cbsa}_{sector}',sid,info.source_urls,str(path.relative_to(ROOT)),f'NAICS2017={sector};EMPSZES=001;LFO=001','2023')
                    vals={}
                    for col,key,unit in [('EMP','cbp_employment','jobs'),('ESTAB','cbp_establishments','establishments'),('PAYANN','cbp_annual_payroll','USD')]:
                        val,status=number(r[col],r.get(col+'_F',''));val=val*1000 if col=='PAYANN' else val; vals[col]=val
                        source_flag=';'.join(f'{c}={r[c]}' for c in [col+'_F',col+'_N_F',col+'_N'] if r.get(c,'')!='')
                        if status=='published' and r.get(col+'_N_F',''):status='published_with_noise_metadata'
                        define(key, f'CBP {col}: all establishment sizes and legal forms; NAICS 2017 broad sectors',unit,'Census CBP','broad_sector_structure')
                        indicator(cbsa,key,'2023',val,status,eid,sector=sector,flag=source_flag)
                    for key,val,unit,formula in [('cbp_employment_share', vals['EMP']/total if total>0 else np.nan,'fraction','Sector EMP / total EMP; totals never summed with components'),
                                                  ('cbp_annual_pay_per_job',vals['PAYANN']/vals['EMP'] if vals['EMP']>0 else np.nan,'USD per job','PAYANN × 1000 / EMP; annual payroll / March employment, not mean employee salary'),
                                                  ('cbp_jobs_per_establishment',vals['EMP']/vals['ESTAB'] if vals['ESTAB']>0 else np.nan,'jobs per establishment','EMP / ESTAB')]:
                        define(key,key.replace('_',' '),unit,'Census CBP','broad_sector_structure',formula=formula)
                        indicator(cbsa,key,'2023',val,'derived' if np.isfinite(val) else 'unavailable',eid,sector=sector)
            elif filename.startswith('qcew_'):
                data=data[(data.own_code=='5')&data.year.isin(['2023','2024'])&((data.agglvl_code=='44')|(data.industry_code=='10'))]
                # Explicit missing rows for the same broad-sector universe in
                # every metro; a missing source row never becomes a zero.
                expected=pd.MultiIndex.from_product([['2023','2024'],['10']+[k for k in sector_names if k!='00']],names=['year','industry_code'])
                data=data.set_index(['year','industry_code']).reindex(expected).reset_index().fillna('')
                for r in data.to_dict('records'):
                    sector='00' if r['industry_code']=='10' else r['industry_code']; period=r['year']
                    eid=ev(f'EV_QCEW_{cbsa}_{period}_{sector}',sid,info.source_urls,str(path.relative_to(ROOT)),f'year={period};own_code=5;industry_code={r["industry_code"]}',period)
                    for col,key,unit in [('annual_avg_emplvl','qcew_private_employment','jobs'),('annual_avg_estabs','qcew_private_establishments','establishments'),('total_annual_wages','qcew_private_annual_payroll','USD'),('avg_annual_pay','qcew_private_annual_pay','USD per job'),('lq_annual_avg_emplvl','qcew_private_employment_lq','ratio to US')]:
                        flag=r.get('lq_disclosure_code','') if col.startswith('lq_') else r['disclosure_code']
                        # BLS Q&A #13: N suppresses employment/wages, while
                        # establishment counts remain disclosed in modern files.
                        val,status=number(r[col],'' if col=='annual_avg_estabs' else flag)
                        if col=='annual_avg_estabs' and flag=='N':status='published_establishment_other_fields_suppressed'
                        if not r['own_code']:status='not_published_source_row'
                        define(key,key.replace('_',' '),unit,'BLS QCEW','broad_sector_structure',scope='Private covered employment; not named company offices')
                        indicator(cbsa,key,period,val,status,eid,sector=sector,flag=flag)
            else:
                for r in data.to_dict('records'):
                    sector=r['NAICS'];eid=ev(f'EV_BDS_{cbsa}_{sector}',sid,info.source_urls,str(path.relative_to(ROOT)),f'YEAR=2023;NAICS={sector}','2023')
                    sector_names.setdefault(sector,r['NAICS_LABEL'])
                    for col,unit in [('EMP','jobs'),('FIRM','firms with metro activity'),('ESTAB','establishments'),('ESTABS_ENTRY','establishments'),('ESTABS_EXIT','establishments'),('ESTABS_ENTRY_RATE','percent'),('ESTABS_EXIT_RATE','percent'),('JOB_CREATION','jobs'),('JOB_DESTRUCTION','jobs'),('NET_JOB_CREATION','jobs'),('NET_JOB_CREATION_RATE','percent')]:
                        key='bds_'+col.lower();val,status=number(r[col],r.get(col+'_F',''))
                        define(key,f'BDS {col}; total or broad industry, dynamics not company relocation',unit,'Census BDS','general_business_dynamics')
                        indicator(cbsa,key,'2023',val,status,eid,sector=sector,flag=r.get(col+'_F',''))
    # Same six general occupation groups plus all occupations, with uncertainty.
    occupations=read(BASE/'tables/metro_occupation_inputs_2024.csv')
    occcols={'occupation_employment':'jobs','occupation_jobs_per_1000':'jobs per 1000 all-occupation jobs',
             'occupation_annual_mean_wage_usd':'USD','occupation_annual_median_wage_usd':'USD',
             'occupation_mean_wage_us_relative':'ratio to US occupation mean',
             'employment_relative_standard_error_percent':'percent','mean_wage_relative_standard_error_percent':'percent'}
    for r in occupations.to_dict('records'):
        eid=ev(f'EV_OEWS_{r["cbsa"]}_{r["soc"]}','SRC_OEWS_2024',r['source_url'],'study_1/expanded_500/tables/metro_occupation_inputs_2024.csv',f'cbsa={r["cbsa"]};soc={r["soc"]}',r['reference_period'])
        for col,unit in occcols.items():
            key='oews_'+col;define(key,col.replace('_',' '),unit,'BLS OEWS','general_occupation_mix')
            val,status=number(r[col]);indicator(r['cbsa'],key,r['reference_period'],val,status,eid,soc=r['soc'],geography='inherited_OEWS_native_geography')
    indicator_table=pd.DataFrame(indicators)
    # Reuse all 500 publisher points, flagging the two existing HQ-role exclusions.
    locs=[]; funcs=[]

    def function(loc_id,company,code,year,date,eid,status,origin):
        funcs.append(dict(function_observation_id=f'FUN_{len(funcs)+1:05d}',location_id=loc_id,company_id=company,
                          function_code=code,reference_year=int(year),reference_date=date,evidence_status=status,
                          date_basis='publisher_edition' if origin=='frozen_hq_benchmark' else 'source_fiscal_period_annotation_not_independent_occupancy_date',
                          observation_origin=origin,evidence_id=eid,local_employment=np.nan,
                          office_area_sqft=np.nan,physical_site_count=np.nan))

    for r in cohort.to_dict('records'):
        key=r['company_id']; i=identities.loc[key]; lid='LOC_HQ_'+key; eid='EV_HQ_'+key
        accepted=policy.loc[key,'eligible_primary']=='1'
        disputed=(key=='f2025_179')  # Block's filing explicitly designates no HQ.
        ev(eid,'SRC_PUBLISHER_2025',r['publisher_source_url'],'study_1/expanded_500/tables/company_cohort_500.csv',f'company_id={key}','2025','Frozen publisher selected-point observation; role exclusions retained.')
        locs.append(dict(location_id=lid,company_id=key,location_label=r['publisher_reported_location'],city='',state='',country='US',cbsa=r['publisher_hq_cbsa'],
                         inside_metro_frame=int(r['publisher_hq_cbsa'] in set(frame.cbsa)),location_unit='publisher_selected_point',latitude=i['latitude'],longitude=i['longitude'],
                         geography_status='inherited_2023_polygon_assignment',hq_benchmark_point=1,hq_benchmark_eligible=int(accepted),
                         qualifying_corporate_presence=int(accepted and not disputed),
                         presence_status='publisher_hq_role_contested' if disputed else 'publisher_reported_hq' if accepted else 'hq_role_unresolved',
                         evidence_id=eid,geography_evidence_id='GEO_PUBLISHER_POINT_2023'))
        if accepted:function(lid,key,'headquarters',2025,'',eid,'publisher_reported_hq_role_contested' if disputed else 'publisher_reported_hq_role','frozen_hq_benchmark')
    facts=read(RAW/'reviewed_office_facts.csv')
    places=read(RAW/'reviewed_place_cbsa_crosswalk.csv').set_index(['city','state'])
    extra_seen={}
    for r in facts.to_dict('records'):
        p=places.loc[(r['city'],r['state'])];group=(r['company_id'],r['city'],r['state']);lid='LOC_CITY_'+hashlib.sha256('|'.join(group).encode()).hexdigest()[:12]
        if group not in extra_seen:
            locs.append(dict(location_id=lid,company_id=r['company_id'],location_label=r['city']+', '+r['state'],city=r['city'],state=r['state'],country='US',cbsa=p.cbsa,
                             inside_metro_frame=int(p.cbsa in set(frame.cbsa)),location_unit='city_function_cluster',latitude=p.latitude,longitude=p.longitude,
                             geography_status=p.geography_status,hq_benchmark_point=0,hq_benchmark_eligible=0,qualifying_corporate_presence=1,
                             presence_status='primary_source_reported_office_or_function',evidence_id=r['evidence_id'],geography_evidence_id=p.geography_evidence_id))
            extra_seen[group]=lid
        ev(r['evidence_id'],r['source_id'],r['source_url'],'raw_archive/reviewed_office_facts.csv',f'evidence_id={r["evidence_id"]};indexed source line={r["source_line"]}',r['reference_date'],r['claim_summary'])
        for code in r['function_codes'].split(';'):
            function(lid,r['company_id'],code,r['reference_year'],r['reference_date'],r['evidence_id'],r['evidence_status'],'new_primary_source_screen')
    loc_table=pd.DataFrame(locs);fun_table=pd.DataFrame(funcs)
    # Sparse, explicitly reported location measurements remain attached to the
    # locality observation. Never repeat them across functional roles or sum
    # unevenly disclosed local jobs/space into an apparent metro total.
    for col in ['local_employment','employment_reference_year','office_area_sqft','area_reference_year']:
        loc_table[col]=np.nan
    for col in ['employment_status','employment_scope','employment_evidence_id','area_status','area_scope','area_evidence_id']:
        loc_table[col]=''
    for r in facts.to_dict('records'):
        lid=extra_seen[(r['company_id'],r['city'],r['state'])]
        for measure,prefix in [('local_employment','employment'),('office_area_sqft','area')]:
            if not r.get(measure,''):continue
            mask=loc_table.location_id.eq(lid)
            loc_table.loc[mask,measure]=float(r[measure])
            loc_table.loc[mask,prefix+'_reference_year']=int(r['reference_year'])
            for suffix in ['status','scope']:loc_table.loc[mask,prefix+'_'+suffix]=r.get(prefix+'_'+suffix,'reported')
            loc_table.loc[mask,prefix+'_evidence_id']=r['evidence_id']
    # Do not turn two positive observations or a functional role into two sites.
    observed=fun_table.merge(loc_table[['location_id','cbsa','qualifying_corporate_presence']],on='location_id')
    observed=observed[observed.qualifying_corporate_presence==1]
    frame_observed=observed[observed.cbsa.isin(frame.cbsa)]
    positives=set(zip(frame_observed.company_id,frame_observed.cbsa,frame_observed.reference_year))
    detailed=frame_observed[~frame_observed.function_code.isin(['headquarters','office_function_unspecified'])]
    detailed_keys=set(zip(detailed.company_id,detailed.cbsa,detailed.reference_year))
    new=frame_observed[frame_observed.observation_origin=='new_primary_source_screen']
    new_keys=set(zip(new.company_id,new.cbsa,new.reference_year))
    attempts=read(RAW/'collection_attempts.csv').set_index('company_id')
    coverage=[]
    for company in cohort.company_id:
        for cbsa in frame.cbsa:
            for year in [2024,2025]:
                k=(company,cbsa,year);hq=(1 if policy.loc[company,'publisher_hq_cbsa']==cbsa else 0) if year==2025 and policy.loc[company,'eligible_primary']=='1' else np.nan
                coverage.append(dict(company_id=company,cbsa=cbsa,reference_year=year,
                                     reported_hq_benchmark=hq,corporate_presence=1 if k in positives else np.nan,
                                     presence_status='reported_positive' if k in positives else 'unknown_not_enumerated',
                                     specific_function_observed=int(k in detailed_keys),
                                     new_primary_source_observation=int(k in new_keys),
                                     office_absence_verified=0,office_census_complete=0,
                                     source_screen_attempted=1,usable_indexed_excerpt=int(attempts.loc[company,'source_lines_returned'])>0,
                                     evidence_id='EV_SCREEN_'+company))
    cov_table=pd.DataFrame(coverage)
    for company,r in attempts.iterrows():
        ev('EV_SCREEN_'+company,r.source_id,r.source_url,'raw_archive/collection_attempts.csv',f'company_id={company}',DATE,'Uniform source screen; completeness remains unknown for offices.')
    targets=read(BASE/'tables/metro_hq_targets_2025.csv').set_index('cbsa')
    rows=[]
    for metro in frame.to_dict('records'):
        cbsa=metro['cbsa'];hq=int(targets.loc[cbsa,'reported_hq_count_2025']);jobs=float(econ.set_index('cbsa').loc[cbsa,'msa_private_employment_2024'])
        row=dict(cbsa=cbsa,metro_name=metro['metro_name'],boundary_vintage='OMB July 2023',reported_hq_count_2025=hq,hq_eligible_company_n=498,
                 office_roster_company_n=500,reported_hq_per_million_private_jobs_2024=hq/jobs*1e6,
                 office_census_complete=0,weighted_score=np.nan,office_ranking_valid=0)
        for year in [2024,2025]:
            f=frame_observed[(frame_observed.cbsa==cbsa)&(frame_observed.reference_year==year)]
            n=f[f.observation_origin=='new_primary_source_screen'];specific=f[~f.function_code.isin(['headquarters','office_function_unspecified'])]
            # Empty observed sets are lower bound 0, not an asserted absence.
            row[f'reported_corporate_presence_{year}_firms_lower_bound']=f.company_id.nunique()
            row[f'new_source_documented_{year}_firms_lower_bound']=n.company_id.nunique()
            row[f'specific_function_{year}_firms_lower_bound']=specific.company_id.nunique()
            row[f'reported_corporate_presence_{year}_unknown_company_n']=500-f.company_id.nunique()
            row[f'reported_corporate_presence_{year}_observation_share']=f.company_id.nunique()/500
            for code in FUNCTIONS:
                row[f'{code}_{year}_firms_lower_bound']=f[f.function_code==code].company_id.nunique()
        # Corporate-management activity is cross-industry, not an industry-specific
        # outcome test. It remains separate from the named-company counts.
        for metric,period,sector,col in [('cbp_employment','2023','55','management_sector_employment_2023'),
                                          ('cbp_establishments','2023','55','management_sector_establishments_2023'),
                                          ('cbp_employment_share','2023','55','management_sector_employment_share_2023'),
                                          ('qcew_private_employment','2024','55','qcew_management_private_jobs_2024')]:
            value=indicator_table[(indicator_table.cbsa==cbsa)&(indicator_table.metric_id==metric)&(indicator_table.reference_period==period)&(indicator_table.sector_code==sector)]
            row[col]=value.value.iloc[0] if len(value)==1 else np.nan
        rows.append(row)
    score_table=pd.DataFrame(rows)
    for code,description in FUNCTIONS.items():
        define('function_'+code,description,'reported function','Primary company sources','company_functions','descriptive_observation',scope='Named company/locality, not whole sector')
    define('location_local_employment','Explicit reported employees at one locality/campus; approximate counts marked; not allocated across functions.',
           'reported employees','Primary company sources','company_locations','sparse_descriptive_measure',scope='Only the source-stated company/locality scope; no completeness claim')
    define('location_office_area_sqft','Explicit reported office square footage; separately disclosed sublet/available space excluded where stated.',
           'square feet','Primary company sources','company_locations','sparse_descriptive_measure',scope='Only the source-stated office footprint; not a metro office-space census')
    for col in score_table.columns:
        if col in {'cbsa','metro_name','boundary_vintage'}: continue
        define('scorecard_'+col,col.replace('_',' '),'fraction' if 'share' in col else 'jobs' if 'jobs' in col or 'employment' in col and 'share' not in col else 'count or flag',
               'Derived linked tables','scorecard','descriptive_scorecard',formula='Distinct company IDs per MSA and stated year; lower bounds only for office/functions; see SCHEMA.md')
    tables={'metro_indicators':indicator_table,'company_locations':loc_table,'location_functions':fun_table,
            'company_msa_coverage':cov_table,'metric_dictionary':pd.DataFrame(definitions.values()),'msa_scorecard':score_table}
    for name,data in tables.items():
        data.to_csv(OUT/'tables'/f'{name}.csv',index=False,float_format='%.12g')
    pd.DataFrame(metas).to_csv(RAW/'regional_source_registry.csv',index=False)
    source_registry.to_csv(RAW/'inherited_economic_source_registry.csv',index=False)
    pd.DataFrame([dict(source_id='METHOD_QCEW_DISCLOSURE',source_url='https://www.bls.gov/cew/questions-and-answers.htm',source_section='Q13; Q15; Q17',access_date=DATE,
                       factual_summary='For 2004 onward, establishment counts remain disclosed under N; other cell fields are suppressed. Administrative reporting changes can affect trends.'),
                  dict(source_id='GEO_COUSUBS_2023',source_url='https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2023_Gazetteer/2023_Gaz_cousubs_national.zip',source_section='National county-subdivision Gazetteer',access_date=DATE,
                       factual_summary='Representative points for exact state/name matches; used with July 2023 CBSA polygons. Unresolved localities are not forced into a metro.')]).to_csv(RAW/'additional_source_definitions.csv',index=False)
    pd.DataFrame(evidence).to_csv(RAW/'evidence_index.csv',index=False)
    # Compact unified source IDs; URLs stay in this archive. Normalized inherited
    # inputs have a local path and separate primary-source registry.
    company_sources=read(RAW/'company_source_registry.csv')
    unified=[dict(source_id=r.source_id,source_url=r.source_url,local_path='',source_type=r.source_type,access_date=r.access_date)
             for r in company_sources.itertuples()]
    unified += [dict(source_id=r['source_id'],source_url=r['source_urls'],local_path=r['local_path'],source_type=r['program'],access_date=r['original_access_date']) for r in metas]
    for sid,path in [('INHERITED_FEATURES','study_1/expanded_500/tables/metro_features_2024.csv'),('INHERITED_ECONOMIC_LEVELS','study_1/expanded_500/tables/metro_economic_inputs_2024.csv')]:
        unified.append(dict(source_id=sid,source_url='',local_path=path,source_type='inherited_normalized_input; primary routes in inherited_economic_source_registry.csv',access_date=DATE))
    unified += [dict(source_id='SRC_OEWS_2024',source_url=occupations.source_url.iloc[0],local_path='study_1/expanded_500/tables/metro_occupation_inputs_2024.csv',source_type='BLS OEWS',access_date=occupations.access_date.iloc[0]),
                dict(source_id='SRC_PUBLISHER_2025',source_url=cohort.publisher_source_url.iloc[0],local_path='study_1/expanded_500/tables/company_cohort_500.csv',source_type='Frozen publisher cohort',access_date=cohort.access_date.iloc[0])]
    for r in read(RAW/'geography_source_registry.csv').to_dict('records'):
        unified.append(dict(source_id=r['source_id'],source_url=r['source_url'],local_path='',source_type='Census 2023 geography',access_date=r['access_date']))
    unified.append(dict(source_id='GEO_COUSUBS_2023',source_url='https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2023_Gazetteer/2023_Gaz_cousubs_national.zip',local_path='raw_archive/2023_Gaz_cousubs_national.zip',source_type='Census 2023 geography',access_date=DATE))
    unified.append(dict(source_id='GEO_PUBLISHER_POINT_2023',source_url='https://interactives.fortune.com/f500-dataviz-2025/map/data.csv',local_path='study_1/expanded_500/tables/company_identity_matches.csv',source_type='Inherited publisher coordinates and 2023 CBSA crosswalk; polygon URLs in geography_source_registry.csv',access_date='2026-11-09'))
    pd.DataFrame(unified).to_csv(RAW/'source_registry.csv',index=False)
    pd.DataFrame(sorted(sector_names.items()),columns=['sector_code','sector_name']).to_csv(OUT/'config/broad_sector_codes.csv',index=False)
    pd.DataFrame(FUNCTIONS.items(),columns=['function_code','definition']).to_csv(OUT/'config/function_codes.csv',index=False)
    # Per-industry evidence differences remain visible before comparing metros.
    coverage_summary=cohort[['company_id','company_broad_industry']].merge(attempts.reset_index()[['company_id','source_lines_returned','properties_heading_found']],on='company_id')
    coverage_summary['new_function_fact']=coverage_summary.company_id.isin(facts.company_id).astype(int)
    coverage_summary['excerpt_available']=(pd.to_numeric(coverage_summary.source_lines_returned)>0).astype(int)
    coverage_summary['properties_section_found']=pd.to_numeric(coverage_summary.properties_heading_found)
    coverage_summary.groupby('company_broad_industry').agg(roster_n=('company_id','size'),excerpt_available_n=('excerpt_available','sum'),properties_section_found_n=('properties_section_found','sum'),companies_with_new_facts_n=('new_function_fact','sum')).reset_index().to_csv(OUT/'reports/industry_evidence_coverage.csv',index=False)
    # Reference entities reuse the existing roster/frame; new SQLite has no URLs.
    database_tables = {**tables, 'company_master_reference': cohort[['company_id','company','company_broad_industry']],
                       'metro_frame_reference': frame}
    if not study_integrity.sqlite_matches(OUT/'linked_msa.sqlite', database_tables):
        with sqlite3.connect(OUT/'linked_msa.sqlite') as db:
            for name,data in tables.items(): data.to_sql(name,db,if_exists='replace',index=False)
            cohort[['company_id','company','company_broad_industry']].to_sql('company_master_reference',db,if_exists='replace',index=False)
            frame.to_sql('metro_frame_reference',db,if_exists='replace',index=False)
            for name,keys in KEYS.items():db.execute(f'CREATE UNIQUE INDEX IF NOT EXISTS key_{name} ON {name} ({",".join(keys)})')
            db.execute('CREATE INDEX IF NOT EXISTS locations_company_metro ON company_locations(company_id, cbsa)')
            db.execute('CREATE INDEX IF NOT EXISTS functions_location_year ON location_functions(location_id, reference_year)')
    write_json(OUT/'reports/collection_summary.json',dict(date=DATE,table_rows={k:len(v) for k,v in tables.items()},
                roster_n=500,msa_n=50,source_screen_attempts=500,usable_indexed_excerpts=int(coverage_summary.excerpt_available.sum()),
                reviewed_office_facts=len(facts),companies_with_new_office_facts=facts.company_id.nunique(),
                locations_with_reported_employment=int(loc_table.local_employment.notna().sum()),locations_with_reported_office_area=int(loc_table.office_area_sqft.notna().sum()),
                office_fact_periods=sorted(facts.reference_year.unique().tolist()),
                unresolved_office_localities=int((loc_table.location_unit.eq('city_function_cluster')&loc_table.cbsa.eq('')).sum()),
                historical_hq_counts_preserved=True,office_census_complete=False,new_training_ready=False,
                weighted_score_computed=False,sector_specific_extensions_collected=False))
    return tables


def validate():
    tables={name:read(OUT/'tables'/f'{name}.csv') for name in KEYS}
    frame=read(BASE/'config/metro_frame.csv');companies=set(read(BASE/'tables/company_cohort_500.csv').company_id)
    evidence=read(RAW/'evidence_index.csv');eids=set(evidence.evidence_id)
    checks=[]
    def check(name,ok,detail=''):
        checks.append(dict(check=name,passed=bool(ok),detail=str(detail)))
    for name,data in tables.items():
        check(name+'_unique_key',not data.duplicated(KEYS[name]).any())
        check(name+'_nonempty',len(data)>0,len(data))
        check(name+'_no_source_urls',not data.apply(lambda col:col.str.contains(r'https?://|www\.',regex=True).any()).any())
        if 'evidence_id' in data:check(name+'_evidence_fk',set(data.evidence_id)<=eids)
        if 'company_id' in data:check(name+'_company_fk',set(data.company_id)<=companies)
    locations=tables['company_locations'];functions=tables['location_functions'];cov=tables['company_msa_coverage'];ind=tables['metro_indicators'];score=tables['msa_scorecard']
    check('function_location_fk',set(functions.location_id)<=set(locations.location_id))
    registry=read(RAW/'source_registry.csv')
    check('raw_source_ids_unique',not registry.source_id.duplicated().any())
    check('evidence_source_fk',set(evidence.source_id)<=set(registry.source_id))
    check('location_geography_source_fk',set(locations.geography_evidence_id)<=set(registry.source_id))
    joined=functions.merge(locations[['location_id','company_id']],on='location_id',suffixes=('','_parent'))
    check('function_company_consistent',joined.company_id.eq(joined.company_id_parent).all())
    check('function_vocabulary',set(functions.function_code)<=set(FUNCTIONS))
    check('metric_dictionary_fk',set(ind.metric_id)<=set(tables['metric_dictionary'].metric_id))
    check('all_50_metros',set(ind.cbsa)==set(frame.cbsa)==set(score.cbsa))
    check('roster_500_points',len(locations[locations.hq_benchmark_point=='1'])==500)
    check('eligible_498_points',len(locations[locations.hq_benchmark_eligible=='1'])==498)
    check('complete_company_metro_year_grid',len(cov)==500*50*2)
    check('unknown_office_values_not_zero',set(cov.corporate_presence)<={'','1.0','1'})
    check('contested_block_point_excluded_from_broader_presence',locations[locations.location_id=='LOC_HQ_f2025_179'].qualifying_corporate_presence.eq('0').all())
    check('no_unverified_office_absences',cov.office_absence_verified.eq('0').all())
    check('office_census_not_claimed',cov.office_census_complete.eq('0').all() and score.office_census_complete.eq('0').all())
    check('no_physical_site_or_local_job_imputation',functions[['physical_site_count','local_employment','office_area_sqft']].eq('').all().all())
    for measure,prefix in [('local_employment','employment'),('office_area_sqft','area')]:
        reported=locations[locations[measure]!='']
        check('location_'+measure+'_evidence',set(reported[prefix+'_evidence_id'])<=eids and reported[prefix+'_status'].ne('').all())
    check('no_weighted_score',score.weighted_score.eq('').all())
    check('unresolved_locations_not_in_frame',locations[locations.cbsa==''].inside_metro_frame.eq('0').all())
    check('all_suppressed_indicators_null',ind[ind.value_status=='suppressed_or_unavailable'].value.eq('').all())
    check('no_2025_private_qcew_detail',ind[(ind.metric_id.str.startswith('qcew_'))&(ind.reference_year=='2025')].empty)
    check('cbp_all_50_management_sectors',len(ind[(ind.metric_id=='cbp_employment')&(ind.sector_code=='55')])==50)
    check('qcew_common_broad_sector_grid',len(ind[ind.metric_id=='qcew_private_employment'])==50*2*21)
    for r in read(RAW/'regional_source_registry.csv').itertuples():
        check('raw_input_sha_'+r.source_id,sha(ROOT/r.local_path)==r.sha256)
        manifest=read((ROOT/r.local_path).parent/'download_manifest.csv')
        expected=manifest[manifest.file==(ROOT/r.local_path).name].sha256.iloc[0]
        check('raw_manifest_sha_'+r.source_id,r.sha256==expected)
    for metric in ['msa_private_employment_2024','msa_private_establishments_2024','msa_private_average_pay_2024','msa_population_2024','msa_nominal_gdp_2024_thousand_usd','median_household_income_2024_usd','median_gross_rent_2024_usd_month']:
        check('level_all_50_'+metric,set(ind[ind.metric_id==metric].cbsa)==set(frame.cbsa))
    establishments=ind[(ind.metric_id=='qcew_private_establishments')&(ind.source_flag=='N')]
    check('disclosed_qcew_establishments_retained',not establishments.empty and pd.to_numeric(establishments.value,errors='coerce').notna().all())
    new=functions[functions.observation_origin=='new_primary_source_screen']
    check('new_sources_period_not_forced_2025',set(new.reference_year)=={'2024','2025'})
    for metro in frame.cbsa:
        loc=locations[(locations.cbsa==metro)&(locations.hq_benchmark_eligible=='1')]
        check('hq_count_preserved_'+metro,len(loc)==int(score[score.cbsa==metro].reported_hq_count_2025.iloc[0]))
    check('hq_total_435',pd.to_numeric(score.reported_hq_count_2025).sum()==435)
    check('atlanta_hq_15',score[score.cbsa=='12060'].reported_hq_count_2025.iloc[0]=='15')
    original=read(BASE/'tables/metro_features_2024.csv').set_index('cbsa')
    for metric in read(BASE/'tables/feature_dictionary.csv').feature_name:
        old=pd.to_numeric(original[metric],errors='coerce').sort_index()
        newvalues=ind[ind.metric_id==metric].set_index('cbsa').value.pipe(pd.to_numeric,errors='coerce').sort_index()
        check('existing_feature_preserved_'+metric,np.allclose(old,newvalues,rtol=1e-10,equal_nan=True))
    snapshot=read(OUT/'config/prior_study_snapshot.csv')
    revision_path=OUT/'config/documentation_revisions.csv'
    revisions=read(revision_path) if revision_path.exists() else pd.DataFrame(columns=['path','before_sha256','after_sha256'])
    original_hashes=snapshot.set_index('path').sha256.to_dict()
    check('documentation_revisions_markdown_only',not revisions.path.duplicated().any() and
          revisions.path.str.endswith('.md').all() and set(revisions.path)<=set(original_hashes))
    check('documentation_revision_original_hashes',all(original_hashes.get(r.path)==r.before_sha256 for r in revisions.itertuples()))
    check('documentation_revision_current_hashes',all(study_integrity.historical_match(ROOT/r.path,r.after_sha256,allow_removed=True) for r in revisions.itertuples()))
    documented={r.path:r.after_sha256 for r in revisions.itertuples()
                if r.path.endswith('.md') and original_hashes.get(r.path)==r.before_sha256}
    changed=[r.path for r in snapshot.itertuples() if not study_integrity.historical_match(
             ROOT/r.path,documented.get(r.path,r.sha256),allow_removed=True)]
    check('prior_study_preserved_except_recorded_markdown_revisions',not changed,changed)
    with sqlite3.connect(OUT/'linked_msa.sqlite') as db:
        check('sqlite_integrity',db.execute('PRAGMA integrity_check').fetchone()[0]=='ok')
        for name,data in tables.items():check('sqlite_rows_'+name,db.execute(f'SELECT COUNT(*) FROM {name}').fetchone()[0]==len(data))
    result=pd.DataFrame(checks);result.to_csv(OUT/'reports/validation_checks.csv',index=False)
    write_json(OUT/'reports/validation_summary.json',dict(passed=int(result.passed.sum()),total=len(result),all_passed=bool(result.passed.all()),failures=result[~result.passed].to_dict('records')))
    print(f'{int(result.passed.sum())}/{len(result)} checks passed')
    if not result.passed.all():raise SystemExit(result[~result.passed].to_string(index=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--validate-only',action='store_true');args=parser.parse_args()
    if not args.validate_only:build()
    validate()
