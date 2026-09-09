"""
Figures and numbers for Lecture 5: the price-quantity trade-off along a
demand curve, and the Cheerios pricing example shared with the worksheet.

Run from the course root:

    python3 slides/figures/make_lecture5.py

No data downloads. The strawberry-stand figure is conceptual: a downward
demand curve with two points showing the trade-off (a higher price sells
fewer baskets), no scales. The Cheerios example uses one linear demand
curve everywhere, Q = 49,000 - 8,000 P, anchored at the single point
section 7.2 states, Hausman's estimate that at $3.00 per pound a typical
city buys 25,000 pounds a week; unit cost is the book's $2. The lecture
skips the isoprofit apparatus (marginal reasoning arrives with 7.6), so the
worksheet finds the best price by computing profit at each price in the
schedule, and the deck's debrief quotes the same numbers. Because this
linear curve is not the book's estimated one, its best price ($4.00) differs
a little from the book's $4.23; the deck says so rather than hiding it.

Output, in slides/img/:
  demand-tradeoff.svg   demand curve with points A and B and no scales, at
                        column size so the slide explains it alongside
  cheerios-demand.svg   the linear demand curve with the $3.00 anchor
                        marked, at column size
  cheerios-profit.svg   two panels, profit rectangles at $3.00 and at the
                        schedule's best price, at full-slide size (kept for
                        the debrief or later lectures; unused if unreferenced)

Accessibility: Okabe-Ito derived colours, every point and rectangle labelled
with its value on the figure itself, so nothing rests on judging positions,
areas, or colours by eye; text converted to paths so the SVG looks the same
on any machine. Alt text lives in the slide file beside each image.
"""

import argparse
import os
import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.patches import Rectangle
from matplotlib.ticker import FuncFormatter

matplotlib.use("Agg")

# matplotlib's font cache does not see fonts installed in ~/Library/Fonts,
# so register the Fira Sans files directly. Lato, the deck's body font, ships
# inside TeX Live (the PDF build uses it from there), so register those TTFs
# too; the figures then match the slide typography. Falls back to sans-serif.
for f in Path.home().glob("Library/Fonts/FiraSans-*.otf"):
    font_manager.fontManager.addfont(str(f))
import glob as _glob
for pat in ("/usr/local/texlive/*/texmf-dist/fonts/truetype/typoland/lato/*.ttf",
            str(Path.home() / "Library/Fonts/Lato-*.ttf")):
    for f in _glob.glob(pat):
        font_manager.fontManager.addfont(f)

ROOT = Path(__file__).resolve().parents[2]
IMG = ROOT / "slides" / "img"
# PDF copies of the figures the worksheets use, so slides and handouts share
# one source. Real text (Type 42) so the PDF stays searchable and taggable.
PDF_DIR = ROOT / "worksheets" / "figures"
# Add a figure's stem here when a worksheet starts using it.
WORKSHEET_FIGS = set()
SCRATCH = Path(os.environ["FIG_PREVIEW_DIR"]) if os.environ.get("FIG_PREVIEW_DIR") else None

INK = "#1a1a1a"
GRID = "#d9d9d9"
DEMAND = "#0072B2"
RECT_FILL = "#f0b27f"
RECT_EDGE = "#BF5700"
COST = "#595a5b"

FULL = (11.2, 6.0)
# Beside text in a column, as in make_lecture4.py.
SIDE = (8.2, 5.9)
FONT = 22

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
UNIT_COST = 2.00
# Hausman's stated point, the anchor for the linear schedule.
P_H, Q_H = 3.00, 25_000
# Q = INTERCEPT - SLOPE * P, so demand hits Q = 0 at P = $6.125.
INTERCEPT, SLOPE = 49_000, 8_000
# The worksheet's schedule: profit peaks inside this range, at $4.00.
PRICES = (3.00, 3.50, 4.00, 4.50, 5.00)

# The conceptual trade-off figure: P = 10 - Q / 50, drawn without scales;
# only the two marked points matter, so no product is named.
TRADEOFF = {"A": (100, 8.0), "B": (300, 4.0)}


def demand(p):
    return INTERCEPT - SLOPE * p


def profit(p):
    return (p - UNIT_COST) * demand(p)


def best_price():
    return max(PRICES, key=profit)


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

def style_axes(ax) -> None:
    ax.grid(color=GRID, lw=1, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=5, width=1)
    ax.set_xlim(0, 50_000)
    ax.set_ylim(0, 6.5)
    ax.set_xticks(range(0, 50_001, 10_000))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x / 1000:g}k"))
    ax.set_yticks(range(0, 7))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"${y:g}"))


