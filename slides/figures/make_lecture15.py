"""
Numbers and figures for Lecture 15: supply and demand with many buyers and
sellers (CORE 8.1 and 8.2), and for Worksheet 15 and Practice 15.

Run from the course root:

    python3 slides/figures/make_lecture15.py

No data downloads. The deck's running example is the taco stands at the
Saturday flea market (CORE 8.2's second-hand textbook market, Figures 8.1
to 8.3, moved to the setting Lecture 14 opened with), with the course's
own numbers:

    buyers    up to 100 tacos wanted; lined up highest first, the Qth
              buyer's willingness to pay is WTP = 10 - Q/10, so at a price
              P the number bought is Q = 100 - 10P
    sellers   up to 100 tacos on offer; lined up lowest first, the Qth
              taco's seller will accept WTA = 1 + Q/20, so at a price P
              the number offered is Q = 20(P - 1)
    clearing  10 - Q/10 = 1 + Q/20 gives Q* = 60 and P* = $4
    too high  at $6: 40 wanted, 100 offered, excess supply of 60
    too low   at $2: 80 wanted, 20 offered, excess demand of 60

Worksheet 15 and Practice 15 use a different market, student resale of
tickets to the homecoming game:

    demand    WTP = 50 - Q, so Q = 50 - P
    supply    WTA = 10 + Q, so Q = P - 10
    clearing  Q* = 20 tickets at P* = $30
    at $40    10 buyers, 30 sellers, excess supply of 20
    at $20    30 buyers, 10 sellers, excess demand of 20

Practice 15 problem 2 is a six-buyer, six-seller market (values 12, 10, 9,
7, 5, 3; costs 2, 4, 5, 6, 9, 11) that clears at $6 to $7 with 4 trades.

main() prints every number quoted in the deck, worksheet, and practice
page and checks them.

Output, in slides/img/:
  taco-demand.svg        the demand curve, with the 20th buyer marked
  taco-supply.svg        the supply curve, with the 20th seller marked
  taco-clearing.svg      both curves, P* = $4 and Q* = 60
  taco-adjust.svg        both curves with $6 and $2 marked, and the
                         excess supply and excess demand bracketed
  tickets-solution.svg   the worksheet market solved, for Practice 15
and in worksheets/figures/:
  tickets.pdf            the worksheet grid with both curves, unmarked

Gridlines sit at every number the slides or questions refer to. Demand in
Okabe-Ito blue, supply in dark orange, each labelled on the figure; text
converted to paths. Alt text lives beside each image in the deck.
"""

import glob as _glob
import os
import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter

matplotlib.use("Agg")

for f in Path.home().glob("Library/Fonts/FiraSans-*.otf"):
    font_manager.fontManager.addfont(str(f))
for pat in ("/usr/local/texlive/*/texmf-dist/fonts/truetype/typoland/lato/*.ttf",
            str(Path.home() / "Library/Fonts/Lato-*.ttf")):
    for f in _glob.glob(pat):
        font_manager.fontManager.addfont(f)

ROOT = Path(__file__).resolve().parents[2]
IMG = ROOT / "slides" / "img"
WS = ROOT / "worksheets" / "figures"
SCRATCH = Path(os.environ["FIG_PREVIEW_DIR"]) if os.environ.get("FIG_PREVIEW_DIR") else None

INK = "#1a1a1a"
GRID = "#d9d9d9"
DEMAND = "#0072B2"               # Okabe-Ito blue, 5.1:1 on white
SUPPLY = "#8f4100"               # dark orange, 7.7:1 on white
GUIDE = "#595a5b"
RULE = "#595a5b"

SIDE = (8.8, 6.0)
FONT = 26

plt.rcParams.update(
    {
        "font.family": ["Lato", "Fira Sans", "sans-serif"],
        "font.size": FONT,
        "svg.fonttype": "path",
        "pdf.fonttype": 42,
        "axes.edgecolor": RULE,
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
    }
)

# ------------------------------------------------------- the taco market
N = 100                # tacos wanted at a price of zero, and on offer at $6


