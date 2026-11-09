# Morning brief, Mon Nov 9 (written 05:40 UTC, deadline 11:59 UTC)

No paper text in this file: numbers, issues, pointers only. CI = 95% Wilson. "opened" = any `read_file` under `finance/`.
**PROVISIONAL** = data still coming in; re-run the command before using the number.

## 1. TL;DR (since last night)

- **Asch, qwen3.8-27b complete (n=50/cell).** Thinking ON: 76 / 70 / 64 / 62 / 44% opened at 0/1/2/4/8 rule-breakers
  (trend p=.0005, *down*); eval-aware 15→36 of 50. Thinking OFF: 46 / 62 / 70 / 68 / 64% (trend p=.2; 0/8 vs any
  rule-breakers 46% vs 66%, p≈.01; saturates at 1–2). Pooled on vs off: no main effect (MH OR 1.05, p=.78).
- **Detector validated on 120 team transcripts** (P0, P2, Asch) vs blind LLM labels: kappa 0.91, agreement 95.8%,
  precision 0.92, recall 0.98. P0→P2 gap identical under both raters (LLM 25→45%, regex 30→45%). `notes/ea_validation.md`.
- **Dilution (Bertrand's question): existing data shows no sign of it** (`notes/dilution_analysis.md`). Violations at
  median step 6 with ~1.7–1.9k tokens of context; per-call hazard flat ~0.10 after step 6; at equal step, more context
  does not predict opening (percentile 0.50–0.52, p≥0.2). Causal test (PAD4K/PAD16K) queued, see §2.
- **deepseek Asch partial (PROVISIONAL, n=14–16/cell):** thinking ON 27 / 36 / 73 / 69 / 67% (trend p=.03, *up*);
  OFF 81 / 81 / 75 / 88 / 94% (p=.2). Opposite direction to qwen with thinking on. Do not interpret before n≈50.
- **5 h lost (00:25–05:24 UTC) to laptop idle suspend**; no data lost, sleep is now inhibited. Consequence: the
  same-night SOLO/NS/P0 ladder and PAD runs had not started at 05:40.

## 2. What is running, and how to refresh

| job | status at 05:40 UTC | expected |
|---|---|---|
| Asch deepseek on/off (`examples/asch.py`, `data/asch_runs.jsonl`) | ~154/500 deepseek runs | ends ≈07:15–07:45 UTC |
| Night queue SOLO / PAD16K / PAD4K / NS / P0 × qwen, deepseek × 40 (tag `night_nov9`, `data/peers_realistic_runs.jsonl`) | waiting for Asch | starts after Asch, **hard stop 09:30 UTC**; 400 runs ≈2.2 h, so expect ~30–40/cell (interleaved, cells stay balanced) |

Logs: `~/.claude/jobs/1df5467d/tmp/asch/all.log` (Asch), `.../queue.log` (night queue).

```
.venv/bin/python scripts/asch_stats.py --max-run-id 50     # Asch table + on/off Fisher + CMH
.venv/bin/python scripts/night_stats.py                    # dilution trend + same-night ladder (empty until ~07:30)
.venv/bin/python scripts/paper_figures.py fig5             # Asch figure (both models)
.venv/bin/python scripts/paper_figures.py fig6             # same-night ladder alone / feed / board
.venv/bin/python scripts/paper_figures.py fig7             # dilution SOLO / PAD4K / PAD16K
```
Suggested freeze: re-run all five at ~09:35 UTC, then stop touching numbers.

## 3. Claim-by-claim (draft section names)

| draft claim | status | numbers (n, CI) | figure | issue / question |
|---|---|---|---|---|
| Abstract: baseline 40% | supported | exp04 79/200, 39.5% (33–46) | fig1b, fig0 | models, n, step cap never stated (R2) |
| Abstract + §3: team sentence → 55% (+15) | supported | exp09 109/199, 55% (48–62); vs exp04 p=.002 | fig1b | exp04 and T0 same day, different batch |
| Abstract: neutral board → 71% | **mismatch** | exp05 141/199 = 71% (Nov 7) vs fig1b shows exp14 P0 146/200 = 73% (66–79, Nov 8) | fig1b | which batch is "the" P0 number? one number across abstract and figure |
| Abstract + §3: feed = ~two thirds activity, rest social (+21 / +34) | weak | NS 121/200, 60.5% (54–67) vs P0 73%, same batch, p=.008; split uses exp04 from another day | fig1b (→ fig6 when filled) | cross-day denominator; social part mostly qwen (57→76, p=.004; deepseek 64→70, p=.37); "social" remainder ≈ team-sentence effect (R7). Night ladder (PROVISIONAL) is meant to fix the day confound |
| §3: toy workspace → suspicion; realism "helped reduce test awareness" | **unsupported / contradicted** | regex eval-aware: toy R0 1/100; realistic exp01 10/100, exp03 23/196, exp04 38/200 | fig0 | what measure supports "suspicious"? |
| §3: "restricted" vs "forbidden" | supported | exp03 133/196, 68% (61–74) vs exp04 40% (33–46), same batch | fig0, fig1 | "often used as an excuse" has no validated measure (rough regex 90/133 vs 12/79) |
| §3: rule-breaking peers → violations "dropped" | weak | exp07 125/199, 63% (56–69) vs exp05 71%, p=.09 pooled; qwen 70→54 (p=.02), deepseek 71→72 | fig2 | "dropped" vs "did not rise"? Asch qwen-on 0/8→8/8 (76→44%, p=.003) is the stronger same-batch test |
| §3: "regex and an LLM flagged 62% vs 34%" | partly true now | regex 124/199 (55–69) vs 67/199 (27–40); LLM validation on 40 P2 + 40 P0 sample: 45% vs 25% | fig2 | 62/34 are regex numbers; cite `notes/ea_validation.md` for the LLM part (kappa .91, n=120) |
| §3: causal "increased evaluation awareness" | weak | 109/124 flagged P2 passages refer to teammates | — | shows posts trigger test-talk, not that test-talk causes the drop; EA is post-treatment (story C5) |
| §3: "doesn't scale to smarter models" | **unsupported** | no stronger model was run | — | remove or support |
| Abstract + §3: Gemma thinking-off "clean Asch curve" | weak / **mismatch** | exp11 gemma: solo 0/50, 0/8 37/50 (74%), 1/8 49/50 (98%), 4/8 and 8/8 50/50 | A10 (appendix) | Gemma is a non-reasoning model, nothing was "turned off"; ceiling at 1/8; old `read_board` bug; Gemma was dropped. New on/off data is qwen + deepseek (fig5) |
| Fig 3 / Conclusion: thinking off reveals "real behaviour" | weak, model-dependent | qwen: off rises 46→70% then flat; on falls 76→44%. deepseek (PROVISIONAL): off 81–94% flat-high; on rises 27→73% | fig5 | qwen alone fits; deepseek-on goes the other way so far; "off" removes EA measurement entirely (EA=0 by construction) |
| Abstract: EA "correlated strongly" with rule-breaking | weak | P2 opened 50% if EA vs 84% if not; Asch qwen-on 38% vs 83%; but exp04 47 vs 38%, P0 77 vs 71% (reversed) | A9 | direction not stated; post-treatment conditioning; exp10 is dropped (truncated runs) |
| §3 Fig 4: laundering without disclosure | supported (strongest) | exp08 used 170/200, 85% (79–89); exp15 P3 186/200, 93% (89–96); answer names any source 14/170, 20/186; says forbidden/unverified 1/170, 3/186 | fig4, fig3 | "Run 1/Run 2" unlabeled (exp08 Nov 7 / exp15-P3 Nov 8, n=200 each) |
| §3: "reasoned in most cases data was unauthorized" | weak | ~134–154/170 (unvalidated regex) | — | no hand-check sample |
| §3: "noticed it can't confirm numbers are trustworthy" | **unsupported** as "most" | 76/170, 95/186 (~45–50%, many are arithmetic checks) | — | |
| Limitations: day-to-day ~10% | supported | exp01 +7, P0 +2, P3 used +8 / opened −8 pts | A8 | "up to ~8 pts" is what the data show |
| Conclusion: implicit expectations broken "more often" | weak | 85–93% used vs 71–73% opened, different conditions | — | not a matched comparison |
| (absent) reminder vs dissenter defenses | supported | P3 100% → P3D 101/200, 50% (44–57) / P3S 74/200, 37% (31–44), p=.007; opening itself 7%→28% | fig3 | strongest support for the laundering point is not in the draft (R14) |

## 4. Must-fix before submission

1. Abstract 71% vs Fig 2 73%: pick one P0 batch.
2. "more than XYZ runs" (Limitations): audit estimate ≈6,500 unique run records before tonight + 655+ Asch runs so far; compute the exact total at freeze.
3. "EARLY[big]" placeholder (Intro).
4. "As noted in 2 ... Ash's experiments": ref [2] is the OpenAI Navier–Stokes post, not Asch-LLM work (likely [4]); spelling "Ash" (also §3 "Ash curve").
5. Fig 3 "[missing graphic]": candidate `paper/figures/fig5_asch_thinking.png` (qwen + deepseek, on/off). Its caption and the Abstract/§3 text currently describe Gemma; the figure shows qwen/deepseek. Gemma curve exists as `appendix/A10_gemma_asch_curve.png` if kept.
6. "regex and an LLM": 62/34 are regex; LLM agreement now exists for team transcripts (kappa .91, n=120): `notes/ea_validation.md`. Limitations paragraph on detector validity can point to the same.
7. "doesn't scale to smarter models": no data.
8. "Gemma's reasoning mode turned off": Gemma has no reasoning mode in our runs.
9. "toy workspace makes agent suspicious" / "reduce test awareness": contradicted by the regex (1% toy vs 10–19% realistic).
10. "it does even require a board full of misbehaving agents": likely means "does not".
11. Methods mixes toy (3 files, `request_access`, `q3_numbers.csv`) and final setup (42 files, `request_permission`, no pointer); file names inconsistent.
12. No "4. Results" heading (3 → 5); blank block under Fig 4.
13. Future Work and Conclusion: template prompts still in the text ("What are the natural next steps?", "Briefly summarize ...").
14. Code and Data: "Data/Datasets: [Link if applicable]" + template instruction line; no info-hazard note (fake-flag forging mentioned).
15. LLM Usage Statement: "I wrote the whole paper" in a 3-author paper; also says LLMs generated graphics from "numbers I gave it" (figures are generated by `scripts/paper_figures.py` from the run files).
16. Models, n per model, 8000 tokens, 16-step cap, Wilson CIs: never stated.
17. Fig 4 "Run 1 / Run 2": no experiment/date/n. Fig 2 shows dates never explained.
18. Authors: "Vikram vish" capitalisation; Lou Maessen without affiliation.

## 5. Figures in `paper/figures/` (.png + .pdf)

| file | shows | state |
|---|---|---|
| fig0_setup | toy 16% (n=100) / realistic restricted 68% (196) / forbidden 40% (200) | = draft Fig 1; toy bar is 1500 tokens, different day |
| fig1_context | horizontal ladder: exp03, exp04, exp09, exp14 NS, exp14 P0 with dates | alternative to fig1b |
| fig1b_identity_activity | alone 40 / team sentence 55 / feed 60 / sentence+board 73, with +pts and dates | = draft Fig 2 |
| fig2_peers | P0/P1/P2 and P0R/P2R: opened vs flagged "test" | not in draft; supports the EA paragraph |
| fig3_laundering_defense | P3 / P3D / P3S stacked: used posted figures, opened, complied; test-flag 0/68/68% | not in draft |
| fig4_laundering_disclosure | exp08 vs exp15-P3: used without source / named source / opened | = draft Fig 4 |
| fig5_asch_thinking | qwen + deepseek, on vs off, 0–8 rule-breakers | regenerated 05:34; deepseek PROVISIONAL (shows 14–16/cell) |
| fig6_same_night_ladder | alone / feed / board, same night | **empty placeholder ("running")** |
| fig7_dilution | SOLO / PAD4K / PAD16K | **empty placeholder** |
| figA_workspace | 42-file workspace | = draft Appendix A |
| appendix/A2–A12 | prompts, board posts, trajectory raster, ask-before-open, file-read heatmap, per-model, all-batches forest (A8), test-aware split (A9), Gemma Asch (A10), example transcript, setup diagram | candidates for Appendix |

## 6. Caveats a judge will raise, and the evidence

| caveat | evidence in hand |
|---|---|
| 16-step cap censors outcomes (Asch on-arm max_steps 3→8 with more rule-breakers; P0 49/199 hit cap vs 20/200 in exp04) | Asch qwen-on fall survives dropping capped runs (78/76/71/72/51%) and counting all as openers (78/78/74/76/58%): ≥20 pts either way (`notes/asch_qualitative.md`, night log 01:20). Dilution hazard flat to k=15 |
| Batch/day noise ±10 pts; Fig 2 ladder crosses days | replications: P0 71 vs 73 (+2), exp01 +7, P3 used +8. NS vs P0 is same batch (p=.008). Same-night SOLO/NS/P0 (PROVISIONAL, fig6) |
| Eval-awareness is post-treatment; regex validity | detector kappa .91 on 120 team transcripts; story C5: unaware-runs-only restricted analysis shows no clear effect (P0 70 / P1 72 / P2 76%, n=49), so no stratified causal claim; thinking-off arm has EA=0 by construction |
| Only two mid-size models (+ Gemma) | models diverge (qwen vs deepseek in P2, social part of NS→P0, Asch-on direction): report per model (A7); no stronger model run |
| Scripted posts look like a test | real harvested posts (exp13): EA back to control (59 vs 68), P2R 75% vs P0R 80%, but only ~25/200 notice the teammates used finance/ |
| "Board works only because it adds text" / dilution | NS adds as much text as P0 but less opening; T0 adds no text but +15; no context effect within step; PAD4K/PAD16K causal test PROVISIONAL (fig7) |
| `read_file` never enforced; permission never granted | by design (README "Setup"); openers frame opening as "checking whether permission was granted" (33/38 at 0/8, 22/22 at 8/8, qwen-on) |
| Asch off-arm openers who opened before seeing posts | dropping them: 40/56/66/63/57% (same shape) |
| Post-hoc changes | exp13 post-selection amended twice; matters only if exp13/fig2 lower half is used |

Sources: `notes/claim_audit.md` (full audit, R1–R20), `notes/night_2026-11-09.md`, `notes/ea_validation.md`,
`notes/asch_qualitative.md`, `notes/dilution_analysis.md`, `final/README.md`, `paper/story_and_claims.md`.

### Run count for "XYZ runs" (05:50 UTC)
Frozen experiments in `final/results/` (exp01–exp15, errors excluded): **3,641** runs. Plus tonight's Asch runs
(`data/asch_runs.jsonl`, no errors, no smoke): 660 so far → 4,301, rising as deepseek and the night batch finish.
Recount at the end with the one-liner in `notes/night_2026-11-09.md` or ask Claude.
