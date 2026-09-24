"""
Figures and numbers for Lecture 9: choosing the price and quantity that
maximize profit, using marginal revenue and marginal cost (CORE 7.6).

Run from the course root:

    python3 slides/figures/make_lecture9.py

No data downloads. The running example is Boba Break, a stall at the
Tuesday farmers market on campus. The numbers are picked so every step is mental arithmetic:

    demand           P = 12 - Q / 10, cups a market day (each $1 off sells 10 more)
    cost             C(Q) = 100 + 4 Q: a $100 stall fee and $4 a cup for tea, milk, and tapioca, MC = 4
    MR = MC          at Q* = 40, the middle column of the worksheet table
    P*               = 12 - 40 / 10 = 8
    profit at Q*     = 8 x 40 - (100 + 4 x 40) = 320 - 260 = 60

Marginal revenue is taught one cup at a time, as CORE does in Figure 7.17:
the change in revenue from selling one more cup. Each extra cup needs the
price $0.10 lower, so at Q = 20 the 21st cup adds 9.90 - 20 x 0.10 = 7.90.
The one-cup values sit on the plotted line MR = 12 - Q / 5 at the half-cup
midpoints (7.90 at Q = 20.5), and MR = MC = 4 exactly at Q* = 40: the 40th
cup adds 4.10 and the 41st adds 3.90.

Output, in slides/img/:
  boba-demand.svg      the demand curve from 0 to 120 cups, both ends
                       labelled, dotted guides at 20 cups and $10
  boba-profit.svg     profit against Q with the five table quantities
                       marked and the peak labelled, at column size
  boba-mr-mc.svg      demand, marginal revenue, and marginal cost, with E
                       and E-prime labelled, at column size

  core-q7-11.svg       CORE Question 7.11 (Figure 7.17) redrawn with the
                       course's Beautiful Cars numbers, for the practice page

Accessibility: Okabe-Ito derived colours, every marked point and every curve
labelled with its value on the figure itself, so nothing rests on reading
positions, areas, or colours by eye; text converted to paths so the SVG
looks the same on any machine. Alt text lives in the slide file beside each
image.
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

# Same font setup as make_lecture6.py: Fira Sans from ~/Library/Fonts, Lato
# from the TeX tree, so the figures match the slide typography.
for f in Path.home().glob("Library/Fonts/FiraSans-*.otf"):
    font_manager.fontManager.addfont(str(f))
for pat in ("/usr/local/texlive/*/texmf-dist/fonts/truetype/typoland/lato/*.ttf",
            str(Path.home() / "Library/Fonts/Lato-*.ttf")):
    for f in _glob.glob(pat):
        font_manager.fontManager.addfont(f)

ROOT = Path(__file__).resolve().parents[2]
IMG = ROOT / "slides" / "img"
SCRATCH = Path(os.environ["FIG_PREVIEW_DIR"]) if os.environ.get("FIG_PREVIEW_DIR") else None

INK = "#1a1a1a"
GRID = "#d9d9d9"
DEMAND = "#0072B2"
ACCENT = "#BF5700"
MARGINAL = "#595a5b"
PROFIT = "#009E73"
GUIDE = "#595a5b"

FULL = (11.2, 6.0)
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
FIXED = 100                      # stall fee for one market day
PER_CUP = 4                      # cost of one more cup
INTERCEPT = 12                   # demand: P = INTERCEPT - Q / CUPS_PER_DOLLAR
CUPS_PER_DOLLAR = 10
TABLE_Q = (20, 30, 40, 50, 60)   # the worksheet and slide table
Q_STAR = 40
Q_MAX = 80


def price(q):
    return INTERCEPT - q / CUPS_PER_DOLLAR


def quantity(p):
    return (INTERCEPT - p) * CUPS_PER_DOLLAR


def revenue(q):
    return price(q) * q


def total_cost(q):
    return FIXED + PER_CUP * q


def average_cost(q):
    return total_cost(q) / q


def profit(q):
    return revenue(q) - total_cost(q)


def marginal_revenue(q):
    """Height of the MR curve. Equals the step average at the step midpoint."""
    return INTERCEPT - 2 * q / CUPS_PER_DOLLAR


def money(x):
    """$8, $6.50, -$4: whole dollars bare, cents only when needed."""
    sign = "−" if x < 0 else ""
    x = abs(x)
    return f"{sign}${x:,.0f}" if float(x).is_integer() else f"{sign}${x:,.2f}"


def save(fig, out: Path) -> None:
    IMG.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format="svg")
    if SCRATCH:
        fig.savefig(SCRATCH / f"{out.stem}.png", format="png", dpi=110)
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


# ----------------------------------------------------------- drawing ------

def axes(size, xmax=Q_MAX, ymin=0, ymax=12, ystep=2, xstep=10,
         ylabel="Price per cup"):
    fig, ax = plt.subplots(figsize=size, dpi=100)
    ax.grid(color=GRID, lw=1, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=5, width=1)
    ax.set_xlim(0, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_xticks(range(0, xmax + 1, xstep))
    ax.set_yticks(range(ymin, ymax + 1, ystep))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: money(y)))
    ax.set_xlabel("Cups sold, Q", fontsize=FONT, labelpad=8)
    ax.set_ylabel(ylabel, fontsize=FONT, labelpad=8)
    return fig, ax


def draw_demand_points(out: Path) -> None:
    """The demand curve from 0 to 120 cups, both ends labelled, guides at 20 cups.

    One series on the plot, so it takes the accent colour rather than the
    demand blue used where demand sits beside other curves.
    """
    fig, ax = axes(SIDE, xmax=120, xstep=20)
    fig.subplots_adjust(left=0.165, right=0.955, top=0.9, bottom=0.15)
    q = np.array([0, 120])
    ax.plot(q, price(q), color=ACCENT, lw=3, solid_capstyle="round", zorder=5)
    for qq in (0, 20, 120):
        ax.plot(qq, price(qq), marker="o", ms=14, color=ACCENT, zorder=7, clip_on=False)
    ax.annotate("Nobody buys at $12", xy=(0, 12), xytext=(12, 4),
                textcoords="offset points", ha="left", va="bottom",
                fontsize=FONT - 2, color=INK, zorder=8, annotation_clip=False)
    ax.plot([20, 20], [0, 10], color=GUIDE, lw=1.6, ls=(0, (4, 3)), zorder=4)
    ax.plot([0, 20], [10, 10], color=GUIDE, lw=1.6, ls=(0, (4, 3)), zorder=4)
    ax.annotate("All 120 buy at $0", xy=(120, 0), xytext=(104, 4.6),
                textcoords="data", ha="center", va="bottom",
                fontsize=FONT - 2, color=INK, zorder=8,
                arrowprops=dict(arrowstyle="-", color=GUIDE, lw=1.4,
                                shrinkA=2, shrinkB=9))
    save(fig, out)


def draw_profit(out: Path) -> None:
    """Profit against Q, the five table quantities marked, peak labelled."""
    fig, ax = axes(SIDE, ymin=-40, ymax=80, ystep=20, ylabel="Profit")
    fig.subplots_adjust(left=0.2, right=0.965, top=0.96, bottom=0.15)
    ax.axhline(0, color=INK, lw=1.4, zorder=3)
    q = np.linspace(10, 70, 400)
    ax.plot(q, profit(q), color=PROFIT, lw=3, solid_capstyle="round", zorder=5)
    for qq in TABLE_Q:
        ax.plot(qq, profit(qq), marker="o", ms=12, color=INK, zorder=7)
    ax.plot(Q_STAR, profit(Q_STAR), marker="o", ms=18, mfc="white", mec=ACCENT,
            mew=3.5, zorder=8)
    ax.annotate(f"{money(profit(Q_STAR))} at {Q_STAR} cups",
                xy=(Q_STAR, profit(Q_STAR)), xytext=(0, 18),
                textcoords="offset points", ha="center", va="bottom",
                fontsize=FONT, color=INK, fontweight="bold", zorder=9)
    save(fig, out)


def draw_mr_mc(out: Path) -> None:
    """Demand, marginal revenue, and marginal cost, with E and E-prime."""
    fig, ax = axes(SIDE, ymin=-4, ymax=12, xstep=20)
    fig.subplots_adjust(left=0.185, right=0.965, top=0.96, bottom=0.15)
    ax.axhline(0, color=INK, lw=1.4, zorder=3)

    q = np.array([0, Q_MAX])
    ax.plot(q, price(q), color=DEMAND, lw=3, solid_capstyle="round", zorder=5)
    ax.annotate("Demand", xy=(62, price(62)), xytext=(0, 12),
                textcoords="offset points", ha="center", va="bottom",
                fontsize=FONT, color=DEMAND, fontweight="bold", zorder=8)

    ax.plot(q, marginal_revenue(q), color=ACCENT, lw=3,
            solid_capstyle="round", zorder=5)
    ax.annotate("MR", xy=(66, marginal_revenue(66)), xytext=(12, 4),
                textcoords="offset points", ha="left", va="bottom",
                fontsize=FONT, color=ACCENT, fontweight="bold", zorder=8)

    ax.axhline(PER_CUP, color=MARGINAL, lw=2.4, ls=(0, (5, 3)), zorder=4)
    ax.annotate(f"MC = {money(PER_CUP)}", xy=(1, PER_CUP), xytext=(0, 10),
                textcoords="offset points", ha="left", va="bottom",
                fontsize=FONT, color=MARGINAL, fontweight="bold", zorder=8)

    ax.plot([Q_STAR, Q_STAR], [PER_CUP, price(Q_STAR)], color=GUIDE, lw=1.6,
            ls=(0, (4, 3)), zorder=4)
    ax.plot(Q_STAR, price(Q_STAR), marker="o", ms=14, color=INK, zorder=7)
    ax.annotate(f"E: {money(price(Q_STAR))}",
                xy=(Q_STAR, price(Q_STAR)), xytext=(16, 8),
                textcoords="offset points", ha="left", va="bottom",
                fontsize=FONT, color=INK, fontweight="bold", zorder=8)
    ax.plot(Q_STAR, PER_CUP, marker="o", ms=14, color=INK, zorder=7)
    ax.annotate("E′: MR = MC", xy=(Q_STAR, PER_CUP),
                xytext=(-16, -12), textcoords="offset points", ha="right",
                va="top", fontsize=FONT, color=INK, fontweight="bold", zorder=8)
    save(fig, out)


def draw_core_q711(out: Path) -> None:
    """CORE Question 7.11 (Figure 7.17), redrawn with the course's Beautiful Cars.

    Lecture 6's costs, C(Q) = 60,000 + 10,000 Q, so MC = 10,000, with demand
    P = 50,000 - 1,000 Q, so MR = 50,000 - 2,000 Q. MR = MC at Q* = 20, where
    P* = 30,000. Ticks sit at every number the question and its solution use.
    """
    fig, ax = plt.subplots(figsize=SIDE, dpi=100)
    ax.grid(color=GRID, lw=1, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=5, width=1)
    fig.subplots_adjust(left=0.24, right=0.965, top=0.96, bottom=0.15)
    ax.set_xlim(0, 40)
    ax.set_ylim(-10_000, 50_000)
    ax.set_xticks([0, 10, 20, 25, 30, 40])
    ax.set_yticks([-10_000, 0, 10_000, 30_000, 50_000])
    ax.yaxis.set_major_formatter(FuncFormatter(
        lambda y, _: f"\u2212${abs(y):,.0f}" if y < 0 else f"${y:,.0f}"))
    ax.set_xlabel("Cars per day, Q", fontsize=FONT, labelpad=8)
    ax.set_ylabel("Price and cost", fontsize=FONT, labelpad=8)
    ax.axhline(0, color=INK, lw=1.4, zorder=3)
    q = np.array([0, 40])
    ax.plot(q, 50_000 - 1_000 * q, color=DEMAND, lw=3, zorder=5)
    ax.annotate("Demand", xy=(10, 50_000 - 1_000 * 10), xytext=(10, 8),
                textcoords="offset points", ha="left", va="bottom",
                fontsize=FONT, color=DEMAND, fontweight="bold", zorder=8)
    qm = np.array([0, 30])
    ax.plot(qm, 50_000 - 2_000 * qm, color=ACCENT, lw=3, zorder=5)
    ax.annotate("MR", xy=(28, 50_000 - 2_000 * 28), xytext=(10, 0),
                textcoords="offset points", ha="left", va="center",
                fontsize=FONT, color=ACCENT, fontweight="bold", zorder=8)
    ax.axhline(10_000, color=MARGINAL, lw=2.4, ls=(0, (5, 3)), zorder=4)
    ax.annotate("MC = $10,000", xy=(0.5, 10_000), xytext=(0, 8), textcoords="offset points",
                ha="left", va="bottom", fontsize=FONT, color=MARGINAL,
                fontweight="bold", zorder=8)
    ax.plot([20, 20], [10_000, 30_000], color=GUIDE, lw=1.6, ls=(0, (4, 3)), zorder=4)
    ax.plot(20, 30_000, marker="o", ms=13, color=INK, zorder=7)
    ax.annotate("E", xy=(20, 30_000), xytext=(10, 6), textcoords="offset points",
                ha="left", va="bottom", fontsize=FONT, color=INK, fontweight="bold", zorder=8)
    ax.plot(20, 10_000, marker="o", ms=13, color=INK, zorder=7)
    ax.annotate("E\u2032", xy=(20, 10_000), xytext=(-10, -8), textcoords="offset points",
                ha="right", va="top", fontsize=FONT, color=INK, fontweight="bold", zorder=8)
    save(fig, out)

# -------------------------------------------------------------- main ------

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.parse_args()

    draw_demand_points(IMG / "boba-demand.svg")
    draw_profit(IMG / "boba-profit.svg")
    draw_mr_mc(IMG / "boba-mr-mc.svg")
    draw_core_q711(IMG / "core-q7-11.svg")

    # Numbers quoted on the slides, the worksheet, and the practice page,
    # printed so they can be checked against what is written in each.
    print("\nvalues used in slide and worksheet text")
    print(f"  C(Q) = {FIXED} + {PER_CUP} Q      P = {INTERCEPT} - Q / {CUPS_PER_DOLLAR}")
    print("  Activity 1 table:")
    print("    Q    P      R      C     profit")
    for qq in TABLE_Q:
        print(f"    {qq:2d}   {money(price(qq)):>4}   {money(revenue(qq)):>4}"
              f"   {money(total_cost(qq)):>4}   {money(profit(qq)):>4}")
    print("  Activity 2, marginal revenue from one more cup:")
    for qq in TABLE_Q[:-1]:
        mr = revenue(qq + 1) - revenue(qq)
        print(f"    Q = {qq}: R = {money(revenue(qq))}, P(Q+1) = {money(price(qq + 1))},"
              f" R(Q+1) = {money(revenue(qq + 1))}, MR = {money(mr)}")
    print(f"  the 40th cup adds {money(revenue(40) - revenue(39))},"
          f" the 41st adds {money(revenue(41) - revenue(40))}, MC = {money(PER_CUP)}")
    print(f"  profit-maximizing point E: Q* = {Q_STAR}, P* = {money(price(Q_STAR))}")
    print(f"    profit at Q* = {money(revenue(Q_STAR))} - {money(total_cost(Q_STAR))}"
          f" = {money(profit(Q_STAR))}")

    # The practice page's own numbers, checked the same way.
    print("\npractice page, Sierra Bikes: C(Q) = 2,000 + 200 Q, P = 1,200 - 10 Q")
    sb_p = lambda q: 1_200 - 10 * q
    sb_r = lambda q: sb_p(q) * q
    for qq in (20, 30, 40, 50, 60):
        cc = 2_000 + 200 * qq
        print(f"    Q = {qq:2d}   P = ${sb_p(qq):5,d}   R = ${sb_r(qq):6,d}"
              f"   C = ${cc:6,d}   profit = ${sb_r(qq) - cc:6,d}")
    for qq in (20, 30, 40, 50):
        print(f"    Q = {qq}: one more bike, MR = ${sb_r(qq + 1) - sb_r(qq):,d}")
    print(f"    50th bike adds ${sb_r(50) - sb_r(49)}, 51st adds ${sb_r(51) - sb_r(50)}, MC = $200")
    print("practice page, Marisol's cakes: C(Q) = 30 + 20 Q, one cake per row")
    cakes = {1: 55, 2: 50, 3: 45, 4: 40, 5: 35, 6: 30}
    prev = 0
    for qq, pp in cakes.items():
        rr, cc = pp * qq, 30 + 20 * qq
        print(f"    Q = {qq}   P = ${pp}   R = ${rr}   MR of this cake = ${rr - prev}"
              f"   C = ${cc}   profit = ${rr - cc}")
        prev = rr
    return 0


if __name__ == "__main__":
    sys.exit(main())
