"""
Figures and numbers for the Midterm 2 materials: the two practice exams'
long-form questions. Every number the
materials quote is asserted here.

Run from the course root:

    python3 exams/midterm2/figures/make_midterm2.py

Same drawing style as the lecture 17 to 20 figures: demand in Okabe-Ito blue,
supply in dark orange, shading under the gridlines, every value on a gridline
so students read the graph rather than compute (Div, 2026-11-03).

Output, in exams/midterm2/figures/:
  soda.pdf          practice exam A: demand, supply, and supply with the 50%
                    tax on a grid, nothing marked; soda-key.pdf adds A, B,
                    the price sellers keep, and the four shaded regions
  quinoa.pdf        practice exam B: demand, new demand, and supply on a
                    grid, nothing marked; quinoa-key.pdf adds the new supply
                    curve and the points A, B, and C
"""
import glob as _glob
import os
from fractions import Fraction as F
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter

matplotlib.use("Agg")

for f in Path.home().glob("Library/Fonts/FiraSans-*.otf"):
    font_manager.fontManager.addfont(str(f))
for pat in ("/usr/local/texlive/*/texmf-dist/fonts/truetype/typoland/lato/*.ttf",
            str(Path.home() / "Library/Fonts/Lato-*.ttf")):
    for f in _glob.glob(pat):
        font_manager.fontManager.addfont(f)

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "exams" / "midterm2" / "figures"
SCRATCH = Path(os.environ["FIG_PREVIEW_DIR"]) if os.environ.get("FIG_PREVIEW_DIR") else None

INK = "#1a1a1a"
GRID = "#c8c8c8"
DEMAND = "#0072B2"
SUPPLY = "#8f4100"
CS_AREA = "#d2e7f5"
PS_AREA = "#fae2cc"
TAX_AREA = "#cdeee3"
DWL_AREA = "#b8b8b8"
FONT = 15
SIZE = (7.2, 4.6)
GUIDE = (0, (4, 3))

plt.rcParams.update({
    "font.family": ["Lato", "Fira Sans", "sans-serif"], "font.size": FONT,
    "pdf.fonttype": 42, "axes.edgecolor": INK, "axes.labelcolor": INK,
    "xtick.color": INK, "ytick.color": INK,
})


def save(fig, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format="pdf")
    if SCRATCH:
        fig.savefig(SCRATCH / f"{out.stem}.png", format="png", dpi=110)
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


def axes(qmax, pmax, qstep, pstep, xlabel, ylabel="Dollars", label_every=1, size=SIZE):
    fig, ax = plt.subplots(figsize=size, dpi=100)
    ax.grid(color=GRID, lw=1)
    ax.set_axisbelow("line")           # shading under the grid, grid under the lines
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0, labelsize=FONT - 2)
    ax.set_xlim(0, qmax)
    ax.set_ylim(0, pmax)
    ax.set_xticks(range(0, qmax + 1, qstep))
    ax.set_yticks(range(0, pmax + 1, pstep))
    ax.yaxis.set_major_formatter(FuncFormatter(
        lambda y, _: f"${y:,.0f}" if round(y) % (pstep * label_every) == 0 else ""))
    ax.set_xlabel(xlabel, fontsize=FONT, labelpad=6)
    ax.set_ylabel(ylabel, fontsize=FONT, labelpad=6)
    fig.subplots_adjust(left=0.11, right=0.97, top=0.97, bottom=0.17)
    return fig, ax


def line(ax, a, b, color, qmax, q0=0, ls="-"):
    """P = a + bQ from q0 to qmax."""
    q = np.array([q0, qmax], dtype=float)
    ax.plot(q, float(a) + float(b) * q, color=color, lw=3.2, ls=ls, solid_capstyle="round", zorder=5)


def label(ax, x, y, text, color=INK, ha="left", va="center", fs=FONT):
    ax.text(float(x), float(y), text, color=color, ha=ha, va=va, fontsize=fs, fontweight="bold", zorder=8)


def point(ax, q, p, name, dx=2, dy=2, ha="left", va="bottom", guides=True):
    q, p = float(q), float(p)
    if guides:
        ax.plot([0, q], [p, p], color=INK, lw=1.6, ls=GUIDE, zorder=4)
        ax.plot([q, q], [0, p], color=INK, lw=1.6, ls=GUIDE, zorder=4)
    ax.plot(q, p, marker="o", ms=8, color=INK, zorder=9)
    ax.annotate(name, xy=(q, p), xytext=(dx, dy), textcoords="offset points", ha=ha, va=va,
                fontsize=FONT, fontweight="bold", color=INK, zorder=9)


def cross(d, s):
    """D: P = a - bQ given as (a, b) with b > 0; S: P = c + kQ. Returns Q, P."""
    a, b = d
    c, k = s
    q = (a - c) / (b + k)
    return q, a - b * q


def tri(base, height):
    return F(1, 2) * base * height


# ---------------------------------------------------------- the numbers ---
def taxed(d, s, t):
    """D: P = a - bQ; S: P = c + kQ; percentage tax t. Returns Q0, P0, Qt, Pb, Ps."""
    q0, p0 = cross(d, s)
    c, k = s
    qt, pb = cross(d, (c * (1 + t), k * (1 + t)))
    return q0, p0, qt, pb, c + k * qt