def wtp(q):
    """Willingness to pay of the qth buyer, highest first."""
    return 10 - q / 10


def wta(q):
    """Willingness to accept of the qth taco's seller, lowest first."""
    return 1 + q / 20


def demand(p):
    """Buyers whose WTP is at least p."""
    return sum(wtp(q) >= p for q in range(1, N + 1))


def supply(p):
    """Sellers whose WTA is at most p."""
    return sum(wta(q) <= p for q in range(1, N + 1))


P_STAR, Q_STAR = 4, 60
P_HIGH, P_LOW = 6, 2
BUYER_MARK, SELLER_MARK = 20, 20

# ------------------------------------------------------- the ticket market
T_N = 50


def t_wtp(q):
    return 50 - q


def t_wta(q):
    return 10 + q


def t_demand(p):
    return sum(t_wtp(q) >= p for q in range(1, T_N + 1))


def t_supply(p):
    return sum(t_wta(q) <= p for q in range(1, T_N + 1))


T_P_STAR, T_Q_STAR = 30, 20
T_P_HIGH, T_P_LOW = 40, 20

# ------------------------------------------------------- practice problem 2
SMALL_VALUES = [12, 10, 9, 7, 5, 3]
SMALL_COSTS = [2, 4, 5, 6, 9, 11]


def small_clearing():
    prices = [p for p in range(1, 13)
              if sum(v >= p for v in SMALL_VALUES) == sum(c <= p for c in SMALL_COSTS)]
    return prices, sum(v >= prices[0] for v in SMALL_VALUES)


# ------------------------------------------------------- drawing ----------
def money(x):
    return f"${x:,.0f}"


def save(fig, out: Path, fmt="svg") -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format=fmt)
    if SCRATCH:
        fig.savefig(SCRATCH / f"{out.stem}.png", format="png", dpi=110)
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


def axes(xmax, ymax, xstep, ystep, xlabel, size=SIDE, fs=FONT):
    fig, ax = plt.subplots(figsize=size, dpi=100)
    # Axes run a little past the last tick so the lines do not touch the frame.
    ax.set_xlim(0, xmax * 1.05)
    ax.set_ylim(0, ymax * 1.05)
    ax.set_xticks(range(0, xmax + 1, xstep))
    ax.set_yticks(range(0, ymax + 1, ystep))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: money(y)))
    ax.grid(color=GRID, lw=1, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0, labelsize=fs - 4)
    ax.set_xlabel(xlabel, fontsize=fs - 2, labelpad=8)
    ax.set_ylabel("Price", fontsize=fs - 2, labelpad=8)
    fig.subplots_adjust(left=0.17, right=0.97, top=0.96, bottom=0.16)
    return fig, ax


def line(ax, f, q0, q1, color, label, label_q, dx, dy, ha="left", va="bottom", lw=4, fs=FONT):
    ax.plot([q0, q1], [f(q0), f(q1)], color=color, lw=lw, solid_capstyle="round", zorder=5)
    ax.annotate(label, xy=(label_q, f(label_q)), xytext=(dx, dy),
                textcoords="offset points", ha=ha, va=va, fontsize=fs,
                color=color, fontweight="bold", zorder=8)


def guides(ax, q, p, color=GUIDE):
    ax.plot([0, q], [p, p], color=color, lw=1.8, ls=(0, (4, 3)), zorder=4)
    ax.plot([q, q], [0, p], color=color, lw=1.8, ls=(0, (4, 3)), zorder=4)


def point(ax, q, p, label, dx, dy, ha="left", va="bottom", fs=FONT):
    ax.plot(q, p, marker="o", ms=12, color=INK, zorder=9)
    if label:
        ax.annotate(label, xy=(q, p), xytext=(dx, dy), textcoords="offset points",
                    ha=ha, va=va, fontsize=fs, color=INK, fontweight="bold", zorder=10)


TACO_AXES = (100, 10, 10, 1, "Tacos, Q")


