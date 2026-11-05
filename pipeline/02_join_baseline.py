"""Join verdicts with PR metadata, then run mechanical checks:
 commit_match: claimed SHA vs head GitHub recorded when the review was submitted (gh commit_id),
   and for notes, vs the set of heads GitHub saw on that PR in any review plus the final head.
 artifacts: every file path the verdict text cites, checked for existence on disk.
 followups: later PRs whose title or body cite this PR number with fix language."""
import json,re,os,collections
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTES='[local-path]'
prs={p['number']:p for p in json.load(open(f'{ROOT}/data/raw/prs.json'))}
V=[json.loads(l) for l in open(f'{ROOT}/data/interim/verdicts_raw.jsonl')]
CL=[r'(?:at|head|of|Reviewed head|re-?review of|re-?gate of)\s+`?(?:head\s+)?`?([0-9a-f]{7,40})',r'\.\.\.?\s*`?([0-9a-f]{7,40})']
def claimed(text):
    head=text[:600]
    for pat in CL:
        ms=re.findall(pat,head,re.I)
        if ms: return ms[-1] if pat.startswith(r'\.') else ms[0]
    m=re.search(r'\b[0-9a-f]{7,40}\b',head); return m.group(0) if m else None
seen=collections.defaultdict(set)
for v in V:
    if v['gh_commit_id']: seen[v['pr']].add(v['gh_commit_id'])
PATH=re.compile(r'`?((?:analysis/|[local-path])[\w./\-]+\.(?:css|png|md|json|txt|html|csv|js))`?|`((?:pr\d+|fontfix|rebase)[\w./\-]*\.(?:css|png|md|json))`')
def artifacts(v):
    res=[]
    for a,b in PATH.findall(v['text']):
        p=a or b
        cands=[p] if p.startswith('/') else [os.path.join('[local-path]',p),os.path.join(NOTES,p),os.path.join(NOTES,os.path.dirname(v.get('file') or ''),p)]
        res.append(dict(path=p,present=any(os.path.exists(c) for c in cands)))
    return res
def followups(n):
    out=[]
    for m,p in prs.items():
        if m<=n: continue
        t=(p['title']+' '+p['body'])
        if re.search(rf'#{n}\b',p['title']) or re.search(rf'(?:fix(?:es)?|follow-?up to|regression (?:from|in)|revert(?:s)?|broken by|introduced (?:by|in))\s+(?:the\s+)?(?:PR\s+)?#{n}\b',t,re.I):
            out.append(m)
    return out
fu={n:followups(n) for n in prs}
from datetime import datetime,timedelta
MON={m:i+1 for i,m in enumerate('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split())}
TP=re.compile(r'(?:(\d{1,2}:\d{2}) ?([AP]M) PT,? (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d{1,2}),? (\d{4})|(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d{1,2}),? (\d{4}),? (\d{1,2}:\d{2}) ?([AP]M) PT)')
def ptime(m):
    g=m.groups()
    if g[0]: hm,ap,mo,d,y=g[0],g[1],g[2],g[3],g[4]
    else: mo,d,y,hm,ap=g[5],g[6],g[7],g[8],g[9]
    h,mi=map(int,hm.split(':')); h=h%12+(12 if ap=='PM' else 0)
    return datetime(int(y),MON[mo],int(d),h,mi)
def ts_check(v):
    t=v['text'][:700]
    rq=re.search(r'Request(?:ed| time):?\s*'+TP.pattern,t); vd=re.search(r'Verdict(?: time)?:?\s*'+TP.pattern,t)
    if not(rq and vd): return None
    a=ptime(TP.search(rq.group(0))); b=ptime(TP.search(vd.group(0)))
    out={'request':a.isoformat(),'verdict':b.isoformat(),'minutes':(b-a).total_seconds()/60}
    if b<a: out['flag']='verdict_before_request'
    if v.get('ts'):
        sub=datetime.fromisoformat(v['ts'].replace('Z',''))-timedelta(hours=7 if sub_dst(v['ts']) else 8)
        out['gh_submit_pt']=sub.isoformat(); out['claim_vs_submit_min']=(sub-b).total_seconds()/60
    return out
def sub_dst(ts): return ts[:10] < '2026-11-01'
rows=[]
for v in V:
    p=prs.get(v['pr']) or {}
    c=claimed(v['text']) if v['source']=='github_review' else v['claimed_sha']
    if v['source']=='github_review':
        gh=v['gh_commit_id']
        named=gh[:7] in v['text']
        cm=True if named else (None if not c else False)
        basis='gh_commit_id_at_submit'
    else:
        heads=seen.get(v['pr'],set())|({p['head_sha']} if p else set())
        cm=None if not c else any(h.startswith(c) for h in heads)
        basis='any_known_head_on_pr'
    arts=artifacts(v)
    ts_issue=ts_check(v)
    rows.append(dict(ts_issue=ts_issue,**{k:v[k] for k in v if k not in ('text','claimed_sha')},claimed_sha=c,commit_match=cm,commit_basis=basis,
        pr_title=p.get('title'),pr_merged=p.get('merged'),pr_final_head=p.get('head_sha'),
        artifacts_cited=len(arts),artifacts_missing=[a['path'] for a in arts if not a['present']],
        followup_fix_prs=fu.get(v['pr'],[]),text=v['text']))
os.makedirs(f'{ROOT}/data/processed',exist_ok=True)
with open(f'{ROOT}/data/interim/joined.jsonl','w') as o:
    for r in rows: o.write(json.dumps(r)+'\n')
# baseline summary
S={}
for src in ['github_review','box_note','all']:
    R=[r for r in rows if src=='all' or r['source']==src]
    wc=[r for r in R if r['claimed_sha']]
    S[src]=dict(n=len(R),with_claimed_sha=len(wc),commit_match=sum(1 for r in wc if r['commit_match']),commit_mismatch=sum(1 for r in wc if r['commit_match'] is False),
      cite_artifacts=sum(1 for r in R if r['artifacts_cited']),missing_artifact_verdicts=sum(1 for r in R if r['artifacts_missing']),
      pass_verdicts=sum(1 for r in R if r['verdict'] in('PASS','PASS_COND')),pass_on_pr_with_followup_fix=sum(1 for r in R if r['verdict'] in('PASS','PASS_COND') and r['followup_fix_prs']))
json.dump(S,open(f'{ROOT}/analysis/baseline_summary.json','w'),indent=1)
T=[r['ts_issue'] for r in rows if r['ts_issue']]
S['timestamps']=dict(with_request_and_verdict=len(T),verdict_before_request=sum(1 for t in T if t.get('flag')),
  median_minutes=sorted(t['minutes'] for t in T)[len(T)//2] if T else None,
  le_2_min=sum(1 for t in T if 0<=t['minutes']<=2),
  claimed_verdict_more_than_10min_off_gh_submit=sum(1 for t in T if 'claim_vs_submit_min' in t and abs(t['claim_vs_submit_min'])>10))
json.dump(S,open(f'{ROOT}/analysis/baseline_summary.json','w'),indent=1)
print(json.dumps(S,indent=1))
for r in rows:
    if r['commit_match'] is False: print('MISMATCH',r['vid'][:50],r['pr'],r['claimed_sha'],(r['gh_commit_id'] or '')[:10])
for r in rows:
    if r['artifacts_missing']: print('MISSING',r['vid'][:60],r['artifacts_missing'][:3])
