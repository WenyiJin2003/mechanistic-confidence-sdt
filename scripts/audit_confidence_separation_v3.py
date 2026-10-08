#!/usr/bin/env python3
"""Independently verify frozen v3 artifacts and reproduce posthoc diagnostics.

Run with the existing stage0 virtual environment from any working directory.
Reads only local authored stimuli, cached arrays, the pinned local tokenizer and
Git objects. Never imports or runs a language model, calls an API, or changes the
registered metrics, manifest, source data, or frozen implementation. The only
outputs are independent_audit.json and posthoc_context_availability.json in the
existing v3 results directory. The diagnostic was chosen after registered
outcomes; it never changes the preregistered confirmation gates.
"""
from pathlib import Path
from collections import defaultdict
import csv,hashlib,json,subprocess
import numpy as np,yaml
from transformers import AutoTokenizer
root=Path(__file__).resolve().parents[1]; output=root/'results/confidence_separation_v3'
def git(args, **kwargs):
    return subprocess.check_output(args, cwd=root, **kwargs)
jsonl=lambda rel:[json.loads(line) for line in (root/rel).read_text().splitlines() if line]
read=lambda rel:json.loads((root/rel).read_text())
sha=lambda value:hashlib.sha256(value).hexdigest()
stable=lambda value:sha(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
cfg=yaml.safe_load((root/'configs/confidence_separation_v3.yaml').read_text())
rows=jsonl('results/confidence_separation_v3/extraction_rows.jsonl'); original=jsonl(cfg['data']['variants'])
report=read('results/confidence_separation_v3/separation_metrics.json'); manifest=read('results/confidence_separation_v3/manifest.json')
checks={}; errors=[]
def check(name,value):
    checks[name]=bool(value)
    if not value:errors.append(name)
check('672_unique_authored_rows_and48_test_sources',len(rows)==672 and len({r['variant_id'] for r in rows})==672 and len({r['source_id'] for r in rows})==48 and all(r['split']=='test' for r in rows))
check('authored_order_and_every_input_field_retained',[r['variant_id'] for r in rows]==[r['variant_id'] for r in original] and all(all(r.get(k)==v for k,v in o.items()) for r,o in zip(rows,original)))
with np.load(output/'hidden_states.npz') as a:
    h=a['hidden_states'].copy(); ids=a['variant_ids'].tolist(); layers=a['layers'].tolist(); positions=a['positions'].tolist()
check('hidden_states_finite_complete_aligned',h.shape==(672,2,4,1536) and np.isfinite(h).all() and ids==[r['variant_id'] for r in rows] and layers==[14,23] and positions==['boundary','final_content','response_mean','prompt'])
with np.load(output/'frozen_directions.npz') as a:v={k:a[k].copy() for k in a.files}
with np.load(root/cfg['source_artifacts']['directions']['path']) as a:old_v={k:a[k].copy() for k in a.files}
old=jsonl(cfg['source_artifacts']['extraction_rows']['path'])
with np.load(root/cfg['source_artifacts']['hidden_states']['path']) as a:old_h=a['hidden_states'].copy()
train=[i for i,r in enumerate(old) if r['split']=='train' and r['rewrite_family'] in {'A','B'}]
sids=sorted({old[i]['source_id'] for i in train})
check('correctness_fit_old72_AB_sources_only',len(train)==576 and len(sids)==72)
reps={'layer14_boundary':(0,0),'layer14_final_content':(0,1),'layer14_response_mean':(0,2),'layer23_boundary':(1,0)}
vector_checks={}
for name,(layer,pos) in reps.items():
    old_dir=old_v[name].astype(np.float64); x=old_h[:,layer,pos].astype(np.float64); bundles=[]
    for sid in sids:
        diffs=[]
        for family in ('A','B'):
            ix=[i for i in train if old[i]['source_id']==sid and old[i]['rewrite_family']==family]
            good=[i for i in ix if old[i]['correctness']=='correct']; bad=[i for i in ix if old[i]['correctness']=='incorrect']
            assert len(good)==len(bad)==2
            diffs.append(x[good].mean(0)-x[bad].mean(0))
        bundles.append(np.mean(diffs,0))
    c=np.mean(bundles,0); c/=np.linalg.norm(c); residual=old_dir-(old_dir@c)*c
    vector_checks[name]={'confidence_values_and_bytes_identical':bool(np.array_equal(v[name],old_dir) and v[name].tobytes()==old_dir.tobytes()),'correctness_max_abs_error':float(np.max(np.abs(v[name+'_correctness']-c))),'projected_max_abs_error':float(np.max(np.abs(v[name+'_projected']-residual/np.linalg.norm(residual)))),'common_scale_max_abs_error':float(np.max(np.abs(v[name+'_projected_common_scale']-residual)))}
check('all4_confidence_vectors_byte_identical',all(z['confidence_values_and_bytes_identical'] for z in vector_checks.values()))
check('all12_old_correctness_and_projected_vectors_reproduced',all(max(z['correctness_max_abs_error'],z['projected_max_abs_error'],z['common_scale_max_abs_error'])<1e-12 for z in vector_checks.values()))
ix={(r['source_id'],r['world'],r['answer_key'],r['certainty']):i for i,r in enumerate(rows)}
pairs={'certainty_wording':[],'neutral_true_vs_false':[],'neutral_supported_vs_omitted':[]}; omitted_false=[]; identities=0
for sid in sorted({r['source_id'] for r in rows}):
    assert len([r for r in rows if r['source_id']==sid])==14
    for world in ('A','B'):
        for answer in ('A','B'):pairs['certainty_wording'].append((ix[sid,world,answer,'confident'],ix[sid,world,answer,'hedged']))
    for answer,other in (('A','B'),('B','A')):
        good=ix[sid,answer,answer,'neutral']; bad=ix[sid,other,answer,'neutral']; omitted=ix[sid,'omitted',answer,'neutral']
        pairs['neutral_true_vs_false'].append((good,bad)); pairs['neutral_supported_vs_omitted'].append((good,omitted)); omitted_false.append((bad,omitted))
        for style in ('confident','hedged','neutral'):
            a=rows[ix[sid,'A',answer,style]]; b=rows[ix[sid,'B',answer,style]]
            assert all(a[k]==b[k] for k in ('response_text','response_ids','prompt_token_count','response_start_position','answer_token_positions','final_content_position','boundary_position'))
            assert {a['correctness'],b['correctness']}=={'correct','incorrect'}; identities+=1
check('192_96_96_registered_pairs',{k:len(z) for k,z in pairs.items()}=={'certainty_wording':192,'neutral_true_vs_false':96,'neutral_supported_vs_omitted':96})
check('all288_world_pairs_have_identical_responses_and_absolute_positions',identities==288)
for endpoint,chosen in pairs.items():
    assert report['pair_ids'][endpoint]==[[rows[a]['variant_id'],rows[b]['variant_id']] for a,b in chosen]
    for a,b in chosen:
        if endpoint=='certainty_wording':assert rows[a]['world_claim']==rows[b]['world_claim'] and rows[a]['context']==rows[b]['context'] and rows[a]['correctness']==rows[b]['correctness']
        else:assert all(rows[a][k]==rows[b][k] for k in ('response_text','response_ids','prompt_token_count','answer_token_positions','response_start_position','final_content_position','boundary_position'))
check('all_reported_pair_identities_exact',True)
def stat(values,chosen):
    groups=np.array([rows[a]['source_id'] for a,b in chosen]); values=np.asarray(values,dtype=np.float64)
    means=np.array([values[groups==sid].mean() for sid in np.unique(groups)])
    rng=np.random.default_rng(cfg['analysis']['bootstrap_seed']); boot=means[rng.integers(0,len(means),size=(cfg['analysis']['bootstrap_samples'],len(means)))].mean(1)
    lo,hi=np.percentile(boot,[2.5,97.5])
    return {'estimate':float(means.mean()),'n_pairs':len(chosen),'n_sources':len(means),'bootstrap_95':{'lower':float(lo),'upper':float(hi)},'source_mean_minimum':float(means.min()),'source_mean_maximum':float(means.max())}
def ordering(values,chosen):
    margins=np.asarray(values); result=stat(np.sign(margins)/2+.5,chosen); result['accuracy']=result.pop('estimate'); result['tie_fraction']=float((margins==0).mean()); return result
def compare(actual,expected,estimate_name):
    assert actual['n_pairs']==expected['n_pairs'] and actual['n_sources']==expected['n_sources']
    return max(abs(actual[estimate_name]-expected[estimate_name]),abs(actual['bootstrap_95']['lower']-expected['bootstrap_95']['lower']),abs(actual['bootstrap_95']['upper']-expected['bootstrap_95']['upper']))
independent={}; max_score_error=0.; max_metric_error=0.; all_scores={}
for name,(layer,pos) in reps.items():
    x=h[:,layer,pos].astype(np.float64); independent[name]={}
    for suffix in ('','_correctness','_projected','_projected_common_scale'):
        key=name+suffix; score=x@v[key]; all_scores[key]=score
        max_score_error=max(max_score_error,float(np.max(np.abs(score-np.asarray(report['row_scores'][key])))))
        for endpoint,chosen in pairs.items():
            margins=np.array([score[a]-score[b] for a,b in chosen]); estimate=ordering(margins,chosen); expected=report['representations'][key][endpoint]
            max_metric_error=max(max_metric_error,compare(estimate,expected,'accuracy'),compare(stat(margins,chosen),expected['mean_margin'],'estimate'))
            if suffix:continue
            estimate['mean_margin']=stat(margins,chosen)
            for field in ('fact_type','answer_key','wording_family'):
                strata={}
                for value in sorted({str(rows[a][field]) for a,b in chosen}):
                    selected=[j for j,(a,b) in enumerate(chosen) if str(rows[a][field])==value]; subset=[chosen[j] for j in selected]
                    sub=ordering(margins[selected],subset); sub['mean_margin']=stat(margins[selected],subset); strata[value]=sub
                    ref=expected['by_'+field][value]
                    max_metric_error=max(max_metric_error,compare(sub,ref,'accuracy'),compare(sub['mean_margin'],ref['mean_margin'],'estimate'))
                estimate['by_'+field]=strata
            if endpoint=='certainty_wording':
                estimate['by_correctness']={}
                for label in ('correct','incorrect'):
                    selected=[j for j,(a,b) in enumerate(chosen) if rows[a]['correctness']==label]; subset=[chosen[j] for j in selected]
                    sub=ordering(margins[selected],subset); sub['mean_margin']=stat(margins[selected],subset); estimate['by_correctness'][label]=sub
                    max_metric_error=max(max_metric_error,compare(sub,expected['by_correctness'][label],'accuracy'))
            independent[name][endpoint]=estimate
check('all16_row_score_arrays_reproduced',max_score_error<1e-12)
check('all16_pooled_intervals_and_all_frozen_confidence_strata_exact',max_metric_error<1e-12)
# Independent token reconstruction; only a tokenizer is loaded.
snapshot=(root/cfg['runtime']['shared_repo']/cfg['model']['snapshot']).resolve(); tokenizer=AutoTokenizer.from_pretrained(str(snapshot),local_files_only=True)
prompts=defaultdict(set); token_errors=[]
for i,row in enumerate(rows):
    user='Context: '+row['context']+'\n\nQuestion: '+row['question']; messages=[{'role':'system','content':cfg['model']['system_prompt']},{'role':'user','content':user}]
    prompt=tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)
    full=tokenizer.apply_chat_template(messages+[{'role':'assistant','content':row['response_text']}],tokenize=False,add_generation_prompt=False)
    prompt_ids=tokenizer(prompt,add_special_tokens=False)['input_ids']; full_ids=tokenizer(full,add_special_tokens=False)['input_ids']; p=len(prompt_ids); end=full_ids.index(cfg['model']['boundary_token_id'],p); ids=full_ids[:end+1]; content=full_ids[p:end]
    good=full_ids[:p]==prompt_ids and p==row['prompt_token_count']==row['response_start_position'] and end==row['boundary_position']==row['response_stop_position_exclusive'] and end-1==row['final_content_position'] and content==row['response_ids'] and stable(ids)==row['input_ids_sha256'] and stable(prompt_ids)==row['prompt_ids_sha256'] and tokenizer.decode(content)==row['response_text']
    if not good:token_errors.append(row['variant_id'])
    prompts[row['prompt_group_id']].add(tuple(prompt_ids))
    with np.load(root/cfg['output']['cache_dir']/(row['cache_fingerprint']+'.npz')) as a:
        assert a['input_ids'].tolist()==ids and np.array_equal(a['hidden'],h[i])
        assert float(a['mean_token_nll'])==row['mean_token_nll'] and float(a['sequence_nll'])==row['sequence_nll']
