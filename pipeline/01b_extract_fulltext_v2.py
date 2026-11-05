"""v2: same extraction as 01_extract.py but WITHOUT the 6000-character clip on box-note verdict blocks.
Writes data/interim/verdicts_raw_v2.jsonl. Verdict boundaries, vids and fields are unchanged."""
import os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src=open(f'{R}/pipeline/01_extract.py').read()
assert src.count('[-6000:]')==1
src=src.replace('[-6000:]','').replace("verdicts_raw.jsonl","verdicts_raw_v2.jsonl")
exec(compile(src,f'{R}/pipeline/01_extract.py','exec'),{'__file__':f'{R}/pipeline/01_extract.py','__name__':'__main__'})
