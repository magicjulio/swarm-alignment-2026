"""Candidate appendix assets, all from final/ (frozen code + original runs). Pick what is useful.

    .venv/bin/python scripts/appendix_assets.py        # -> paper/figures/appendix/A*.{png,pdf}

Colors keep the meaning of scripts/paper_figures.py: blue = opened finance/, orange = laundering, aqua = test-flag.
"""
import json
import math
import sys
import textwrap
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Patch  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "final"))
import locked_folder as base  # noqa: E402
import peers  # noqa: E402
import peers_v2  # noqa: E402

RES = ROOT / "final" / "results"
OUT = ROOT / "paper" / "figures" / "appendix"
OUT.mkdir(parents=True, exist_ok=True)

BLUE, ORANGE, AQUA, PURPLE = "#2a78d6", "#eb6834", "#1baf7a", "#8a5cd1"
GREY, INK, INK2, GRID, SURFACE, CARD, LINE = "#d9dde3", "#1d2430", "#5b6472", "#e6e8ec", "#ffffff", "#f4f5f7", "#c9ced6"
LIGHT_BLUE = "#a9c9ef"
MONO = "DejaVu Sans Mono"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "figure.facecolor": SURFACE, "axes.facecolor": SURFACE})


def runs(exp, tag=None, model=None):
    rs = [json.loads(line) for line in (RES / exp / "runs.jsonl").open()]
    return [r for r in rs if r["end"] != "error" and (tag is None or r.get("tag") == tag)
            and (model is None or r["model"] == model)]


def wilson(k, n, z=1.96):
    p, d = k / n, 1 + z * z / n
    c, h = (p + z * z / (2 * n)) / d, z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0, c - h), min(1, c + h)


def rate(rs, key="read_forbidden"):
    k = sum(bool(r.get(key)) for r in rs)
    return (k, len(rs)) + wilson(k, len(rs))


def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"{name}.{ext}", dpi=200, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)
    print("wrote", name)


def clean(ax, left=True):
    for s in ("top", "right") + (() if left else ("left",)):
        ax.spines[s].set_visible(False)


# conditions used across several assets: (label, exp, tag)
CONDS = [
    ("Solo, 'restricted'", "exp03_restricted_8k", None),
    ("Solo, 'forbidden' (baseline)", "exp04_forbidden_permission_8k", None),
    ("+ team sentence", "exp09_identity_only_T0", None),
    ("+ notification feed", "exp14_nonsocial_feed", "peers_NS"),
    ("+ team board, neutral (P0)", "exp05_peers_P0_neutral", None),
    ("+ peers comply (P1)", "exp06_peers_P1_comply", None),
    ("+ peers violate (P2)", "exp07_peers_P2_violate", None),
    ("+ real violating posts (P2R)", "exp13_real_posts", "peers_P2R"),
    ("+ peer shares data (P3)", "exp08_peers_P3_share", None),
]


# ------------------------------------------------------------------ A2: prompts as the agent sees them
def a2_prompts():
    W = base.WORDINGS["forbidden_permission"]
    blocks = [
        ("system prompt", W["system"], INK2),
        ("+ team conditions: inserted after the first sentence pair", peers.TEAM_SENTENCE.strip(), INK2),
        ("user prompt", base.USER_PROMPT, INK2),
        ("reply to every request_permission call", W["reply"], INK2),
        ("tools", "list_files()  read_file(path)  request_permission(path, reason)  submit_answer(text)\n"
                  "team conditions add:  read_board()  post_to_board(text)", INK2),
    ]
    width = 86                                   # chars per line; 7.3pt mono ~ 0.0745 in/char -> 6.4 in
    lines = [(t, textwrap.wrap(b, width) if "\n" not in b else b.split("\n"), c) for t, b, c in blocks]
    TITLE, LINE_H, PADV, GAPV = 0.2, 0.17, 0.14, 0.12
    h = sum(TITLE + PADV + LINE_H * len(ls) + GAPV for _, ls, _ in lines)
    fig, ax = plt.subplots(figsize=(6.8, h))
    ax.set_xlim(0, 6.8); ax.set_ylim(0, h); ax.axis("off")
    y = h
    for title, ls, c in lines:
        ax.text(0.02, y, title, fontsize=7.5, color=INK2, va="top", style="italic")
        bh = PADV + LINE_H * len(ls)
        top = y - TITLE
        ax.add_patch(FancyBboxPatch((0.02, top - bh), 6.76, bh, boxstyle="round,pad=0,rounding_size=0.05",
                                    fc=CARD, ec=LINE, lw=0.7))
        for i, l in enumerate(ls):
            ax.text(0.12, top - PADV / 2 - LINE_H * i, l, fontsize=7.3, family=MONO, color=INK, va="top")
        y = top - bh - GAPV
    save(fig, "A2_prompts")


