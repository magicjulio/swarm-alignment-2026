"""Appendix figure: the dummy workspace the agent sees (folder cards with file names, finance/ locked).

    .venv/bin/python scripts/workspace_figure.py      # -> paper/figures/figA_workspace.{png,pdf}

Reads dummy_files/workspace/ directly, so the figure always matches the generated files.
Only text in the figure: folder and file names.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Arc, FancyBboxPatch, Polygon, Rectangle  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
WS = ROOT / "dummy_files" / "workspace"
OUT = ROOT / "paper" / "figures"

BLUE = "#2a78d6"
INK, INK2, LINE, CARD, SURFACE = "#1d2430", "#5b6472", "#c9ced6", "#f4f5f7", "#ffffff"
BLUE_BG = "#e8f1fc"
plt.rcParams.update({"font.family": "DejaVu Sans"})

# folders in the order of README.txt; root files get their own card
FOLDERS = ["archive", "config", "data", "exports", "finance", "inventory",
           "marketing", "ops", "product", "reports", "scripts"]
cards = [("workspace/", sorted(p.name for p in WS.iterdir() if p.is_file()))]
for f in FOLDERS:
    files = sorted(str(p.relative_to(WS / f)) for p in (WS / f).rglob("*") if p.is_file())
    cards.append((f + "/", files))

NCOL = 4
SCALE = 0.62                                   # inches per data unit
CHAR = 0.7 * 6.6 / 72 / SCALE                 # width of one 6.6pt monospace char in data units
GAP, LH, HEAD, PAD = 0.22, 0.30, 0.50, 0.18    # gap, line height, header, padding (data units)
CW = 0.46 + CHAR * max(len(f) for _, fs in cards for f in fs) + 0.2   # card width fits the longest name


def file_icon(ax, x, y, color):
    """Tiny page icon with folded corner, lower-left at (x, y)."""
    w, h, c = 0.13, 0.18, 0.05
    ax.add_patch(Polygon([(x, y), (x + w, y), (x + w, y + h - c), (x + w - c, y + h), (x, y + h)],
                         closed=True, fc=SURFACE, ec=color, lw=0.6, zorder=3))
    for ly in (0.05, 0.085, 0.12):            # placeholder "content" lines
        ax.plot([x + 0.025, x + w - 0.035], [y + ly, y + ly], color=color, lw=0.35, alpha=0.6, zorder=4)


def folder_icon(ax, x, y, color):
    w, h = 0.28, 0.19
    ax.add_patch(Polygon([(x, y), (x + w, y), (x + w, y + h), (x + 0.13, y + h), (x + 0.10, y + h + 0.05),
                          (x, y + h + 0.05)], closed=True, fc=color, ec=color, lw=0.6, zorder=3))


def lock_icon(ax, x, y, color):
    ax.add_patch(Rectangle((x, y), 0.22, 0.17, fc=color, ec=color, zorder=4))
    ax.add_patch(Arc((x + 0.11, y + 0.17), 0.15, 0.20, theta1=0, theta2=180, ec=color, lw=1.6, zorder=4))


# pack cards into NCOL columns, greedy by current column height (keeps the figure compact)
heights = [HEAD + PAD + LH * len(files) for _, files in cards]
col_h, placed = [0.0] * NCOL, []
for (name, files), h in zip(cards, heights):
    c = min(range(NCOL), key=lambda i: col_h[i])
    placed.append((c, col_h[c], name, files, h))
    col_h[c] += h + GAP
total_h = max(col_h) - GAP
total_w = NCOL * CW + (NCOL - 1) * GAP

fig, ax = plt.subplots(figsize=(total_w * SCALE, total_h * SCALE))
for c, top, name, files, h in placed:
    x0, y0 = c * (CW + GAP), total_h - top - h
    locked = name == "finance/"
    accent = BLUE if locked else INK2
    ax.add_patch(FancyBboxPatch((x0, y0), CW, h, boxstyle="round,pad=0,rounding_size=0.08",
                                fc=BLUE_BG if locked else CARD, ec=BLUE if locked else LINE,
                                lw=1.4 if locked else 0.7, zorder=1))
    hy = y0 + h - HEAD / 2 - 0.06
    folder_icon(ax, x0 + 0.14, hy - 0.11, accent)
    ax.text(x0 + 0.52, hy, name, va="center", fontsize=8.5, fontweight="bold",
            color=BLUE if locked else INK, family="DejaVu Sans Mono")
    if locked:
        lock_icon(ax, x0 + CW - 0.38, hy - 0.10, BLUE)
    for i, fn in enumerate(files):
        fy = y0 + h - HEAD - PAD / 2 - LH * (i + 0.5)
        file_icon(ax, x0 + 0.22, fy - 0.09, accent)
        ax.text(x0 + 0.46, fy, fn, va="center", fontsize=6.6, color=INK, family="DejaVu Sans Mono")

ax.set_xlim(-0.05, total_w + 0.05)
ax.set_ylim(-0.05, total_h + 0.05)
ax.set_aspect("equal")
ax.axis("off")
OUT.mkdir(parents=True, exist_ok=True)
for ext in ("png", "pdf"):
    fig.savefig(OUT / f"figA_workspace.{ext}", dpi=200, bbox_inches="tight", pad_inches=0.03)
print(f"{len(cards) - 1} folders, {sum(len(f) for _, f in cards)} files -> {OUT}/figA_workspace.{{png,pdf}}")
