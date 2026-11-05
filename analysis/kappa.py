import json,os,collections
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
a={json.loads(l)['vid']:json.loads(l) for l in open(f'{R}/labels/rater1.jsonl')}
b={json.loads(l)['vid']:json.loads(l) for l in open(f'{R}/labels/rater2_blind.jsonl')}
ids=[k for k in a if not a[k]['parse_error']]
def kappa(x,y):
  n=len(x);po=sum(p==q for p,q in zip(x,y))/n;cx,cy=collections.Counter(x),collections.Counter(y)
  pe=sum(cx[k]*cy[k] for k in set(x)|set(y))/n/n;return round((po-pe)/(1-pe),3) if pe<1 else None,round(po,3)
out={'n':len(ids),'grounding':kappa([a[i]['grounding'] for i in ids],[b[i]['grounding'] for i in ids])}
for f in ['F1_head','F2_scope_cut','F3_restamp','F4_condition_offload','F5_unbacked_claim','F6_deference']:
  out[f]=kappa([a[i][f] for i in ids],[b[i][f] for i in ids])
dis=[dict(vid=i,r1=a[i]['grounding'],r2=b[i]['grounding'],r1_note=a[i]['note']) for i in ids if a[i]['grounding']!=b[i]['grounding']]
out['grounding_disagreements']=len(dis)
json.dump(out,open(f'{R}/analysis/kappa.json','w'),indent=1)
with open(f'{R}/labels/disagreements.jsonl','w') as o:
  for d in dis:o.write(json.dumps(d)+'\n')
print(json.dumps(out))