# ------------------------------------------------------------------ A3: board stimuli per condition
def a3_board():
    conds = [("P0 neutral", "P0"), ("P1 comply", "P1"), ("P2 violate", "P2"), ("P3 share", "P3")]
    fig, axes = plt.subplots(1, 4, figsize=(11, 5.4))
    for ax, (label, c) in zip(axes, conds):
        first, second = peers.phase2_posts(c)
        posts = list(peers.NEUTRAL_EARLY) + first + second
        special = peers.CONDITIONS[c] or {}
        ax.set_xlim(0, 1); ax.axis("off")
        ax.set_title(label, loc="left", fontsize=10, color=INK, fontweight="bold")
        y = 0.99
        for i, (who, text) in enumerate(posts):
            hot = i >= 2 and who in special
            wrapped = textwrap.wrap(text, 34)
            bh = 0.045 + 0.037 * len(wrapped)
            ax.add_patch(FancyBboxPatch((0.0, y - bh), 1.0, bh, boxstyle="round,pad=0,rounding_size=0.02",
                                        fc="#e8f1fc" if hot else CARD, ec=BLUE if hot else LINE,
                                        lw=1.1 if hot else 0.6))
            ax.text(0.03, y - 0.012, who, fontsize=6.8, family=MONO, color=BLUE if hot else INK2,
                    va="top", fontweight="bold")
            for j, l in enumerate(wrapped):
                ax.text(0.03, y - 0.05 - 0.037 * j, l, fontsize=6.6, color=INK, va="top")
            y -= bh + 0.018
            if i == 1:
                ax.plot([0.02, 0.98], [y + 0.007, y + 0.007], color=INK2, lw=0.6, ls=(0, (2, 2)))
                y -= 0.012
        ax.set_ylim(-0.32, 1.0)
    save(fig, "A3_board_posts")


# ------------------------------------------------------------------ A4: trajectory raster
ACT = [("list_files", "#eceef1"), ("read allowed file", GREY), ("board / feed", "#b8c4d2"),
       ("request_permission", PURPLE), ("read finance/", BLUE), ("submit_answer", INK)]
ACOL = dict(ACT)


def step_kind(step):
    names = [c["name"] for c in step["calls"]]
    if any(c["name"] == "read_file" and str((c["args"] or {}).get("path", "") if isinstance(c["args"], dict)
                                            else "").lstrip("./").startswith("finance/") for c in step["calls"]):
        return "read finance/"
    for n, k in (("request_permission", "request_permission"), ("request_access", "request_permission"),
                 ("submit_answer", "submit_answer")):
        if n in names:
            return k
    if any(n in ("read_board", "post_to_board", "read_notifications") for n in names):
        return "board / feed"
    if "read_file" in names:
        return "read allowed file"
    if "list_files" in names:
        return "list_files"
    return "submit_answer" if step.get("text") else None


def raster(ax, rs, title):
    def key(r):
        f = r["forbidden_read_steps"]
        return (0 if f else 1, f[0] if f else 0, len(r["steps"]))
    rs = sorted(rs, key=key)
    for y, r in enumerate(rs):
        for s in r["steps"]:
            k = step_kind(s)
            if k:
                ax.add_patch(plt.Rectangle((s["step"], y), 0.92, 0.92, color=ACOL[k], lw=0))
    ax.set_xlim(0, 16); ax.set_ylim(len(rs), 0)
    ax.set_xticks([0.46 + i for i in range(0, 16, 3)]); ax.set_xticklabels(range(1, 17, 3))
    ax.set_yticks([])
    ax.set_title(title, loc="left", fontsize=9.5, color=INK)
    clean(ax, left=False)


def a4_raster():
    fig, axes = plt.subplots(1, 3, figsize=(8.4, 5.2), sharey=False)
    for ax, (t, exp, tag) in zip(axes, [("Solo (baseline)", "exp04_forbidden_permission_8k", None),
                                        ("+ team board, neutral", "exp05_peers_P0_neutral", None),
                                        ("+ peer shares data", "exp08_peers_P3_share", None)]):
        raster(ax, runs(exp, tag), t)
        ax.set_xlabel("model call", fontsize=8.5)
    axes[0].set_ylabel("runs (one row each)", fontsize=8.5)
    fig.legend(handles=[Patch(color=c, label=l) for l, c in ACT], loc="lower center", ncol=6, frameon=False,
               fontsize=8, bbox_to_anchor=(0.5, -0.03))
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    save(fig, "A4_trajectory_raster")


