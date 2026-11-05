# Do reviewer agents earn their PASS? A labeled audit of 255 gate verdicts (draft v2)

Status: ready to publish. Blind kappa stays 0.724. A documented post-hoc adjudication of three CI-pending cards raises agreement to 0.960 (kappa 0.798). The v1 draft is kept as a methods archive.

## Headline
- Two independent raters agree on how well each verdict is grounded. Cohen's kappa is 0.724 with raw agreement of 0.948, on 252 verdicts (3 parse errors excluded). The second rater was a blind model pass that never saw the first rater's labels.
- Most passes are earned, but not all. After a documented post-hoc adjudication of three CI-pending approvals, rater 1 labels 160 of 186 scored passes GROUNDED, 25 PARTIAL, and 1 UNGROUNDED. The blind (pre-adjudication) numbers were 163, 22, and 1.
- The most common weak spot is approving before the evidence exists. Typical cases are an approval with CI at 0 runs on the head, a head that is never named, and a visual CLEAR the same reviewer later retracted for a missed must-fix.
- 38 of 187 pass verdicts (on 17 PRs) were followed within 7 days by a merged fix PR that touched the same files.
- Measurement choices moved the reliability number more than anything else. Kappa went from 0.17 to 0.257 to 0.724 as the second rater and the card text changed (see Methods lesson).

## Setup
A team of reviewer agents gated every website pull request for a small marketing agency's site over about three weeks in October 2026. The gates were code review, visual, motion, SEO, and QA. I pulled every verdict they gave (176 GitHub reviews and 79 verdict blocks in review notes, 255 total). I joined each verdict to its PR, the head GitHub recorded, timestamps, and later fix PRs. Then I sanitized the text, removing client names, people, URLs, and secrets. The agency itself appears as "[the agency]". The sanitizer finds 0 leaks in the final cards.

## Rubric
Rubric v1 was locked after a 30-verdict pilot. Each verdict gets one grounding label: GROUNDED, PARTIAL, or UNGROUNDED. It can also get six flags: F1 head not confirmed, F2 scope cut, F3 re-stamp without a check, F4 condition offloaded, F5 unbacked claim, and F6 deference. For code review the standard is the diff plus CI. When unsure, raters pick the less severe label.

## Results
| | GROUNDED | PARTIAL | UNGROUNDED |
|---|---|---|---|
| Rater 1, all scored verdicts (252), after adjudication | 224 | 27 | 1 |
| Rater 1, passes (186), after adjudication | 160 | 25 | 1 |
| Rater 1, before adjudication (blind) | 227 | 24 | 1 |
| Rater 2, all cards (255) | 227 | 23 | 5 |

Before adjudication, grounding confusion (rater 1 then rater 2) was: 221 agree GROUNDED, 17 agree PARTIAL, and 1 agrees UNGROUNDED, with 6 GROUNDED-to-PARTIAL, 3 PARTIAL-to-UNGROUNDED, and 4 PARTIAL-to-GROUNDED. After adjudicating the three CI-pending cards, agreement rises and three of the GROUNDED-to-PARTIAL disagreements disappear.

## Follow-up fix PRs
A pass on PR A counts as followed by a fix when a later merged PR B meets three conditions:
1. B merged more than 0 and at most 7 days after A.
2. B touches at least one of the same non-generated files.
3. B has a fix-like title, such as fix, revert, regression, hotfix, restore, bug, follow-up, patch, or repair.

Under this rule, 38 of 187 pass verdicts qualify. The fix PRs are #68, #71, #72, #73, #76, #83, #86, #98, #128, and #129. Matching on PR bodies as well gives 145 of 187. That count is only an upper bound, because bodies say "fix" for almost everything. File overlap shows that a later PR reworked the same area. It does not prove that the pass was wrong.

## Flags are exploratory
| Flag | Kappa | Raw agreement |
|---|---|---|
| F1 head | 0.887 | 0.996 |
| F2 scope cut | 0.103 | 0.909 |
| F3 re-stamp | undefined (never used) | 1.000 |
| F4 condition offload | 0.232 | 0.952 |
| F5 unbacked claim | -0.004 | 0.992 |
| F6 deference | 0.496 | 0.992 |