def fig_demand(out: Path) -> None:
    fig, ax = axes(*TACO_AXES)
    line(ax, wtp, 0, 100, DEMAND, "Demand", 72, 12, 8)
    guides(ax, BUYER_MARK, wtp(BUYER_MARK))
    point(ax, BUYER_MARK, wtp(BUYER_MARK), f"20th buyer, {money(wtp(BUYER_MARK))}", 12, 6)
    save(fig, out)


def fig_supply(out: Path) -> None:
    fig, ax = axes(*TACO_AXES)
    line(ax, wta, 0, 100, SUPPLY, "Supply", 80, -10, 12, ha="right")
    guides(ax, SELLER_MARK, wta(SELLER_MARK))
    point(ax, SELLER_MARK, wta(SELLER_MARK), f"20th seller, {money(wta(SELLER_MARK))}", 14, -4, va="top")
    save(fig, out)


def both(ax, supply_below=False):
    """Both curves. Demand is labelled above its right end; Supply above
    its line, left of the crossing when a bracket sits at $6 (the adjust
    figure)."""
    line(ax, wtp, 0, 100, DEMAND, "Demand", 80, 10, 8)
    if supply_below:
        line(ax, wta, 0, 100, SUPPLY, "Supply", 50, -8, 10, ha="right")
    else:
        line(ax, wta, 0, 100, SUPPLY, "Supply", 82, -8, 10, ha="right")


def fig_clearing(out: Path) -> None:
    fig, ax = axes(*TACO_AXES)
    both(ax)
    guides(ax, Q_STAR, P_STAR, INK)
    point(ax, Q_STAR, P_STAR, "", 0, 0)
    ax.annotate(f"P* = {money(P_STAR)}", xy=(0, P_STAR), xytext=(8, 8),
                textcoords="offset points", ha="left", va="bottom",
                fontsize=FONT, color=INK, fontweight="bold")
    ax.annotate(f"Q* = {Q_STAR}", xy=(Q_STAR, 0), xytext=(-8, 6),
                textcoords="offset points", ha="right", va="bottom",
                fontsize=FONT, color=INK, fontweight="bold")
    save(fig, out)


def bracket(ax, q0, q1, p, text, color, above=True):
    """A horizontal bracket from q0 to q1 at price p with a label."""
    tick = ax.get_ylim()[1] / 40 * (1 if above else -1)
    ax.plot([q0, q1], [p, p], color=color, lw=2.2, zorder=6)
    ax.plot([q0, q0], [p, p + tick], color=color, lw=2.2, zorder=6)
    ax.plot([q1, q1], [p, p + tick], color=color, lw=2.2, zorder=6)
    ax.annotate(text, xy=((q0 + q1) / 2, p), xytext=(0, 10 if above else -10),
                textcoords="offset points", ha="center",
                va="bottom" if above else "top", fontsize=FONT - 4,
                color=color, fontweight="bold", zorder=8)


def fig_adjust(out: Path) -> None:
    fig, ax = axes(*TACO_AXES)
    both(ax, supply_below=True)
    qd, qs = demand(P_HIGH), supply(P_HIGH)
    ax.plot([0, qs], [P_HIGH, P_HIGH], color=GUIDE, lw=1.8, ls=(0, (4, 3)), zorder=4)
    point(ax, qd, P_HIGH, "", 0, 0)
    point(ax, qs, P_HIGH, "", 0, 0)
    bracket(ax, qd, qs, P_HIGH, f"Excess supply, {qs - qd}", SUPPLY, above=True)
    qd, qs = demand(P_LOW), supply(P_LOW)
    ax.plot([0, qd], [P_LOW, P_LOW], color=GUIDE, lw=1.8, ls=(0, (4, 3)), zorder=4)
    point(ax, qd, P_LOW, "", 0, 0)
    point(ax, qs, P_LOW, "", 0, 0)
    bracket(ax, qs, qd, P_LOW, f"Excess demand, {qd - qs}", DEMAND, above=False)
    point(ax, Q_STAR, P_STAR, "", 0, 0)
    save(fig, out)