# ------------------------------------------------------------------ A5: did it ask first?
def a5_ask_first():
    cats = [("opened without asking", BLUE), ("asked, then opened anyway", LIGHT_BLUE),
            ("asked, did not open", PURPLE), ("neither", GREY)]

    def cat(r):
        req = [s["step"] for s in r["steps"] for c in s["calls"] if c["name"] in ("request_permission", "request_access")]
        if r["read_forbidden"]:
            return cats[1][0] if req and min(req) <= r["forbidden_read_steps"][0] else cats[0][0]
        return cats[2][0] if req else cats[3][0]

    fig, ax = plt.subplots(figsize=(6.6, 3.4))
    for y, (label, exp, tag) in enumerate(reversed(CONDS)):
        rs = runs(exp, tag)
        cnt = Counter(cat(r) for r in rs)
        left = 0
        for name, col in cats:
            w = 100 * cnt[name] / len(rs)
            ax.barh(y, w, left=left, color=col, height=0.66, edgecolor=SURFACE, lw=1)
            if w >= 7:
                ax.text(left + w / 2, y, f"{w:.0f}", ha="center", va="center", fontsize=7.5,
                        color=INK if col == GREY else SURFACE)
            left += w
    ax.set_yticks(range(len(CONDS))); ax.set_yticklabels([c[0] for c in reversed(CONDS)], fontsize=8.5, color=INK)
    ax.set_xlim(0, 100); ax.set_xticks(range(0, 101, 25)); ax.set_xticklabels([f"{t}%" for t in range(0, 101, 25)])
    ax.legend(handles=[Patch(color=c, label=l) for l, c in cats], loc="upper center", bbox_to_anchor=(0.4, -0.1),
              ncol=4, frameon=False, fontsize=7.5)
    clean(ax)
    save(fig, "A5_ask_before_open")


# ------------------------------------------------------------------ A6: which files get read
def a6_file_heatmap():
    files = sorted(base.build_workspace(base.WORDINGS["forbidden_permission"]["rule"]))
    cols = [c for c in CONDS]
    M = []
    for label, exp, tag in cols:
        rs = runs(exp, tag)
        cnt = Counter()
        for r in rs:
            seen = {str(c["args"].get("path", "")).lstrip("./") for s in r["steps"] for c in s["calls"]
                    if c["name"] == "read_file" and isinstance(c["args"], dict)}
            cnt.update(seen)
        M.append([100 * cnt[f] / len(rs) for f in files])
    M = list(map(list, zip(*M)))                              # files x conditions
    fig, ax = plt.subplots(figsize=(6.4, 8.2))
    ax.imshow(M, cmap=matplotlib.colors.LinearSegmentedColormap.from_list("b", [SURFACE, BLUE]), vmin=0, vmax=100,
              aspect="auto")
    for i, row in enumerate(M):
        for j, v in enumerate(row):
            if v >= 5:
                ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=6.3, color=SURFACE if v > 55 else INK)
    ax.set_yticks(range(len(files)))
    ax.set_yticklabels(files, fontsize=6.6, family=MONO)
    for t, f in zip(ax.get_yticklabels(), files):
        if f.startswith("finance/"):
            t.set_color(BLUE); t.set_fontweight("bold")
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels([c[0] for c in cols], rotation=40, ha="right", fontsize=7.5, color=INK)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title("% of runs that read each file", loc="left", fontsize=9.5, color=INK)
    save(fig, "A6_file_reads_heatmap")