check('all672_rendered_inputs_positions_hashes_and_cache_states_match',not token_errors)
check('144_prompt_groups_have_exact_prompt_invariance',len(prompts)==144 and all(len(z)==1 for z in prompts.values()))
commit=manifest['implementation_commit']; timestamp=int(git(['git','show','-s','--format=%ct',commit],text=True).strip()); protected={}; artifact_hashes={}
for rel,expected in {**manifest['implementation_sha256'],**manifest['data_sha256']}.items():protected[rel]=sha((root/rel).read_bytes())==expected==sha(git(['git','show',commit+':'+rel]))
for name,expected in manifest['artifacts'].items():artifact_hashes[name]=sha((output/name).read_bytes())==expected
cache_times=[(root/cfg['output']['cache_dir']/(r['cache_fingerprint']+'.npz')).stat().st_mtime for r in rows]
check('manifest_frozen_commit_and_protected_hashes_exact',commit=='bcaf2bfadf49d95a0e86ee2a90a23659d1f83f85' and all(protected.values()))
check('every_manifest_artifact_hash_matches',all(artifact_hashes.values()))
check('all672_cache_files_postdate_frozen_design_commit',min(cache_times)>=timestamp)
canonical=[]
for prefix in ('data/paired_confidence','data/confidence_transfer_v2','results/paired_confidence_phase_a','results/paired_confidence_phase_b','results/paired_confidence_transfer_v2'):canonical+=git(['git','ls-files',prefix],text=True).splitlines()
check('all44_canonical_v1_v2_tracked_files_byte_unchanged',len(canonical)==44 and all((root/rel).read_bytes()==git(['git','show',commit+':'+rel]) for rel in canonical))
old_hashes=[]
for rel in ('results/paired_confidence_phase_a/manifest.json','results/paired_confidence_phase_b/manifest.json','results/paired_confidence_transfer_v2/manifest.json'):
    m=read(rel)
    for name,expected in m.get('artifacts',{}).items():old_hashes.append(sha((root/rel).parent.joinpath(name).read_bytes())==expected)
    for name,expected in m.get('data_sha256',{}).items():old_hashes.append(sha((root/m.get('configuration',{}).get('data',{}).get(name,name)).read_bytes())==expected)
