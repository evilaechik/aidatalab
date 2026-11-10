#!/usr/bin/env python3
"""Single-threaded R1 comparison; reuse frozen R0 outputs and core fit helpers."""
import hashlib
import importlib.metadata
import json
import platform
import sys
import time
import warnings
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from threadpoolctl import threadpool_limits

import build_feature_refinement as prep
import train_hq_2025 as core
import study_integrity

ROOT, BASE, STUDY = prep.ROOT, prep.BASE, prep.STUDY
FITTED = ['A_poisson', 'A_xgboost', 'B_logistic', 'B_xgboost', 'B_logistic_main', 'B_xgboost_main']
VERSIONS = ['numpy','pandas','scipy','scikit-learn','xgboost','joblib','threadpoolctl']


def read_report(root, name):
    return pd.read_csv(root / 'reports/training' / (name + '.csv'), dtype={'cbsa': str,'company_id':str})


def reuse_reference():
    frozen = json.loads((BASE / 'reports/training/selection_frozen.json').read_text())
    metadata = json.loads((BASE / 'reports/training/run_metadata.json').read_text())
    assert prep.sha(BASE / 'reports/training/selection_frozen.json') == metadata['frozen_selection_sha256']
    for path, value in {**frozen['input_sha256'], **metadata['atlanta_assessment_sha256']}.items():
        assert study_integrity.historical_match(BASE / path, value), path
    assert {p:importlib.metadata.version(p) for p in VERSIONS} == metadata['versions']
    paths = [p for folder in ['models','reports/training'] for p in sorted((BASE / folder).rglob('*')) if p.is_file()]
    pd.DataFrame([dict(feature_set='R0',path=str(p.relative_to(STUDY)),sha256=prep.sha(p)) for p in paths]).to_csv(ROOT / 'reports/reference_reuse_manifest.csv',index=False)
    return read_report(BASE, 'oof_metro_predictions'), read_report(BASE, 'oof_company_probabilities')


def compare_features(r0, r1, plan, output):
    metros = sorted(r0.cbsa.unique())
    weights = np.random.default_rng(plan['seed']).multinomial(len(metros),np.repeat(1/len(metros),len(metros)),size=plan['bootstrap_replicates'])
    rows=[]
    for model in core.LABELS:
        a=r0[r0.model.eq(model)].set_index('cbsa').loc[metros]
        b=r1[r1.model.eq(model)].set_index('cbsa').loc[metros]
        np.testing.assert_array_equal(a.observed,b.observed)
        la,lb=core.count_losses(a.observed,a.expected),core.count_losses(b.observed,b.expected)
        difference=lb['mae']-la['mae'];samples=weights@difference/len(metros)
        low,high=np.quantile(samples,[.025,.975])
        rows.append(dict(model=model,mae_r1_minus_r0=float(difference.mean()),lower=float(low),upper=float(high),
                         metros_improved=int((difference < -1e-10).sum()),metros_worse=int((difference > 1e-10).sum()),
                         rmse_r1_minus_r0=core.count_metrics(b.observed,b.expected)['rmse']-core.count_metrics(a.observed,a.expected)['rmse']))
    result=pd.DataFrame(rows);result.to_csv(output/'paired_r1_vs_r0.csv',index=False)
    return result


