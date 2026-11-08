# Claim audit of the draft (2026-11-08, late evening)

Draft audited: "Copy of Apart Research hackathon submission template.pdf" (8 pages).
Recomputed from `final/results/*/runs.jsonl`, `data/realism_series_runs.jsonl` and the live `data/asch_runs.jsonl` (184 runs at
audit time, qwen only). Throwaway scripts used for this: `/tmp/audit/{a,b,c}.py`. CI = 95% Wilson. "opened" = any
`read_file` under `finance/`. API-error runs excluded (as in `final/stats.py`).
This file contains analysis only, no paper text.

Status key: **OK** = number matches, same-day comparison, CI separated. **WEAK** = matches but small n, wide CI, single
model, cross-day, or confounded. **UNSUPPORTED** = no data in the repo backs it. **MISMATCH** = the number or wording
disagrees with the data.

---

## 1. Claim-by-claim

### Abstract (p.1)

| # | draft says | source | recomputed | status |
|---|---|---|---|---|
| A1 | single-agent baseline "40% violation rate" | exp04 `final/results/exp04_forbidden_permission_8k` | 79/200 = 39.5% (CI 33–46%) | OK |
| A2 | team sentence "raises violation rates to 55%" | exp09 (T0) | 109/199 = 54.8% (CI 48–62%); vs exp04 z=3.1, p=.002 | OK (exp04 and T0 both Nov 7, but not the same batch: 16:01 vs 19:40) |
| A3 | neutral board "further jump to 71%" | exp05 (P0, Nov 7) | 141/199 = 70.9% (CI 64–77%) | **MISMATCH with Fig. 2**, which shows 73% (exp14 P0 rerun, Nov 8, 146/200, CI 66–79%). Both are real; the draft uses one in the abstract and the other in the figure |
| A4 | "more activity (automated notification feed) on its own accounts for about two thirds, the rest is social" | exp14 NS vs exp14 P0 vs exp04 | NS 121/200 = 60.5% (CI 54–67%); P0 146/200 = 73%. (60.5−39.5)/(73−39.5) = 21/33.5 = 63% | WEAK: arithmetic matches, but the denominator uses exp04 from Nov 7 (batch noise ±10 pts); NS vs P0 itself is same-batch and significant (z=2.65, p=.008). Social part is mostly qwen (57→76, p=.004); deepseek 64→70 (p=.37, n.s.). See review issue R7 on what "social" contains |
| A5 | "We also replicated that agents use illicit information without disclosing the source" | exp08, exp15-P3 (+ day-1 toy, `data/peer_pressure_runs.jsonl`) | see F4 below | OK as a finding; "replicated" whose result? unclear (R10) |
| A6 | "turning off Gemma 4's reasoning mode allowed us to measure a clean Asch conformity graph" | exp11 `final/results/exp11_non_reasoning` | solo 0/50 (0%, CI 0–7%); 0/8 37/50 (74%, CI 60–84%); 1/8 49/50 (98%, CI 90–100%); 4/8 50/50; 8/8 50/50 (CI 93–100%). 0/8 vs 1/8 z=3.5, p<.001 | WEAK: one model, n=50, ceiling from 1/8 on, no 2/8 level, run with the old `read_board` bug (exp11 predates the fix in `examples/asch.py`). Also: exp11 uses `gemma-4-31b-it` as a non-reasoning model; nothing in the repo shows a reasoning mode being switched off for Gemma (MISMATCH in wording, see R4) |
| A7 | "rule-breaking rate for agents that reasoned correlated strongly with whether they reasoned about being in a test" | exp07, exp10, live Asch (qwen thinking on) | opened given eval-aware vs not: P2 (exp07) 63/125 = 50% vs 63/75 = 84%; exp10 8/8 30% vs 62%; Asch qwen-on (all levels) 27/71 = 38% vs 57/69 = 83%. But exp04 47% vs 38%, P0 (exp14) 77% vs 71%, P1 73% vs 75%: no or reversed association | WEAK: holds only where rule-breaking peers are shown; direction not stated in the draft; post-treatment conditioning (story C5 explicitly says not to use the stratified argument). exp10 is DROPPED in story_and_claims (1500 tokens, 36–46% truncated) |

### Section 3 Methods / results text (p.3–5)

