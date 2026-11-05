"""Build compact rating cards (no labels) for rater passes: labels/cards.jsonl"""
import json,re,os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIG=re.compile(r'[^\n]*(speed|directive|ruling|re-?stamp|carry|carries|not run|provisional|pending|must[- ]fix|before merge|not tested|untested|skipped|assum|incomplete|condition)[^\n]*',re.I)
with open(f'{ROOT}/labels/cards.jsonl','w') as o:
  for l in open(f'{ROOT}/data/processed/verdicts.jsonl'):
    v=json.loads(l); t=v['text']
    i=0 if v['source']=='github_review' else max(0,t.rfind('Verdict') if 'Verdict' in t else 0)
    m=re.search(r'(NOT CLEAR|CLEAR|PASS|FAIL)',t[i:i+400]) if v['source']=='box_note' else None
    body=t[i:i+520]
    sig=[s.strip()[:170] for s in SIG.findall(t) if s.strip()[:170] not in body][:0]
    sl=[x.group(0).strip()[:170] for x in SIG.finditer(t) if x.group(0).strip()[:60] not in body][:3]
    o.write(json.dumps(dict(vid=v['vid'],pr=v['pr'],gate=v['gate'],verdict=v['verdict'],commit_match=v['commit_match'],ts_flag=(v['ts_issue'] or {}).get('flag'),body=body,signals=sl))+'\n')