def tickets_axes(size, fs):
    fig, ax = axes(50, 50, 5, 5, "Tickets, Q", size=size, fs=fs)
    ax.tick_params(labelsize=fs - 4)
    return fig, ax


def fig_tickets(out: Path, solved: bool) -> None:
    fs = FONT - 6 if not solved else FONT
    fig, ax = tickets_axes((8.2, 5.0) if not solved else SIDE, fs)
    lw = 2.6 if not solved else 4
    line(ax, t_wtp, 0, 50, DEMAND, "Demand", 40, 10, 8, lw=lw, fs=fs)
    line(ax, t_wta, 0, 40, SUPPLY, "Supply", 36, -10, 10, ha="right", lw=lw, fs=fs)
    if solved:
        guides(ax, T_Q_STAR, T_P_STAR, INK)
        point(ax, T_Q_STAR, T_P_STAR, "", 0, 0)
        ax.annotate(f"P* = {money(T_P_STAR)}", xy=(0, T_P_STAR), xytext=(8, 8),
                    textcoords="offset points", ha="left", va="bottom",
                    fontsize=fs, color=INK, fontweight="bold")
        ax.annotate(f"Q* = {T_Q_STAR}", xy=(T_Q_STAR, 0), xytext=(-8, 6),
                    textcoords="offset points", ha="right", va="bottom",
                    fontsize=fs, color=INK, fontweight="bold")
        save(fig, out)
    else:
        fig.subplots_adjust(left=0.13, right=0.97, top=0.97, bottom=0.17)
        save(fig, out, fmt="pdf")


# ------------------------------------------------------- main -------------
def main() -> int:
    print("Taco market (deck)")
    for q in (10, BUYER_MARK, Q_STAR, 80, 100):
        print(f"  buyer {q:3d}: WTP = 10 - {q}/10 = {wtp(q):g}")
    for q in (10, SELLER_MARK, Q_STAR, 100):
        print(f"  seller {q:3d}: WTA = 1 + {q}/20 = {wta(q):g}")
    for p in (P_HIGH, P_STAR, P_LOW):
        print(f"  at ${p}: {demand(p)} wanted, {supply(p)} offered")
    assert demand(P_STAR) == supply(P_STAR) == Q_STAR
    assert wtp(Q_STAR) == wta(Q_STAR) == P_STAR
    assert (demand(P_HIGH), supply(P_HIGH)) == (40, 100)
    assert (demand(P_LOW), supply(P_LOW)) == (80, 20)
    assert wtp(BUYER_MARK) == 8 and wta(SELLER_MARK) == 2

    print("\nTicket market (worksheet and practice)")
    for p in (T_P_HIGH, T_P_STAR, T_P_LOW):
        print(f"  at ${p}: {t_demand(p)} buyers, {t_supply(p)} sellers")
    assert t_demand(T_P_STAR) == t_supply(T_P_STAR) == T_Q_STAR
    assert (t_demand(T_P_HIGH), t_supply(T_P_HIGH)) == (10, 30)
    assert (t_demand(T_P_LOW), t_supply(T_P_LOW)) == (30, 10)
    print(f"  10th buyer WTP = {t_wtp(10)}, 10th seller WTA = {t_wta(10)}")

    prices, q = small_clearing()
    print(f"\nSix-trader market: clears at ${prices[0]}" +
          (f" to ${prices[-1]}" if len(prices) > 1 else "") + f", Q = {q}")
    for p in (5, 6, 7):
        print(f"  at ${p}: {sum(v >= p for v in SMALL_VALUES)} buyers,"
              f" {sum(c <= p for c in SMALL_COSTS)} sellers")
    assert prices == [6, 7] and q == 4

    fig_demand(IMG / "taco-demand.svg")
    fig_supply(IMG / "taco-supply.svg")
    fig_clearing(IMG / "taco-clearing.svg")
    fig_adjust(IMG / "taco-adjust.svg")
    fig_tickets(WS / "tickets.pdf", solved=False)
    fig_tickets(IMG / "tickets-solution.svg", solved=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