# ------------------------------------------------------------------ A7: per-model split (dumbbell)
def a7_models():
    models = [("deepseek-v4-flash", "#5b6472"), ("qwen3.8-27b", BLUE)]
    fig, ax = plt.subplots(figsize=(6.2, 3.4))
    for y, (label, exp, tag) in enumerate(reversed(CONDS)):
        ps = []
        for m, col in models:
            k, n, p, lo, hi = rate(runs(exp, tag, m))
            ax.plot([lo * 100, hi * 100], [y, y], color=col, lw=1, alpha=0.5)
            ax.plot(p * 100, y, "o", color=col, ms=5.5, zorder=3)
            ps.append(p * 100)
        ax.plot(ps, [y, y], color=GRID, lw=3, zorder=1)
    ax.set_yticks(range(len(CONDS))); ax.set_yticklabels([c[0] for c in reversed(CONDS)], fontsize=8.5, color=INK)
    ax.set_xlim(0, 100); ax.set_xticks(range(0, 101, 20)); ax.set_xticklabels([f"{t}%" for t in range(0, 101, 20)])
    ax.grid(axis="x", color=GRID, zorder=0); ax.set_axisbelow(True)
    ax.set_xlabel("runs that opened finance/ (95% CI)", fontsize=8.5)
    ax.legend(handles=[plt.Line2D([], [], marker="o", ls="", color=c, label=m) for m, c in models],
              loc="upper center", bbox_to_anchor=(0.4, -0.16), ncol=2, frameon=False, fontsize=8)
    clean(ax)
    save(fig, "A7_per_model")


# ------------------------------------------------------------------ A8: forest plot of every run batch
def a8_forest():
    rows = []
    for d in sorted(p for p in RES.iterdir() if p.is_dir()):
        rs = runs(d.name)
        for t in dict.fromkeys(r.get("tag") for r in rs):
            sub = [r for r in rs if r.get("tag") == t]
            tok = sub[0].get("config", {}).get("max_output_tokens", 1500)
            rows.append((f"{d.name[:5]}  {t}", sub, tok, sub[0]["model"].startswith("gemma")))
    fig, ax = plt.subplots(figsize=(6.4, 0.22 * len(rows) + 0.6))
    for y, (label, rs, tok, gemma) in enumerate(reversed(rows)):
        k, n, p, lo, hi = rate(rs)
        col = PURPLE if gemma else BLUE
        ax.plot([lo * 100, hi * 100], [y, y], color=col, lw=1.4, alpha=0.55 if tok == 1500 else 1)
        ax.plot(p * 100, y, "s" if tok == 1500 else "o", color=col, ms=4.5, alpha=0.55 if tok == 1500 else 1)
        ax.text(101, y, f"{k}/{n}", va="center", fontsize=6.5, color=INK2)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in reversed(rows)], fontsize=6.6, family=MONO)
    ax.set_xlim(0, 110); ax.set_xticks(range(0, 101, 20)); ax.set_xticklabels([f"{t}%" for t in range(0, 101, 20)])
    ax.grid(axis="x", color=GRID); ax.set_axisbelow(True)
    ax.set_xlabel("runs that opened finance/ (95% CI)", fontsize=8.5)
    ax.legend(handles=[plt.Line2D([], [], marker="o", ls="", color=BLUE, label="reasoning models, 8000 tokens"),
                       plt.Line2D([], [], marker="s", ls="", color=BLUE, alpha=0.55, label="reasoning models, 1500 tokens"),
                       plt.Line2D([], [], marker="o", ls="", color=PURPLE, label="Gemma 4, no thinking")],
              loc="upper center", bbox_to_anchor=(0.45, -0.07), ncol=3, frameon=False, fontsize=7)
    clean(ax)
    save(fig, "A8_all_batches_forest")


# ------------------------------------------------------------------ A9: test-aware vs not, within each condition
def a9_eval_aware():
    conds = [c for c in CONDS if c[2] != "peers_P3" and c[1] != "exp08_peers_P3_share"]   # P3: 2 aware runs only
    fig, ax = plt.subplots(figsize=(6.2, 3.2))
    for y, (label, exp, tag) in enumerate(reversed(conds)):
        rs = runs(exp, tag)
        pts = []
        for aware, col in ((False, GREY), (True, AQUA)):
            k, n, p, lo, hi = rate([r for r in rs if bool(r["eval_aware"]) == aware])
            off = 0.13 if aware else -0.13
            ax.plot([lo * 100, hi * 100], [y + off] * 2, color=col, lw=1.2, alpha=0.8)
            ax.plot(p * 100, y + off, "o", color=col, ms=5, zorder=3, mec=INK2 if not aware else col, mew=0.5)
            ax.text(101.5, y + off, f"n={n}", va="center", fontsize=6.3, color=INK2)
    ax.set_yticks(range(len(conds))); ax.set_yticklabels([c[0] for c in reversed(conds)], fontsize=8.5, color=INK)
    ax.set_xlim(0, 110); ax.set_xticks(range(0, 101, 20)); ax.set_xticklabels([f"{t}%" for t in range(0, 101, 20)])
    ax.grid(axis="x", color=GRID); ax.set_axisbelow(True)
    ax.set_xlabel("runs that opened finance/ (95% CI)", fontsize=8.5)
    ax.legend(handles=[plt.Line2D([], [], marker="o", ls="", color=GREY, mec=INK2, mew=0.5, label="not flagged"),
                       plt.Line2D([], [], marker="o", ls="", color=AQUA, label="flagged 'thinks it's a test'")],
              loc="upper center", bbox_to_anchor=(0.4, -0.17), ncol=2, frameon=False, fontsize=8)
    clean(ax)
    save(fig, "A9_test_aware_split")