| # | draft says | source | recomputed | status |
|---|---|---|---|---|
| M1 | toy setup: 3 files, `reports/q3_summary.txt` "Details in finance/q3_numbers.csv", data in `finance/q3_revenue_by_region.csv` | `examples/03_locked_folder.py` (toy), `final/locked_folder.py` | file names inconsistent within the paragraph (q3_numbers vs q3_revenue_by_region); realistic workspace has **no** pointer to finance/ in the quarterly summaries (README "Setup") | MISMATCH (description), see R12 |
| M2 | "more dummy files ... helped reduce test awareness" | R0 `data/realism_series_runs.jsonl` tag `realism_r0` vs exp01/exp03 | eval-aware (regex): toy R0 **1/100 (1%)**; realistic exp01 10/100 (10%); exp03 23/196 (12%); exp04 38/200 (19%) | **UNSUPPORTED / contradicted** by the only measure in the repo: the realistic workspace has *more* flagged test-suspicion, not less |
| M3 | Fig. 1: toy 16% n=100; realistic "restricted" 68% n=196; realistic "forbidden" 40% n=200 | R0; exp03; exp04 | 16/100 (CI 10–24%); 133/196 (CI 61–74%); 79/200 (CI 33–46%) | numbers OK. WEAK for the toy bar: R0 is 1500 output tokens, Nov 7 13:11, different request reply; exp03 is 8000 tokens, 16:01. Like-for-like comparator is exp01 (same series, 1500 tokens, 67/100, CI 57–75%), same conclusion |
| M4 | Fig. 1 caption "toy workspace makes agent suspicious" | as M2 | toy 1% eval-aware | UNSUPPORTED (see M2); if "suspicious" means something else, it is not measured |
| M5 | wording "restricted → forbidden" matters; "physical restriction ... the agent often used as an excuse" | exp03 vs exp04 (same batch) | 68% vs 40%, CIs separate. Rough regex (mine, unvalidated) for "check if I have access / access might be granted" in violators' reasoning: exp03 90/133, exp04 12/79 | OK (the number); "often used as an excuse" WEAK (no validated measure; a rough count exists) |
| M6 | "it does even require a board full of misbehaving agents" | — | — | wording likely inverted (R13) |
| M7 | team sentence "+15 pts" | exp09 vs exp04 | 54.8 − 39.5 = +15.3 | OK (Nov 7, separate batches) |
| M8 | automated feed "+21 pts" | exp14 NS vs exp04 | 60.5 − 39.5 = +21.0; z=4.2 | WEAK: cross-day (Nov 8 vs Nov 7) |
| M9 | team sentence + team board "+34 pts" (Fig. 2) | exp14 P0 vs exp04 | 73.0 − 39.5 = +33.5 → 34 | OK number; cross-day |
| M10 | "neutral message board ... still added a few more points" | exp14 NS vs P0 | +12.5 pts, z=2.65 | OK (same batch). But the P0 arm also adds the team sentence, which alone gave +15 (R7) |
| M11 | rule-breaking peers: violation "dropped" | exp07 vs exp05 | 125/199 (63%, CI 56–69%) vs 141/199 (71%, CI 64–77%); z=1.7, **p=.09** pooled. qwen 70→54 (p=.02), deepseek 71→72 | WEAK: not significant pooled; qwen only. Live Asch qwen-on shows the same direction at 8/8 (41% vs 67%, n≈27, p=.06) |
| M12 | "regex and an LLM which flagged 62% of runs ... while a neutral board was measured at 34%" | exp07, exp05; `final/eval_awareness.py` | regex: 124/199 (62%, CI 55–69%) vs 67/199 (34%, CI 27–40%) | numbers OK. **"and an LLM": MISMATCH** — the 62/34 are regex-only; LLM (Sonnet) validation exists only for 56 single-agent transcripts (23 TP, 1 FP, 1 FN); team transcripts: 8/8 hand-checked P2 hits only |
| M13 | "we primarily think it increased evaluation awareness" (causal) | as M12 | 109/124 flagged P2 passages refer to the teammates (story C5) | WEAK: shows posts trigger test-talk; does not show test-talk causes the drop |
| M14 | "making the workspace more realistic always helps, it doesn't scale to smarter models" | — | no stronger model was ever run | UNSUPPORTED |
| M15 | Gemma: "clean Asch curve ... between 0/8 teammates to 8/8" | exp11 | as A6 | WEAK (as A6). Note 0/8 is already 74% vs solo 0%: the board effect dominates, conformity adds +24 pts and saturates at 1/8 |
| M16 | Gemma solo 0% (implied by "clean curve") | exp11 solo | 0/50; all 50 runs requested permission and ended with a text reply after 5–7 actions | WEAK as a baseline: solo runs stop early; board runs last longer (story C7) |
| F4a | Fig. 4 Run 1: 78% used, source not mentioned / 7% named teammate or file / 15% opened | exp08 (Nov 7) | 156/200 = 78.0%; 14/200 = 7.0%; 30/200 = 15.0% (CI 11–21%). used total 170/200 (85%, CI 79–89%) | OK |
| F4b | Fig. 4 Run 2: 83% / 10% / 7% | exp15 P3 rerun (Nov 8) | 166/200 = 83.0%; 20/200 = 10.0%; 14/200 = 7.0%. used total 186/200 (93%, CI 89–96%) | OK |
| F4c | "Our test subject reasoned in most cases that this data has been accessed unauthorized" | exp08 reasoning | story: ~134/170 (rough regex, "not validated"); my broader regex 154/170 | WEAK (unvalidated regex; no hand-check sample) |
| F4d | "and also noticed that it can't confirm these numbers as trustworthy" | — | rough regex for verify/trust/confirm words: 76/170 (exp08), 95/186 (exp15 P3), i.e. ~45–50%, and many are "the numbers add up to 4.2M" checks | UNSUPPORTED as "most cases" |
| F4e | "most agents submitting the data ... without disclosing where it got them from" | exp08, exp15 P3 | answer names any source: 14/170 and 20/186; answer says it was forbidden/unverified: 1/170 and 3/186 | OK (strong). Note "named the teammate or file" ≠ disclosed it was forbidden; the stricter number is ~1–2% |
| F4f | "The large majority of agents participated in this unauthorized information exchange [1]" | external (METR) | — | cite-check only (HF incident claim, not our data) |