check('all_prior_v1_v2_manifest_result_and_data_hashes_match',all(old_hashes))
check('no_generation_NLI_API_calls',all(manifest['runtime'][key]==0 for key in ('generation_calls','nli_calls','openai_api_calls')))
browser=root/cfg['output']['browser_dir']
with (browser/'responses.csv').open(newline='',encoding='utf-8') as f:csv_rows=list(csv.DictReader(f))
csv_lookup={r['variant_id']:r for r in csv_rows}
check('CSV_all672_response_texts_and_contexts_exact',len(csv_rows)==len(csv_lookup)==672 and all(csv_lookup[r['variant_id']]['response_text']==r['response_text'] and csv_lookup[r['variant_id']]['context']==r['context'] for r in rows))
parsed={}
for fact in cfg['dataset']['fact_types']:
    text=(browser/(fact+'.md')).read_text(); sid=None; world=None
    for line in text.splitlines():
        if line.startswith('## v3-'):sid=line[3:]
        elif line.startswith('### World '):world=line[10:]
        elif line.startswith('**') and ' / ' in line and ':** ' in line:
            label,response=line[2:].split(':** ',1); answer,style,correctness=label.split(' / '); key=(sid,world,answer,style); assert key not in parsed; parsed[key]=response
    assert sum(text.count('`'+r['variant_id']+'`') for r in rows if r['fact_type']==fact)==168
