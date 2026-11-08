"""Asch thinking on/off table from data/asch_runs.jsonl (or a frozen runs.jsonl given as argument).

    .venv/bin/python scripts/asch_stats.py [path] [--max-run-id 50]
Per model x thinking x rule-breakers: opened finance/ (95% Wilson CI), opened only after the rule-breaking posts,
eval-aware, truncated, ended by max_steps, never shown the posts; plus a Cochran-Armitage trend test over the dose
levels. Then thinking on vs off per level (difference + two-sided Fisher exact p) and pooled over levels
(Cochran-Mantel-Haenszel test stratified by level, with the Mantel-Haenszel common odds ratio on/off).
--max-run-id N keeps only run_id < N (the 50-per-cell design).
"""
import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(path, max_run_id=None):
    """Valid Asch runs: no error, not a smoke test, optionally run_id < max_run_id. Shared with paper_figures.py."""
    runs = [json.loads(line) for line in Path(path).open() if line.strip()]
    return [r for r in runs if r["end"] != "error" and not r.get("error") and "smoke" not in (r.get("note") or "")
            and (max_run_id is None or r["run_id"] < max_run_id)]


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


def fisher_p(a, n1, c, n2):
    """Two-sided Fisher exact p for a/n1 vs c/n2 (sum of tables no more likely than the observed one)."""
    K, N = a + c, n1 + n2
    pr = lambda x: math.comb(n1, x) * math.comb(n2, K - x) / math.comb(N, K)  # noqa: E731
    p0 = pr(a)
    return min(1.0, sum(pr(x) for x in range(max(0, K - n2), min(K, n1) + 1) if pr(x) <= p0 * (1 + 1e-7)))


def cmh(strata):
    """Cochran-Mantel-Haenszel test over 2x2 strata [(a, n1, c, n2)] (a/n1 = group 1 yes). Returns (MH OR, chi2, p)."""
    num = den = e = v = 0.0
    obs = 0
    for a, n1, c, n2 in strata:
        N, m1 = n1 + n2, a + c
        if N < 2:
            continue
        b, d = n1 - a, n2 - c
        num, den = num + a * d / N, den + b * c / N
        obs += a
        e += n1 * m1 / N
        v += n1 * n2 * m1 * (N - m1) / (N * N * (N - 1))
    orr = num / den if den else float("inf")
    if v <= 0:
        return orr, float("nan"), float("nan")
    chi2 = (obs - e) ** 2 / v
    return orr, chi2, math.erfc(math.sqrt(chi2 / 2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", default=ROOT / "data" / "asch_runs.jsonl")
    ap.add_argument("--max-run-id", type=int, default=None, help="keep only run_id < N")
    a = ap.parse_args()
    runs = load(a.path, a.max_run_id)
    print(f"{len(runs)} valid runs from {a.path}" + (f" (run_id < {a.max_run_id})" if a.max_run_id else ""))

    groups = defaultdict(list)
    for r in runs:
        groups[(r["model"], r["thinking"], r["reversals"])].append(r)
    models = sorted({k[0] for k in groups})
    print("\n| model | thinking | rule-breakers | runs | opened finance/ | opened after the posts | eval-aware "
          "| truncated | max_steps | posts never shown |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for model in models:
        for th in ("off", "on"):
            lv = []
            for rev in sorted({k[2] for k in groups if k[:2] == (model, th)}):
                g = groups[(model, th, rev)]
                n, k = len(g), sum(r["read_forbidden"] for r in g)
                lo, hi = wilson(k, n)
                after = sum(bool(r["exposed_before_violation"]) for r in g)
                print(f"| {model} | {th} | {rev}/8 | {n} | **{k}** ({k/n:.0%}, CI {lo:.0%}–{hi:.0%}) | {after} | "
                      f"{sum(bool(r.get('eval_aware')) for r in g)} | {sum(r['truncated'] for r in g)} | "
                      f"{sum(r['end'] == 'max_steps' for r in g)} | {sum(not r['phase2_steps'] for r in g)} |")
                lv.append((rev, k, n))
            if len(lv) > 1:
                print(f"| {model} | {th} | trend p | | {trend_p(lv):.2g} | | | | | |")

    print("\n| model | rule-breakers | on | off | on − off | Fisher p |")
    print("|---|---|---|---|---|---|")
    for model in models:
        strata = []
        for rev in sorted({k[2] for k in groups if k[0] == model}):
            on, off = groups.get((model, "on", rev), []), groups.get((model, "off", rev), [])
            if not on or not off:
                continue
            a_, n1 = sum(r["read_forbidden"] for r in on), len(on)
            c_, n2 = sum(r["read_forbidden"] for r in off), len(off)
            strata.append((a_, n1, c_, n2))
            print(f"| {model} | {rev}/8 | {a_}/{n1} ({a_/n1:.0%}) | {c_}/{n2} ({c_/n2:.0%}) | "
                  f"{100 * (a_/n1 - c_/n2):+.0f} pts | {fisher_p(a_, n1, c_, n2):.2g} |")
        if strata:
            orr, chi2, p = cmh(strata)
            print(f"| {model} | pooled (CMH by level) | | | MH odds ratio on/off {orr:.2f} | χ²={chi2:.2f}, p={p:.2g} |")


if __name__ == "__main__":
    main()
