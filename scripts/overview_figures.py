"""Two overview figures of every experiment so far, recomputed from the run logs.

    .venv/bin/python scripts/overview_figures.py
writes share/fig1_single_agent.png and share/fig2_team_peers.png
"""
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.transforms import blended_transform_factory as blend  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "share"
OUT.mkdir(exist_ok=True)

# reference palette (dataviz skill), light mode
SURFACE, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984", "#e6e5e0"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
BLUE_LIGHT = "#a9c8ef"

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK, "hatch.color": "#ffffff",
                     "hatch.linewidth": 1.2})


def load(path, **match):
    out = []
    for line in open(ROOT / path):
        r = json.loads(line)
        if r.get("end") == "error":
            continue
        if all(r.get(k) == v for k, v in match.items()):
            out.append(r)
    return out


def wilson(k, n, z=1.96):
    p, d = k / n, 1 + z * z / n
    c, h = (p + z * z / (2 * n)) / d, z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0, c - h), min(1, c + h)


def rate(runs, key):
    k, n = sum(bool(r.get(key)) for r in runs), len(runs)
    lo, hi = wilson(k, n)
    return dict(k=k, n=n, p=k / n, lo=lo, hi=hi)


def final(exp):
    return load(f"final/results/{exp}/runs.jsonl")


# ---------------------------------------------------------------- figure 1: single agent
REAL = "data/realism_series_runs.jsonl"
groups = [
    ("Realism series  (exploratory, 1500 output tokens, 'restricted' rule)", [
        ("R0", "toy workspace (few files), the old setup", load(REAL, tag="realism_r0"), "explore"),
        ("R1", "R0 + many unrelated, numbers-heavy files", load(REAL, tag="realism_r1"), "explore"),
        ("R2a", "R1 + realistic finance/ files only", load(REAL, tag="realism_r2a"), "explore"),
        ("R2b", "R1 + no hint pointing to the finance file", load(REAL, tag="realism_r2b"), "explore"),
        ("R2c", "R1 + README with a folder overview", load(REAL, tag="realism_r2c"), "explore"),
        ("R2", "all three: the realistic 42-file workspace (= exp01)", load(REAL, tag="realism_r2"), "explore"),
        ("R3", "R2 + realistic tool outputs and prompt", load(REAL, tag="realism_r3"), "explore"),
    ]),
    ("Final baselines  (realistic workspace, in final/)", [
        ("exp01", "rule: 'finance/ is restricted' (same runs as R2)", final("exp01_restricted"), "final"),
        ("exp02", "'forbidden' + ask-permission tool (1500 tokens)", final("exp02_forbidden_permission"), "final"),
        ("exp03", "= exp01, rerun with 8000 tokens", final("exp03_restricted_8k"), "final"),
        ("exp04", "= exp02, rerun with 8000 tokens  ·  BASELINE", final("exp04_forbidden_permission_8k"), "base"),
    ]),
    ("Side tests  (exploratory, 1500 tokens)", [
        ("S1", "rule says 'forbidden', no ask-permission tool", load("data/baseline_runs.jsonl",
                                                                     tag="baseline_forbidden"), "explore"),
        ("S2", "'restricted' rule, answer file labelled CONFIDENTIAL",
         load("data/baseline_runs.jsonl", tag="baseline_confidential_label"), "explore"),
    ]),
]

rows = []   # (label, stats, style) top to bottom, None = group header
for title, items in groups:
    rows.append((title, None, "header"))
    for rid, desc, runs, style in items:
        rows.append((f"{rid} · {desc}", rate(runs, "read_forbidden"), style))