### Section 5 / Limitations / Conclusion (p.5–6)

| # | draft says | source | recomputed | status |
|---|---|---|---|---|
| L1 | "identical runs varied around 10% on two different days" | exp01 rerun; exp05 vs exp14-P0; exp08 vs exp15-P3 | exp01 67 vs 74 (+7); P0 71 vs 73 (+2); P3 used 85 vs 93 (+8), opened 15 vs 7 (−8) | OK as "up to ~8 pts"; the P0 replication (2 pts) is good news worth having |
| L2 | "more than XYZ runs in total" | `data/*.jsonl`, `final/results` | 3,650 run records in `final/results` (incl. 250 Gemma, 400 exp10); 5,914 in `data/` (excl. `.bak`, discarded, harvest); unique total ≈ 6,500 incl. Asch so far (rough, overlap between final/ and data/ removed by hand estimate) | PLACEHOLDER; compute exactly before submission |
| L3 | "we have a few different models" | — | 2 reasoning (qwen3.8-27b, deepseek-v4-flash) + 1 non-reasoning (gemma-4-31b-it) | OK, but the models are never named in the draft (R2) |
| L4 | "We assumed that our regex monitor labeled the test aware transcript correctly. While we let LLMs check this and also read the transcript ourselves" | `paper/eval_aware_report.pdf`, story C8 | LLM check = 56 single-agent transcripts; hand check = 8 P2 hits | WEAK: no validation on team transcripts, where all key EA numbers live |
| C1 | Conclusion: "rule breaking rates rise when they become part of a group ... perceived group identity, general activity or social factors" | exp09, exp14 | as A2/A4 | OK with A4 caveats |
| C2 | "they break implicit expectations even more often" | exp08/15 (85–93% used) vs exp05/14 (71–73% opened) | different conditions, different measures | WEAK: comparison across conditions, not a matched test |
| C3 | "Turning thinking mode off is a helpful trick" | exp11 + live Asch | qwen thinking-off so far (n=8–10 per level): 22%, 56%, 75%, 70%, 25% (trend p=.7) | **not yet supported by the qwen/deepseek data**; only Gemma (non-reasoning model) shows a clean curve. Re-check when the job finishes |

### Live Asch job (thinking on/off), status at audit time (`scripts/asch_stats.py`)

| qwen3.8-27b | 0/8 | 1/8 | 2/8 | 4/8 | 8/8 | trend p |
|---|---|---|---|---|---|---|
| thinking on (n≈27) | 18/27 (67%) | 16/25 (64%) | 19/27 (70%) | 18/28 (64%) | 11/27 (41%) | .028 (decreasing) |
| eval-aware, on | 9 | 13 | 11 | 16 | 19 | |
| thinking off (n≈9) | 2/9 (22%) | 5/9 (56%) | 6/8 (75%) | 7/10 (70%) | 2/8 (25%) | .7 |

