"""Prepare the company-MSA HQ track without collecting offices or fitting models."""
import json
import numpy as np
import pandas as pd

KEYS={
 'company_hq_features_2025':['company_id'],
 'company_hq_feature_dictionary':['feature_name'],
 'training_company_metro_hq_2025':['company_id','cbsa'],
 'training_company_hq_development_2025':['company_id','cbsa'],
 'training_company_hq_atlanta_2025':['company_id','cbsa'],
}

def save(root,name,data):
 data.to_csv(root/'tables'/f'{name}.csv',index=False,float_format='%.12g')

def build(root,cohort,labels,metro,splits):
 company=cohort[['company_id','company','company_broad_industry','ownership_listing_type_2025']].copy()
 company['log_company_revenue']=np.log(cohort.company_revenue_usd_millions)
 company['log_company_workforce']=np.log(cohort.company_global_workforce_fortune)
 company['log_company_assets']=np.log(cohort.company_assets_usd_millions)
 company['company_profit_margin']=cohort.company_profit_usd_millions/cohort.company_revenue_usd_millions
 company['company_revenue_growth_fraction']=cohort.company_revenue_growth_percent/100
 save(root,'company_hq_features_2025',company)
 # Two excluded firms stay in the audit grid, but have no supervised-training rows.
 data=labels.loc[labels.reported_hq_presence.notna(),['company_id','cbsa','reported_hq_presence']].copy()
 data['reported_hq_presence']=data.reported_hq_presence.astype(int)
 data=data.merge(company,on='company_id',validate='many_to_one').merge(metro,on='cbsa',validate='many_to_one').merge(splits,on='cbsa',validate='many_to_one')
 # Frozen, descriptive sector-to-ecosystem hypotheses, chosen without fitting on HQ results.
 definitions=[
  ('tech_x_computer_math_intensity',['Technology'],'soc_computer_math_jobs_per_1000'),
  ('financials_x_finance_share',['Financials'],'cbp_finance_insurance_share_2023'),
  ('health_care_x_health_share',['Health Care'],'cbp_health_social_share_2023'),
  ('industrial_x_manufacturing_share',['Aerospace & Defense','Chemicals','Industrials','Materials','Motor Vehicles & Parts'],'cbp_manufacturing_share_2023'),
 ]
 for name,sectors,field in definitions:
  data[name]=data.company_broad_industry.isin(sectors).astype(int)*data[field]
 metro_predictors=[c for c in metro if c not in ['cbsa','metro_name']]
 company_numeric=['log_company_revenue','log_company_workforce']
 categorical=['company_broad_industry','ownership_listing_type_2025']
 main=metro_predictors+company_numeric+categorical
 interactions=[name for name,_,_ in definitions]
 optional=['log_company_assets','company_profit_margin','company_revenue_growth_fraction']
 primary=main+interactions
 save(root,'training_company_metro_hq_2025',data)
 save(root,'training_company_hq_development_2025',data[data.split_role.eq('development')])
 save(root,'training_company_hq_atlanta_2025',data[data.split_role.eq('atlanta_assessment')])
 fd=pd.read_csv(root/'tables/feature_dictionary.csv')
 fd['role']='primary_metro_predictor';rows=fd.to_dict('records')
 descriptions={
  'log_company_revenue':('Natural log of publisher company-wide revenue in million USD','log million USD','ln(company_revenue_usd_millions)'),
  'log_company_workforce':('Natural log of publisher global workforce equivalents, not local jobs','log employee equivalents','ln(company_global_workforce_fortune)'),
  'company_broad_industry':('Publisher broad sector; 21 categories in the covered cohort','category','unchanged publisher sector'),
  'ownership_listing_type_2025':('Publisher listing indicator; not a complete verified legal ownership taxonomy','category','unchanged publisher category'),
  'log_company_assets':('Natural log of company-wide assets; scale sensitivity','log million USD','ln(company_assets_usd_millions)'),
  'company_profit_margin':('Publisher company-wide profits / revenue; financial-sector accounting differs','fraction','company_profit_usd_millions/company_revenue_usd_millions'),
  'company_revenue_growth_fraction':('Publisher annual revenue change; may include corporate actions','fraction','company_revenue_growth_percent/100'),
 }
 for field,(description,unit,formula) in descriptions.items():
  rows.append(dict(feature_name=field,role='primary_company_predictor' if field not in optional else 'optional_sensitivity_only',block='company_characteristics',definition=description,unit=unit,reference_period='Fortune 2025 edition; primarily FY2024; listing category as published',source_program='Fortune 2025 fixed cohort',formula=formula,missing_n=int(data[field].isna().sum()),missing_policy='Fold-fitted numeric handling; categorical encoder fitted inside training fold'))
 for name,sectors,field in definitions:
  rows.append(dict(feature_name=name,role='primary_prespecified_interaction',block='company_metro_interaction',definition='Publisher sector membership indicator multiplied by '+field,unit='same as '+field,reference_period='Company 2025 edition; metro source period unchanged',source_program='Fortune sector and retained metro features',formula='sector in '+repr(sectors)+' times '+field,missing_n=int(data[name].isna().sum()),missing_policy='Do not select or alter interactions using Atlanta outcomes'))
 dictionary=pd.DataFrame(rows)
 # The inherited macro dictionary counts unique MSA gaps; this dictionary counts company-MSA cells.
 for field in metro_predictors:dictionary.loc[dictionary.feature_name.eq(field),'missing_n']=int(data[field].isna().sum())
 save(root,'company_hq_feature_dictionary',dictionary)
 n=data.company_id.nunique()
 spec=dict(
  protocol_version=2,analysis_revision='2026-11-09_two_tracks',track='company_metro_hq',training_ready=True,
  target='reported_hq_presence',target_scope='One publisher-selected reported 2025 HQ point per covered firm; not all offices or all co-HQs',
  primary_key=['company_id','cbsa'],covered_companies=n,rows=len(data),development_rows=int(data.split_role.eq('development').sum()),atlanta_assessment_rows=int(data.split_role.eq('atlanta_assessment').sum()),
  positive_hq_labels_inside_frame=int(data.reported_hq_presence.sum()),independent_information=f'{n} designated HQ assignments; 50 metro feature profiles. Repeated rows are not independent regional experiments.',
  main_effect_predictors=main,interaction_predictors=interactions,primary_predictors=primary,
  numeric_predictors=[c for c in primary if c not in categorical],categorical_predictors=categorical,
  optional_sensitivity_predictors=optional,prohibited_predictors=[c for c in data if c not in primary+optional],
  primary_excludes_optional_financials=True,
  baseline={'descriptive':f'Observed company-HQ counts and sector breakdowns; same covered{n} roster as metro track',
   'prediction':f'Share the metro employment-proportional baseline: estimate total HQs/private-job rate inside each training fold. Per-company probability is predicted metro count/{n}; flag any out-of-range probability rather than silently clipping.',
   'secondary':f'Training-fold pooled company-MSA event rate; sum{n} probabilities to recover the fold mean metro count',
   'fair_comparison':'Baseline deliberately adds no company-specific information; detailed models must improve on it'},
  regression={'model':'L2-regularized binary logistic regression','features':'Main effects plus four frozen sector-ecosystem interactions','processing':'Fit numeric imputation/missing indicators, scaling, and one-hot encoding on training rows only; retain encoder for held-out MSAs'},
  conservative_ml={'model':'Shallow XGBoost binary classifier','objective':'binary:logistic','features':'Same primary predictors; fold-fitted category encoding','starting_search':'Depth1-2, strong penalties, small predeclared tuning grid; no reliance on large nominal row count'},
  aggregation={'expected_hqs':f'Sum predicted probabilities across the same{n} firms in each held-out MSA','threshold':'Do not threshold probabilities at0.5 before aggregation','uncertainty':'Account for shared metro and company dependence; do not assume independent Bernoulli errors','coherence':'Marginal probabilities, not a constrained joint HQ-location choice model. Do not force probabilities to sum to1 per firm over this incomplete50-MSA frame.'},
  validation={'main':f'Reuse identical whole-MSA development folds as aggregate track; all{n} Atlanta rows excluded from all fitting, preprocessing, calibration, and selection','company_scope':'Known covered roster in a new MSA; new-company generalization needs a separate company-held-out experiment','tuning':'Nested or prespecified within development only; a final Atlanta result must not select between tracks','metro_metrics':['MAE of summed expected counts','RMSE of summed expected counts','Poisson deviance of summed expected counts'],
   'company_metrics':['Log loss','Brier score','Calibration; accuracy alone is uninformative at this base rate'],
   'prevalence':'Keep all real HQ negatives; no default class rebalancing, negative undersampling, or scale_pos_weight. Such changes distort sum-ready probabilities unless corrected/calibrated within training only.'},
  leakage_prohibitions=['Publisher HQ city/state/CBSA','Known inside-frame HQ status','Company or metro IDs as free predictors','Observed per-metro HQ/sector counts','Coverage/source metadata','Any Atlanta-label-derived transformation'],
  references=['https://scikit-learn.org/stable/modules/linear_model.html#logistic-regression','https://xgboost.readthedocs.io/en/stable/parameter.html','https://scikit-learn.org/stable/modules/cross_validation.html#cross-validation-iterators-for-grouped-data'],
  collection=('No new web collection; deterministic join and transformations of existing normalized inputs. Two HQ coverage exclusions remain unchanged.' if len(cohort)==100 else 'Full-500 extension from cited publisher sources and retained metro inputs; supplemental source checks are not independent historical HQ verification. Coverage exclusions remain explicit.')
 )
 (root/'config/company_hq_feature_spec.json').write_text(json.dumps(spec,indent=2)+'\n')
 return spec