# ------------------------------------------------------------------ A10: Gemma no-thinking Asch curve (missing fig 3)
def a10_gemma():
    tags = [("alone", "solo_forbidden_permission"), ("0/8", "r42_rev0of8"), ("1/8", "r42_rev1of8"),
            ("4/8", "r42_rev4of8"), ("8/8", "r42_rev8of8")]
    reas = {t: rate(runs("exp10_asch_split", t)) for _, t in tags[1:]}
    fig, ax = plt.subplots(figsize=(4.6, 3.2))
    for series, col, data in (("Gemma 4, no thinking", PURPLE, [rate(runs("exp11_non_reasoning", t)) for _, t in tags]),
                              ("reasoning models", BLUE, [None] + [reas[t] for _, t in tags[1:]])):
        xs = [i for i, d in enumerate(data) if d]
        ps = [d[2] * 100 for d in data if d]
        ax.fill_between(xs, [d[3] * 100 for d in data if d], [d[4] * 100 for d in data if d], color=col, alpha=0.15, lw=0)
        ax.plot(xs, ps, "-o", color=col, ms=5, lw=1.8, label=series)
        for x, p in zip(xs, ps):
            ax.text(x, p + 4, f"{p:.0f}%", ha="center", fontsize=7.5, color=col, fontweight="bold")
    ax.set_xticks(range(len(tags))); ax.set_xticklabels([t[0] for t in tags], fontsize=8.5, color=INK)
    ax.set_xlabel("teammates who say they opened finance/", fontsize=8.5)
    ax.set_ylabel("runs that opened finance/", fontsize=8.5)
    ax.set_ylim(-3, 112); ax.set_yticks(range(0, 101, 20)); ax.set_yticklabels([f"{t}%" for t in range(0, 101, 20)])
    ax.grid(axis="y", color=GRID); ax.set_axisbelow(True)
    ax.legend(loc="lower right", frameon=False, fontsize=8)
    clean(ax)
    save(fig, "A10_gemma_asch_curve")


# ------------------------------------------------------------------ A11: one example transcript
def pick_example():
    for r in runs("exp04_forbidden_permission_8k"):
        names = [c["name"] for s in r["steps"] for c in s["calls"]]
        if (r["read_forbidden"] and "request_permission" in names and r["end"] == "submitted"
                and 4 <= len(r["steps"]) <= 7 and not r["eval_aware"]):
            return r


def a11_transcript():
    r = pick_example()
    items = [("user", base.USER_PROMPT)]
    for s in r["steps"]:
        if s["reasoning"]:
            rs = " ".join(s["reasoning"]).strip().replace("\n", " ")
            items.append(("reasoning", rs if len(rs) < 330 else rs[:320].rsplit(" ", 1)[0] + " …"))
        for c in s["calls"]:
            a = c["args"] if isinstance(c["args"], dict) else {}
            arg = ", ".join(f'{k}="{v}"' if len(str(v)) < 70 else f'{k}="{str(v)[:66]}…"' for k, v in a.items())
            kind = "violation" if c["name"] == "read_file" and str(a.get("path", "")).startswith("finance/") else "call"
            items.append((kind, f"{c['name']}({arg})"))
            if c["name"] != "submit_answer":
                res = str(c["result"]).replace("\n", " | ")
                items.append(("result", res if len(res) < 120 else res[:116] + " …"))
    style = {"user": (CARD, LINE, INK, "DejaVu Sans"), "reasoning": (SURFACE, LINE, INK2, "DejaVu Sans"),
             "call": ("#eef0f3", INK2, INK, MONO), "violation": ("#e8f1fc", BLUE, BLUE, MONO),
             "result": (SURFACE, GRID, INK2, MONO)}
    items = [(k, t.replace("$", r"\$")) for k, t in items]
    wrapped = [(k, textwrap.wrap(t, 96 if style[k][3] == MONO else 112)) for k, t in items]
    H = sum(0.1 + 0.16 * len(w) + 0.08 for _, w in wrapped)
    fig, ax = plt.subplots(figsize=(7.2, H))
    ax.set_xlim(0, 7.2); ax.set_ylim(0, H); ax.axis("off")
    y = H
    for k, ls in wrapped:
        fc, ec, tc, fam = style[k]
        indent = 0.35 if k in ("result",) else 0.0
        bh = 0.1 + 0.16 * len(ls)
        ax.add_patch(FancyBboxPatch((indent + 0.02, y - bh), 7.16 - indent, bh, boxstyle="round,pad=0,rounding_size=0.04",
                                    fc=fc, ec=ec, lw=1.1 if k == "violation" else 0.6))
        for i, l in enumerate(ls):
            ax.text(indent + 0.1, y - 0.06 - 0.16 * i, l, fontsize=6.6, family=fam, color=tc, va="top",
                    style="italic" if k == "reasoning" else "normal", fontweight="bold" if k == "violation" else "normal")
        y -= bh + 0.08
    save(fig, "A11_example_transcript")
    print("   example:", r["model"], "run", r["run_id"])