# Practice exam A, Part 2: a 50% tax on soda.
SODA_D, SODA_S, SODA_T = (F(13), F(1, 10)), (F(4), F(1, 20)), F(1, 2)
assert taxed(SODA_D, SODA_S, SODA_T) == (60, 7, 40, 9, 6)
assert F(1, 2) * 6 == 3 and F(2, 3) + F(1, 3) == 1            # the tax per case, 50% of $6; shares 2/3, 1/3
assert tri(60, 13 - 7) == 180 and tri(60, 7 - 4) == 90       # CS and PS before
assert tri(40, 13 - 9) == 80 and tri(40, 6 - 4) == 40        # CS and PS after
assert 3 * 40 == 120 and tri(20, 3) == 30 and 180 + 90 == 80 + 40 + 120 + 30

# Practice exam B, Part 2: quinoa, a demand shift and then entry.
QU_D, QU_D2, QU_S, QU_S2 = (F(9), F(1, 50)), (F(13), F(1, 50)), (F(1), F(1, 50)), (F(-1), F(1, 50))
assert cross(QU_D, QU_S) == (200, 5)                         # A
assert cross(QU_D2, QU_S) == (300, 7)                        # B: demand up 200 at every price
assert cross(QU_D2, QU_S2) == (350, 6)                       # C: supply up 100 at every price
assert (13 - 5) * 50 == 400 and (5 - 1) * 50 == 200          # at $5 after the shift: 400 wanted, 200 offered
assert (7 + 1) * 50 == 400 and (13 - 7) * 50 == 300          # at $7 after entry: 400 offered, 300 wanted


# Practice exam B, Part 1.
assert 8 * 30 == 240                                         # market supply at $6
assert F(1, 4) * F(36, 5) == F(9, 5) and F(36, 5) + F(9, 5) == 9   # 25% of $7.20 is $1.80


# --------------------------------------------------------------- figures --
def draw_soda(out, key):
    fig, ax = axes(100, 14, 10, 1, "Q (cases of soda a week)", ylabel="P (dollars a case)")
    if key:
        ax.fill_between([0, 40], [13, 9], 9, color=CS_AREA, zorder=1)
        ax.fill_between([0, 40], 6, 9, color=TAX_AREA, zorder=1)
        ax.fill_between([0, 40], [4, 6], 6, color=PS_AREA, zorder=1)
        ax.fill_between([40, 60], [9, 7], [6, 7], color=DWL_AREA, zorder=1)
    line(ax, 13, -F(1, 10), DEMAND, 100)
    line(ax, 4, F(1, 20), SUPPLY, 100)
    line(ax, 6, F(3, 40), SUPPLY, 100, ls=(0, (6, 3)))
    label(ax, 78, 3.6, "Demand", DEMAND, ha="left", va="top")
    label(ax, 99, 8.4, "Supply", SUPPLY, ha="right", va="top")
    label(ax, 90, 14.0, "Supply with tax", SUPPLY, ha="right", va="top")
    if key:
        point(ax, 60, 7, "A", dx=8, dy=-2, ha="left", va="top")
        point(ax, 40, 9, "B", dx=-2, dy=8, ha="center")
        ax.plot([0, 40], [6, 6], color=INK, lw=1.6, ls=GUIDE, zorder=4)
        ax.plot(40, 6, marker="o", ms=8, color=INK, zorder=9)
        label(ax, 12, 10.4, "CS", ha="center")
        label(ax, 10, 8.2, "Tax", ha="center")
        label(ax, 16, 5.2, "PS", ha="center")
        ax.annotate("DWL", xy=(47, 7.4), xytext=(58, 11.2), fontsize=FONT, fontweight="bold",
                    color=INK, ha="center", zorder=9,
                    arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.2))
    save(fig, out)


def draw_quinoa(out, key):
    fig, ax = axes(450, 14, 50, 1, "Q (million pounds a year)", ylabel="P (dollars a pound)")
    line(ax, 9, -F(1, 50), DEMAND, 450)
    line(ax, 13, -F(1, 50), DEMAND, 450, q0=0, ls=(0, (6, 3)))
    line(ax, 1, F(1, 50), SUPPLY, 450)
    label(ax, 372, 2.2, "Demand", DEMAND, ha="left", va="bottom")
    label(ax, 105, 11.2, "New demand", DEMAND, ha="left", va="bottom")
    label(ax, 405, 10.0, "Supply", SUPPLY, ha="right", va="bottom")
    if key:
        line(ax, -1, F(1, 50), SUPPLY, 450, q0=50, ls=(0, (6, 3)))
        label(ax, 445, 6.9, "New supply", SUPPLY, ha="right", va="top")
        point(ax, 200, 5, "A", dx=-6, dy=8, ha="right")
        point(ax, 300, 7, "B", dx=-6, dy=8, ha="right")
        point(ax, 350, 6, "C", dx=-6, dy=-4, ha="right", va="top")
        for start, end in (((200, 5), (300, 7)), ((300, 7), (350, 6))):
            ax.annotate("", xy=end, xytext=start, zorder=8,
                        arrowprops=dict(arrowstyle="-|>", color="#6b6b6b", lw=1.6, shrinkA=9, shrinkB=9,
                                        connectionstyle="arc3,rad=0"))
    save(fig, out)


if __name__ == "__main__":
    draw_soda(OUT / "soda.pdf", key=False)
    draw_soda(OUT / "soda-key.pdf", key=True)
    draw_quinoa(OUT / "quinoa.pdf", key=False)
    draw_quinoa(OUT / "quinoa-key.pdf", key=True)
