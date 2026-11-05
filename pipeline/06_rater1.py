import json,os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
O=json.load(open(f'{R}/labels/rater1_overrides.json'));F=['F1_head','F2_scope_cut','F3_restamp','F4_condition_offload','F5_unbacked_claim','F6_deference']
with open(f'{R}/labels/rater1.jsonl','w') as o:
  for i,l in enumerate(open(f'{R}/labels/cards.jsonl')):
    c=json.loads(l);x=O.get(str(i),{})
    o.write(json.dumps(dict(vid=c['vid'],grounding=x.get('grounding','GROUNDED'),parse_error=x.get('parse_error',0),note=x.get('why',''),**{f:x.get(f,0) for f in F}))+'\n')
