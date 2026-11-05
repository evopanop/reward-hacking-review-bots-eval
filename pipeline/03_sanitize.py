"""Sanitize verdict text for public release. Rules: people as roles or first names at most,
no client identifiers, no employer name, no secrets, tokens, or private URLs.
Produces data/processed/verdicts.jsonl and fails loudly if any banned pattern survives."""
import json,re,os,sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R=[ # order matters: longest first
 (r'[employer]\s?U\b|\bPrager\b','[employer]'),
 (r'\bN\.?D\.?A\.?s?\b','[confidentiality term]'),
 (r'\b951 Marketing\b|\b951\b(?= Marketing)','[former agency name]'),
 (r'\bAmanda(?: [surname])?\b','[client contact A]'),(r'\bRob(?: [surname])?\b(?!ot)','[client contact B]'),(r'\bLacey(?: [surname])?\b','[client contact C]'),
 (r'\bBrad\b','[client contact D]'),(r'\b(?:[surname]|[surname]|[surname])\b','[surname]'),(r'\([area code]\)|\b951\b','[area code]'),
 (r'\bDFW [client 1 service]\b','[client 1]'),(r'\[client-2-slug]\b','[client 1 service]'),(r'\bThe Gym(?: [client city])?\b','[client 2]'),
 (r'(?i)[client-5-slug]','[client-5-slug]'),(r'(?i)[a-z]*-?[client-2-slug]','[client-2-slug]'),(r'Desert Outdoor Co\.|[demo label]','[demo label]'),(r'\bJunk Control\b','[client 3]'),(r'\bjunk-control\b','[client-3-slug]'),(r'\bvegas-dumpsters\b','[client-4-slug]'),(r'\bJunk\b','[client 3]'),(r'\bSolve For Why(?: TV| Academy)?\b','[client 6]'),(r'\bVegas Dumpsters\b','[client 4]'),(r'\bHorizon Patios\b','[client 5]'),(r'\bHorizon\b','[client 5]'),
 (r'\bDFW\b','[client 1]'),(r'\bLas Vegas\b|\bMurrieta\b','[client city]'),
 (r'https?://[^\s)`"\']*[preview host]\.page[^\s)`"\']*','[preview-url]'),(r'[\w-]*\.[preview host]\.page\b','[preview-url]'),(r'(?i)\bkinsta\b','[preview host]'),
 (r'https?://(?:www\.)?winwithprime\.com[^\s)`"\']*','[site-url]'),(r'\bwinwithprime\.com\b','[site-domain]'),
 (r'https?://github\.com/[owner][^\s)`"\']*','[repo-url]'),(r'\bevopanop\b','[owner]'),(r'[site-repo]','[site-repo]'),
 (r'\bPrime Marketing\b','[the agency]'),(r'\bPrime\b','[the agency]'),
 (r'[\w.+-]+@[\w-]+\.[\w.]+','[email]'),
 (r'\b(?:ghp|gho|ghs|github_pat)_[A-Za-z0-9_]{20,}\b','[secret]'),(r'\bsk-[A-Za-z0-9]{20,}\b','[secret]'),(r'\bAKIA[0-9A-Z]{16}\b','[secret]'),
 (r'(?i)\b(?:api[_-]?key|secret|password|bearer)\s*[:=]\s*\S+','[secret]'),
 (r'[local-path][\w./\-]+','[local-path]'),(r'[local-path][\w./\-]+','[local-path]'),
 (r'https?://(?!(?:developer\.mozilla|www\.w3\.org|web\.dev|schema\.org))[^\s)`"\']+','[url]'),
]
BANNED=[r'[employer]',r'\bNDA\b',r'\b951\b',r'[client contact A]|[client contact C]|[surname]|[surname]|\bSmith\b',r'[client 3]|[client 4]|[client-4-slug]|[client-3-slug]|(?i:\bhorizon\b)|[client 1 service]|[client 6]',r'(?i:winwithprime|[preview host]|[owner])',r'\bPrime\b',r'ghp_|sk-[A-Za-z0-9]{20}']
def clean(s):
    if not isinstance(s,str): return s
    for a,b in R: s=re.sub(a,b,s)
    return s
def check(s):
    return [b for b in BANNED if re.search(b,s)]
out=[];bad=0
for l in open(f'{ROOT}/data/interim/joined.jsonl'):
    r=json.loads(l)
    for k in ('text','pr_title','file','vid'): r[k]=clean(r.get(k))
    r['artifacts_missing']=[clean(a) for a in r['artifacts_missing']]
    hits=check(json.dumps(r))
    if hits: bad+=1; print('LEAK',r['vid'],hits)
    out.append(r)
os.makedirs(f'{ROOT}/data/processed',exist_ok=True)
with open(f'{ROOT}/data/processed/verdicts.jsonl','w') as o:
    for r in out: o.write(json.dumps(r)+'\n')
print(len(out),'sanitized;',bad,'with leaks'); sys.exit(1 if bad else 0)