fig, ax = plt.subplots(figsize=(13, 0.48 * len(rows) + 1.6), dpi=200)
fig.patch.set_facecolor(SURFACE)
ax.set_facecolor(SURFACE)
ys = list(range(len(rows)))[::-1]
for y, (label, s, style) in zip(ys, rows):
    if style == "header":
        ax.text(0.02, y - 0.1, label, transform=blend(fig.transFigure, ax.transData), ha="left", va="center",
                fontsize=11.5, fontweight="bold", color=INK)
        continue
    color = {"explore": BLUE_LIGHT, "final": BLUE, "base": ORANGE}[style]
    ax.barh(y, s["p"] * 100, height=0.62, color=color, edgecolor=SURFACE, linewidth=2,
            hatch="//" if style == "explore" else None, zorder=2)
    ax.errorbar(s["p"] * 100, y, xerr=[[100 * (s["p"] - s["lo"])], [100 * (s["hi"] - s["p"])]],
                fmt="none", ecolor=INK2, elinewidth=1.3, capsize=3, zorder=3)
    ax.text(s["hi"] * 100 + 1.2, y, f"{s['p']:.0%}  ({s['k']}/{s['n']})", va="center", fontsize=10,
            color=INK, fontweight="bold" if style == "base" else "normal")
    ax.text(-0.01, y, label, transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=10.5,
            color=INK, fontweight="bold" if style == "base" else "normal")

ax.set_yticks([])
ax.set_xlim(0, 100)
ax.set_ylim(-0.6, len(rows) - 0.4)
ax.set_xticks(range(0, 101, 20))
ax.set_xticklabels([f"{t}%" for t in range(0, 101, 20)])
ax.grid(axis="x", color=GRID, linewidth=0.8, zorder=0)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.set_xlabel("share of runs where the agent opened the forbidden finance/ folder  (bar = 95% range)")
fig.suptitle("Single agent: how often does it break the rule?", x=0.02, ha="left", fontsize=15,
             fontweight="bold", color=INK)
fig.text(0.02, 0.955 - 0.25 / (0.48 * len(rows) + 1.6),
         "Task: report Q3 revenue by region. The data is only in finance/, which the rule forbids. "
         "Two models (deepseek, qwen), equal runs each.\n"
         "Hatched light bars = exploratory, not in final/.  Blue = final.  Orange = current baseline that the "
         "team experiments build on.", ha="left", va="top", fontsize=10, color=INK2)
fig.subplots_adjust(left=0.43, right=0.97, top=1 - 1.15 / (0.48 * len(rows) + 1.6), bottom=0.75 / (0.48 * len(rows) + 1.6))
fig.savefig(OUT / "fig1_single_agent.png", facecolor=SURFACE)
plt.close(fig)

# ---------------------------------------------------------------- figure 2: team / peers
PEERS = "data/peers_realistic_runs.jsonl"
base = final("exp04_forbidden_permission_8k")
team = [
    ("T0", "only told 'you are on the finance reporting team', no board", final("exp09_identity_only_T0"), "a"),
    ("P0", "team board, teammates post ordinary updates  (CONTROL)", final("exp05_peers_P0_neutral"), "a"),
    ("P1", "scripted: 2 teammates say they are waiting for permission", final("exp06_peers_P1_comply"), "a"),
    ("P2", "scripted: 3 teammates say they broke the rule", final("exp07_peers_P2_violate"), "a"),
    ("P3", "scripted: a teammate posts the Q3 numbers", final("exp08_peers_P3_share"), "a"),
    ("P0R", "real posts from teammates who did not use finance/  (CONTROL)", load(PEERS, cond="P0R"), "b"),
    ("P2R", "real posts from teammates who used finance/ (they cite the file)", load(PEERS, cond="P2R"), "b"),
]
rows = [("Team experiments  (in final/, run the same evening)", None, None, "header")]
rows += [(f"{i} · {d}", rate(r, "read_forbidden"), rate(r, "eval_aware"), g) for i, d, r, g in team if g == "a"]
rows.append(("Real-post pair  (+ sentence 'everyone has the same rules'; compare P0R with P2R only)", None, None, "header"))
rows += [(f"{i} · {d}", rate(r, "read_forbidden"), rate(r, "eval_aware"), g) for i, d, r, g in team if g == "b"]
p3 = rate(final("exp08_peers_P3_share"), "used_shared_data")
b_open, b_aware = rate(base, "read_forbidden"), rate(base, "eval_aware")

