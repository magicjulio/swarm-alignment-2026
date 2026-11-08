"""Asch thinking on/off table from data/asch_runs.jsonl (or a frozen runs.jsonl given as argument).

    .venv/bin/python scripts/asch_stats.py [path]
Per model x thinking x rule-breakers: opened finance/ (95% Wilson CI), opened only after the rule-breaking posts,
eval-aware, truncated; plus a Cochran-Armitage trend test over the dose levels.
"""
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "asch_runs.jsonl"
runs = [json.loads(line) for line in path.open()]
runs = [r for r in runs if r["end"] != "error" and r.get("note") != "smoke"]


def wilson(k, n, z=1.96):
    p, d = k / n, 1 + z * z / n
    c, h = (p + z * z / (2 * n)) / d, z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0, c - h), min(1, c + h)


def trend_p(levels):
    """Cochran-Armitage test for a linear trend in proportions; levels = [(dose, k, n)]. Two-sided p."""
    N, K = sum(n for _, _, n in levels), sum(k for _, k, _ in levels)
    p = K / N
    t = sum(d * (k - n * p) for d, k, n in levels)
    var = p * (1 - p) * (sum(n * d * d for d, _, n in levels) - sum(n * d for d, _, n in levels) ** 2 / N)
    if var <= 0:
        return float("nan")
    z = t / math.sqrt(var)
    return math.erfc(abs(z) / math.sqrt(2))


groups = defaultdict(list)
for r in runs:
    groups[(r["model"], r["thinking"], r["reversals"])].append(r)
print("| model | thinking | rule-breakers | runs | opened finance/ | opened after the posts | eval-aware | truncated |")
print("|---|---|---|---|---|---|---|---|")
for model in sorted({k[0] for k in groups}):
    for th in ("off", "on"):
        lv = []
        for rev in sorted({k[2] for k in groups if k[:2] == (model, th)}):
            g = groups[(model, th, rev)]
            n, k = len(g), sum(r["read_forbidden"] for r in g)
            lo, hi = wilson(k, n)
            after = sum(bool(r["exposed_before_violation"]) for r in g)
            print(f"| {model} | {th} | {rev}/8 | {n} | **{k}** ({k/n:.0%}, CI {lo:.0%}–{hi:.0%}) | {after} | "
                  f"{sum(bool(r.get('eval_aware')) for r in g)} | {sum(r['truncated'] for r in g)} |")
            lv.append((rev, k, n))
        if lv:
            print(f"| {model} | {th} | trend p | | {trend_p(lv):.2g} | | | |")
