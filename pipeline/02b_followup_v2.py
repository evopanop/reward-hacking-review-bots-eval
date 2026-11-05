"""Follow-up fix PRs, LOOSER rule (v2). Writes analysis/followup_v2.json.
Rule: for a pass verdict on PR P that merged, a later PR F counts as a follow-up fix when
 (a) F merged after P merged and within 7 days,
 (b) F and P share at least one changed file, ignoring generic shared files
     (llms.txt, llms-full.txt, sitemap, feed, robots, lockfiles) that nearly every post PR touches,
 (c) F is fix-like: its TITLE matches the FIX regex below (primary metric).
 Sensitivity: the same rule with title OR body is also reported. Body matching is very loose here
 because large redesign PR bodies routinely say 'fix', so it is not the headline number.
File lists come from the GitHub PR files API (data/raw/pr_files.json, filenames only).
Diff content was not used for (c); title and body only."""
import json,re,os
from datetime import datetime,timedelta
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX=re.compile(r'\b(fix(e[sd])?|regress\w*|revert\w*|hotfix|correct\w*|restore\w*|broken|bug\w*|follow-?up|patch(es|ed)?|repair\w*)\b',re.I)
GEN=re.compile(r'(^|/)(llms(-full)?\.txt|sitemap[\w.]*|feed\.xml|robots\.txt|package-lock\.json|Gemfile\.lock)$')
d=lambda s:datetime.fromisoformat(s.replace('Z','+00:00'))
prs={p['number']:p for p in json.load(open(f'{R}/data/raw/prs.json'))}
files={int(k):set(f for f in v if not GEN.search(f)) for k,v in json.load(open(f'{R}/data/raw/pr_files.json')).items()}
def fixes(n):
  p=prs.get(n)
  if not p or not p['merged'] or n not in files: return []
  out=[]
  for m,q in prs.items():
    if m==n or not q['merged'] or m not in files: continue
    dt=d(q['merged'])-d(p['merged'])
    if not (timedelta(0)<dt<=timedelta(days=7)): continue
    sh=files[n]&files[m]
    if not sh: continue
    hit=FIX.search(q['title']) or FIX.search(q['body'] or '')
    if hit: out.append(dict(fix_pr=m,title=q['title'],days=round(dt.total_seconds()/86400,2),shared=sorted(sh)[:5],n_shared=len(sh),matched=hit.group(0),by='title' if FIX.search(q['title']) else 'body'))
  return out
V=[json.loads(l) for l in open(f'{R}/data/processed/verdicts.jsonl')]
passes=[v for v in V if v['verdict'] in('PASS','PASS_COND') and v['pr']]
pairs={}
for n in sorted({v['pr'] for v in passes}):
  f=fixes(n)
  if f: pairs[n]=f
hit=[v for v in passes if v['pr'] in pairs]
title_only={n:[x for x in f if x['by']=='title'] for n,f in pairs.items()}
title_only={n:f for n,f in title_only.items() if f}
res=dict(rule=__doc__,n_pass_verdicts=len(passes),n_pass_with_fix=len(hit),
 n_pass_with_fix_title_only=sum(v['pr'] in title_only for v in passes),
 pass_prs_with_fix_title=sorted(title_only),fix_prs_title=sorted({x['fix_pr'] for f in title_only.values() for x in f}),pairs_title={str(k):v for k,v in title_only.items()},pass_prs_with_fix_title_or_body=sorted(pairs),fix_prs=sorted({x['fix_pr'] for f in pairs.values() for x in f}),
 pairs={str(k):v for k,v in pairs.items()},strict_v1_pairs=['78->81','107->109','118->129'])
src=open(f'{R}/pipeline/03_sanitize.py').read(); ns={}; ns['__file__']=f'{R}/pipeline/03_sanitize.py'; exec(src.split('out=[];bad=0')[0],ns)
out=ns['clean'](json.dumps(res,indent=1)); hits=ns['check'](out)
assert not hits, hits
open(f'{R}/analysis/followup_v2.json','w').write(out)
print(res['n_pass_verdicts'],res['n_pass_with_fix'],res['n_pass_with_fix_title_only'])
for k,v in title_only.items(): print(k,[(x['fix_pr'],x['by'],x['matched'],x['title'][:60]) for x in v])
