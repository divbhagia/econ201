"""
Figures and numbers for Lecture 6: the cost function of Beautiful Cars
(CORE Figures 7.7 and 7.8), and the worksheet's cost table.

Run from the course root:

    python3 slides/figures/make_lecture6.py

No data downloads. One cost function everywhere. The book's Beautiful Cars
has C(Q) = 80,000 + 14,400 Q; the deck and worksheet use easier numbers so
students can do the arithmetic in their heads, C(Q) = 60,000 + 10,000 Q per
day, so average cost is 10,000 + 60,000 / Q and marginal cost is 10,000 at
every Q. Two outputs, 20 and 50 cars a day,
are marked on every figure, labelled with their values.

Output, in slides/img/:
  cheerios-schedule.svg   the lecture 5 demand curve on its own, column size
  cheerios-curves.svg     four panels, the worksheet schedule's demand,
                          revenue, cost, and profit against Q, full-slide
                          size; numbers imported from make_lecture5.py
  cars-total-cost.svg     the cost function with the fixed cost intercept
                          and the 10-car point labelled with its total,
                          full width, to sit under a line of text
  cars-average-cost.svg   the average cost curve through the same two
                          points, each labelled with its cost per car
  cars-ac-mc.svg          average cost and the flat marginal cost line
The AC figures at column size so the slide explains them alongside.

Accessibility: Okabe-Ito derived colours, every point labelled with its
value on the figure itself, so nothing rests on reading positions or
colours by eye; text converted to paths so the SVG looks the same on any
machine. Alt text lives in the slide file beside each image.
"""

import argparse
import glob as _glob
import os
import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter

matplotlib.use("Agg")

# Same font setup as make_lecture5.py: Fira Sans from ~/Library/Fonts, Lato
# from the TeX tree, so the figures match the slide typography.
for f in Path.home().glob("Library/Fonts/FiraSans-*.otf"):
    font_manager.fontManager.addfont(str(f))
for pat in ("/usr/local/texlive/*/texmf-dist/fonts/truetype/typoland/lato/*.ttf",
            str(Path.home() / "Library/Fonts/Lato-*.ttf")):
    for f in _glob.glob(pat):
        font_manager.fontManager.addfont(f)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_lecture5 as l5  # noqa: E402  the Cheerios schedule, one source

ROOT = Path(__file__).resolve().parents[2]
IMG = ROOT / "slides" / "img"
PDF_DIR = ROOT / "worksheets" / "figures"
# Add a figure's stem here when a worksheet starts using it.
WORKSHEET_FIGS = set()
SCRATCH = Path(os.environ["FIG_PREVIEW_DIR"]) if os.environ.get("FIG_PREVIEW_DIR") else None

INK = "#1a1a1a"
GRID = "#d9d9d9"
TOTAL = "#0072B2"
AVERAGE = "#BF5700"
MARGINAL = "#595a5b"

FULL = (11.2, 6.0)
SIDE = (8.2, 5.9)
FONT = 22
PROFIT = "#009E73"

plt.rcParams.update(
    {
        "font.family": ["Lato", "Fira Sans", "sans-serif"],
        "font.size": FONT,
        "svg.fonttype": "path",
        "pdf.fonttype": 42,
        "axes.edgecolor": INK,
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "xtick.labelsize": FONT,
        "ytick.labelsize": FONT,
    }
)

# ------------------------------------------------------- the example ------
FIXED = 60_000
PER_CAR = 10_000
# Marked outputs, labelled by value only: one on the total cost figure,
# two on the average cost figures.
TOTAL_POINTS = (10,)
POINTS = (20, 50)
# The worksheet's table uses the same cost function at three outputs.
WS_FIXED = FIXED
WS_PER_CAR = PER_CAR
TABLE_Q = (10, 20, 50)
Q_MAX = 60


def total_cost(q):
    return FIXED + PER_CAR * q


def average_cost(q):
    return total_cost(q) / q


def save(fig, out: Path) -> None:
    IMG.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format="svg")
    if out.stem in WORKSHEET_FIGS:
        PDF_DIR.mkdir(parents=True, exist_ok=True)
        fig.savefig(PDF_DIR / f"{out.stem}.pdf", format="pdf")
    if SCRATCH:
        fig.savefig(SCRATCH / f"{out.stem}.png", format="png", dpi=110)
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


# ----------------------------------------------------------- drawing ------

def style_axes(ax, ymax, ystep) -> None:
    ax.grid(color=GRID, lw=1, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=5, width=1)
    ax.set_xlim(0, Q_MAX)
    ax.set_ylim(0, ymax)
    ax.set_xticks(range(0, Q_MAX + 1, 10))
    ax.set_yticks(range(0, ymax + 1, ystep))
    ax.yaxis.set_major_formatter(FuncFormatter(
        lambda y, _: f"${y / 1e6:g}M" if y >= 1e6 else f"${y / 1000:g}k"))
    ax.set_xlabel("Cars per day, Q", fontsize=FONT, labelpad=8)


