"""
Numbers and figures for Lecture 16: price-taking firms and consumers in
competitive markets (CORE 8.3 and 8.4), and for Worksheet 16 and
Practice 16.

Run from the course root:

    python3 slides/figures/make_lecture16.py

No data downloads. The deck's running example is CORE's city of small
bakeries (Figures 8.7 to 8.11) with the course's own numbers, in dollars:

    Sunrise Bakery   one of many bakeries in town selling the same
                     sourdough loaf. It can bake 100 loaves a day at a
                     marginal cost of $2, and up to 50 more on an overnight
                     shift at $5 each. Its fixed cost is $120 a day.
    going price      $4 a loaf, set by the whole market
    best quantity    100 loaves: each of the first 100 earns 4 - 2 = $2,
                     each overnight loaf would lose 5 - 4 = $1
    surplus          (4 - 2) x 100 = $200; profit = 200 - 120 = $80
    supply schedule  below $2: 0; between $2 and $5: 100; above $5: 150

    the town         Sunrise plus Hearth ($3, 100 loaves), Crumb ($5, 100),
                     and Golden Crust ($6, 200). Market supply, lowest cost
                     first: 100 at $2, 200 at $3, 350 at $5, 550 at $6.
    market demand    the Qth buyer's WTP is 8 - Q/50, so Q = 400 - 50P
    equilibrium      P* = $4, Q* = 200 (Sunrise 100 and Hearth 100)
    smooth version   with many bakeries the steps blur into the line
                     P = 2 + Q/100, which also crosses demand at (200, $4)

Worksheet 16 and Practice 16 use Lena's lemonade stand at the county fair:
going price $3 a cup, MC $1 up to 60 cups and $4 up to 90, stand fee $40.
Best quantity 60, surplus $120, profit $80; at $2 still 60 cups, at $5
all 90. Practice 16 adds strawberries at the farmers market (demand
P = 20 - Q/10, supply P = 2 + Q/20, solved by algebra), pumpkin farms, and
the multiple-choice numbers; the market
(problem 3); main() prints and checks those numbers too.

Output, in slides/img/:
  bakery-demand.svg      Sunrise's marginal cost steps and the going price
                         as its demand curve
  bakery-surplus.svg     the same with the surplus on 100 loaves shaded
  bakery-supply.svg      the marginal cost curve as Sunrise's supply curve,
                         with $3 and $6 price lines read off it
  bread-supply.svg       the four bakeries' quantities stacked by cost
  bread-equilibrium.svg  market supply steps and demand, P* = $4, Q* = 200
  bread-smooth.svg       the smooth supply curve and demand, same crossing
  lemonade-solution.svg  the worksheet firm solved, for Practice 16
  strawberries-equilibrium.svg  the practice algebra problem, solved
and in worksheets/figures/:
  lemonade.pdf           the worksheet grid with Lena's marginal cost only

Gridlines sit at every number the slides or questions refer to. Demand in
Okabe-Ito blue, supply and marginal cost in dark orange, each labelled on
the figure; text converted to paths. Alt text lives beside each image.
"""

import glob as _glob
import os
import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle
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
PS_AREA = "#fae2cc"              # light tint of the accent orange

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

# ------------------------------------------------------- Sunrise Bakery ---
PRICE = 4
MC_DAY, CAP_DAY = 2, 100
MC_NIGHT, CAP_NIGHT = 5, 150
FIXED = 120


def firm_supply(p, steps=((MC_DAY, CAP_DAY), (MC_NIGHT, CAP_NIGHT))):
    """Loaves a firm bakes at price p: every step whose cost is below p."""
    q = 0
    for mc, cap in steps:
        if p > mc:
            q = cap
    return q


def firm_surplus(p, steps=((MC_DAY, CAP_DAY), (MC_NIGHT, CAP_NIGHT))):
    s, prev = 0, 0
    for mc, cap in steps:
        if p > mc:
            s += (p - mc) * (cap - prev)
        prev = cap
    return s


# ------------------------------------------------------- the town ---------
# name -> (marginal cost, loaves at that cost)
TOWN = [("Sunrise", MC_DAY, CAP_DAY), ("Hearth", 3, 100),
        ("Sunrise overnight", MC_NIGHT, CAP_NIGHT - CAP_DAY), ("Crumb", 5, 100),
        ("Golden Crust", 6, 200)]


