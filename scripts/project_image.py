"""Project image for the submission (16:9). Numbers from final/results (exp04, exp09, exp14).
    python3 scripts/project_image.py  -> paper/project_image.png"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyBboxPatch  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "paper" / "project_image.png"
BG, INK, INK2, BLUE, LIGHT, ORANGE, LINE = "#0f1726", "#f3f5f9", "#9aa6b8", "#3d8bff", "#7fa6d9", "#ff7a45", "#26324a"

fig = plt.figure(figsize=(16, 9), dpi=120)
fig.patch.set_facecolor(BG)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 160)
ax.set_ylim(0, 90)
ax.axis("off")

# title block (left)
ax.text(8, 70, "Peerless", fontsize=64, fontweight="bold", color=INK, va="baseline")
ax.text(8, 57, "Pressure", fontsize=64, fontweight="bold", color=ORANGE, va="baseline")
ax.text(8, 47, "How team context makes AI agents\nbreak more rules", fontsize=22, color=INK, va="top", linespacing=1.3)
ax.text(8, 30, "No teammate pushes. No teammate breaks the rule.\nJust being on a team is enough.",
        fontsize=15, color=INK2, va="top", linespacing=1.45)
ax.text(8, 8, "Großerode · Viswanath · Maessen   |   Apart Research Swarm Alignment Hackathon 2026",
        fontsize=12, color=INK2)

# chart (right): % of runs that opened the forbidden folder
bars = [("Alone", 40, LIGHT, 1), ("+ \"you are on\nthe team\"", 55, BLUE, 1), ("+ team board,\nordinary posts", 73, BLUE, 5)]
x0, w, gap, base, scale = 92, 15, 6, 16, 0.62
ax.plot([x0 - 3, x0 + 3 * w + 2 * gap + 3], [base, base], color=LINE, lw=2)
for i, (lab, v, col, n_agents) in enumerate(bars):
    x = x0 + i * (w + gap)
    h = v * scale
    ax.add_patch(FancyBboxPatch((x, base), w, h, boxstyle="round,pad=0,rounding_size=1.2", fc=col, ec="none"))
    ax.text(x + w / 2, base + h + 2.2, f"{v}%", ha="center", fontsize=30, fontweight="bold", color=INK)
    ax.text(x + w / 2, base - 2.5, lab, ha="center", va="top", fontsize=13, color=INK2, linespacing=1.25)
    # agents: the tested agent (orange ring) plus teammates
    cx = x + w / 2 - (n_agents - 1) * 1.5
    for j in range(n_agents):
        ax.add_patch(Circle((cx + j * 3.0, base + h - 3.2), 1.25, fc=ORANGE if j == 0 else INK, ec="none"))
ax.text(x0 - 3, 83, "Agents that opened the forbidden folder", fontsize=15, color=INK, fontweight="bold")
ax.text(x0 - 3, 79.5, "orange = the tested agent, white = teammates\n~200 runs per bar, Qwen3.8-27B + DeepSeek-V4-Flash", va="top", linespacing=1.4,
        fontsize=11.5, color=INK2)
fig.savefig(OUT, facecolor=BG)
print("wrote", OUT)