def draw_curve(ax) -> None:
    p = np.linspace(1.0, INTERCEPT / SLOPE, 2)
    ax.plot(demand(p), p, color=DEMAND, lw=2.6, solid_capstyle="round", zorder=5)


def draw_tradeoff(out: Path) -> None:
    """The price-quantity trade-off, with no scales at all.

    Two labelled points on one downward line carry the whole idea: A sells
    few units at a high price, B sells many at a low one. Scales would
    invite reading numbers off a curve that is not estimated from anything.
    """
    fig, ax = plt.subplots(figsize=SIDE, dpi=100)
    fig.subplots_adjust(left=0.09, right=0.965, top=0.96, bottom=0.13)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(0, 500)
    ax.set_ylim(0, 10.5)

    q = np.array([25, 425])
    ax.plot(q, 10 - q / 50, color=DEMAND, lw=2.6, solid_capstyle="round", zorder=5)
    ax.annotate("Demand", xy=(390, 10 - 390 / 50), xytext=(4, 12),
                textcoords="offset points", ha="left", va="bottom",
                fontsize=FONT, color=DEMAND, fontweight="bold", zorder=8)

    labels = {
        "A": ("A: high price,\nfew units sold", (16, 10), "left", "bottom"),
        "B": ("B: low price,\nmany units sold", (16, 8), "left", "bottom"),
    }
    for name, (qq, pp) in TRADEOFF.items():
        text, off, ha, va = labels[name]
        ax.plot(qq, pp, marker="o", ms=13, color=INK, zorder=7)
        ax.annotate(text, xy=(qq, pp), xytext=off, textcoords="offset points",
                    ha=ha, va=va, fontsize=FONT, color=INK, zorder=8)

    ax.set_xlabel("Quantity sold", fontsize=FONT, labelpad=8)
    ax.set_ylabel("Price", fontsize=FONT, labelpad=8)
    save(fig, out)


def draw_demand(out: Path) -> None:
    """The Cheerios demand curve with the one point the text quotes.

    Dashed guides tie the $3.00 anchor to both axes so reading the point off
    the curve is the slide's whole exercise: price on the vertical axis,
    pounds per week on the horizontal.
    """
    fig, ax = plt.subplots(figsize=SIDE, dpi=100)
    fig.subplots_adjust(left=0.125, right=0.965, top=0.96, bottom=0.15)
    style_axes(ax)
    draw_curve(ax)

    ax.plot([Q_H, Q_H], [0, P_H], color=COST, lw=1.6, ls=(0, (4, 3)), zorder=4)
    ax.plot([0, Q_H], [P_H, P_H], color=COST, lw=1.6, ls=(0, (4, 3)), zorder=4)
    ax.plot(Q_H, P_H, marker="o", ms=13, color=DEMAND, zorder=7)
    ax.annotate("$3.00, 25,000 lb", xy=(Q_H, P_H), xytext=(14, 10),
                textcoords="offset points", ha="left", va="bottom",
                fontsize=FONT, color=DEMAND, fontweight="bold", zorder=8)
    ax.annotate("Demand", xy=(demand(5.5), 5.5), xytext=(16, 0),
                textcoords="offset points", ha="left", va="center",
                fontsize=FONT, color=DEMAND, fontweight="bold", zorder=8)

    ax.set_xlabel("Pounds of cereal per week", fontsize=FONT, labelpad=8)
    ax.set_ylabel("Price per pound", fontsize=FONT, labelpad=8)
    save(fig, out)