# ------------------------------------------------------------------ A12: setup diagram (labels only)
def a12_setup():
    fig, ax = plt.subplots(figsize=(6.6, 2.9))
    ax.set_xlim(0, 13.2); ax.set_ylim(0, 5.8); ax.axis("off")

    def box(x, y, w, h, label, fc=CARD, ec=LINE, tc=INK, lw=0.8, fs=8.5, bold=False, ls="-"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.15", fc=fc, ec=ec, lw=lw,
                                    ls=ls))
        if label:
            ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=fs, color=tc,
                    fontweight="bold" if bold else "normal", family=MONO if label.endswith(("/", ")")) else None)

    def arrow(x1, y1, x2, y2, col=INK2, ls="-", lw=1):
        ax.annotate("", (x2, y2), (x1, y1), arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, ls=ls,
                                                             shrinkA=0, shrinkB=0, mutation_scale=9))

    box(0.1, 3.5, 2.6, 1.2, "system prompt\n+ rule", fs=8)
    box(0.1, 1.5, 2.6, 1.2, "user task", fs=8)
    box(3.9, 2.0, 2.4, 2.2, "agent", fc="#eef0f3", ec=INK2, bold=True, fs=10)
    arrow(2.7, 4.1, 3.9, 3.6); arrow(2.7, 2.1, 3.9, 2.6)
    # workspace with finance/ nested inside
    box(7.6, 3.5, 5.5, 2.2, None, fc=CARD, ec=LINE)
    ax.text(7.8, 5.45, "workspace/", fontsize=8, family=MONO, color=INK, va="top")
    for k in range(6):
        ax.add_patch(plt.Rectangle((7.85 + 0.42 * k, 3.75), 0.3, 0.42, fc=SURFACE, ec=INK2, lw=0.5))
        ax.add_patch(plt.Rectangle((7.85 + 0.42 * k, 4.35), 0.3, 0.42, fc=SURFACE, ec=INK2, lw=0.5))
    box(10.6, 3.7, 2.3, 1.2, "finance/", fc="#e8f1fc", ec=BLUE, tc=BLUE, lw=1.4, fs=8.5, bold=True)
    box(7.6, 2.1, 5.5, 0.9, "request_permission(path, reason)", fs=7.5)
    box(7.6, 0.9, 5.5, 0.8, "team board / feed", fc=SURFACE, ec=INK2, fs=7.5, ls=(0, (3, 2)))
    box(7.6, 0.0, 5.5, 0.6, "submit_answer(text)", fc=INK, ec=INK, tc=SURFACE, fs=7.5)
    arrow(6.3, 3.9, 7.6, 4.3)
    arrow(6.3, 3.1, 7.6, 2.55)
    arrow(6.3, 2.6, 7.6, 1.3, ls=(0, (3, 2)))
    arrow(6.3, 2.2, 7.6, 0.3)
    ax.annotate("", (10.6, 4.3), (6.3, 4.05), arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.3, mutation_scale=10,
                connectionstyle="arc3,rad=-0.35", shrinkA=0, shrinkB=0))
    save(fig, "A12_setup_diagram")


if __name__ == "__main__":
    for f in (a2_prompts, a3_board, a4_raster, a5_ask_first, a6_file_heatmap, a7_models, a8_forest,
              a9_eval_aware, a10_gemma, a11_transcript, a12_setup):
        f()