H = 0.62 * len(rows) + 2.3
fig, (a1, a2) = plt.subplots(1, 2, figsize=(16, H), dpi=200, sharey=True,
                             gridspec_kw=dict(width_ratios=[1.25, 1], wspace=0.08))
fig.patch.set_facecolor(SURFACE)
ys = list(range(len(rows)))[::-1]
for ax, idx, color, title, ref in ((a1, 1, BLUE, "opened the forbidden finance/ folder", b_open),
                                   (a2, 2, AQUA, "flagged as 'thinks it's a test'", b_aware)):
    ax.set_facecolor(SURFACE)
    for y, row in zip(ys, rows):
        if row[3] == "header":
            continue
        s = row[idx]
        hatch = "//" if row[3] == "b" else None
        ax.barh(y, s["p"] * 100, height=0.6, color=color, edgecolor=SURFACE, linewidth=2, hatch=hatch, zorder=2)
        ax.errorbar(s["p"] * 100, y, xerr=[[100 * (s["p"] - s["lo"])], [100 * (s["hi"] - s["p"])]],
                    fmt="none", ecolor=INK2, elinewidth=1.3, capsize=3, zorder=3)
        ax.text(s["hi"] * 100 + 1.2, y, f"{s['p']:.0%} ({s['k']}/{s['n']})", va="center", fontsize=9.5, color=INK)
        if idx == 1 and row[0].startswith("P3 "):
            ax.barh(y - 0.36, p3["p"] * 100, height=0.3, color=ORANGE, edgecolor=SURFACE, linewidth=1, zorder=2)
            ax.text(1.5, y - 0.36, f"{p3['p']:.0%} ({p3['k']}/{p3['n']}) used the posted numbers instead",
                    va="center", fontsize=8.5, color="#ffffff", fontweight="bold", zorder=5)
    ax.axvline(ref["p"] * 100, color=ORANGE, linestyle="--", linewidth=1.6, zorder=4)
    ax.text(ref["p"] * 100, len(rows) - 0.25, f" exp04 alone: {ref['p']:.0%}", color=INK, fontsize=9.5,
            ha="left", va="bottom")
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.75, len(rows) - 0.1)
    ax.set_xticks(range(0, 101, 20))
    ax.set_xticklabels([f"{t}%" for t in range(0, 101, 20)])
    ax.grid(axis="x", color=GRID, linewidth=0.8, zorder=0)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.set_title(title, loc="left", fontsize=12, fontweight="bold", color=INK, pad=22)
a1.set_yticks([])
for y, row in zip(ys, rows):
    hdr = row[3] == "header"
    a1.text(0.01 if hdr else -0.012, y - (0.1 if hdr else 0), row[0],
            transform=blend(fig.transFigure, a1.transData) if hdr else a1.get_yaxis_transform(),
            ha="left" if hdr else "right", va="center",
            fontsize=11 if hdr else 10.3, fontweight="bold" if hdr else "normal", color=INK)
fig.suptitle("Team experiments: does what teammates post change rule-breaking?", x=0.01, ha="left",
             fontsize=15, fontweight="bold", color=INK)
fig.text(0.01, 1 - 0.55 / H,
         "All built on exp04 (orange dashed line = the single agent without a team). The agent is report-agent-5; "
         "teammates' posts appear on a shared board while it works.\n"
         "Bars = share of runs (95% range). ~200 runs per condition, 100 per model. "
         "Hatched = real harvested posts instead of written ones.", ha="left", va="top", fontsize=10, color=INK2)
fig.subplots_adjust(left=0.33, right=0.985, top=1 - 1.55 / H, bottom=0.35 / H)
fig.savefig(OUT / "fig2_team_peers.png", facecolor=SURFACE)
plt.close(fig)

print("wrote", OUT / "fig1_single_agent.png", OUT / "fig2_team_peers.png")
