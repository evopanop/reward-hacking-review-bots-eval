"""Extract every review verdict: GitHub PR reviews plus box review notes. Output data/interim/verdicts_raw.jsonl"""
import json,re,os,glob
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTES='[local-path]'
SHA=re.compile(r'\b[0-9a-f]{7,40}\b')
def norm_verdict(s):
    u=s.upper()
    for k,v in [('NOT CLEAR','BLOCK'),('CHANGES REQUESTED','BLOCK'),('BLOCK','BLOCK'),('FAIL','BLOCK'),('APPROVED WITH CONDITIONS','PASS_COND'),('APPROVED, WITH','PASS_COND'),('APPROVED','PASS'),('CLEAR','PASS'),('PASS','PASS')]:
        if k in u: return v
    return None
out=[]
for r in json.load(open(f'{ROOT}/data/raw/reviews.json')):
    head=r['body'][:400]
    mm=re.search(r'(CHANGES REQUESTED|NOT CLEAR|APPROVED,? with (?:a merge-time )?conditions?|APPROVED|BLOCK(?!ing)|CLEAR)',head,re.I)
    v=norm_verdict(mm.group(1)) if mm else None
    m=SHA.search(head)
    out.append(dict(vid=f"gh-{r['id']}",source='github_review',pr=r['pr'],gate='code_review',verdict=v,claimed_sha=m.group(0) if m else None,
        gh_commit_id=r['commit_id'],ts=r['submitted'],text=r['body']))
VL=re.compile(r'^(?:#+\s*)?(?:\*\*)?(?:[A-Za-z ]{0,25})?Verdict[^:\n]{0,30}:\s*\**\s*(NOT CLEAR|CLEAR|PASS|FAIL|BLOCK|APPROVED[^.\n]*|CHANGES REQUESTED)',re.M)
VL2=re.compile(r'^(?:\*\*)?(SEO|Copy|CRO|QA|Motion|Visual)[^:\n]{0,40}:\s*\**\s*(PASS|FAIL|BLOCK|CLEAR|NOT CLEAR|APPROVED)',re.M|re.I)
VL3=re.compile(r'^#+\s.*#(\d{2,3})[^:\n]*:\s*(NOT CLEAR|CLEAR)',re.M)
VL4=re.compile(r'^(?:\d{1,2}:\d{2} [AP]M:? )?(SEO|QA|perf check|Copy)[^\n]{0,25}?\b(PASS|FAIL)\b',re.M)
def gate_of(path):
    p=path.lower()
    for k,g in [('motion','motion'),('visual-review','visual'),('seo','seo'),('copy','copy'),('cro','cro'),('qa','qa')]:
        if k in p: return g
    return 'visual'
for f in sorted(glob.glob(NOTES+'/**/*.md',recursive=True)):
    t=open(f,errors='ignore').read(); rel=os.path.relpath(f,NOTES)
    prs=[int(x) for x in re.findall(r'(?:PR|pr)[-_ ]?#?(\d{2,3})',rel)]
    ms=sorted([(m.start(),m) for m in VL.finditer(t)]+[(m.start(),m) for m in VL2.finditer(t)]+[(m.start(),m) for m in VL3.finditer(t)]+[(m.start(),m) for m in VL4.finditer(t)],key=lambda x:x[0])
    for i,(pos,m) in enumerate(ms):
        end=ms[i+1][0] if i+1<len(ms) else len(t)
        line=t[pos:t.find('\n',pos) if t.find('\n',pos)>0 else len(t)]
        g=gate_of(rel)
        if VL2.match(line): g=m.group(1).lower(); g='visual' if g=='visual' else g
        if VL3.match(line): prs=[int(VL3.match(line).group(1))]+prs
        if VL4.match(line): g={'seo':'seo','qa':'qa','perf check':'qa','copy':'copy'}[m.group(1).lower()]
        sh=SHA.search(line)
        # section text: up to 60 lines before (the evidence) and verdict line through next verdict
        start=max(0,ms[i-1][0] if i>0 else 0)
        out.append(dict(vid=f"note-{rel}:{t[:pos].count(chr(10))+1}",source='box_note',pr=prs[0] if prs else None,prs=prs,gate=g,
            verdict=norm_verdict(m.group(m.lastindex)),claimed_sha=sh.group(0) if sh else None,gh_commit_id=None,ts=None,file=rel,
            mtime=os.path.getmtime(f),text=t[start:end][-6000:]))
os.makedirs(f'{ROOT}/data/interim',exist_ok=True)
with open(f'{ROOT}/data/interim/verdicts_raw.jsonl','w') as o:
    for x in out: o.write(json.dumps(x)+'\n')
import collections
print(len(out),collections.Counter((x['source'],x['gate'],x['verdict']) for x in out))