def report(metrics, atlanta, paired, probability, winner, elapsed, output):
    scores=metrics.set_index(['feature_set','model']); a=atlanta.set_index(['feature_set','model'])
    meanings={**core.LABELS}
    lines=['# Feature-refinement model results','', 'Run: November 10, 2026. R0 is the unchanged expanded-cohort reference; R1 adds three general regional features. The same 498 HQ firms and 49 development metros are used.','',
           'MAE is average absolute HQ-count error; RMSE penalizes large errors; lower is better. Atlanta observed 15 HQs. Positive observed-minus-expected gaps mean the count exceeds the benchmark.','',
           '| Model | R0 MAE | R1 MAE | Change | R0 RMSE | R1 RMSE | R0 Atlanta expected | R1 Atlanta expected | R1 Atlanta gap |',
           '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for model in core.LABELS:
        old,new=scores.loc[('R0',model)],scores.loc[('R1',model)]
        x,y=a.loc[('R0',model)],a.loc[('R1',model)]
        lines.append(f'| {meanings[model]} | {old.mae:.3f} | {new.mae:.3f} | {new.mae-old.mae:+.3f} | {old.rmse:.3f} | {new.rmse:.3f} | {x.expected:.2f} | {y.expected:.2f} | {y.residual:+.2f} |')
    lines += ['', 'The two B baselines duplicate A after dividing/summing over 498 firms. Main-effects-only fits are diagnostic and are excluded from primary model selection.','', '## What each model means','']
    descriptions={
        'A_employment':'Scales expected HQs with private employment; ignores the new feature bundle.',
        'A_mean':'Uses the training-metro average count; ignores differences in metro conditions.',
        'A_poisson':'Tests whether the regional factors improve direct HQ-count prediction.',
        'A_xgboost':'Tests shallow nonlinear relationships among the regional factors.',
        'B_employment':'Expresses the shared employment expectation as 498 equal company probabilities.',
        'B_mean':'Expresses the shared mean-count expectation as 498 equal company probabilities.',
        'B_logistic':'Uses company attributes and regional conditions to estimate company probabilities, then sums them.',
        'B_xgboost':'Tests shallow nonlinear company–metro probability relationships, then sums them.',
        'B_logistic_main':'Removes the four preset company–metro interactions from logistic regression.',
        'B_xgboost_main':'Removes explicit interaction columns; trees can still represent interactions.'}
    for row in paired.itertuples():
        lines.append(f'- **{meanings[row.model]}:** {descriptions[row.model]} R1 changes MAE by {row.mae_r1_minus_r0:+.3f} HQs per metro; the paired 95% fixed-prediction interval is {row.lower:+.3f} to {row.upper:+.3f}.')
    selected=a.loc[(winner['feature_set'],winner['model'])]
    best=metrics[metrics.primary].sort_values(['mae','rmse','feature_set']).iloc[0]
    baseline=float(scores.loc[('R0','A_employment'),'mae'])
    lines += ['', '## Conclusions','',
              f'- The frozen primary rule selects **{winner["feature_set"]} / {meanings[winner["model"]]}**, with OOF MAE **{best.mae:.3f}** versus employment baseline **{baseline:.3f}**.',
              f'- Its Atlanta expectation is **{selected.expected:.2f}** versus **15** observed, a gap of **{selected.residual:+.2f} HQs**. Its heuristic 90% prediction-error band is **{selected.band90_lower:.2f}–{selected.band90_upper:.2f}**.',
              '- '+('Atlanta does not fall below the selected expectation; this run does not identify an overall HQ deficit.' if selected.residual>=0 else 'Atlanta falls below the selected expectation; the size of that gap must be compared with the prediction-error band before interpreting a deficit.'),
              '- '+('The added feature/model complexity does not improve the selected MAE benchmark.' if winner['model'] in ['A_employment','B_employment'] else 'The selected model improves point-estimate MAE; paired uncertainty and the secondary metrics determine how convincing that improvement is.'),
              '- Paired intervals compare R1 with the corresponding R0 model on identical held-out metros. They are descriptive, reuse fixed OOF predictions, and omit model-refitting and selection uncertainty.',
              '- No model or feature was selected from its Atlanta result. Atlanta has been inspected in prior work, so this remains a follow-up rather than an analyst-blind test.']
    lines += ['', '## Probability quality','', '| Company model | R0 log loss | R1 log loss | R0 Brier | R1 Brier |', '| --- | ---: | ---: | ---: | ---: |']
    p=probability.set_index(['feature_set','model'])
    for model in [k for k in core.LABELS if k.startswith('B')]:
        x,y=p.loc[('R0',model)],p.loc[('R1',model)]
        lines.append(f'| {meanings[model]} | {x.log_loss:.5f} | {y.log_loss:.5f} | {x.brier:.5f} | {y.brier:.5f} |')
    lines += ['', '## Scope and next steps','',
              'The new inputs are CBP 2023 corporate-management employment share and BDS 2023 all-industry establishment entry/exit rates. Geography passed the documented July 2023 gate, including Connecticut and the Providence statewide-code exception. The source metrics are regional activity proxies, not office openings, attraction effects or assigned Fortune-company jobs.',
              'Only 49 development metro environments remain. The office collection has positives and unknowns, and does not support a presence classifier or office-gap rankings. Weighted scoring and bespoke tech/healthcare outcomes remain deferred. SHAP values or coefficients would describe associations, not effects of changing a factor.',
              'Use the retained company-function evidence to verify sector/function leads and improve comparable dated office coverage. Any later broader-outcome benchmark needs a separately specified target and must exclude features that mechanically reconstruct it.', '',
              f'New fitting and reporting took {elapsed:.1f} seconds. R0 was reused after hash/version checks; its models were not retrained. See [README.md](README.md), [VALIDATION.md](VALIDATION.md), [all metrics](reports/training/model_comparison.csv), [paired differences](reports/training/paired_r1_vs_r0.csv), and [Atlanta assessment](reports/training/atlanta_assessment.csv).','']
    (ROOT/'FINAL_RESULTS.md').write_text('\n'.join(lines))


def main():
    start=time.perf_counter();output=ROOT/'reports/training';r1out=output/'r1';r1out.mkdir(parents=True,exist_ok=True)
    modeldir=ROOT/'models/r1';modeldir.mkdir(parents=True,exist_ok=True)
    plan=json.loads((ROOT/'config/training_plan.json').read_text())
    specs={t:json.loads((ROOT/'config'/f).read_text()) for t,f in [('A','feature_spec.json'),('B','company_hq_feature_spec.json')]}
    assert plan==json.loads((BASE/'config/training_plan.json').read_text())
    r0,r0pairs=reuse_reference()
    data={'A':prep.table(ROOT,'training_development_2025'),'B':prep.table(ROOT,'training_company_hq_development_2025')}
    assert len(data['A'])==49 and len(data['B'])==24402
    assert '12060' not in set(data['A'].cbsa)|set(data['B'].cbsa)
    counts,pairs,tuning,params,attempts=[],[],[],{},[]
    for fold in sorted(data['A'].validation_fold.unique()):
        train_a,test_a=data['A'][data['A'].validation_fold.ne(fold)],data['A'][data['A'].validation_fold.eq(fold)]
        test_b=data['B'][data['B'].validation_fold.eq(fold)]
        for method in ['employment','mean']:
            p,_=core.baseline(train_a,test_a,method)
            core.add_predictions('A_'+method,test_a,p,specs['A']['target'],fold,counts,pairs)
            core.add_predictions('B_'+method,test_b,test_b.cbsa.map(dict(zip(test_a.cbsa,p))).to_numpy()/498,specs['B']['target'],fold,counts,pairs)
        for model in FITTED:
            frame=data[model[0]];context=f'outer_{int(fold)}'
            train,test=frame[frame.validation_fold.ne(fold)],frame[frame.validation_fold.eq(fold)]
            t=time.perf_counter()
            try:
                fit,features,settings=core.tune_fit(model,train,specs[model[0]],plan,context,tuning)
                core.add_predictions(model,test,core.predict(fit,test[features],model),specs[model[0]]['target'],fold,counts,pairs)
            except Exception as error:
                attempts.append(dict(context=context,model=model,status='failed',error=str(error)));pd.DataFrame(attempts).to_csv(output/'fit_attempts.csv',index=False);raise
            params[context+'_'+model]=settings
            attempts.append(dict(context=context,model=model,status='passed',seconds=time.perf_counter()-t))
        print(f'Completed R1 outer fold {int(fold)}',flush=True)
    r1,r1pairs=pd.concat(counts,ignore_index=True),pd.concat(pairs,ignore_index=True)
    r1.to_csv(r1out/'oof_metro_predictions.csv',index=False);r1pairs.to_csv(r1out/'oof_company_probabilities.csv',index=False)
    combined=pd.concat([r0.assign(feature_set='R0'),r1.assign(feature_set='R1')],ignore_index=True)
    combined.to_csv(output/'oof_metro_predictions.csv',index=False)
    metrics=pd.DataFrame([dict(feature_set=s,model=m,primary=m in plan['primary_model_order'],**core.count_metrics(g.observed,g.expected)) for (s,m),g in combined.groupby(['feature_set','model'],sort=False)])
    metrics.to_csv(output/'model_comparison.csv',index=False)
    pd.DataFrame([dict(feature_set=s,model=m,fold=int(f),**core.count_metrics(g.observed,g.expected)) for (s,m,f),g in combined.groupby(['feature_set','model','fold'])]).to_csv(output/'fold_metrics.csv',index=False)
    eligible=metrics[metrics.primary].to_dict('records')
    ranking=sorted(eligible,key=lambda r:(round(r['mae'],12),round(r['rmse'],12),r['feature_set'],plan['primary_model_order'].index(r['model'])))
    winner=ranking[0];final={};final_params={}
    for model in FITTED:
        fit,features,settings=core.tune_fit(model,data[model[0]],specs[model[0]],plan,'final_development',tuning)
        final[model]=(fit,features);final_params[model]=settings
        joblib.dump(dict(pipeline=fit,features=features,params=settings,track=model[0],feature_set='R1'),modeldir/(model+'.joblib'),compress=3)
        if 'xgboost' in model:fit.named_steps['model'].save_model(modeldir/(model+'.ubj'))
        attempts.append(dict(context='final_development',model=model,status='passed'))
    frozen=dict(frozen_at_utc=datetime.now(timezone.utc).isoformat(),selected_feature_set=winner['feature_set'],selected_model=winner['model'],
                ranking=ranking,final_params=final_params,outer_params=params,atlanta_loaded_for_model_assessment=False,
                input_manifest_sha256=prep.sha(ROOT/'config/input_manifest.csv'),reference_manifest_sha256=prep.sha(ROOT/'reports/reference_reuse_manifest.csv'))
    prep.save_json(output/'selection_frozen.json',frozen)
    print(f'Selection frozen: {winner["feature_set"]} / {winner["model"]}; assessing Atlanta.',flush=True)
    reserved={'A':prep.table(ROOT,'training_atlanta_2025'),'B':prep.table(ROOT,'training_company_hq_atlanta_2025')}
    ac,ap,baseline=[],[],{}
    for method in ['employment','mean']:
        p,baseline[method]=core.baseline(data['A'],reserved['A'],method)
        core.add_predictions('A_'+method,reserved['A'],p,specs['A']['target'],'atlanta',ac,ap)
        core.add_predictions('B_'+method,reserved['B'],np.repeat(p/498,498),specs['B']['target'],'atlanta',ac,ap)
    prep.save_json(modeldir/'baselines.json',baseline)
    coefficients=[]
    for model,(fit,features) in final.items():
        frame=reserved[model[0]];core.add_predictions(model,frame,core.predict(fit,frame[features],model),specs[model[0]]['target'],'atlanta',ac,ap)
        if 'xgboost' not in model:
            names=fit.named_steps['preprocess'].get_feature_names_out();coef=np.ravel(fit.named_steps['model'].coef_)
            coefficients.extend(dict(model=model,feature=f,coefficient=float(c),scope='final development fit; standardized numeric inputs; association only') for f,c in zip(names,coef))
    atl,ap=pd.concat(ac,ignore_index=True),pd.concat(ap,ignore_index=True)
    for i,row in atl.iterrows():
        residuals=r1[r1.model.eq(row.model)].residual.abs().to_numpy();rank=min(len(residuals),int(np.ceil((len(residuals)+1)*.9)));q=np.sort(residuals)[rank-1]
        atl.loc[i,'band90_lower'],atl.loc[i,'band90_upper']=max(0,row.expected-q),row.expected+q
    atl.to_csv(r1out/'atlanta_assessment.csv',index=False);ap.to_csv(r1out/'atlanta_company_probabilities.csv',index=False)
    all_atl=pd.concat([read_report(BASE,'atlanta_assessment').assign(feature_set='R0'),atl.assign(feature_set='R1')],ignore_index=True)
    all_atl.to_csv(output/'atlanta_assessment.csv',index=False)
    p1=core.calibration(r1pairs,r1out);u1=core.uncertainty(r1,r1pairs,plan,r1out)
    probability=pd.concat([read_report(BASE,'probability_comparison').assign(feature_set='R0'),p1.assign(feature_set='R1')],ignore_index=True)
    probability.to_csv(output/'probability_comparison.csv',index=False)
    pd.concat([read_report(BASE,'uncertainty').assign(feature_set='R0'),u1.assign(feature_set='R1')],ignore_index=True).to_csv(output/'uncertainty.csv',index=False)
    paired=compare_features(r0,r1,plan,output)
    pd.DataFrame(tuning).to_csv(r1out/'tuning_scores.csv',index=False);pd.DataFrame(attempts).to_csv(output/'fit_attempts.csv',index=False)
    pd.DataFrame(coefficients).to_csv(output/'feature_coefficients.csv',index=False)
    all_pairs=pd.concat([r1pairs.assign(assessment='development_oof'),ap.assign(assessment='atlanta')])
    sectors=all_pairs.groupby(['assessment','model','company_broad_industry']).agg(observed=('observed','sum'),expected=('probability','sum'),n=('observed','size')).reset_index()
    sectors['residual']=sectors.observed-sectors.expected;sectors.to_csv(r1out/'sector_diagnostics.csv',index=False)
    elapsed=time.perf_counter()-start
    prep.save_json(output/'run_metadata.json',dict(completed_at_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=elapsed,
              seed=plan['seed'],versions={p:importlib.metadata.version(p) for p in VERSIONS},python=sys.version,platform=platform.platform(),
              selected_feature_set=winner['feature_set'],selected_model=winner['model'],reference_reused=True,threads=1,
              new_model_fits=6*(5+1),new_inner_candidate_fits=sum(4 if 'xgboost' in k else 3 for k in FITTED)*(5*4+5),
              input_manifest_sha256=frozen['input_manifest_sha256'],frozen_selection_sha256=prep.sha(output/'selection_frozen.json')))
    report(metrics,all_atl,paired,probability,winner,elapsed,output)
    print(metrics.to_string(index=False),flush=True);print(f'Finished R1 in {elapsed:.1f}s.',flush=True)


if __name__=='__main__':
    warnings.simplefilter('error',ConvergenceWarning)
    with threadpool_limits(limits=1):main()
