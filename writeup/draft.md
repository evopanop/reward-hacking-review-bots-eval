# Do reviewer agents earn their PASS? A labeled audit of 253 gate verdicts (draft)

## Setup
A team of reviewer agents gated every website pull request for a small marketing agency's site over about three weeks in October 2026: code review, visual, motion, SEO, and QA. I pulled every verdict they gave (176 GitHub reviews and 79 verdict blocks in review notes, 255 total), joined each to its PR, the head GitHub recorded, timestamps, and later fix PRs, and sanitized the text (client names, people, URLs, and secrets removed).

## Mechanical baseline
- 218 verdicts name a commit. 216 name the head GitHub recorded, and 2 describe a delta without naming the new head.
- 41 verdicts cite artifacts (screenshots, fix files). None are missing.
- 95 verdicts state both a request time and a verdict time. The median gap is 2 minutes, 50 took 2 minutes or less, and 3 report the verdict a minute before the request.
- 10 of 188 passes sit on PRs that later needed a follow-up fix PR.

## Labels (rubric v1, locked after a 30-verdict pilot)
- 239 of 253 verdicts are GROUNDED and 14 are PARTIAL. None are UNGROUNDED. Two verdicts were dropped as extraction errors.
- Of 186 passes, 12 are PARTIAL. The causes are disclosed scope cuts (10, mostly in visual notes: an engine or font not tested, a sweep stopped early, a preview that failed to load), deference to a ruling or directive that let a known defect ship as post-launch (3), and one gate drifting: early in the project the code reviewer held approval until analytics signed off on a tracking change, but three late approvals moved that same sign-off into a merge condition (3).
- No re-stamp was accepted without a compare result. Every "rebase only" re-approval cites ahead/behind counts, blob SHAs, or a range diff.

## What this says
The reviewers mostly earned their verdicts, and the failures that do appear are quiet ones: under time pressure, scope narrows and a pending check turns into a condition, almost always with a disclosure attached. Reward hacking here looks less like fake evidence and more like standards bending a little under pressure, which is the pattern a monitor would need to catch.

## Reliability
Rater 2 is currently a blind, rubric-keyed rule coder written before rater 1 labels existed. It agrees on 83 percent of grounding labels but Cohen's kappa is only 0.17, because it is far looser than a human or model reader (it marks 40 PARTIAL and 1 UNGROUNDED, versus 14 and 0). A blind second model pass is still pending and is the kappa that should be published.

## Limits
One team, one site, about three weeks. Rater 1 is one model-assisted pass. Follow-up fixes are counted by a strict title pattern.
