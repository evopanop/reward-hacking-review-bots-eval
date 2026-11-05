import json,os,collections
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V={json.loads(l)['vid']:json.loads(l) for l in open(f'{R}/data/processed/verdicts.jsonl')}
A=[json.loads(l) for l in open(f'{R}/labels/rater1.jsonl')];A=[a for a in A if not a['parse_error']]
F=['F1_head','F2_scope_cut','F3_restamp','F4_condition_offload','F5_unbacked_claim','F6_deference']
pas=[a for a in A if V[a['vid']]['verdict'] in('PASS','PASS_COND')]
m=dict(n_labeled=len(A),n_pass=len(pas),grounding_all=collections.Counter(a['grounding'] for a in A),
 grounding_pass=collections.Counter(a['grounding'] for a in pas),flags_all={f:sum(a[f] for a in A) for f in F},
 by_source={s:collections.Counter(a['grounding'] for a in A if V[a['vid']]['source']==s) for s in('github_review','box_note')},
 baseline=json.load(open(f'{R}/analysis/baseline_summary.json')),kappa=json.load(open(f'{R}/analysis/kappa.json')))
json.dump(m,open(f'{R}/analysis/metrics.json','w'),indent=1,default=dict);print(json.dumps(m,default=dict)[:1500])
