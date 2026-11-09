"""Experiment 16, ASCH CURVE WITH THINKING ON vs OFF: exp10's 8-teammate board, 0/1/2/4/8 of 8 teammates post that
they opened finance/ themselves; qwen3.8-27b and deepseek-v4-flash, thinking on (default) vs off (reasoning.effort
"none", 0 reasoning tokens). 50 runs per cell (run_id 0-49, same run_id = same shuffled board in every arm).
Core: asch_v1.py (frozen copy of examples/asch.py; board texts/timing from exp10_asch_split.py, plus the read_board fix).

Opened finance/ at 0/1/2/4/8 rule-breakers (n = 50 per cell, deepseek-on 0/8: 49), trend p = Cochran-Armitage:
  qwen      ON : 76 / 70 / 64 / 62 / 44%  (38 35 32 31 22)  trend p=.0005  eval-aware 15/24/25/29/36
  qwen      OFF: 46 / 62 / 70 / 68 / 64%  (23 31 35 34 32)  trend p=.2     eval-aware 0 (no reasoning)
  deepseek  ON : 49 / 48 / 64 / 58 / 52%  (24 24 32 29 26)  trend p=.81    eval-aware 23/25/35/34/41
  deepseek  OFF: 68 / 78 / 84 / 84 / 96%  (34 39 42 42 48)  trend p=.0005  eval-aware 0
  on - off: qwen +30 / +8 / -6 / -6 / -20 pts (CMH OR 1.05, p=.78); deepseek -19 / -30 / -20 / -26 / -44 pts
  (CMH OR 0.26, p=2e-11).
  Runs ending at the 16-step cap (max_steps): qwen ON 3/4/6/8/8, OFF 7/0/0/1/0; deepseek ON 23/22/17/15/16,
  OFF 18/17/14/6/3. Sensitivity: notes/night_2026-11-09.md (01:20 qwen, 07:25 deepseek).
Numbers: .venv/bin/python scripts/asch_stats.py final/results/exp16_asch_thinking/runs.jsonl

Original runs: final/results/exp16_asch_thinking/runs.jsonl = data/asch_runs.jsonl with run_id < 50, no error,
no smoke note (999 runs). Produced with examples/asch.py in one process behind one shared rate limiter, resumed
across restarts, night of Nov 8-9 2026:
  batches 20261108-225109_* (asch.py at b423388), 20261108-231037_* (at 89c8811), 20261108-235302_* (at 9fd59e8);
  notes "... 4th start with shared rate limiter (Nov 8 evening)" and "... one shared rate limiter, resumed
  (Nov 8-9 night)". Between these commits only the limiter and job scheduling changed; run_once is identical.
  asch_v1.py is byte-identical to examples/asch.py at 9fd59e8.
Replicate (appends to final/results/exp16_asch_thinking/replication_runs.jsonl; resumes from it):
    .venv/bin/python final/exp16_asch_thinking.py
  = .venv/bin/python final/asch_v1.py --arms qwen3.8-27b:on qwen3.8-27b:off deepseek-v4-flash:on \\
        deepseek-v4-flash:off -n 50 --rpm 45 --max-rpm 60 \\
        --out final/results/exp16_asch_thinking/replication_runs.jsonl --note "exp16 replication"
"""
import asyncio
import sys
from pathlib import Path

FINAL = Path(__file__).resolve().parent
sys.path.insert(0, str(FINAL))
import asch_v1  # noqa: E402

ARGS = ["--arms", "qwen3.8-27b:on", "qwen3.8-27b:off", "deepseek-v4-flash:on", "deepseek-v4-flash:off",
        "-n", "50", "--rpm", "45", "--max-rpm", "60",
        "--out", str(FINAL / "results" / "exp16_asch_thinking" / "replication_runs.jsonl"),
        "--note", "exp16 replication"]

if __name__ == "__main__":
    sys.argv = [sys.argv[0]] + ARGS + sys.argv[1:]
    asyncio.run(asch_v1.main())