def draw_total(out: Path) -> None:
    """The cost function: a straight line from the fixed cost intercept."""
    fig, ax = plt.subplots(figsize=(11.2, 5.6), dpi=100)
    fig.subplots_adjust(left=0.12, right=0.975, top=0.95, bottom=0.15)
    style_axes(ax, 800_000, 200_000)
    # Runs a little past the last tick so the line does not end on it.
    x_max = 55
    ax.set_xlim(0, x_max)
    ax.set_xticks(range(0, 51, 10))

    q = np.array([0, x_max])
    ax.plot(q, total_cost(q), color=TOTAL, lw=2.6, solid_capstyle="round", zorder=5)
    ax.annotate("C(Q)", xy=(x_max, total_cost(x_max)), xytext=(-6, 12),
                textcoords="offset points", ha="right", va="bottom",
                fontsize=FONT, color=TOTAL, fontweight="bold", zorder=8)

    ax.plot(0, FIXED, marker="o", ms=13, color=INK, zorder=7)
    ax.annotate(f"F = ${FIXED:,}", xy=(0, FIXED), xytext=(14, -4),
                textcoords="offset points", ha="left", va="top",
                fontsize=FONT, color=INK, zorder=8)
    # One worked point is enough here; the AC figures mark two.
    for qq in TOTAL_POINTS:
        ax.plot(qq, total_cost(qq), marker="o", ms=13, color=INK, zorder=7)
        ax.annotate(f"${total_cost(qq):,}", xy=(qq, total_cost(qq)),
                    xytext=(14, -6), textcoords="offset points",
                    ha="left", va="top", fontsize=FONT, color=INK, zorder=8)

    ax.set_ylabel("Total cost per day", fontsize=FONT, labelpad=8)
    save(fig, out)


def draw_average(out: Path, with_mc: bool) -> None:
    """Average cost through A, B, D; optionally the flat marginal cost too."""
    fig, ax = plt.subplots(figsize=SIDE, dpi=100)
    fig.subplots_adjust(left=0.15, right=0.965, top=0.96, bottom=0.15)
    style_axes(ax, 30_000, 10_000)

    q = np.linspace(3, Q_MAX, 300)
    ax.plot(q, average_cost(q), color=AVERAGE, lw=2.6, solid_capstyle="round", zorder=5)
    ax.annotate("AC", xy=(6, average_cost(6)), xytext=(12, 0),
                textcoords="offset points", ha="left", va="center",
                fontsize=FONT, color=AVERAGE, fontweight="bold", zorder=8)

    for qq in POINTS:
        ax.plot(qq, average_cost(qq), marker="o", ms=13, color=INK, zorder=7)
        ax.annotate(f"${average_cost(qq):,.0f}", xy=(qq, average_cost(qq)),
                    xytext=(0, 12), textcoords="offset points",
                    ha="center", va="bottom", fontsize=FONT, color=INK, zorder=8)

    if with_mc:
        ax.axhline(PER_CAR, color=MARGINAL, lw=2.2, ls=(0, (5, 3)), zorder=4)
        ax.annotate(f"MC = ${PER_CAR:,}", xy=(1, PER_CAR), xytext=(0, -8),
                    textcoords="offset points", ha="left", va="top",
                    fontsize=FONT, color=MARGINAL, fontweight="bold", zorder=8)

    ax.set_ylabel("Cost per car", fontsize=FONT, labelpad=8)
    save(fig, out)


def draw_cheerios_schedule(out: Path) -> None:
    """The lecture 5 demand curve on its own, no points, at column size."""
    fig, ax = plt.subplots(figsize=SIDE, dpi=100)
    fig.subplots_adjust(left=0.125, right=0.965, top=0.96, bottom=0.15)
    ax.grid(color=GRID, lw=1, zorder=0)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(length=5, width=1)
    ax.set_xlim(0, 50_000)
    ax.set_ylim(0, 6.5)
    ax.set_xticks(range(0, 50_001, 10_000))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x / 1000:g}k"))
    ax.set_yticks(range(0, 7))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"${y:g}"))

    pr = np.linspace(1.0, l5.INTERCEPT / l5.SLOPE, 2)
    ax.plot(l5.demand(pr), pr, color=TOTAL, lw=2.6, solid_capstyle="round", zorder=5)
    ax.annotate("Demand", xy=(l5.demand(1.4), 1.4), xytext=(12, 4),
                textcoords="offset points", ha="left", va="bottom",
                fontsize=FONT, color=TOTAL, fontweight="bold", zorder=8)
    ax.set_xlabel("Pounds of cereal per week", fontsize=FONT, labelpad=8)
    ax.set_ylabel("Price per pound", fontsize=FONT, labelpad=8)
    save(fig, out)


