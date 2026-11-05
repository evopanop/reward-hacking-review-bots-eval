import json,os,collections
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(p): return {json.loads(l)['vid']:json.loads(l) for l in open(p) if l.strip()}
a=load(f'{R}/labels/rater1_v2.jsonl'); b=load(f'{R}/labels/rater2_model_v2.jsonl')
common=[k for k in a if k in b]
ids=[k for k in common if not a[k].get('parse_error') and not b[k].get('parse_error')]
def kappa(x,y):
  n=len(x);po=sum(p==q for p,q in zip(x,y))/n;cx,cy=collections.Counter(x),collections.Counter(y)
  pe=sum(cx[k]*cy[k] for k in set(x)|set(y))/n/n
  return {'kappa':round((po-pe)/(1-pe),3) if pe<1 else None,'agreement':round(po,3)}
F=['F1_head','F2_scope_cut','F3_restamp','F4_condition_offload','F5_unbacked_claim','F6_deference']
out={'n_rater1':len(a),'n_rater2':len(b),'n_common':len(common),'n_used':len(ids),
     'excluded_parse_error':len(common)-len(ids),
     'grounding':kappa([a[i]['grounding'] for i in ids],[b[i]['grounding'] for i in ids])}
for f in F: out[f]=kappa([bool(a[i][f]) for i in ids],[bool(b[i][f]) for i in ids])
dis=[]
for i in ids:
  fd=[f for f in F if bool(a[i][f])!=bool(b[i][f])]
  if a[i]['grounding']!=b[i]['grounding'] or fd:
    dis.append(dict(vid=i,r1=a[i]['grounding'],r2=b[i]['grounding'],flag_diffs=fd,r1_note=a[i].get('note'),r2_note=b[i].get('note')))
out['grounding_disagreements']=sum(d['r1']!=d['r2'] for d in dis)
out['any_disagreements']=len(dis)
out['grounding_confusion']={f'{x}->{y}':c for (x,y),c in collections.Counter((a[i]['grounding'],b[i]['grounding']) for i in ids).items()}
json.dump(out,open(f'{R}/analysis/kappa_model_v2.json','w'),indent=1)
with open(f'{R}/analysis/disagreements_model_v2.jsonl','w') as o:
  for d in dis:o.write(json.dumps(d)+'\n')
print(json.dumps(out,indent=1))