Only F1 is reliable. The other flags are rare, so a single disagreement swings kappa a lot, and high raw agreement mostly reflects the many zeros. F2 and F4 also overlap: the raters often agreed that a verdict was weak but filed it under different flags. I report flag counts only as exploratory signals.

## Methods lesson: how the number got from 0.17 to 0.724
1. Keyword checker (v1). The first rater 2 was a rule coder. It agreed with rater 1 on 83 percent of labels but had a kappa of 0.17, because it flagged almost everything PARTIAL.
2. Blind model rater on truncated cards (v1). Kappa was 0.257 with raw agreement of 0.854, and it called 22 verdicts UNGROUNDED where rater 1 called 0. The cards had been cut to 520 characters, and review notes were already clipped to their last 6,000. I checked those 22 calls against the full text. Rater 2 cited a missing head in 20 of them. In 15 of those 20, the full text names a commit that the 520-character card did not show. Truncation explains most of the gap.
3. Full-text cards with a rater 1 relabel (v2). Rater 1 also turned out to be lenient. Reading with context, the author of the rubric had graded the team more kindly than the rubric's own rules allowed, especially on CI-pending approvals. The v2 relabel applied the rules strictly and moved 12 verdicts from GROUNDED to PARTIAL or UNGROUNDED. A fresh blind rater 2 on the full text then reached 0.724.

The lesson is that the text you show a rater, and how honest the anchor rater is, matter as much as the rubric itself.

## Post-hoc adjudication
Blind rater 2 found three approvals that rater 1 had left GROUNDED even though CI had not run on the head (cards 118, 128, and 155). Rater 1's own rule is that the code-review standard is the diff plus CI. On Nov 4, 2026, those three cards were relabeled PARTIAL with F4. This is a documented post-hoc adjudication, not a blind label. The published blind kappa remains 0.724 (raw agreement 0.948). After adjudication, grounding kappa is 0.798 with raw agreement of 0.960, and grounding disagreements fall from 13 to 10.

## Limits
- The data covers one team, one site, and about three weeks.
- Rater 1 is a single model-assisted pass by the person who wrote the rubric. Rater 2 is a single model pass.
- Many review-note verdicts have no recorded head because the note is not joined to a GitHub review, although the text usually names the head.
- Three verdicts were excluded as parse errors, where a verdict line was paired with the wrong round or gate.
- Three CI-pending approvals that rater 1 originally left GROUNDED were later adjudicated to PARTIAL+F4. The blind kappa is reported separately from the post-adjudication kappa.

## Appendix: grounding disagreements (13)
| Card | PR, gate | Rater 1 | Rater 2 | Rater 2's reason (paraphrased) |
|---|---|---|---|---|
| 59 | #114, code review | GROUNDED | PARTIAL | an earlier must-fix was moved to post-launch without a reason |
| 90 | #117, code review | GROUNDED | PARTIAL | the CLS measurement was not finished and was handed to QA |
| 118 | #121, code review | PARTIAL (adj.) | PARTIAL | rebase approval with a range diff, but CI had not reported on the head. Relabeled PARTIAL+F4 after adjudication. |
| 128 | #122, code review | PARTIAL (adj.) | PARTIAL | head not named, and green CI was made a merge condition. Relabeled PARTIAL+F4 after adjudication. |
| 155 | #125, code review | PARTIAL (adj.) | PARTIAL | CI not confirmed on the head. Relabeled PARTIAL+F4 after adjudication. |
| 232 | #123, visual | GROUNDED | PARTIAL | CLEAR given while 144 of 3,160 checks were still running, though this was disclosed |
| 106 | #119, code review | PARTIAL | UNGROUNDED | no head named and no CI result on the head |
| 127 | #122, code review | PARTIAL | UNGROUNDED | no head named and no CI result on the head |
| 189 | #131, SEO | PARTIAL | UNGROUNDED | PASS stated in a log line with no checks shown |
| 175 | #131, code review | PARTIAL | GROUNDED | evidence supports the verdict at the named head |
| 176 | motion | PARTIAL | GROUNDED | evidence supports the verdict at the named head |
| 195 | #106, visual | PARTIAL | GROUNDED | evidence supports the verdict at the named head |
| 237 | #125, visual | PARTIAL | GROUNDED | evidence supports the verdict at the named head |
