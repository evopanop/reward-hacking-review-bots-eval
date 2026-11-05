"""v2 rating cards: FULL sanitized verdict text, no truncation. Writes labels/cards_v2.jsonl.
Text source: data/interim/verdicts_raw_v2.jsonl (01b, no 6000-char clip), cleaned with the same
sanitizer rules as 03_sanitize.py and checked against its BANNED list. Same vids and order as v1 cards."""
import json,os,sys
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src=open(f'{R}/pipeline/03_sanitize.py').read(); ns={'__file__':f'{R}/pipeline/03_sanitize.py'}
exec(src.split('out=[];bad=0')[0],ns); clean,check=ns['clean'],ns['check']
v1=[json.loads(l) for l in open(f'{R}/labels/cards.jsonl')]
raw={}
for l in open(f'{R}/data/interim/verdicts_raw_v2.jsonl'):
  x=json.loads(l); raw[clean(x['vid'])]=x
leaks=0;fixed=0;missing=0;out=[]
for c in v1:
  x=raw.get(c['vid'])
  if x is None: missing+=1; print('MISSING',c['vid'],file=sys.stderr); continue
  t=clean(x['text'])
  if len(c['body'])<len(t): fixed+=1
  card=dict(vid=c['vid'],pr=c['pr'],gate=c['gate'],verdict=c['verdict'],commit_match=c['commit_match'],ts_flag=c['ts_flag'],body=t)
  h=check(json.dumps(card))
  if h: leaks+=1; print('LEAK',c['vid'],h,file=sys.stderr)
  out.append(card)
with open(f'{R}/labels/cards_v2.jsonl','w') as o:
  for c in out: o.write(json.dumps(c)+'\n')
st=dict(cards=len(out),truncation_fixed=fixed,missing=missing,leaks=leaks,
 max_len=max(len(c['body']) for c in out),v1_body_max=max(len(c['body']) for c in v1))
json.dump(st,open(f'{R}/labels/cards_v2_stats.json','w'),indent=1);print(st)
sys.exit(1 if leaks or missing else 0)
