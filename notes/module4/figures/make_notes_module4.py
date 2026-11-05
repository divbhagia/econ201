"""
Numbers and figures for the Module IV notes. Run from the course root:

    python3 notes/module4/figures/make_notes_module4.py

One stylized example throughout (Div, 2026-11-03): eggs at a large farmers
market, dollars a dozen and dozens a week.

    demand  P = 8 - Q/40     supply  P = 2 + Q/80     clears at 160 and $4

Evenly spaced ticks and gridlines on every figure, with every point the text
quotes on a labelled tick (Div, 2026-11-03: no exceptions). The deadweight-loss
figure has gridlines every 50 cents, labelled at whole dollars and at its $3.50
cap, the one quoted price off the whole-dollar grid. The tax figure has
whole-dollar gridlines, with $3.75 and $4.50 labelled at their guides in place
of the $4 label, which would collide, so A carries its price. Axes are labelled P and Q.
Everything prints at 8 points or more. The numbers are not real egg data.
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
from matplotlib.transforms import offset_copy

matplotlib.use("Agg")
for f in Path.home().glob("Library/Fonts/FiraSans-*.otf"):
    font_manager.fontManager.addfont(str(f))
for pat in ("/usr/local/texlive/*/texmf-dist/fonts/truetype/typoland/lato/*.ttf",
            str(Path.home() / "Library/Fonts/Lato-*.ttf")):
    for f in _glob.glob(pat):
        font_manager.fontManager.addfont(f)

OUT = Path(__file__).resolve().parent
SCRATCH = Path(os.environ["FIG_PREVIEW_DIR"]) if os.environ.get("FIG_PREVIEW_DIR") else None
INK, GRID, DEMAND, SUPPLY = "#1a1a1a", "#c8c8c8", "#0072B2", "#8f4100"
CS, PS, TAX, DWL = "#d2e7f5", "#fae2cc", "#cdeee3", "#b8b8b8"
FONT = 16
GUIDE = (0, (4, 3))
NEW = (0, (6, 3))
plt.rcParams.update({"font.family": ["Lato", "Fira Sans", "sans-serif"], "font.size": FONT,
                     "pdf.fonttype": 42, "axes.edgecolor": INK, "axes.labelcolor": INK,
                     "xtick.color": INK, "ytick.color": INK})


def cross(a, b, c, k):
    q = F(a - c) / (F(b) + F(k))
    return q, a - F(b) * q


def tri(x, y):
    return F(1, 2) * x * y


# ------------------------------------------------------------ the numbers
B, K = F(1, 40), F(1, 80)
assert cross(8, B, 2, K) == (160, 4)
assert 320 - 40 * 4 == 160 and 80 * 4 - 160 == 160          # the same curves with Q on the left
assert (8 - 5) * 40 == 120 and (5 - 2) * 80 == 240          # excess supply 120 at $5
assert (8 - 2) * 40 == 240 and (2 - 2) * 80 == 0            # excess demand 240 at $2
assert 8 - F(80, 40) == 6 and 2 + F(80, 80) == 3            # 80th buyer, 80th dozen
assert tri(160, 4) == 320 and tri(160, 2) == 160            # CS and PS at E, total 480
assert (8 - 6) * 40 == 80 and 2 + F(80, 80) == 3            # cartel at $6
assert tri(80, 2) == 80 and 3 * 80 + tri(80, 1) == 280 and tri(80, 3) == 120
assert 80 + 280 + 120 == 480
CAP = F(7, 2)
assert (CAP - 2) * 80 == 120 and (8 - CAP) * 40 == 180      # cap at $3.50: 120 offered, 180 wanted
assert 8 - F(120, 40) == 5                                  # 120th buyer
assert tri(120, 3) + (5 - CAP) * 120 == 360 and tri(120, CAP - 2) == 90 and tri(40, 5 - CAP) == 30
assert 360 + 90 + 30 == 480
# The four shocks, each from A.
assert cross(11, B, 2, K) == (240, 5) and (11 - 4) * 40 == 280            # demand right 120
assert cross(5, B, 2, K) == (80, 3) and (5 - 4) * 40 == 40                # demand left 120
assert cross(8, B, F(1, 2), K) == (200, 3) and (4 - F(1, 2)) * 80 == 280  # cost down $1.50, right 120
assert cross(8, B, F(7, 2), K) == (120, 5) and (4 - F(7, 2)) * 80 == 40   # cost up $1.50, left 120
# The long run after demand shifts right: new farms offer 120 more at every price.
assert cross(11, B, F(1, 2), K) == (280, 4) and (5 - F(1, 2)) * 80 == 360 and (11 - 5) * 40 == 240
# A 20% tax on sellers: supply P = 12/5 + 3Q/200.
assert cross(8, B, F(12, 5), F(6, 5) * K) == (140, F(9, 2)) and 2 + F(140, 80) == F(15, 4)
assert F(9, 2) - F(15, 4) == F(3, 4) == F(1, 5) * F(15, 4)
assert tri(140, F(7, 2)) == 245 and tri(140, F(7, 4)) == F(245, 2) and F(3, 4) * 140 == 105
assert tri(20, F(3, 4)) == F(15, 2) and 245 + F(245, 2) + 105 + F(15, 2) == 480
# A $0.75 unit tax on sellers reaches the same point: supply P = 11/4 + Q/80.
assert cross(8, B, F(11, 4), K) == (140, F(9, 2))
# Section 2: 25 shoppers, then three farms.
SHOPPERS = [(6, 5), (4, 10), (2, 10)]
FARMS = [(3, 10), (4, 10), (6, 20)]    # Sunny Side 10 at $3 and 10 at $6, Red Barn 10 at $4, Golden Yolk 10 at $6
assert sum(n for w, n in SHOPPERS if w >= 2) == 25
assert sum(n for w, n in SHOPPERS if w >= 4) == 15
assert sum(n for w, n in SHOPPERS if w >= 6) == 5
assert sum(n for m, n in FARMS if m <= 3) == 10
assert 2 + F(80, 80) == 3 and 2 + F(160, 80) == 4 and 2 + F(320, 80) == 6   # many sellers: 8 times the three farms at $3, $4, $6
assert sum(n for m, n in FARMS if m <= 4) == 20
assert sum(n for m, n in FARMS if m <= 6) == 40


# ---------------------------------------------------------------- drawing
def style(ax, qmax=320, pmax=8, qstep=40, pstep=1):
    """Evenly spaced ticks and gridlines."""
    ax.grid(color=GRID, lw=1)
    ax.set_axisbelow("line")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0, labelsize=FONT)
    ax.set_xlim(0, qmax)
    ax.set_ylim(0, pmax)
    ax.set_xticks(range(0, qmax + 1, qstep))
    ax.set_yticks(np.arange(0, pmax + pstep, pstep))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"${y:.0f}" if y == int(y) else f"${y:.2f}"))
    ax.set_xlabel("Q", fontsize=FONT, labelpad=4)
    ax.annotate("P", xy=(0, 1), xycoords="axes fraction", xytext=(0, 4), textcoords="offset points",
                ha="center", va="bottom", fontsize=FONT)


def arrow(ax, start, end, n=4):
    """Little grey arrows just beside the curve the market moves along, from one equilibrium to the next."""
    (x0, y0), (x1, y1) = start, end
    px0, py0 = ax.transData.transform((x0, y0))
    px1, py1 = ax.transData.transform((x1, y1))
    nx, ny = -(py1 - py0), px1 - px0
    size = (nx ** 2 + ny ** 2) ** 0.5
    nx, ny = nx / size, ny / size
    if ny < 0:
        nx, ny = -nx, -ny
    shifted = offset_copy(ax.transData, fig=ax.figure, x=6 * nx, y=6 * ny, units="points")
    step = 0.84 / n
    for i in range(n):
        t0 = 0.08 + i * step
        t1 = t0 + step * 0.72
        ax.annotate("", xy=(x0 + t1 * (x1 - x0), y0 + t1 * (y1 - y0)), xytext=(x0 + t0 * (x1 - x0), y0 + t0 * (y1 - y0)),
                    xycoords=shifted, textcoords=shifted, zorder=10,
                    arrowprops=dict(arrowstyle="-|>", color="#7a7a7a", lw=1.6, mutation_scale=12, shrinkA=0, shrinkB=0))


def ln(ax, a, b, color, q0, q1, ls="-"):
    q = np.array([q0, q1], float)
    ax.plot(q, float(a) + float(b) * q, color=color, lw=3, ls=ls, solid_capstyle="round", zorder=5)


def guides(ax, q, p):
    ax.plot([0, q], [p, p], color=INK, lw=1.5, ls=GUIDE, zorder=4)
    ax.plot([q, q], [0, p], color=INK, lw=1.5, ls=GUIDE, zorder=4)
    ax.plot(q, p, marker="o", ms=8, color=INK, zorder=9)


def pt(ax, q, p, name, dx, dy, ha="left", va="center"):
    guides(ax, q, p)
    ax.annotate(name, xy=(q, p), xytext=(dx, dy), textcoords="offset points", ha=ha, va=va,
                fontsize=FONT, fontweight="bold", zorder=9)


def tx(ax, x, y, s, color=INK, ha="center", va="center", fs=FONT):
    ax.text(x, y, s, color=color, ha=ha, va=va, fontsize=fs, fontweight="bold", zorder=8)


def save(fig, name):
    fig.savefig(OUT / f"{name}.pdf", format="pdf", bbox_inches="tight", pad_inches=0.04)
    if SCRATCH:
        fig.savefig(SCRATCH / f"{name}.png", dpi=110, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)


def tiers_xy(tiers):
    xs, ys, left = [], [], 0
    for h, n in tiers:
        xs += [left, left + n]
        ys += [h, h]
        left += n
    return xs, ys


TOP = (0, 8, "center", "bottom")
RIGHT = (9, 0, "left", "center")
LABELS = dict(ha="left", fs=FONT - 1)


def base(ax, qmax=320):
    ln(ax, 8, -B, DEMAND, 0, min(qmax, 320))
    ln(ax, 2, K, SUPPLY, 0, qmax)


# Every panel from section 3 on has the same size, in inches.
PW, PH, LEFT, BOTTOM, TOPROOM = 4.73, 3.3, 0.7, 0.62, 0.6


def single():
    w, h = LEFT + PW + 0.2, BOTTOM + PH + TOPROOM
    fig = plt.figure(figsize=(w, h), dpi=100)
    return fig, fig.add_axes([LEFT / w, BOTTOM / h, PW / w, PH / h])


def double():
    gap = 0.72
    w, h = LEFT + 2 * PW + gap + 0.2, BOTTOM + PH + TOPROOM
    fig = plt.figure(figsize=(w, h), dpi=100)
    a1 = fig.add_axes([LEFT / w, BOTTOM / h, PW / w, PH / h])
    a2 = fig.add_axes([(LEFT + PW + gap) / w, BOTTOM / h, PW / w, PH / h])
    return fig, (a1, a2)


def two_panels():
    return plt.subplots(1, 2, figsize=(11.0, 4.1), dpi=100)


def finish_two(fig):
    fig.subplots_adjust(left=0.065, right=0.985, top=0.89, bottom=0.17, wspace=0.14)


# ---------------------------------------------------------------- figures
fig, (a1, a2) = two_panels()
style(a1, qmax=30, qstep=5, pstep=2)
xs, ys = tiers_xy(SHOPPERS)
a1.plot(xs, ys, color=DEMAND, lw=3.2, solid_capstyle="butt", zorder=5)
a1.set_title("(a) The example above", fontsize=FONT + 3, pad=8)
style(a2, qstep=80, pstep=2)
ln(a2, 8, -B, DEMAND, 0, 320)
guides(a2, 160, 4)
a2.set_title("(b) Many buyers", fontsize=FONT + 3, pad=8)
finish_two(fig)
save(fig, "eggs-demand")

fig, (a1, a2) = two_panels()
style(a1, qmax=50, qstep=10, pstep=1)
xs, ys = tiers_xy(FARMS)
a1.plot(xs, ys, color=SUPPLY, lw=3.2, solid_capstyle="butt", zorder=5)
a1.set_title("(a) The example above", fontsize=FONT + 3, pad=8)
tx(a1, 5, 2.5, "Sunny Side", SUPPLY, fs=FONT - 1)
tx(a1, 15.5, 3.5, "Red Barn", SUPPLY, fs=FONT - 1)
tx(a1, 30.5, 5.5, "Golden Yolk, Sunny Side", SUPPLY, fs=FONT - 1)
style(a2, qstep=80, pstep=1)
ln(a2, 2, K, SUPPLY, 0, 320)
guides(a2, 160, 4)
a2.set_title("(b) Many sellers", fontsize=FONT + 3, pad=8)
finish_two(fig)
save(fig, "eggs-supply")

fig, ax = single()
style(ax)
base(ax)
pt(ax, 160, 4, "E", *TOP)
ax.plot([0, 120], [5, 5], color=GRID, lw=1.5, ls=GUIDE, zorder=4)
ax.plot([120, 240], [5, 5], color="#d9a06b", lw=2.2, ls=NEW, zorder=3)
ax.plot([0, 240], [2, 2], color="#7fb6d9", lw=2.2, ls=NEW, zorder=3)
ax.plot([120, 120], [0, 5], color="#d9a06b", lw=2.0, ls=NEW, zorder=3)
ax.plot([240, 240], [0, 5], color="#d9a06b", lw=2.0, ls=NEW, zorder=3)
ax.text(180, 5.45, "Excess supply, 120", color=SUPPLY, ha="center", va="center", fontsize=FONT - 1, zorder=8)
ax.text(70, 1.55, "Excess demand, 240", color=DEMAND, ha="center", va="center", fontsize=FONT - 1, zorder=8,
        bbox=dict(fc="white", ec="none", pad=1.2))
tx(ax, 250, 2.2, "Demand", DEMAND, ha="left", fs=FONT - 1)
tx(ax, 318, 6.3, "Supply", SUPPLY, ha="right", fs=FONT - 1)
save(fig, "eggs-equilibrium")

fig, (a1, a2) = double()
for ax, title in ((a1, "(a) One buyer and one seller"), (a2, "(b) All buyers and sellers")):
    style(ax)
    base(ax)
    ax.set_title(title, fontsize=FONT + 3, pad=8)
    tx(ax, 245, 2.25, "Demand", DEMAND, ha="left", fs=FONT - 1)
    tx(ax, 318, 6.3, "Supply", SUPPLY, ha="right", fs=FONT - 1)
pt(a1, 160, 4, "E", *TOP)
a1.plot([80, 80], [0, 3], color=INK, lw=1.5, ls=GUIDE, zorder=4)
a1.plot([80, 80], [4, 6], color=DEMAND, lw=5, solid_capstyle="butt", zorder=6)
a1.plot([80, 80], [3, 4], color=SUPPLY, lw=5, solid_capstyle="butt", zorder=6)
a1.plot(80, 6, marker="o", ms=7, color=INK, zorder=9)
a1.plot(80, 3, marker="o", ms=7, color=INK, zorder=9)
# The same position and style for both labels: left of their bars, not bold.
a1.text(74, 5, "Buyer gains\n\\$2", color=DEMAND, ha="right", va="center", fontsize=FONT - 1, linespacing=1.05, zorder=8)
a1.text(74, 3.42, "Seller gains\n\\$1", color=SUPPLY, ha="right", va="center", fontsize=FONT - 1, linespacing=1.05, zorder=8)
a2.fill_between([0, 160], [8, 4], 4, color=CS, zorder=1)
a2.fill_between([0, 160], [2, 4], 4, color=PS, zorder=1)
pt(a2, 160, 4, "E", *TOP)
tx(a2, 44, 5.25, "CS")
tx(a2, 44, 3.4, "PS")
save(fig, "eggs-surplus")

fig, (a1, a2) = double()
for ax, p, q, title in ((a1, 6, 80, "(a) Price held at \\$6"), (a2, 3.5, 120, "(b) Price held at \\$3.50")):
    style(ax, pstep=0.5)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _, p=p: f"${y:.0f}" if y == int(y) else (f"${y:.2f}" if y == p else "")))
    wtp, mc = 8 - q / 40, 2 + q / 80
    ax.fill_between([0, q], [8, wtp], p, color=CS, zorder=1)
    ax.fill_between([0, q], [2, mc], p, color=PS, zorder=1)
    ax.fill_between([q, 160], [wtp, 4], [mc, 4], color=DWL, zorder=1)
    base(ax)
    ax.plot([0, q], [p, p], color=INK, lw=1.5, ls=GUIDE, zorder=4)
    ax.plot([q, q], [0, wtp], color=INK, lw=1.5, ls=GUIDE, zorder=4)
    guides(ax, 160, 4)
    ax.annotate("E", xy=(160, 4), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=FONT, fontweight="bold", zorder=9)
    ax.plot(q, wtp, marker="o", ms=7, color=INK, zorder=9)
    ax.plot(q, mc, marker="o", ms=7, color=INK, zorder=9)
    if p == 6:
        tx(ax, 20, 6.55, "CS")
        tx(ax, 32, 4.75, "PS")
        dx = 115
    else:
        tx(ax, 40, 4.75, "CS")
        tx(ax, 28, 3.05, "PS")
        dx = 140
    ax.annotate("DWL", xy=(dx, 4.25), xytext=(dx, 1.25), fontsize=FONT - 1, fontweight="bold", ha="center",
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.2), zorder=9)
    tx(ax, 245, 2.25, "Demand", DEMAND, ha="left", fs=FONT - 1)
    tx(ax, 318, 6.3, "Supply", SUPPLY, ha="right", fs=FONT - 1)
    ax.set_title(title, fontsize=FONT + 3, pad=8)
save(fig, "eggs-dwl")


LIGHT_SUPPLY, LIGHT_DEMAND = "#d9a06b", "#7fb6d9"


def shift_figure(stop):
    """Demand, supply, and A. The $4 guide stops where the excess line begins."""
    fig, ax = single()
    style(ax)
    base(ax)
    ax.plot([0, stop], [4, 4], color=INK, lw=1.5, ls=GUIDE, zorder=4)
    ax.plot([160, 160], [0, 4], color=INK, lw=1.5, ls=GUIDE, zorder=4)
    ax.plot(160, 4, marker="o", ms=8, color=INK, zorder=9)
    ax.annotate("A", xy=(160, 4), xytext=(0, 8), textcoords="offset points", ha="center", va="bottom",
                fontsize=FONT, fontweight="bold", zorder=9)
    return fig, ax


def excess(ax, q1, q2, p, color, light, name, x, y, tip=None, drop=None):
    """A light dashed line for the gap at the old price, a light drop to the
    axis from the far end so its quantity can be read, and a plain label."""
    ax.plot([q1, q2], [p, p], color=light, lw=2.4, ls=NEW, zorder=4)
    ax.plot([drop, drop], [0, p], color=light, lw=2.0, ls=NEW, zorder=3)
    props = dict(arrowstyle="-|>", color=color, lw=1.2) if tip else None
    ax.annotate(name, xy=tip if tip else (x, y), xytext=(x, y), color=color, fontsize=FONT - 1, ha="center", va="center",
                linespacing=1.05, zorder=9, arrowprops=props,
                bbox=dict(fc="white", ec="none", pad=1.2))


# Demand shifts right: excess demand at $4, then along supply from A to B.
fig, ax = shift_figure(160)
ln(ax, 11, -B, DEMAND, 120, 320, ls=NEW)
excess(ax, 160, 280, 4, DEMAND, LIGHT_DEMAND, "Excess\ndemand, 120", 282, 2.45, tip=(268, 3.95), drop=280)
pt(ax, 240, 5, "B", *TOP)
arrow(ax, (160, 4), (240, 5))
tx(ax, 165, 7.3, "New demand", DEMAND, ha="left", fs=FONT - 1)
tx(ax, 65, 6.72, "Demand", DEMAND, ha="left", fs=FONT - 1)
tx(ax, 318, 6.3, "Supply", SUPPLY, ha="right", fs=FONT - 1)
save(fig, "eggs-shift-a")

# Demand shifts left: excess supply at $4, then along supply from A to B.
fig, ax = shift_figure(40)
ln(ax, 5, -B, DEMAND, 0, 200, ls=NEW)
excess(ax, 40, 160, 4, SUPPLY, LIGHT_SUPPLY, "Excess\nsupply, 120", 76, 4.62, drop=40)
pt(ax, 80, 3, "B", -6, -8, ha="right", va="top")
arrow(ax, (160, 4), (80, 3))
tx(ax, 111, 1.1, "New\ndemand", DEMAND, fs=FONT - 1)
tx(ax, 205, 3.2, "Demand", DEMAND, ha="left", fs=FONT - 1)
tx(ax, 318, 6.3, "Supply", SUPPLY, ha="right", fs=FONT - 1)
save(fig, "eggs-shift-b")

# Supply shifts right: excess supply at $4, then along demand from A to B.
fig, ax = shift_figure(160)
ln(ax, F(1, 2), K, SUPPLY, 0, 320, ls=NEW)
excess(ax, 160, 280, 4, SUPPLY, LIGHT_SUPPLY, "Excess\nsupply, 120", 282, 2.85, tip=(258, 3.95), drop=280)
pt(ax, 200, 3, "B", 6, -8, ha="left", va="top")
arrow(ax, (160, 4), (200, 3), n=3)
tx(ax, 55, 0.82, "New supply", SUPPLY, ha="left", fs=FONT - 1)
tx(ax, 205, 1.3, "Demand", DEMAND, ha="left", fs=FONT - 1)
tx(ax, 318, 6.3, "Supply", SUPPLY, ha="right", fs=FONT - 1)
save(fig, "eggs-shift-c")

# Supply shifts left: excess demand at $4, then along demand from A to B.
fig, ax = shift_figure(40)
ln(ax, F(7, 2), K, SUPPLY, 0, 320, ls=NEW)
excess(ax, 40, 160, 4, DEMAND, LIGHT_DEMAND, "Excess\ndemand, 120", 70, 1.7, tip=(90, 3.95), drop=40)
pt(ax, 120, 5, "B", *TOP)
arrow(ax, (160, 4), (120, 5), n=3)
tx(ax, 245, 6.98, "New supply", SUPPLY, ha="right", fs=FONT - 1)
tx(ax, 245, 2.25, "Demand", DEMAND, ha="left", fs=FONT - 1)
tx(ax, 318, 5.1, "Supply", SUPPLY, ha="right", fs=FONT - 1)
save(fig, "eggs-shift-d")

# The market of the demand-shifts-right figure, A to B, carried on to C: the long
# run as (a) another shift and (b) a flatter supply curve through A and C.
fig, (a1, a2) = double()
for ax, title in ((a1, "(a) As another shift"), (a2, "(b) As a flatter supply curve")):
    style(ax, qmax=360)
    ln(ax, 8, -B, DEMAND, 0, 320)
    ln(ax, 11, -B, DEMAND, 120, 360, ls=NEW)
    ln(ax, 2, K, SUPPLY, 0, 360)
    pt(ax, 160, 4, "A", *TOP)
    pt(ax, 240, 5, "B", *TOP)
    pt(ax, 280, 4, "C", 10, 8, ha="left", va="bottom")
    arrow(ax, (160, 4), (240, 5))
    tx(ax, 65, 6.72, "Demand", DEMAND, ha="left", fs=FONT - 1)
    tx(ax, 165, 7.3, "New demand", DEMAND, ha="left", fs=FONT - 1)
    ax.set_title(title, fontsize=FONT + 3, pad=8)
ln(a1, F(1, 2), K, SUPPLY, 0, 360, ls=NEW)
arrow(a1, (240, 5), (280, 4), n=3)
excess(a1, 240, 360, 5, SUPPLY, LIGHT_SUPPLY, "Excess\nsupply, 120", 325, 1.5, tip=(310, 4.95), drop=360)
tx(a1, 358, 6.85, "Supply", SUPPLY, ha="right", fs=FONT - 1)
tx(a1, 70, 0.85, "New supply", SUPPLY, ha="left", fs=FONT - 1)
a2.plot([0, 360], [4, 4], color=SUPPLY, lw=3, ls=NEW, zorder=5)
arrow(a2, (160, 4), (280, 4))
tx(a2, 358, 6.85, "Short-run supply", SUPPLY, ha="right", fs=FONT - 1)
tx(a2, 8, 4.38, "Long-run supply", SUPPLY, ha="left", fs=FONT - 1)
save(fig, "eggs-longrun")

fig, ax = single()
style(ax, qmax=200, qstep=20)
ax.set_yticks(range(9), ["$0", "$1", "$2", "$3", "", "$5", "$6", "$7", "$8"])
ax.set_yticks([3.75, 4.5], ["$3.75", "$4.50"], minor=True)
ax.tick_params(which="minor", length=0, labelsize=FONT)
ax.fill_between([0, 140], [8, 4.5], 4.5, color=CS, zorder=1)
ax.fill_between([0, 140], 3.75, 4.5, color=TAX, zorder=1)
ax.fill_between([0, 140], [2, 3.75], 3.75, color=PS, zorder=1)
ax.fill_between([140, 160], [4.5, 4], [3.75, 4], color=DWL, zorder=1)
base(ax, 200)
ln(ax, F(12, 5), F(6, 5) * K, SUPPLY, 0, 200, ls=NEW)
pt(ax, 160, 4, "A ($4)", 34, -2, "left", "center")
pt(ax, 140, 4.5, "B", 0, 8, "center", "bottom")
ax.plot([0, 140], [3.75, 3.75], color=INK, lw=1.5, ls=GUIDE, zorder=4)
ax.plot(140, 3.75, marker="o", ms=8, color=INK, zorder=9)
tx(ax, 35, 5.05, "CS")
tx(ax, 70, 4.12, "Tax")
tx(ax, 25, 3.3, "PS")
ax.annotate("DWL", xy=(147, 4.1), xytext=(118, 1.8), fontsize=FONT, fontweight="bold", ha="center",
            arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.2), zorder=9)
tx(ax, 196, 2.55, "Demand", DEMAND, ha="right")
tx(ax, 72, 2.2, "Supply", SUPPLY, ha="left")
tx(ax, 118, 6.3, "Supply with tax", SUPPLY, ha="left")
save(fig, "eggs-tax")