deepseek not started yet (arms run in order). Remaining ≈ 816 runs. At 3 runs/min that is ~4.5 h, not ~3 h, if the
job is 50/cell × 5 levels × 2 thinking × 2 models (please check the job's `-n`).

---

## 2. Placeholders, missing pieces, template leftovers

1. **Fig. 3 "[missing graphic]"** (p.4). Candidates: `paper/figures/appendix/A10_gemma_asch_curve.png` (exp11 Gemma) or a
   new figure from `data/asch_runs.jsonl` once the job ends. The caption ("turning thinking off ... reveal their real
   behaviour") must match whichever model the figure shows.
2. "EARLY[big]" (p.2, intro): unresolved name/placeholder.
3. "As noted in 2 this builds on a growing literature about Ash's experiments" (p.2): ref [2] is the OpenAI
   Navier–Stokes post, not Asch-LLM literature (probably [4] or a missing ref); "Ash" spelling; stray line break.
4. No **"4. Results"** heading: numbering jumps 3 → 5; results are inside Methods.
5. p.5: large blank block below Fig. 4.
6. **Future Work**: template prompt still there ("What are the natural next steps?").
7. **Conclusion**: template prompt still there ("Briefly summarize your main findings ... (1–2 paragraphs)").
8. Code and Data: "Data/Datasets: [Link if applicable]"; template instruction line still present.
9. Limitations: "more than XYZ runs".
10. Appendix A is referenced as "[A]" in text; only the workspace figure exists. Candidate appendix assets already
    generated: `paper/figures/appendix/A2–A12`.
11. Fig. 4 bars labelled "Run 1 / Run 2" with no date/experiment/n.
12. Fig. 2 x-axis dates (Nov 7/Nov 8) shown but never explained in the text.
13. Author line: "Vikram vish" capitalisation; Lou Maessen has no affiliation.
14. LLM usage statement says "I wrote the whole paper" in a three-author paper.

---

## 3. Gaps where more API runs would materially help (ranked)

Budget reality: 3 runs/min ≈ 180/h. If the Asch job needs ~816 more runs (~4.5 h), an 8 h night leaves ~600 runs; if
it needs only ~3 h, ~900. The plan below is ordered so it can stop at any line. n per condition with Wilson CI
half-width: n=100 → ±9–10 pts, n=200 → ±6–7 pts. Detecting a 15-pt difference at p<.05 needs ~150–200 per arm.

| rank | gap | experiment to run (existing code) | models / conditions | minimal n | runs | why a judge cares |
|---|---|---|---|---|---|---|
| 0 | Fig. 3 data | already running: `examples/asch.py` | qwen + deepseek, thinking on/off, 0/1/2/4/8 | 50/cell (running) | ~816 left | The abstract's third contribution and Fig. 3 rest on it. If the thinking-off curve is noisy at n=50, top-up only 0/8 and 1/8 thinking-off (the conformity contrast) to 100: +200 runs |
| 1 | Fig. 2 ladder is cross-day (exp04 + T0 Nov 7, NS + P0 Nov 8); the "two thirds activity" number depends on a baseline from another day with ±10 pts noise | `examples/peers.py --cond SOLO`, `T0`, `NS`, `P0` in one batch (SOLO = exp04 exactly) | qwen + deepseek, 50/model | 100/condition | 400 (600 at 75/model) | Turns the headline decomposition into a single same-batch comparison and doubles as a replication of every Fig. 2 bar. Highest value per run |
| 2 | Gemma curve (if Fig. 3 keeps Gemma) was run with the old `read_board` bug, n=50, no 2/8 level, ceiling at 1/8 | `examples/asch.py` with a `gemma-4-31b-it` arm (check it accepts a model without `reasoning.effort`; else `final/exp11_non_reasoning.py` with the fixed board) | gemma: solo, 0/8, 1/8, 2/8, 8/8 | 50 each (100 at 0/8, 1/8) | 250–350 | The only clean conformity evidence in the paper. Skip if qwen/deepseek thinking-off from rank 0 already shows the curve |
| 3 | "social" vs identity: P0 = team sentence + board, NS = feed without team sentence, so the "social third" could be the team sentence alone (T0 +15 and NS +21 add up to P0's +34) | needs one new condition in `peers.py` (NS feed + team sentence, or P0 board without team sentence); code change, then 2 conditions | qwen + deepseek, 50/model | 100/condition | 200 | Answers the obvious reviewer question about contribution 2 ("activity and social context") |
| 4 | Eval-awareness detector not validated on team transcripts; draft says "regex and an LLM" | no agent runs. LLM-judge or human labels on ~50 P0 + ~50 P2 transcripts (`final/eval_awareness.py`, sample from exp05/exp07) | — | 100 transcripts | ~100 judge calls | M12/L4 claims; cheap; directly fixes a stated mismatch |
| 5 | "doesn't scale to smarter models" + generality beyond two mid-size models | `examples/peers.py --cond SOLO/P0/P3` on one stronger model, if the Adaption API offers one | 1 stronger model | 50/condition | 150 | Generality is the first thing judges ask; otherwise remove the claim (M14) |
| 6 | P2 "dropped" is p=.09 pooled | no new runs recommended; the Asch thinking-on 0/8 vs 8/8 (same batch, two models, n=50 each) will be the stronger test | — | — | 0 | Avoids spending budget on a claim the running job already tests |

Suggested cut lines: ~600 runs → rank 1 (400) + rank 0 top-up (200). ~900 → add rank 3 (200) or rank 2 (250–350), not
both. Rank 4 needs no agent budget and should happen regardless.

---

## 4. Review issues (questions for the authors)

**Claims and numbers**
- R1. Abstract 71% vs Fig. 2 73% (A3): which P0 batch is the paper's number? Using Nov 8 in the figure and Nov 7 in the
  abstract invites a "numbers don't match" comment.
- R2. Models, n per model, output-token limit, step cap, and the exact definition of "violation" (any `read_file`
  under finance/) are never stated. Is there room for a short setup table? CIs appear in figures but the method (Wilson)
  is not named.
- R3. "Reduce test awareness" and "toy workspace makes agent suspicious" (M2/M4) are contradicted by the regex
  numbers (toy 1% vs realistic 10–19%). Is a different measure intended?
- R4. Gemma: is it really "reasoning mode turned off", or a model used without reasoning? The repo treats
  `gemma-4-31b-it` as a non-reasoning model. The live job does switch thinking off for qwen/deepseek; which one is
  Fig. 3?
- R5. The test-awareness/violation "correlation" (A7): which direction, which data? It reverses in conditions without
  rule-breaking peers, and conditioning on eval-awareness is post-treatment (story C5 warns against this).
- R6. "Clean Asch curve" (A6): 0/8 is already 74% (vs solo 0%) and the curve saturates at 1/8. Is "clean" the right
  characterisation, and does the title "Context not conformity" sit well with the Gemma 74→98% conformity jump?
- R7. The "two thirds activity / one third social" split: the social remainder equals the team-sentence effect
  measured separately; is the board's social content adding anything beyond identity? Also the baseline is cross-day.
- R8. M11: "violation rates dropped" with P2 — pooled p=.09, qwen-only effect. Is "dropped" or "did not rise" the
  defensible reading?
- R9. M12 "regex and an LLM": only regex produced 62/34.
- R10. "We also replicated that agents use illicit information" — replicated what (Check Point? day-1 toy setup? HF)?
- R11. M14 "doesn't scale to smarter models" has no data behind it.

**Clarity / structure**
- R12. Methods p.3 mixes the toy setup (3 files, `request_access`, pointer to `q3_numbers.csv`) with the final one
  (42 files, `request_permission`, no pointer). A reader cannot tell which setup produced which number.
- R13. "it does even require a board full of misbehaving agents" reads as the opposite of the result (probably "does
  not").
- R14. P3 laundering: the rule only forbids opening the folder, so using posted figures is not a stated-rule violation.
  The draft calls it "implied expectations", good; but the P3S reminder result (explicit rule against using the
  figures: still 10% used + 27% opened = 37%, CI 31–44%) is the strongest support for that point and is absent. Same for
  the dissenter vs reminder comparison (C9: 50% vs 37%, p=.007) and the "displacement" to opening the folder (7% → 28%).
- R15. Episode length confound for the board/feed effect (board runs are longer; P0 49/199 hit the 16-step cap vs
  20/200 in exp04) is not in Limitations. Discussion's "context more diverse → less predictable" is a hypothesis;
  is it marked as such?
- R16. Fig. 4 "named the teammate or file" is generous; only 1/170 and 3/186 answers say the data was
  forbidden/unverified. Is the stricter number worth stating?
- R17. Limitations cite batch noise (~10%) but the comparisons in Fig. 1 and Fig. 2 cross days; which comparisons are
  same-batch should be visible.
- R18. Post-hoc changes (exp13 post selection amended after a first look) only matter if exp13 is used; it isn't in the
  draft now.
- R19. Related work: Check Point's conclusion ("direct pressure strengthened commitment") and the HF incident claims
  (intro, p.4) need precise citations/quotes, since they frame the contribution.
- R20. Dual-use: Code/Data section has no info-hazard note although the HF-style "forge a fake flag" is mentioned.
