#!/usr/bin/env python3
"""Independent data, prediction, selection and model-reload checks for R1."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

import build_feature_refinement as prep
import study_integrity

ROOT,BASE,STUDY=prep.ROOT,prep.BASE,prep.STUDY


def validate(data_only=False):
    checks=[]
    def check(name,condition):
        checks.append(dict(check=name,passed=bool(condition)))
        if not condition:raise AssertionError(name)
    prior=json.loads((ROOT/'config/prior_study_snapshot.json').read_text())
    check('historical fingerprints and documented cleanup verified',study_integrity.validate_cleanup() and all(study_integrity.historical_match(STUDY.parent/p,h,allow_removed=True) for p,h in prior.items()))
    for r in pd.read_csv(ROOT/'config/input_manifest.csv').itertuples():
        check('input hash '+r.path,study_integrity.historical_match(STUDY/r.path,r.sha256))
    plan=json.loads((ROOT/'config/training_plan.json').read_text())
    check('identical original grids and seed',plan==json.loads((BASE/'config/training_plan.json').read_text()))
    specs={t:json.loads((ROOT/'config'/f).read_text()) for t,f in [('A','feature_spec.json'),('B','company_hq_feature_spec.json')]}
    extra=prep.table(ROOT,'metro_refinement_features_2023')
    check('50 unique metro additions',len(extra)==50 and extra.cbsa.is_unique)
    check('only three declared additions',list(extra.columns)==['cbsa']+list(prep.ADDITIONS))
    check('complete finite additions',np.isfinite(extra[list(prep.ADDITIONS)].to_numpy()).all())
    check('100 accepted geography checks',len(pd.read_csv(ROOT/'reports/geography_audit.csv'))==100 and pd.read_csv(ROOT/'reports/geography_audit.csv').accepted.eq(1).all())
    for track,full,dev,atl,n_features in [('A','training_aggregate_2025','training_development_2025','training_atlanta_2025',34),
                                       ('B','training_company_metro_hq_2025','training_company_hq_development_2025','training_company_hq_atlanta_2025',42)]:
        spec=specs[track];keys=['company_id','cbsa'] if track=='B' else ['cbsa']
        check(track+' exact predictor size',len(spec['primary_predictors'])==n_features)
        check(track+' predictors exclude prohibited fields',not set(spec['primary_predictors'])&set(spec['prohibited_predictors']))
        for name in [full,dev,atl]:
            old,new=prep.table(BASE,name),prep.table(ROOT,name)
            check(name+' keys/labels/old columns preserved',len(old)==len(new) and all(np.allclose(old[c],new[c],rtol=1e-10,equal_nan=True)
                  if pd.api.types.is_numeric_dtype(old[c]) else old[c].equals(new[c]) for c in old.columns))
            check(name+' unique key',not new.duplicated(keys).any())
        d,a=prep.table(ROOT,dev),prep.table(ROOT,atl)
        check(track+' Atlanta reserved',not d.cbsa.eq('12060').any() and a.cbsa.eq('12060').all())
    da,db=prep.table(ROOT,'training_development_2025'),prep.table(ROOT,'training_company_hq_development_2025')
    check('unchanged 49 development and 24402 pairs',len(da)==49 and len(db)==24402 and db.groupby('cbsa').size().eq(498).all())
    check('435 HQ positives, 15 Atlanta',prep.table(ROOT,'training_company_metro_hq_2025').reported_hq_presence.sum()==435 and prep.table(ROOT,'training_company_hq_atlanta_2025').reported_hq_presence.sum()==15)
    check('common whole metro folds',db.validation_fold.eq(db.cbsa.map(da.set_index('cbsa').validation_fold)).all())
    check('B main-only contract size 38',len(specs['B']['main_effect_predictors'])==38)
    if not data_only:
        import joblib
        from sklearn.metrics import mean_absolute_error,mean_poisson_deviance,root_mean_squared_error
        out=ROOT/'reports/training'
        def report(name,sub=''):
            return pd.read_csv(out/sub/(name+'.csv'),dtype={'cbsa':str,'company_id':str})
        counts,pairs=report('oof_metro_predictions'),report('oof_company_probabilities','r1')
        metrics,atl=report('model_comparison'),report('atlanta_assessment')
        frozen=json.loads((out/'selection_frozen.json').read_text());metadata=json.loads((out/'run_metadata.json').read_text())
        check('frozen selection hash',prep.sha(out/'selection_frozen.json')==metadata['frozen_selection_sha256'])
        check('frozen input manifest hash',prep.sha(ROOT/'config/input_manifest.csv')==frozen['input_manifest_sha256'])
        check('reference manifest frozen hash',prep.sha(ROOT/'reports/reference_reuse_manifest.csv')==frozen['reference_manifest_sha256'])
        for r in pd.read_csv(ROOT/'reports/reference_reuse_manifest.csv').itertuples():
            check('R0 artifact unchanged '+r.path,prep.sha(STUDY/r.path)==r.sha256)
        check('20 models x49 OOF metros',len(counts)==980 and not counts.duplicated(['feature_set','model','cbsa']).any())
        check('OOF excludes Atlanta','12060' not in set(counts.cbsa)|set(pairs.cbsa))
        check('same supplied count folds',counts.fold.eq(counts.cbsa.map(da.set_index('cbsa').validation_fold)).all())
        check('same supplied company folds',pairs.fold.eq(pairs.cbsa.map(da.set_index('cbsa').validation_fold)).all())
        check('six complete company OOF grids',len(pairs)==6*498*49 and not pairs.duplicated(['model','company_id','cbsa']).any())
        check('sum-ready strict probabilities',pairs.probability.between(0,1,inclusive='neither').all())
        check('36 fits completed',len(report('fit_attempts'))==36 and report('fit_attempts').status.eq('passed').all())
        for (feature_set,model),g in counts.groupby(['feature_set','model']):
            score=metrics[(metrics.feature_set==feature_set)&(metrics.model==model)].iloc[0]
            recomputed=[mean_absolute_error(g.observed,g.expected),root_mean_squared_error(g.observed,g.expected),mean_poisson_deviance(g.observed,g.expected)]
            check(feature_set+'/'+model+' metrics independently reproduced',np.allclose(recomputed,score[['mae','rmse','poisson_deviance']].to_numpy(dtype=float),rtol=1e-10))
        r1=counts[counts.feature_set.eq('R1')]
        summed=pairs.groupby(['model','cbsa'])[['observed','probability']].sum().sort_index()
        expected=r1[r1.track.eq('B')].set_index(['model','cbsa']).sort_index()
        check('company sums reproduce counts',np.allclose(summed.probability,expected.expected,rtol=1e-7) and np.array_equal(summed.observed,expected.observed))
        for method in ['employment','mean']:
            same=counts[counts.model.isin(['A_'+method,'B_'+method])].pivot(index='cbsa',columns=['feature_set','model'],values='expected')
            check(method+' shared R0/R1 A/B baselines',np.allclose(same,same.iloc[:,0].to_numpy()[:,None],rtol=1e-10))
        order=plan['primary_model_order']
        ranked=sorted(metrics[metrics.primary].to_dict('records'),key=lambda r:(round(r['mae'],12),round(r['rmse'],12),r['feature_set'],order.index(r['model'])))
        check('selection follows MAE/RMSE/reference/order rule',(ranked[0]['feature_set'],ranked[0]['model'])==(frozen['selected_feature_set'],frozen['selected_model']))
        check('selection frozen before modeled Atlanta',frozen['atlanta_loaded_for_model_assessment'] is False)
        check('all Atlanta counts target15',atl.cbsa.eq('12060').all() and atl.observed.eq(15).all())
        ap=report('atlanta_company_probabilities','r1')
        for feature_set,modelroot in [('R0',BASE/'models'),('R1',ROOT/'models/r1')]:
            for path in sorted(modelroot.glob('*.joblib')):
                artifact=joblib.load(path);model=path.stem;track=artifact['track'];features=artifact['features'];pipeline=artifact['pipeline']
                table_name='training_atlanta_2025' if track=='A' else 'training_company_hq_atlanta_2025'
                frame=prep.table(ROOT,table_name)
                pred=pipeline.predict_proba(frame[features])[:,1] if track=='B' else pipeline.predict(frame[features])
                if track=='B':
                    ref=ap if feature_set=='R1' else pd.read_csv(BASE/'reports/training/atlanta_company_probabilities.csv')
                    values=ref[ref.model.eq(model)].set_index('company_id').loc[frame.company_id].probability
                else:values=atl[(atl.feature_set==feature_set)&(atl.model==model)].expected
                check(feature_set+'/'+model+' saved pipeline reload',np.allclose(pred,values,rtol=1e-7))
                if feature_set=='R1':
                    expected_features=specs[track]['main_effect_predictors' if model.endswith('_main') else 'primary_predictors']
                    check(model+' exact allowlist used',features==expected_features)
                    if 'xgboost' not in model:
                        trans=pipeline.named_steps['preprocess'];cols=trans.transformers_[0][2]
                        check(model+' development-only imputation',np.allclose(trans.named_transformers_['numeric'].named_steps['simpleimputer'].statistics_,(da if track=='A' else db)[cols].median(),equal_nan=True))
        pair=report('paired_r1_vs_r0')
        for row in pair.itertuples():
            c=counts[counts.model.eq(row.model)].pivot(index='cbsa',columns='feature_set',values='expected')
            y=counts[counts.model.eq(row.model)&counts.feature_set.eq('R0')].set_index('cbsa').loc[c.index].observed
            delta=np.mean(np.abs(y-c.R1)-np.abs(y-c.R0))
            check(row.model+' paired point estimate',np.isclose(delta,row.mae_r1_minus_r0,atol=1e-10))
    result=pd.DataFrame(checks);suffix='data' if data_only else 'artifact'
    result.to_csv(ROOT/'reports'/(suffix+'_validation_checks.csv'),index=False)
    prep.save_json(ROOT/'reports'/(suffix+'_validation.json'),dict(validation='PASS',checks_passed=len(checks),data_only=data_only))
    print(f'PASS: {len(checks)} {suffix} checks',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--data-only',action='store_true');args=parser.parse_args()
    validate(args.data_only)