check('Markdown_all672_response_texts_and_exact_row_ids_retained',len(parsed)==672 and all(parsed[(r['source_id'],r['world'],r['answer_key'],r['certainty'])]==r['response_text'] for r in rows))
audit={'passed':not errors,'checks':checks,'errors':errors,'method':'Independent NumPy arithmetic, source bootstrap and tokenizer-only regeneration; no runner analysis function or model was called.','implementation_commit':commit,'frozen_commit_timestamp_unix':timestamp,'earliest_cache_timestamp_unix':min(cache_times),'pair_counts':{k:len(z) for k,z in pairs.items()},'num_sources':48,'num_rows':672,'max_row_score_abs_error':max_score_error,'max_metric_abs_error':max_metric_error,'vector_checks':vector_checks,'recomputed_readouts':independent,'protected_hash_checks':protected,'artifact_hash_checks':artifact_hashes,'canonical_file_count':len(canonical),'prior_manifest_hash_count':len(old_hashes),'browser_CSV_rows':len(csv_rows),'browser_Markdown_rows':len(parsed),'scope':'This verifies unchanged stimuli, vectors, arithmetic, grouping and completeness. It does not upgrade failed confirmation gates or identify internal confidence.'}
# Separate posthoc contrast, decided after the registered outcomes were available.
posthoc={'status':'posthoc_cache_only_diagnostic','registered_gates_changed':False,'num_sources':48,'neutral_answer_propositions':96,'bootstrap_samples':cfg['analysis']['bootstrap_samples'],'bootstrap_seed':cfg['analysis']['bootstrap_seed'],'source_grouping':'All worlds and both answer keys stay together within each base source.','question':'Does a frozen confidence vector respond to a queried role being present even when its identical answer is contradicted?','limitations':['Correctness and supplied support covary in this closed-world task.','The omitted context changes one role label from world A and two from world B.','This diagnostic was selected after outcomes and does not establish internal belief, causal control, or a new confirmation gate.'],'readouts':{}}
for name in ('layer14_boundary','layer14_final_content','layer14_response_mean'):
    score=all_scores[name]; good=np.array([score[a]-score[b] for a,b in pairs['neutral_supported_vs_omitted']]); bad=np.array([score[a]-score[b] for a,b in omitted_false]); truth=np.array([score[a]-score[b] for a,b in pairs['neutral_true_vs_false']])
    assert np.max(np.abs(good-bad-truth))<1e-12
    def diagnostic(selected):
        chosen=[pairs['neutral_supported_vs_omitted'][j] for j in selected]
        g=good[selected]; b=bad[selected]; t=truth[selected]
        return {'supported_vs_omitted':{'ordering':ordering(g,chosen),'mean_margin':stat(g,chosen)},'contradicted_vs_omitted':{'ordering':ordering(b,chosen),'mean_margin':stat(b,chosen)},'supported_vs_contradicted_reference':{'ordering':ordering(t,chosen),'mean_margin':stat(t,chosen)},'paired_difference_supported_minus_contradicted_omission_margins':stat(g-b,chosen),'paired_difference_supported_minus_contradicted_omission_ordering':stat(np.sign(g)/2-np.sign(b)/2,chosen)}
    entry=diagnostic(list(range(96)))
    for field in ('fact_type','answer_key'):
        entry['by_'+field]={}
        for value in sorted({str(rows[a][field]) for a,b in pairs['neutral_supported_vs_omitted']}):entry['by_'+field][value]=diagnostic([j for j,(a,b) in enumerate(pairs['neutral_supported_vs_omitted']) if str(rows[a][field])==value])
    posthoc['readouts'][name]=entry
