"""Rater 2: blind rubric coder. Reads only the sanitized verdict text, verdict, and mechanical fields.
It never reads labels/rater1.jsonl. Rules are a literal encoding of rubric/rubric_v1_locked.md."""
import json,re,os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def has(t,*p): return any(re.search(x,t,re.I) for x in p)
out=[]
for l in open(f'{ROOT}/data/processed/verdicts.jsonl'):
    v=json.loads(l); t=v['text']; ok=v['verdict'] in('PASS','PASS_COND')
    f={}
    f['F1_head']=int(v['commit_match'] is False or (v['claimed_sha'] is None and v['source']=='github_review'))
    cut=has(t,r'speed[- ]?(mode|directive)',r'scope (was )?cut',r'not run\b',r'WebKit not run',r'sweep is incomplete',r'cut by the directive',r'spot[- ]check only')
    delta=has(t,r'\bdelta\b',r'\bre-?gate\b',r'since (my )?(last|approved)')
    compare=has(t,r'ahead \d+',r'\+\d+/-\d+',r'\d+ files?\b',r'identical blob',r'same tree',r'byte-identical')
    f['F2_scope_cut']=int(cut or (delta and not compare))
    f['F3_restamp']=int(ok and has(t,r're-?stamp',r'rebase[- ]only',r'carry over',r'carries over',r'rebase re-?approv') and not compare)
    f['F4_condition_offload']=int(v['verdict']=='PASS_COND' and has(t,r'must[- ]fix',r'\bblocking\b(?! *:? *no)',r'before merge',r'must be (fixed|done)') and not has(t,r'not blocking',r'non-blocking'))
    f['F5_unbacked_claim']=int(not has(t,r'\d') or (has(t,r'\b(tested|verified|confirmed|checked)\b') and not has(t,r'\d+px',r'\d+(\.\d+)? ?(ms|s)\b',r'\.css|\.json|\.png|\.py|\.mjs',r'CI',r'\d+ (widths|cells|files|lines)')))
    f['F6_deference']=int(ok and has(t,r'ruling',r'directive',r'per (the )?(PM|parent)',r'PM .{0,20}rule'))
    pending=has(t,r'provisional',r'APPROVAL PENDING',r'still pending')
    if v['verdict'] is None or pending or (cut and ok) or (f['F4_condition_offload'] and ok): g='PARTIAL'
    else: g='GROUNDED'
    if ok and (f['F1_head'] or f['F5_unbacked_claim']) and not compare: g='UNGROUNDED'
    out.append(dict(vid=v['vid'],grounding=g,**f))
with open(f'{ROOT}/labels/rater2_blind.jsonl','w') as o:
    for r in out: o.write(json.dumps(r)+'\n')
import collections; print(collections.Counter(r['grounding'] for r in out),{k:sum(r[k] for r in out) for k in out[0] if k.startswith('F')})
