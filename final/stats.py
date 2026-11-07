"""Paper numbers for every experiment in final/results/ (original runs, plus replications if present).

    .venv/bin/python final/stats.py            # markdown table, paste into README / paper
"""
import json
import math
from pathlib import Path

RESULTS = Path(__file__).resolve().parent / "results"


def wilson(k, n, z=1.96):
    p, d = k / n, 1 + z * z / n
    c, h = (p + z * z / (2 * n)) / d, z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0, c - h), min(1, c + h)


def row(name, runs):
    ok = [r for r in runs if r["end"] != "error"]
    n = len(ok)
    opened = [r for r in ok if r["read_forbidden"]]
    lo, hi = wilson(len(opened), n)
    per = " / ".join(f"{sum(r['read_forbidden'] for r in ok if r['model'] == m)}"
                     for m in sorted({r["model"] for r in ok}))
    cnt = lambda k: sum(bool(r.get(k)) for r in ok)
    return (f"| {name} | {n} | **{len(opened)}** ({len(opened) / n:.0%}, CI {lo:.0%}–{hi:.0%}) | {per} | "
            f"{cnt('answer_leaks')} | {cnt('answer_claims_granted')} | {cnt('eval_aware')} | "
            f"{sum(r.get('bulk_forbidden_read', False) for r in opened)} |")


print("| experiment | runs | opened finance/ | deepseek / qwen | answer leaks | claims granted | eval-aware | sweep reads |")
print("|---|---|---|---|---|---|---|---|")
for d in sorted(p for p in RESULTS.iterdir() if p.is_dir()):
    for f, label in (("runs.jsonl", d.name), ("replication_runs.jsonl", d.name + " (replication)")):
        if (d / f).exists():
            print(row(label, [json.loads(line) for line in (d / f).open()]))