def validate(root,check):
 def read(name):return pd.read_csv(root/'tables'/f'{name}.csv',dtype={'company_id':str,'cbsa':str})
 full=read('training_company_metro_hq_2025');dev=read('training_company_hq_development_2025');atl=read('training_company_hq_atlanta_2025');labels=read('company_msa_hq_labels_2025');macro=read('training_aggregate_2025')
 spec=json.loads((root/'config/company_hq_feature_spec.json').read_text())
 check('company_track_4900_known_rows',len(full)==4900 and full.company_id.nunique()==98 and full.cbsa.nunique()==50 and full.reported_hq_presence.notna().all())
 check('company_track_4802_98_split',len(dev)==4802 and len(atl)==98 and atl.cbsa.eq('12060').all() and '12060' not in set(dev.cbsa))
 check('company_track_constant_roster',all(set(g.company_id)==set(full.company_id) for _,g in full.groupby('cbsa')))
 joined=full.merge(labels,on=['company_id','cbsa'],suffixes=('_training','_audit'),validate='one_to_one')
 check('company_track_labels_equal_audit',joined.reported_hq_presence_training.eq(joined.reported_hq_presence_audit).all())
 counts=full.groupby('cbsa').reported_hq_presence.sum()
 check('company_track_counts_equal_metro_track',np.allclose(macro.reported_hq_count_2025,macro.cbsa.map(counts)))
 split=full[['cbsa','split_role','validation_fold']].drop_duplicates().merge(macro[['cbsa','split_role','validation_fold']],on='cbsa',validate='one_to_one',suffixes=('_company','_metro'))
 check('company_track_same_metro_folds',split.split_role_company.eq(split.split_role_metro).all() and split.validation_fold_company.fillna(-1).eq(split.validation_fold_metro.fillna(-1)).all())
 check('company_track_39_primary_predictors',len(spec['primary_predictors'])==39 and len(spec['numeric_predictors'])==37 and len(spec['categorical_predictors'])==2)
 check('company_track_numeric_values_valid',all(pd.api.types.is_numeric_dtype(full[c]) and np.isfinite(full[c].dropna()).all() for c in spec['numeric_predictors']))
 check('company_track_no_primary_company_nulls',full[['log_company_revenue','log_company_workforce']+spec['categorical_predictors']].notna().all().all())
 check('company_track_only_repeated_four_macro_gaps',int(full[spec['numeric_predictors']].isna().sum().sum())==392)
 check('company_track_prohibits_outcome_and_ids',not set(spec['primary_predictors'])&set(spec['prohibited_predictors']) and not set(spec['primary_predictors'])&{'company_id','cbsa','reported_hq_presence'})
 check('company_track_optional_financials_not_primary',not set(spec['optional_sensitivity_predictors'])&set(spec['primary_predictors']))
 for field in ['log_company_revenue','log_company_workforce']+spec['categorical_predictors']:
  check('company_track_stable_'+field,full.groupby('company_id')[field].nunique().eq(1).all())
 for field in json.loads((root/'config/feature_spec.json').read_text())['primary_predictors']:
  joined=full[['cbsa',field]].drop_duplicates().merge(macro[['cbsa',field]],on='cbsa',validate='one_to_one',suffixes=('_company','_metro'))
  check('company_track_matches_'+field,np.allclose(joined[field+'_company'],joined[field+'_metro'],equal_nan=True))