def market_steps():
    """(cost, cumulative loaves, names) in order of cost."""
    out, q = [], 0
    for mc in sorted({mc for _, mc, _ in TOWN}):
        names = [n for n, c, _ in TOWN if c == mc]
        q += sum(cap for _, c, cap in TOWN if c == mc)
        out.append((mc, q, names))
    return out


def market_supply(p):
    return sum(cap for _, mc, cap in TOWN if p > mc)


def market_demand(p):
    return 400 - 50 * p


def wtp(q):
    return 8 - q / 50


def smooth_supply(q):
    return 2 + q / 100


P_STAR, Q_STAR = 4, 200

# ------------------------------------------------------- Lena's lemonade --
L_PRICE = 3
L_STEPS = ((1, 60), (4, 90))
L_FIXED = 40


def lemonade_demand(p):
    """Worksheet 16: cups fairgoers want at the going price p."""
    return 2400 - 400 * p

# ------------------------------------------------------- practice ---------
# Practice 16 problem 5: pumpkin farms. Small (type A): 10 farms, $4 up to
# 40 each, then $5 up to 60. Large (type B): 5 farms, $2 up to 100 each, the
# lower cost. Demand P = 8 - Q/100.
A_N, A_STEPS = 10, ((4, 40), (5, 60))
B_N, B_STEPS = 5, ((2, 100),)


def pumpkin_supply(p):
    return A_N * firm_supply(p, A_STEPS) + B_N * firm_supply(p, B_STEPS)


def pumpkin_demand(p):
    return 800 - 100 * p


# Strawberries at the Saturday farmers market, baskets a day:
# demand P = 20 - Q/10, supply P = 2 + Q/20.
def straw_wtp(q):
    return 20 - q / 10


def straw_wta(q):
    return 2 + q / 20


def straw_demand(p):
    return 10 * (20 - p)


def straw_supply(p):
    return 20 * (p - 2)


STRAW_P, STRAW_Q = 8, 120

# Multiple choice: ten identical bakeries, each 50 loaves at MC $3 and 30
# more at $6.
MC_BAKERIES, MC_STEPS = 10, ((3, 50), (6, 80))


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


