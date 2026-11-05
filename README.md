# Reward hacking in review bots: a labeled audit

Do reviewer agents earn the PASS and APPROVED verdicts they give? This repository holds a sanitized dataset of 255 gate verdicts from a real multi-agent website review team, a locked labeling rubric, two independent rater passes, and a short writeup.

Nothing here identifies clients, private repositories, or employers. Private paths and URLs are replaced with placeholders such as `[the agency]`, `[site-repo]`, `[preview-url]`, and `[local-path]`.

## Headline findings
- Blind inter-rater agreement on grounding is solid: Cohen's kappa **0.724**, raw agreement **0.948**, on 252 scored verdicts (3 parse errors excluded).
- After a documented post-hoc adjudication of three CI-pending approvals (cards 118, 128, and 155), kappa is **0.798** with raw agreement **0.960**. Cite the blind number unless you are discussing the adjudication.
- After adjudication, rater 1 labels **160 of 186** scored passes GROUNDED, **25** PARTIAL, and **1** UNGROUNDED.
- **38 of 187** pass verdicts were followed within 7 days by a merged fix PR that touched the same non-generated files and had a fix-like title.
- Flag kappas are exploratory. Only F1 (head) is reliable at 0.887. Rare flags swing kappa with a single disagreement.

## Layout
- `rubric/`: locked labeling rubric (v1) and the pilot draft
- `labels/`: sanitized rating cards (`cards_v2.jsonl`), rater 1 and rater 2 labels, overrides, and disagreements
- `analysis/`: kappa and metrics scripts and JSON outputs, including the post-adjudication file
- `pipeline/`: extraction, join, sanitize, card, and rater scripts (raw private inputs are not included)
- `data/processed/verdicts.jsonl`: sanitized joined verdicts
- `writeup/draft_v2.md`: the writeup

v1 truncated cards and the keyword-checker rater are kept as a methods lesson. Raw GitHub extracts and private review notes are not published.

## How to reproduce the kappa
```bash
python3 analysis/kappa_model_v2.py
# post-adjudication numbers are in analysis/kappa_model_v2_adjudicated.json
```

## License
MIT. See LICENSE.