def draw_worksheet_grid(out: Path) -> None:
    """Four empty plotting panels for the worksheet, PDF only.

    Students fill the schedule's five (P, Q) rows into the table, then plot
    each column here: demand (P against Q), revenue, cost, and profit, all
    against Q so the habit matches the cost and marginal curves of 7.3-7.6.
    Gridlines are the whole point: they make plotting by hand feasible.
    """
    fig, axes = plt.subplots(2, 2, figsize=(7.4, 6.0), dpi=100)
    fig.subplots_adjust(left=0.09, right=0.98, top=0.94, bottom=0.09,
                        hspace=0.42, wspace=0.30)

    panels = [
        ("Demand curve", "Price, P ($ per pound)", 7, 1),
        ("Total revenue, R = P × Q", "R ($ thousands)", 80, 20),
        ("Total cost, C(Q) = 2Q", "C ($ thousands)", 60, 20),
        ("Profit = R − C(Q)", "Profit ($ thousands)", 40, 10),
    ]
    for ax, (title, ylab, ymax, ystep) in zip(axes.flat, panels):
        ax.set_xlim(0, 30)
        ax.set_ylim(0, ymax)
        ax.set_xticks(range(0, 31, 5))
        ax.set_yticks(range(0, ymax + 1, ystep))
        ax.grid(color=GRID, lw=0.8, zorder=0)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.tick_params(length=3, width=0.8, labelsize=10)
        ax.set_title(title, fontsize=11, color=INK, pad=6)
        ax.set_ylabel(ylab, fontsize=10, labelpad=4)
        ax.set_xlabel("Quantity, Q (thousands of pounds per week)",
                      fontsize=10, labelpad=4)

    PDF_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(PDF_DIR / f"{out.stem}.pdf", format="pdf")
    if SCRATCH:
        fig.savefig(SCRATCH / f"{out.stem}.png", format="png", dpi=110)
    plt.close(fig)
    print(f"wrote {(PDF_DIR / (out.stem + '.pdf')).relative_to(ROOT)}")


def draw_profit(out: Path) -> None:
    """Profit at two candidate prices, as rectangles under the curve.

    One panel per price so the two areas are never overlaid: height is the
    margin above the $2 unit cost, width is the pounds sold at that price,
    and the dollar value sits inside each rectangle, so the comparison does
    not depend on judging areas by eye.
    """
    fig, axes = plt.subplots(1, 2, figsize=FULL, dpi=100, sharey=True)
    fig.subplots_adjust(left=0.085, right=0.985, top=0.87, bottom=0.16, wspace=0.12)

    best = best_price()
    for ax, p in zip(axes, (P_H, best)):
        q = demand(p)
        style_axes(ax)
        draw_curve(ax)
        ax.add_patch(Rectangle((0, UNIT_COST), q, p - UNIT_COST,
                               facecolor=RECT_FILL, edgecolor=RECT_EDGE,
                               lw=2.2, zorder=3))
        ax.axhline(UNIT_COST, color=COST, lw=1.6, ls=(0, (4, 3)), zorder=4)
        ax.annotate("Unit cost $2.00", xy=(49_500, UNIT_COST), xytext=(0, -6),
                    textcoords="offset points", ha="right", va="top",
                    fontsize=FONT - 4, color=COST, zorder=8)
        ax.plot(q, p, marker="o", ms=13, color=DEMAND, zorder=7)
        ax.annotate(f"${p:.2f}, {q:,.0f} lb", xy=(q, p), xytext=(12, 10),
                    textcoords="offset points", ha="left", va="bottom",
                    fontsize=FONT - 4, color=DEMAND, fontweight="bold", zorder=8)
        ax.annotate(f"${profit(p):,.0f}\nper week",
                    xy=(q / 2, UNIT_COST + (p - UNIT_COST) / 2), ha="center",
                    va="center", fontsize=FONT - 2, color=INK,
                    fontweight="bold", zorder=8)
        ax.set_title(f"Charge ${p:.2f}", fontsize=FONT, color=INK, pad=10)
        ax.set_xlabel("Pounds per week", fontsize=FONT - 2, labelpad=6)

    axes[0].set_ylabel("Price per pound", fontsize=FONT - 2, labelpad=8)
    save(fig, out)


# -------------------------------------------------------------- main ------

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.parse_args()

    draw_tradeoff(IMG / "demand-tradeoff.svg")
    draw_demand(IMG / "cheerios-demand.svg")
    draw_profit(IMG / "cheerios-profit.svg")
    draw_worksheet_grid(Path("cheerios-grid"))

    # Numbers quoted on the slides and in the worksheet, printed so they can
    # be checked against what is written in both.
    print("\nvalues used in slide and worksheet text")
    print("  worksheet schedule (unit cost $2):")
    for p_ in PRICES:
        q_ = demand(p_)
        print(f"    ${p_:.2f}: {q_:9,.0f} lb   revenue ${p_ * q_:10,.0f}"
              f"   cost ${UNIT_COST * q_:9,.0f}   profit ${profit(p_):9,.0f}")
    print(f"  best price in the schedule: ${best_price():.2f}"
          f" (profit ${profit(best_price()):,.0f}; the book's estimated"
          f" curve gives $4.23)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