def axes(xmax, ymax, xticks, ystep, xlabel, size=SIDE, fs=FONT, xgrid=None):
    fig, ax = plt.subplots(figsize=size, dpi=100)
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, ymax)
    ax.set_xticks(xticks)
    ax.set_yticks(range(0, ymax + 1, ystep))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: money(y)))
    ax.grid(color=GRID, lw=1, zorder=0)
    if xgrid is not None:
        ax.set_xticks(xgrid, minor=True)
        ax.grid(which="minor", axis="x", color=GRID, lw=1, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(which="both", length=0, labelsize=fs - 4)
    ax.set_xlabel(xlabel, fontsize=fs - 2, labelpad=8)
    ax.set_ylabel("Price and cost", fontsize=fs - 2, labelpad=8)
    fig.subplots_adjust(left=0.15, right=0.97, top=0.96, bottom=0.16)
    return fig, ax


def step_curve(ax, steps, xmax, color, lw=4, risers=True):
    """Horizontal segments at each cost, joined by vertical risers."""
    prev = 0
    for i, (mc, cap) in enumerate(steps):
        ax.plot([prev, cap], [mc, mc], color=color, lw=lw, solid_capstyle="round", zorder=5)
        if risers and i + 1 < len(steps):
            ax.plot([cap, cap], [mc, steps[i + 1][0]], color=color, lw=lw, zorder=5)
        prev = cap
    if risers:
        ax.plot([prev, prev], [steps[-1][0], ax.get_ylim()[1]], color=color, lw=lw, zorder=5)


def label(ax, x, y, text, color, dx, dy, ha="left", va="bottom", fs=FONT, bold=True):
    ax.annotate(text, xy=(x, y), xytext=(dx, dy), textcoords="offset points",
                ha=ha, va=va, fontsize=fs, color=color,
                fontweight="bold" if bold else "normal", zorder=8)


def price_line(ax, p, xmax, color=DEMAND, lw=4, ls="-"):
    ax.plot([0, xmax], [p, p], color=color, lw=lw, ls=ls, solid_capstyle="round", zorder=5)


def guides(ax, q, p, color=GUIDE):
    ax.plot([0, q], [p, p], color=color, lw=1.8, ls=(0, (4, 3)), zorder=4)
    ax.plot([q, q], [0, p], color=color, lw=1.8, ls=(0, (4, 3)), zorder=4)


def point(ax, q, p):
    ax.plot(q, p, marker="o", ms=12, color=INK, zorder=9)


FIRM_X = [0, 50, 100, 150]
FIRM_STEPS = ((MC_DAY, CAP_DAY), (MC_NIGHT, CAP_NIGHT))


def fig_bakery(out: Path, shade: bool) -> None:
    fig, ax = axes(160, 8, FIRM_X, 1, "Loaves a day, Q")
    if shade:
        ax.add_patch(Rectangle((0, MC_DAY), CAP_DAY, PRICE - MC_DAY, fc=PS_AREA, ec="none", zorder=2))
        label(ax, CAP_DAY / 2, (MC_DAY + PRICE) / 2, f"Surplus, {money(firm_surplus(PRICE))}",
              SUPPLY, 0, 0, ha="center", va="center", fs=FONT - 2)
    step_curve(ax, FIRM_STEPS, 160, SUPPLY, risers=False)
    ax.plot([CAP_DAY, CAP_DAY], [MC_DAY, MC_NIGHT], color=SUPPLY, lw=4, zorder=5)
    label(ax, 10, MC_DAY, f"MC = {money(MC_DAY)}", SUPPLY, 0, -8, va="top")
    label(ax, 110, MC_NIGHT, f"MC = {money(MC_NIGHT)}", SUPPLY, 0, 8)
    price_line(ax, PRICE, 160)
    label(ax, 4, PRICE, f"Firm's demand, P = {money(PRICE)}", DEMAND, 0, 8)
    if shade:
        ax.plot([CAP_DAY, CAP_DAY], [0, MC_DAY], color=GUIDE, lw=1.8, ls=(0, (4, 3)), zorder=4)
        label(ax, CAP_DAY, 0, "Q* = 100", INK, 8, 6)
    save(fig, out)


def fig_firm_supply(out: Path) -> None:
    fig, ax = axes(160, 8, FIRM_X, 1, "Loaves a day, Q")
    step_curve(ax, FIRM_STEPS, 160, SUPPLY)
    label(ax, 150, 7.4, "Supply = MC", SUPPLY, -10, 0, ha="right", va="center")
    for p in (3, 6):
        q = firm_supply(p)
        ax.plot([0, q], [p, p], color=DEMAND, lw=2.2, ls=(0, (4, 3)), zorder=4)
        ax.plot([q, q], [0, p], color=DEMAND, lw=2.2, ls=(0, (4, 3)), zorder=4)
        point(ax, q, p)
        label(ax, 0, p, f"P = {money(p)}: {q} loaves", DEMAND, 6, 8)
    save(fig, out)


MARKET_X = list(range(0, 601, 100))
MARKET_XGRID = list(range(0, 601, 50))


def fig_market_supply(out: Path, with_demand: bool) -> None:
    fig, ax = axes(600, 8, MARKET_X, 1, "Loaves a day, Q", xgrid=MARKET_XGRID)
    steps = [(mc, q) for mc, q, _ in market_steps()]
    step_curve(ax, steps, 600, SUPPLY)
    if with_demand:
        ax.plot([0, 400], [wtp(0), wtp(400)], color=DEMAND, lw=4, solid_capstyle="round", zorder=5)
        label(ax, 330, wtp(330), "Demand", DEMAND, 12, 4)
        label(ax, 550, 7.4, "Supply", SUPPLY, -10, 0, ha="right", va="center")
        guides(ax, Q_STAR, P_STAR, INK)
        point(ax, Q_STAR, P_STAR)
        label(ax, 0, P_STAR, f"P* = {money(P_STAR)}", INK, 8, 8)
        label(ax, Q_STAR, 0, f"Q* = {Q_STAR}", INK, 8, 6)
    else:
        prev = 0
        names = {2: "Sunrise", 3: "Hearth", 5: "Sunrise overnight,\nCrumb", 6: "Golden Crust"}
        for mc, q in steps:
            x = (prev + q) / 2 - (12 if mc == 5 else 0)   # keep the two-line label off the riser
            label(ax, x, mc, names[mc], SUPPLY, 0, 8, ha="center", fs=FONT - 8)
            prev = q
        label(ax, 550, 7.4, "Supply", SUPPLY, -10, 0, ha="right", va="center")
    save(fig, out)


def fig_smooth(out: Path) -> None:
    fig, ax = axes(600, 8, MARKET_X, 1, "Loaves a day, Q", xgrid=MARKET_XGRID)
    ax.plot([0, 600], [smooth_supply(0), smooth_supply(600)], color=SUPPLY, lw=4,
            solid_capstyle="round", zorder=5)
    ax.plot([0, 400], [wtp(0), wtp(400)], color=DEMAND, lw=4, solid_capstyle="round", zorder=5)
    label(ax, 330, wtp(330), "Demand", DEMAND, 12, 4)
    label(ax, 520, smooth_supply(520), "Supply", SUPPLY, -10, 10, ha="right")
    guides(ax, Q_STAR, P_STAR, INK)
    point(ax, Q_STAR, P_STAR)
    label(ax, 0, P_STAR, f"P* = {money(P_STAR)}", INK, 8, 8)
    label(ax, Q_STAR, 0, f"Q* = {Q_STAR}", INK, 8, 6)
    save(fig, out)


def fig_lemonade(out: Path, solved: bool) -> None:
    fs = FONT - 6 if not solved else FONT
    size = (8.2, 4.8) if not solved else SIDE
    fig, ax = axes(100, 6, list(range(0, 101, 10)), 1, "Cups of lemonade, Q", size=size, fs=fs)
    lw = 2.6 if not solved else 4
    if solved:
        q = firm_supply(L_PRICE, L_STEPS)
        ax.add_patch(Rectangle((0, L_STEPS[0][0]), q, L_PRICE - L_STEPS[0][0], fc=PS_AREA, ec="none", zorder=2))
        label(ax, q / 2, (L_STEPS[0][0] + L_PRICE) / 2, f"Surplus, {money(firm_surplus(L_PRICE, L_STEPS))}",
              SUPPLY, 0, 0, ha="center", va="center", fs=fs - 2)
        price_line(ax, L_PRICE, 100, lw=lw)
        label(ax, 2, L_PRICE, f"Lena's demand, P = {money(L_PRICE)}", DEMAND, 0, 8, fs=fs)
        ax.plot([q, q], [0, L_STEPS[0][0]], color=GUIDE, lw=1.8, ls=(0, (4, 3)), zorder=4)
        label(ax, q, 0, f"Q* = {q}", INK, 8, 6, fs=fs)
    step_curve(ax, L_STEPS, 100, SUPPLY, lw=lw, risers=False)
    ax.plot([L_STEPS[0][1]] * 2, [L_STEPS[0][0], L_STEPS[1][0]], color=SUPPLY, lw=lw, zorder=5)
    label(ax, 5, L_STEPS[0][0], f"MC = {money(L_STEPS[0][0])}", SUPPLY, 0, -8, va="top", fs=fs)
    label(ax, 65, L_STEPS[1][0], f"MC = {money(L_STEPS[1][0])}", SUPPLY, 0, 8, fs=fs)
    if solved:
        save(fig, out)
    else:
        fig.subplots_adjust(left=0.12, right=0.97, top=0.97, bottom=0.17)
        save(fig, out, fmt="pdf")


def fig_firewood(out: Path) -> None:
    """Practice 16 multiple choice: firewood bundles near a campground,
    demand P = 10 - Q/20, supply P = 1 + Q/40, with the price line at $7.
    The crossing ($4, 120) is left unmarked."""
    fig, ax = axes(300, 10, list(range(0, 301, 60)), 1, "Bundles a day, Q",
                   xgrid=list(range(0, 301, 20)))
    ax.set_xlim(0, 315)
    ax.set_ylim(0, 10.5)
    ax.plot([0, 200], [10, 0], color=DEMAND, lw=4, solid_capstyle="round", zorder=5)
    ax.plot([0, 300], [1, 8.5], color=SUPPLY, lw=4, solid_capstyle="round", zorder=5)
    ax.plot([0, 300], [7, 7], color=GUIDE, lw=1.8, ls=(0, (4, 3)), zorder=4)
    label(ax, 300, 7, "P = $7", INK, -4, -6, ha="right", va="top")
    label(ax, 150, 10 - 150 / 20, "Demand", DEMAND, 10, 6)
    label(ax, 270, 1 + 270 / 40, "Supply", SUPPLY, -10, 10, ha="right")
    save(fig, out)


def fig_pumpkins(out: Path) -> None:
    """Practice 16, problem 5(c): the pumpkin market. Market supply steps up
    by marginal cost (large farms 500 at $2, small farms 400 at $4 and 200
    more at $5); demand P = 8 - Q/100 crosses the riser at 500, at $3."""
    fig, ax = axes(1200, 8, list(range(0, 1201, 200)), 1, "Pumpkins, Q",
                   xgrid=list(range(0, 1201, 100)))
    ax.set_xlim(0, 1260)
    ax.set_ylim(0, 8.4)
    steps = [(2, B_N * 100), (4, B_N * 100 + A_N * 40), (5, B_N * 100 + A_N * 60)]
    step_curve(ax, steps, 1200, SUPPLY)
    ax.plot([0, 800], [8, 0], color=DEMAND, lw=4, solid_capstyle="round", zorder=5)
    label(ax, 250, 2, "Large farms", SUPPLY, 0, -10, ha="center", va="top", fs=FONT - 6)
    label(ax, 700, 4, "Small farms", SUPPLY, 0, 8, ha="center", fs=FONT - 6)
    label(ax, 1100, 7.4, "Supply", SUPPLY, -10, 0, ha="right", va="center")
    label(ax, 650, 8 - 650 / 100, "Demand", DEMAND, 10, 4)
    guides(ax, 500, 3, INK)
    point(ax, 500, 3)
    label(ax, 0, 3, "P* = $3", INK, 8, 8)
    label(ax, 500, 0, "Q* = 500", INK, -8, 6, ha="right")
    save(fig, out)


def fig_pumpkin_supply(out: Path) -> None:
    """Practice 16, problem 4(c): the pumpkin market supply curve alone."""
    fig, ax = axes(1200, 8, list(range(0, 1201, 200)), 1, "Pumpkins, Q",
                   xgrid=list(range(0, 1201, 100)))
    ax.set_xlim(0, 1260)
    ax.set_ylim(0, 8.4)
    steps = [(2, B_N * 100), (4, B_N * 100 + A_N * 40), (5, B_N * 100 + A_N * 60)]
    step_curve(ax, steps, 1200, SUPPLY)
    label(ax, 250, 2, "Large farms", SUPPLY, 0, 8, ha="center", fs=FONT - 6)
    label(ax, 700, 4, "Small farms", SUPPLY, 0, 8, ha="center", fs=FONT - 6)
    label(ax, 1100, 7.4, "Supply", SUPPLY, -10, 0, ha="right", va="center")
    save(fig, out)

# ------------------------------------------------------- main -------------
def main() -> int:
    print("Sunrise Bakery at the going price")
    print(f"  each of the first {CAP_DAY} loaves earns {PRICE} - {MC_DAY} = {PRICE - MC_DAY}")
    print(f"  each overnight loaf would lose {MC_NIGHT} - {PRICE} = {MC_NIGHT - PRICE}")
    print(f"  Q* = {firm_supply(PRICE)}, surplus = ({PRICE} - {MC_DAY}) x {CAP_DAY} = {firm_surplus(PRICE)},"
          f" profit = {firm_surplus(PRICE)} - {FIXED} = {firm_surplus(PRICE) - FIXED}")
    assert firm_supply(PRICE) == 100 and firm_surplus(PRICE) == 200
    print("  supply schedule:")
    for p in (1, 3, 6):
        print(f"    P = ${p}: {firm_supply(p)} loaves, surplus {firm_surplus(p)}")
    assert [firm_supply(p) for p in (1, 3, 6)] == [0, 100, 150]

    print("\nThe town's market supply, lowest cost first")
    for mc, q, names in market_steps():
        print(f"  at ${mc}: {', '.join(names)} -> {q} loaves in all")
    for p in (3, 4, 5):
        print(f"  P = ${p}: supply {market_supply(p)} (costs below P), demand {market_demand(p)}")
    assert market_supply(P_STAR) == market_demand(P_STAR) == Q_STAR
    assert market_demand(5) == 150 and market_demand(3) == 250
    assert abs(smooth_supply(Q_STAR) - P_STAR) < 1e-9 and abs(wtp(Q_STAR) - P_STAR) < 1e-9
    print(f"  equilibrium: P* = ${P_STAR}, Q* = {Q_STAR}; smooth supply at {Q_STAR}: ${smooth_supply(Q_STAR):.0f},"
          f" WTP of buyer {Q_STAR}: ${wtp(Q_STAR):.0f}")

    print("\nLena's lemonade (worksheet and practice 1)")
    for p in (L_PRICE, 2, 5):
        q, s = firm_supply(p, L_STEPS), firm_surplus(p, L_STEPS)
        print(f"  P = ${p}: {q} cups, surplus {s}, profit {s - L_FIXED}")
    assert firm_supply(L_PRICE, L_STEPS) == 60 and firm_surplus(L_PRICE, L_STEPS) == 120
    assert firm_supply(2, L_STEPS) == 60 and firm_surplus(2, L_STEPS) == 60
    assert firm_supply(5, L_STEPS) == 90 and firm_surplus(5, L_STEPS) == 270

    print("\nPumpkin farms (practice 16, problem 5)")
    for p in (3, 4.5, 6):
        print(f"  P = ${p}: type A {firm_supply(p, A_STEPS)} each x {A_N}, type B {firm_supply(p, B_STEPS)} each x {B_N},"
              f" market {pumpkin_supply(p)}, demand {pumpkin_demand(p):.0f}")
    assert pumpkin_supply(3) == 500 and pumpkin_demand(3) == 500
    assert pumpkin_supply(4.5) == 900 and pumpkin_supply(6) == 1100
    assert all(pumpkin_supply(p) == 500 for p in (2.01, 3, 3.99))
    large_at = lambda p: firm_supply(p, B_STEPS) * p - 2 * firm_supply(p, B_STEPS)
    print(f"  large farm surplus at $3: {large_at(3):g}, at $2.50: {large_at(2.5):g}")
    assert large_at(3) - large_at(2.5) == 50

    print("\nStrawberries (practice, algebra)")
    from fractions import Fraction as F
    q = F(20 - 2) / (F(1, 10) + F(1, 20))
    print(f"  20 - Q/10 = 2 + Q/20 -> 18 = 3Q/20 -> Q* = {q}, P* = 20 - {q}/10 = {20 - q / 10},"
          f" supply 2 + {q}/20 = {2 + q / 20}")
    assert q == STRAW_Q and 20 - q / 10 == 2 + q / 20 == STRAW_P
    for p in (10, 6):
        print(f"  P = ${p}: demand {straw_demand(p)}, supply {straw_supply(p)}")
    assert (straw_demand(10), straw_supply(10)) == (100, 160)
    assert (straw_demand(6), straw_supply(6)) == (140, 80)
    fw_d = lambda p: 20 * (10 - p)           # firewood: P = 10 - Q/20
    fw_s = lambda p: 40 * (p - 1)            # P = 1 + Q/40
    print(f"  firewood: at $4 {fw_d(4)} and {fw_s(4)}; at $7 demand {fw_d(7)}, supply {fw_s(7)}")
    assert fw_d(4) == fw_s(4) == 120 and (fw_d(7), fw_s(7)) == (60, 240)
    print(f"  multiple choice: at $14, demand {straw_demand(14)}, supply {straw_supply(14)},"
          f" excess supply {straw_supply(14) - straw_demand(14)}")
    assert straw_supply(14) - straw_demand(14) == 180

    print("\nLena: 30th cup adds", L_PRICE - 1, "; 70th cup adds", L_PRICE - 4)
    print("\nWorksheet 16 table (price, Lena, twenty stands, fairgoers want):")
    for p in (0.5, 2, 3, 5):
        q = firm_supply(p, L_STEPS)
        print(f"  ${p}: {q}, {20 * q}, {lemonade_demand(p):g}")
    assert 20 * firm_supply(3, L_STEPS) == lemonade_demand(3) == 1200
    assert all(20 * firm_supply(p, L_STEPS) != lemonade_demand(p) for p in (0.5, 2, 5))
    print("Multiple choice bakeries at $5:", MC_BAKERIES * firm_supply(5, MC_STEPS))
    assert MC_BAKERIES * firm_supply(5, MC_STEPS) == 500
    print("Pumpkin demand P = 8 - Q/100: price for 500 pumpkins is", 8 - 500 / 100)

    fig_bakery(IMG / "bakery-demand.svg", shade=False)
    fig_bakery(IMG / "bakery-surplus.svg", shade=True)
    fig_firm_supply(IMG / "bakery-supply.svg")
    fig_market_supply(IMG / "bread-supply.svg", with_demand=False)
    fig_market_supply(IMG / "bread-equilibrium.svg", with_demand=True)
    fig_smooth(IMG / "bread-smooth.svg")
    fig_lemonade(WS / "lemonade.pdf", solved=False)
    fig_lemonade(IMG / "lemonade-solution.svg", solved=True)
    fig_firewood(IMG / "firewood-market.svg")
    fig_pumpkins(IMG / "pumpkins-equilibrium.svg")
    fig_pumpkin_supply(IMG / "pumpkins-supply.svg")
    return 0


if __name__ == "__main__":
    sys.exit(main())