def draw_cheerios_curves(out: Path) -> None:
    """The worksheet's four curves, one point per price in the schedule.

    Each panel is a column of the completed table plotted against Q, the
    same layout as the worksheet's empty grid, so the debrief shows what
    the students drew: demand, then revenue, cost, and profit. The $4.00
    point is picked out in every panel so the eye can follow one price
    across all four, and the profit peak carries its value.
    """
    fig, axes = plt.subplots(2, 2, figsize=(12.4, 6.6), dpi=100)
    fig.subplots_adjust(left=0.085, right=0.985, top=0.93, bottom=0.12,
                        hspace=0.62, wspace=0.24)
    prices = np.array(l5.PRICES)
    q = l5.demand(prices) / 1000
    rev = prices * l5.demand(prices) / 1000
    cost = l5.UNIT_COST * l5.demand(prices) / 1000
    prof = l5.profit(prices) / 1000
    best = l5.best_price()
    ib = list(l5.PRICES).index(best)
    tick = FONT - 4

    panels = [
        ("Demand curve", prices, "Price, $ per pound", 7, 2, TOTAL),
        ("Revenue, R = P × Q", rev, "$ thousands", 80, 20, TOTAL),
        ("Cost, C(Q) = 2Q", cost, "$ thousands", 60, 20, MARGINAL),
        ("Profit = R − C(Q)", prof, "$ thousands", 50, 10, PROFIT),
    ]
    for k, (ax, (title, y, ylab, ymax, ystep, colour)) in enumerate(zip(axes.flat, panels)):
        ax.set_xlim(0, 30)
        ax.set_ylim(0, ymax)
        ax.set_xticks(range(0, 31, 10))
        ax.set_yticks(range(0, ymax + 1, ystep))
        ax.grid(color=GRID, lw=1, zorder=0)
        ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.tick_params(length=4, width=1, labelsize=tick)
        ax.plot(q, y, color=colour, lw=3, marker="o", ms=11, zorder=5)
        ax.plot(q[ib], y[ib], marker="o", ms=17, mfc="white", mec=AVERAGE,
                mew=3, zorder=6)
        ax.set_title(title, fontsize=FONT, color=INK, pad=8)
        ax.set_ylabel(ylab, fontsize=tick, labelpad=6)
        if k >= 2:
            ax.set_xlabel("Q, thousand pounds per week", fontsize=tick, labelpad=4)

    # price labels on the demand points, profit label on the best one
    for pp, qq in zip(prices, q):
        axes[0, 0].annotate(f"${pp:.2f}", xy=(qq, pp), xytext=(0, 13),
                            textcoords="offset points", ha="center", va="bottom",
                            fontsize=tick, color=INK, zorder=8)
    # Two dollar signs in one string would switch matplotlib into mathtext.
    axes[1, 1].annotate(f"\\${best:.2f}: \\${prof[ib]:,.0f}k", xy=(q[ib], prof[ib]),
                        xytext=(0, 12), textcoords="offset points", ha="center",
                        va="bottom", fontsize=tick, color=INK, fontweight="bold",
                        zorder=8)
    save(fig, out)


# -------------------------------------------------------------- main ------

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.parse_args()

    draw_cheerios_schedule(IMG / "cheerios-schedule.svg")
    draw_cheerios_curves(IMG / "cheerios-curves.svg")
    draw_total(IMG / "cars-total-cost.svg")
    draw_average(IMG / "cars-average-cost.svg", with_mc=False)
    draw_average(IMG / "cars-ac-mc.svg", with_mc=True)

    # Numbers quoted on the slides and in the worksheet, printed so they can
    # be checked against what is written in both.
    print("\nvalues used in slide and worksheet text")
    print(f"  C(Q) = {FIXED:,} + {PER_CAR:,} Q")
    print("  marked points:")
    for qq in POINTS:
        print(f"    Q = {qq:2d}   C = ${total_cost(qq):9,}"
              f"   AC = ${average_cost(qq):9,.0f}")
    print(f"  worksheet table, C(Q) = {WS_FIXED:,} + {WS_PER_CAR:,} Q:")
    for qq in TABLE_Q:
        c = WS_FIXED + WS_PER_CAR * qq
        ac = f"${c / qq:9,.0f}" if qq else " undefined"
        print(f"    Q = {qq:2d}   C = ${c:9,}   AC = {ac}   MC = ${WS_PER_CAR:,}")
    print(f"  second factory, F = {2 * WS_FIXED:,}: AC at Q = 10 is"
          f" ${(2 * WS_FIXED + WS_PER_CAR * 10) / 10:,.0f}, MC unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