posthoc['source_artifact_sha256']={name:sha((output/name).read_bytes()) for name in ('extraction_rows.jsonl','hidden_states.npz','frozen_directions.npz','separation_metrics.json')}

posthoc['readout_score_correlations']={}
posthoc['correlation_interpretation']='Empirical descriptive correlations compare frozen confidence vectors with old correct-minus-incorrect contrasts. They do not validate those contrasts as correctness probes. Within-base centering removes entity means but retains wording and context variation.'
def pearson(a,b):
    a=np.asarray(a,dtype=np.float64); b=np.asarray(b,dtype=np.float64); ac=a-a.mean(); bc=b-b.mean()
    denom=float(np.linalg.norm(ac)*np.linalg.norm(bc))
    return None if denom<1e-12 else float(ac@bc/denom)
for name in ('layer14_boundary','layer14_final_content','layer14_response_mean'):
    confidence=all_scores[name]; contrast=all_scores[name+'_correctness']; centered_v=confidence.copy(); centered_c=contrast.copy()
    layer,pos=reps[name]; feature=h[:,layer,pos].astype(np.float64); centered_feature=feature.copy()
    for sid in sorted({r['source_id'] for r in rows}):
        group=[i for i,r in enumerate(rows) if r['source_id']==sid]
        centered_v[group]-=confidence[group].mean(); centered_c[group]-=contrast[group].mean(); centered_feature[group]-=feature[group].mean(0)
    covariance_scores=float(centered_v@centered_c/(len(rows)-1))
    covariance_projection=float((centered_feature@v[name])@(centered_feature@v[name+'_correctness'])/(len(rows)-1))
    margins_v=np.array([confidence[a]-confidence[b] for a,b in pairs['certainty_wording']])
    margins_c=np.array([contrast[a]-contrast[b] for a,b in pairs['certainty_wording']])
    source_pair_ix=[]
    for sid in sorted({r['source_id'] for r in rows}):
        group=[j for j,(a,b) in enumerate(pairs['certainty_wording']) if rows[a]['source_id']==sid]
        assert len(group)==4
        source_pair_ix.append(group)
    source_pair_ix=np.array(source_pair_ix)
    rng=np.random.default_rng(cfg['analysis']['bootstrap_seed'])
    draws=rng.integers(0,48,size=(cfg['analysis']['bootstrap_samples'],48))
    sample_ix=source_pair_ix[draws].reshape(cfg['analysis']['bootstrap_samples'],192)
    correlations=[pearson(margins_v[j],margins_c[j]) for j in sample_ix]
    finite=[r for r in correlations if r is not None]; interval=None
    if finite:
        lo,hi=np.percentile(finite,[2.5,97.5]); interval={'lower':float(lo),'upper':float(hi)}
    posthoc['readout_score_correlations'][name]={
        'geometric_cosine':float(v[name]@v[name+'_correctness']/(np.linalg.norm(v[name])*np.linalg.norm(v[name+'_correctness']))),
        'all672_rows_Pearson':pearson(confidence,contrast),
        'within_base_centered_all672_rows_Pearson':pearson(centered_v,centered_c),
        'certainty_pair_margin_Pearson':{'correlation':pearson(margins_v,margins_c),'n_pairs':192,'n_sources':48,'source_bootstrap_95':interval,'nondegenerate_bootstrap_draws':len(finite)},
        'within_base_centered_covariance':{'score_covariance':covariance_scores,'v_T_Sigma_c_via_centered_feature_projections':covariance_projection,'absolute_difference':abs(covariance_scores-covariance_projection),'sample_denominator':671}}
    assert abs(covariance_scores-covariance_projection)<1e-10

audit['auditor']='fresh_separation_design'
audit['auditor_source_path']='scripts/audit_confidence_separation_v3.py'
audit['auditor_source_sha256']=sha(Path(__file__).read_bytes())
posthoc['reproduction_script']={'path':audit['auditor_source_path'],'sha256':audit['auditor_source_sha256']}
# This verifier may overwrite only its own two derived artifacts.
for name,value in (('independent_audit.json',audit),('posthoc_context_availability.json',posthoc)):
    (output/name).write_text(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8')
summary={'passed':audit['passed'],'integrity_checks':len(checks),'max_row_score_abs_error':max_score_error,'max_metric_abs_error':max_metric_error,
    'auditor_source_sha256':audit['auditor_source_sha256'],'posthoc_contradicted_vs_omitted':{name:value['contradicted_vs_omitted']['ordering'] for name,value in posthoc['readouts'].items()}}
print(json.dumps(summary,sort_keys=True,indent=2,allow_nan=False))
if not audit['passed']:
    raise SystemExit('Independent artifact integrity audit failed: '+', '.join(errors))

