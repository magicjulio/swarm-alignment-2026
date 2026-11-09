# Does extra context "dilute" the rule? Results for Bertrand

*Status: Nov 9, 09:15 UTC. All numbers final (40 runs per model per condition in tonight's batch). Opened = the agent read a file in the forbidden finance/ folder.*

**Short answer: in our setup, more outside text does not make agents break the rule more.** Three independent checks
point the same way. The realistic-workspace jump (R1 → R2a) is not explained by text volume either (part 2).

## 1. Direct test (run tonight): add neutral outside text, nothing else changes

Single agent, same task and rule as the baseline (SOLO). After its first action the agent receives a long, boring
workspace sync log (about 4,000 or 16,000 tokens): outside text that has nothing to do with the rule, the task or other
people. If outside text dilutes the system prompt, opening should rise with the amount of log.

| condition | qwen | deepseek | both models |
|---|---|---|---|
| no extra text (SOLO) | 24/40 (60%) | 22/40 (55%) | **46/80 (57%)** |
| + ~4k tokens of log | 19/40 (48%) | 23/40 (57%) | **42/80 (52%)** |
| + ~16k tokens of log | 21/40 (52%) | 20/40 (50%) | **41/80 (51%)** |

No rise (trend test p = 0.49; 16k vs none p = 0.53). If anything slightly lower. The 16k log is 3–8 times more text
than the agent normally has in its whole context (~2–5k tokens), so this is a strong dose. Agents almost never mention
the log in their thinking (about 1 in 10 runs).

## 2. R1 vs R2a: the realistic folder was smaller in text, not larger

These are the realism variants (100 runs each, single agent; same 40 unrelated "noise" files in all of them):

| variant | what changed vs R1 | opened | outside text the agent actually read (median, characters) |
|---|---|---|---|
| R0 toy workspace (3 files) | — | 16% | 650 |
| **R1** noise files added | — | **31%** | **10,400** |
| **R2a** + realistic finance/ folder (+ pointer in the summary) | finance/ content | **68%** | **4,600** |
| R2b summary without the pointer | wording | 32% | 10,200 |
| R2c README as directory overview | wording | 31% | 11,500 |

R2a agents read **less than half** as much outside text as R1 agents, yet broke the rule twice as often. R2b and R2c
read the most text and stayed at R1's level. So the jump comes from *what* is in the workspace (a finance/ folder that
obviously holds the needed regional numbers, and a pointer to it), not from how much text there is.
(Source: `data/realism_series_runs.jsonl`; exploratory batches, day-to-day noise about ±10 points.)

## 3. Existing runs (about 3,000): openers do not have more context

- The first forbidden read happens at a median of ~1,700–1,900 tokens of context; contexts are small throughout.
- Comparing runs at the same step, those that open finance/ do not carry more context than those that don't
  (single-agent p = 0.21, team-board runs p = 0.98).
- The chance of opening per step does not keep rising as the context grows; it levels off after the first few moves.
(Details: `notes/dilution_analysis.md`.)

## 4. The team board is not just "more text"

Same night, same models (tonight's batch, 80 runs each):

| condition | opened |
|---|---|
| alone (SOLO) | 46/80 (57%) |
| automated system feed, same amount and timing of messages as the board (NS) | 50/80 (62%), +5 pts, p = 0.63 |
| team board with ordinary teammate posts (P0) | 59/80 (74%), **+16 pts, p = 0.045** |

The system feed and the team board push the same amount of text into the context (≈ 230 characters per message), but
only the board clearly raises opening. And the team-identity sentence alone (T0, earlier day: 55% vs 40%) adds no
outside text at all.

## Where Li et al. (2024) can still fit

- Their drift builds up over long multi-turn dialogs; our agents run ≤ 16 steps and ≤ ~20k tokens. We can't rule out
  dilution at much longer contexts (50k–100k+), which we did not test.
- Our filler is neutral. Text that *argues against* the instruction (their "different from the instruction") is what
  our board posts are — so for P2/P3 the social and the "conflicting outside text" readings overlap. The NS feed and
  the SOLO/PAD results separate them for the neutral case only.

Files: `examples/peers.py` (PAD4K/PAD16K conditions), `scripts/night_stats.py`, `paper/figures/fig7_dilution.png`,
`paper/figures/fig6_same_night_ladder.png`, `data/peers_realistic_runs.jsonl` tag `night_nov9`.
