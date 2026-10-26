"""
Numbers and figures for Lecture 17: gains from trade in competitive
equilibrium, allocation and distribution (CORE 8.5), and for Worksheet 17
and Practice 17.

Run from the course root:

    python3 slides/figures/make_lecture17.py

No data downloads. The running example is Lecture 16's bread market with
many bakeries (slides/figures/make_lecture16.py), in dollars:

    demand     the Qth buyer's WTP is 8 - Q/50
    supply     the Qth loaf's marginal cost is 2 + Q/100
    equilibrium  P* = $4, Q* = 200

    the 100th loaf   WTP 8 - 100/50 = $6, MC 2 + 100/100 = $3: the buyer
                     gains 6 - 4 = $2, the baker 4 - 3 = $1, joint 6 - 3 = $3
    consumer surplus  (1/2) x 200 x (8 - 4) = $400
    producer surplus  (1/2) x 200 x (4 - 2) = $200
    total surplus     $600
    cartel at $6      the bakeries bake what buyers want at $6, 100 loaves
                      (CORE Exercise 8.4 part 1): CS = (1/2) x 100 x (8 - 6)
                      = $100, PS = (6 - 3) x 100 + (1/2) x 100 x (3 - 2) =
                      $350, total $450, deadweight loss (1/2) x 100 x (6 - 3)
                      = $150
    elasticity panels curves rotated through (200, $4), the other fixed:
                      steep supply P = Q/50 gives PS $400, flat supply
                      P = 3 + Q/200 gives $100, CS stays $400; steep demand
                      P = 8 - Q/50 gives CS $400, flat demand P = 5 - Q/200
                      gives $100, PS stays $200

Worksheet 17 (CORE Question 8.6 adapted) caps the bread price at $3:
bakeries bake supply(3) = 100 loaves though buyers want 250; CS = 3 x 100 +
(1/2) x 100 x (8 - 6) = $400, unchanged, PS = (1/2) x 100 x (3 - 2) = $50,
total $450, deadweight loss $150 again, since the same trades are lost.

Practice 17: problem 1 is the worksheet with solutions. Problem 2 is hot
cider at the fall festival: demand P = 8 - Q/25, supply P = 2 + Q/50,
equilibrium 100 cups at $4 with CS $200 and PS $100; the 50th cup has WTP
$6 and MC $3; the stands' cartel at $6 sells 50 cups: CS (1/2) x 50 x 2 =
$50, PS (6 - 3) x 50 + (1/2) x 50 x 1 = $175, total $225, deadweight loss
(1/2) x 50 x (6 - 3) = $75. Multiple choice: demand P = 20 - Q/5 at a
price of $10 sells 50 with CS $250.

Output, in slides/img/:
  bread-one-loaf.svg    the two gains on the 100th loaf
  bread-cs.svg          consumer surplus shaded
  bread-ps.svg          producer surplus shaded
  bread-total.svg       both shaded, total surplus
  cars-mr-dwl.svg       Beautiful Cars (Lecture 10's numbers: demand
                        P = 50,000 - 1,000 Q, MR = 50,000 - 2,000 Q, MC
                        $10,000) choosing 20 cars where MR = MC, priced at
                        $30,000 off the demand curve, with CS, PS, and the
                        deadweight loss triangle out to 40 cars
  bread-cartel.svg      the market under the $6 cartel: CS, PS, and the
                        deadweight loss on the trades that no longer happen
  bread-cap-grid.svg        the worksheet grid, for Practice 17 problem 1
  bread-cap-solution.svg    the worksheet's $3 cap solved, for Practice 17
  cider-equilibrium-solution.svg  the cider equilibrium with CS and PS, for Practice 17
  cider-cartel-solution.svg the cider cartel solved, for Practice 17
  bread-supply-elasticity.svg  two panels, steep and flat supply
  bread-demand-elasticity.svg  two panels, steep and flat demand
and in worksheets/figures/:
  bread-cap.pdf         the worksheet grid with demand and supply only

Gridlines sit at every number the slides or questions refer to. Demand in
Okabe-Ito blue, supply in dark orange, each labelled on the figure; text
converted to paths. Alt text lives beside each image.
"""

import glob as _glob
import os
import sys
from fractions import Fraction as F
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
CS_AREA = "#d2e7f5"              # light tint of the demand blue
PS_AREA = "#fae2cc"              # light tint of the accent orange
LOST = "#b8b8b8"
# Shaded areas are drawn at zorder 1, under the grid (axisbelow "line"), so
# the gridlines stay visible through them and every value can be read off.

SIDE = (8.8, 6.0)
PAIR = (11.6, 5.4)
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

# ------------------------------------------------------- the bread market -
P_STAR, Q_STAR = 4, 200
D_INT, D_SLOPE = 8, F(1, 50)        # WTP of the Qth buyer: 8 - Q/50
S_INT, S_SLOPE = 2, F(1, 100)       # MC of the Qth loaf: 2 + Q/100


def wtp(q):
    return D_INT - D_SLOPE * q


def mc(q):
    return S_INT + S_SLOPE * q


def demand(p):
    return (D_INT - p) / D_SLOPE


def supply(p):
    return (p - S_INT) / S_SLOPE


ONE_LOAF = 100                      # the loaf the deck looks at first
CAP_P = 3                           # the worksheet's price cap


def cs(p, q, intercept=D_INT):
    """Consumer surplus when q loaves sell at price p, demand linear."""
    return F(1, 2) * q * (intercept - wtp(q)) + q * (wtp(q) - p)


def ps(p, q, s_int=S_INT, s_slope=S_SLOPE):
    """Producer surplus when q loaves sell at price p, supply linear."""
    top = s_int + s_slope * q
    return F(1, 2) * q * (top - s_int) + q * (p - top)


# Elasticity panels: one curve rotated through (200, $4), the other fixed.
# (title, intercept, slope); supply slopes up, demand down.
SUPPLY_PANELS = [
    ("Steep (inelastic) supply", 0, F(1, 50)),
    ("Flat (elastic) supply", 3, F(1, 200)),
]
DEMAND_PANELS = [
    ("Steep (inelastic) demand", D_INT, D_SLOPE),
    ("Flat (elastic) demand", 5, F(1, 200)),
]


def triangle(intercept):
    """Surplus of a side whose curve runs from intercept to (Q*, P*)."""
    return F(1, 2) * Q_STAR * abs(intercept - P_STAR)

# Beautiful Cars, from slides/figures/make_lecture10.py: demand
# P = 50,000 - 1,000 Q, MC $10,000 a car, 20 cars at $30,000 where MR = MC,
# and demand meets MC at 40 cars.
CAR_INT, CAR_SLOPE, CAR_MC = 50_000, 1_000, 10_000
CAR_Q, CAR_QEFF, CAR_QMAX = 20, 40, 50


def car_price(q):
    return CAR_INT - CAR_SLOPE * q


def car_mr(q):
    return CAR_INT - 2 * CAR_SLOPE * q


# The cartel price on the deck and the quantity buyers want at it.
CARTEL_P = 6
CARTEL_Q = 100

# Practice 17: hot cider at the fall festival, cups a day.
CI_D_INT, CI_D_SLOPE = 8, F(1, 25)
CI_S_INT, CI_S_SLOPE = 2, F(1, 50)
CI_P, CI_Q = 4, 100


def cider_wtp(q):
    return CI_D_INT - CI_D_SLOPE * q


def cider_mc(q):
    return CI_S_INT + CI_S_SLOPE * q


# Multiple choice: demand P = 20 - Q/5 at a price of $10.
MC_D_INT, MC_D_SLOPE, MC_PRICE = 20, F(1, 5), 10


# ------------------------------------------------------- drawing ----------
def money(x):
    x = float(x)
    return f"${x:,.2f}".replace(".00", "") if x != int(x) else f"${x:,.0f}"


def save(fig, out: Path, fmt="svg") -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format=fmt)
    if SCRATCH:
        fig.savefig(SCRATCH / f"{out.stem}.png", format="png", dpi=110)
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


X_TICKS = list(range(0, 401, 100))
X_GRID = list(range(0, 401, 50))


def style(ax, fs=FONT, xlabel="Loaves a day, Q", xmax=400, ymax=8):
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, ymax)
    ax.set_xticks(X_TICKS)
    ax.set_xticks(X_GRID, minor=True)
    ax.set_yticks(range(0, ymax + 1, 1))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: money(y)))
    ax.grid(color=GRID, lw=1, zorder=0)
    ax.grid(which="minor", axis="x", color=GRID, lw=1, zorder=0)
    ax.set_axisbelow("line")   # grid above fills, below the curves
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(which="both", length=0, labelsize=fs - 4)
    ax.set_xlabel(xlabel, fontsize=fs - 2, labelpad=8)
    ax.set_ylabel("Price and cost", fontsize=fs - 2, labelpad=8)


def axes(size=SIDE, fs=FONT):
    fig, ax = plt.subplots(figsize=size, dpi=100)
    style(ax, fs)
    fig.subplots_adjust(left=0.15, right=0.97, top=0.96, bottom=0.16)
    return fig, ax


def label(ax, x, y, text, color, dx, dy, ha="left", va="bottom", fs=FONT, bold=True):
    ax.annotate(text, xy=(x, y), xytext=(dx, dy), textcoords="offset points",
                ha=ha, va=va, fontsize=fs, color=color,
                fontweight="bold" if bold else "normal", zorder=8)


def curves(ax, fs=FONT, s_int=S_INT, s_slope=S_SLOPE, d_int=D_INT, d_slope=D_SLOPE,
           lw=4, labels=True):
    """Demand and supply lines, labelled near their right ends."""
    ax.plot([0, 400], [d_int, float(d_int - d_slope * 400)], color=DEMAND, lw=lw,
            solid_capstyle="round", zorder=5)
    ax.plot([0, 400], [s_int, float(s_int + s_slope * 400)], color=SUPPLY, lw=lw,
            solid_capstyle="round", zorder=5)
    if labels:
        label(ax, 330, float(d_int - d_slope * 330), "Demand", DEMAND, 12, 4, fs=fs)
        label(ax, 360, float(s_int + s_slope * 360), "Supply", SUPPLY, -10, 10, ha="right", fs=fs)


def guides(ax, q, p, color=GUIDE):
    ax.plot([0, q], [p, p], color=color, lw=1.8, ls=(0, (4, 3)), zorder=4)
    ax.plot([q, q], [0, p], color=color, lw=1.8, ls=(0, (4, 3)), zorder=4)


def point(ax, q, p):
    ax.plot(q, p, marker="o", ms=12, color=INK, zorder=9)


def equilibrium(ax, fs=FONT, labels=True):
    guides(ax, Q_STAR, P_STAR, INK)
    point(ax, Q_STAR, P_STAR)
    if labels:
        label(ax, 0, P_STAR, f"P* = {money(P_STAR)}", INK, 8, 8, fs=fs)
        label(ax, Q_STAR, 0, f"Q* = {Q_STAR}", INK, 8, 6, fs=fs)


def fig_one_loaf(out: Path) -> None:
    fig, ax = axes()
    curves(ax)
    q = ONE_LOAF
    w, c = float(wtp(q)), float(mc(q))
    # Kept sparse (Div, lecture 17): the price line, the two gaps on the
    # 100th loaf, and their endpoints. The bullets give the arithmetic.
    ax.plot([0, Q_STAR], [P_STAR, P_STAR], color=INK, lw=1.8, ls=(0, (4, 3)), zorder=4)
    point(ax, Q_STAR, P_STAR)
    label(ax, 0, P_STAR, f"P* = {money(P_STAR)}", INK, 8, 8)
    ax.plot([q, q], [P_STAR, w], color=DEMAND, lw=7, solid_capstyle="butt", zorder=6)
    ax.plot([q, q], [c, P_STAR], color=SUPPLY, lw=7, solid_capstyle="butt", zorder=6)
    ax.plot([q, q], [0, c], color=GUIDE, lw=1.8, ls=(0, (4, 3)), zorder=4)
    point(ax, q, w)
    point(ax, q, c)
    label(ax, q, w, f"WTP = {money(w)}", DEMAND, 10, 4)
    label(ax, q, c, f"MC = {money(c)}", SUPPLY, 10, -6, va="top")
    label(ax, q, 0, f"{q}th loaf", INK, 8, 6)
    save(fig, out)


def fig_surplus(out: Path, show_cs: bool, show_ps: bool) -> None:
    fig, ax = axes()
    # Both labels left-aligned at the same x, PS straight under CS (Div);
    # no P* and Q* labels, since the slides before have named them.
    if show_cs:
        ax.fill([0, 0, Q_STAR], [D_INT, P_STAR, P_STAR], color=CS_AREA, lw=0, zorder=1)
        ax.text(15, 5.6, f"CS {money(cs(P_STAR, Q_STAR))}", ha="left", va="center",
                fontsize=FONT - 2, color=INK, fontweight="bold", zorder=8)
    if show_ps:
        ax.fill([0, 0, Q_STAR], [P_STAR, S_INT, P_STAR], color=PS_AREA, lw=0, zorder=1)
        ax.text(15, 3.2, f"PS {money(ps(P_STAR, Q_STAR))}", ha="left", va="center",
                fontsize=FONT - 2, color=INK, fontweight="bold", zorder=8)
    curves(ax)
    equilibrium(ax, labels=False)
    save(fig, out)


def fig_cars(out: Path) -> None:
    """Beautiful Cars: demand, marginal revenue, flat marginal cost, the
    choice at MR = MC, and the deadweight loss triangle."""
    fs = FONT - 4
    fig, ax = plt.subplots(figsize=SIDE, dpi=100)
    ax.grid(color=GRID, lw=1, zorder=0)
    ax.set_axisbelow("line")   # grid above fills, below the curves
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(length=0, labelsize=fs - 4)
    ax.set_xlim(0, CAR_QMAX)
    ax.set_ylim(0, 52_000)
    ax.set_xticks(range(0, CAR_QMAX + 1, 10))
    ax.set_yticks(range(0, 50_001, 10_000))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"${y / 1000:,.0f}k"))
    ax.set_xlabel("Cars a day, Q", fontsize=fs - 2, labelpad=8)
    ax.set_ylabel("Price and cost", fontsize=fs - 2, labelpad=8)
    fig.subplots_adjust(left=0.16, right=0.97, top=0.96, bottom=0.16)
    p_star = car_price(CAR_Q)
    ax.fill([0, 0, CAR_Q], [CAR_INT, p_star, p_star], color=CS_AREA, lw=0, zorder=1)
    ax.fill([0, 0, CAR_Q, CAR_Q], [p_star, CAR_MC, CAR_MC, p_star], color=PS_AREA, lw=0, zorder=1)
    ax.fill([CAR_Q, CAR_QEFF, CAR_Q], [p_star, CAR_MC, CAR_MC], color=LOST, lw=0, zorder=1)
    ax.text(1.5, 35_500, "CS", ha="left", va="center", fontsize=fs - 2, color=INK,
            fontweight="bold", zorder=8)
    ax.text(1.5, 20_000, "PS", ha="left", va="center", fontsize=fs - 2, color=INK,
            fontweight="bold", zorder=8)
    ax.plot([0, CAR_QMAX], [car_price(0), car_price(CAR_QMAX)], color=DEMAND, lw=4,
            solid_capstyle="round", zorder=5)
    ax.plot([0, 25], [car_mr(0), car_mr(25)], color=DEMAND, lw=3, ls=(0, (5, 3)), zorder=5)
    ax.plot([0, CAR_QMAX], [CAR_MC, CAR_MC], color=SUPPLY, lw=4, solid_capstyle="round", zorder=5)
    ax.plot([0, CAR_Q], [p_star, p_star], color=GUIDE, lw=1.8, ls=(0, (4, 3)), zorder=4)
    ax.plot([CAR_Q, CAR_Q], [0, p_star], color=GUIDE, lw=1.8, ls=(0, (4, 3)), zorder=4)
    point(ax, CAR_Q, p_star)
    point(ax, CAR_Q, CAR_MC)
    label(ax, 36, car_price(36), "Demand", DEMAND, 10, 6, fs=fs)
    label(ax, 14, car_mr(14), "MR", DEMAND, 10, 2, fs=fs)
    label(ax, 49, CAR_MC, "MC", SUPPLY, 0, 8, ha="right", fs=fs)
    label(ax, CAR_Q, p_star, "P = $30k", INK, 10, 6, fs=fs)
    label(ax, CAR_Q, CAR_MC, "MR = MC", INK, 10, -8, va="top", fs=fs)
    ax.text(25.5, 17_500, "DWL", ha="left", va="center", fontsize=fs - 2, color=INK,
            fontweight="bold", zorder=8)
    save(fig, out)


def fig_cartel(out: Path) -> None:
    """The market under the cartel: 100 loaves at $6, CS and PS shaded up
    to 100, and the lost trades from 100 to 200 grey."""
    fig, ax = axes()
    q = CARTEL_Q
    c = float(mc(q))
    ax.fill([0, 0, q], [D_INT, CARTEL_P, CARTEL_P], color=CS_AREA, lw=0, zorder=1)
    ax.fill([0, 0, q, q], [CARTEL_P, S_INT, c, CARTEL_P], color=PS_AREA, lw=0, zorder=1)
    ax.fill([q, Q_STAR, q], [CARTEL_P, P_STAR, c], color=LOST, lw=0, zorder=1)
    curves(ax, labels=False)
    label(ax, 330, float(wtp(330)), "Demand", DEMAND, 12, 4)
    label(ax, 395, float(mc(395)), "Supply", SUPPLY, -6, 14, ha="right")   # clear of the $6 line
    ax.plot([0, 400], [CARTEL_P, CARTEL_P], color=INK, lw=1.8, ls=(0, (4, 3)), zorder=4)
    ax.plot([q, q], [0, c], color=GUIDE, lw=1.8, ls=(0, (4, 3)), zorder=4)
    point(ax, Q_STAR, P_STAR)
    point(ax, q, CARTEL_P)
    ax.text(10, 6.45, f"CS {money(cs(CARTEL_P, q))}", ha="left", va="center",
            fontsize=FONT - 2, color=INK, fontweight="bold", zorder=8)
    ax.text(15, 4.2, f"PS {money(ps(CARTEL_P, q))}", ha="left", va="center",
            fontsize=FONT - 2, color=INK, fontweight="bold", zorder=8)
    ax.text(q + 22, 4.5, f"DWL\n{money(triangle_lost(q))}", ha="left", va="center",
            fontsize=FONT - 4, color=INK, fontweight="bold", zorder=8, linespacing=1.05)
    label(ax, q, CARTEL_P, f"Cartel price, {money(CARTEL_P)}", INK, 12, 6)
    label(ax, q, 0, f"{q} loaves", INK, 8, 6)
    save(fig, out)


def fig_cap_solution(out: Path) -> None:
    """The worksheet's price cap solved: 100 loaves at $3, CS and PS shaded
    up to 100, the lost trades from 100 to 200 grey."""
    fig, ax = axes()
    q = int(supply(CAP_P))
    w = float(wtp(q))
    ax.fill([0, 0, q, q], [D_INT, CAP_P, CAP_P, w], color=CS_AREA, lw=0, zorder=1)
    ax.fill([0, 0, q], [CAP_P, S_INT, CAP_P], color=PS_AREA, lw=0, zorder=1)
    ax.fill([q, Q_STAR, q], [w, P_STAR, CAP_P], color=LOST, lw=0, zorder=1)
    curves(ax, labels=False)
    label(ax, 330, float(wtp(330)), "Demand", DEMAND, 12, 4)
    label(ax, 395, float(mc(395)), "Supply", SUPPLY, -6, 14, ha="right")
    ax.plot([0, 400], [CAP_P, CAP_P], color=INK, lw=1.8, ls=(0, (4, 3)), zorder=4)
    ax.plot([q, q], [0, w], color=GUIDE, lw=1.8, ls=(0, (4, 3)), zorder=4)
    point(ax, Q_STAR, P_STAR)
    point(ax, q, CAP_P)
    ax.text(15, 5.3, f"CS {money(cs(CAP_P, q))}", ha="left", va="center",
            fontsize=FONT - 2, color=INK, fontweight="bold", zorder=8)
    ax.text(15, 2.55, f"PS {money(ps(CAP_P, q))}", ha="left", va="center",
            fontsize=FONT - 2, color=INK, fontweight="bold", zorder=8)
    ax.text(q + 22, 4.5, f"DWL\n{money(triangle_lost(q))}", ha="left", va="center",
            fontsize=FONT - 4, color=INK, fontweight="bold", zorder=8, linespacing=1.05)
    label(ax, 400, CAP_P, f"Price cap, {money(CAP_P)}", INK, -4, 6, ha="right")
    label(ax, q, 0, f"{q} loaves", INK, 8, 6)
    save(fig, out)


def fig_cider_solution(out: Path, cartel: bool) -> None:
    """Practice 17, problem 2: the cider market at its equilibrium with CS
    and PS shaded (2b), or under the cartel at $6 with the deadweight loss
    (2c). No gridlines: the problem gives equations, not a graph."""
    fig, ax = plt.subplots(figsize=SIDE, dpi=100)
    ax.set_xlim(0, 200)
    ax.set_ylim(0, 8)
    ax.set_xticks(range(0, 201, 50))
    ax.set_yticks(range(0, 9))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: money(y)))
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(which="major", length=4, width=1, labelsize=FONT - 4)
    ax.set_xlabel("Cups a day, Q", fontsize=FONT - 2, labelpad=8)
    ax.set_ylabel("Price and cost", fontsize=FONT - 2, labelpad=8)
    fig.subplots_adjust(left=0.15, right=0.97, top=0.96, bottom=0.16)
    ax.plot([0, 200], [CI_D_INT, float(cider_wtp(200))], color=DEMAND, lw=4, solid_capstyle="round", zorder=5)
    ax.plot([0, 200], [CI_S_INT, float(cider_mc(200))], color=SUPPLY, lw=4, solid_capstyle="round", zorder=5)
    label(ax, 165, float(cider_wtp(165)), "Demand", DEMAND, 12, 4)
    label(ax, 198, float(cider_mc(198)), "Supply", SUPPLY, -6, 14, ha="right")
    if not cartel:
        ax.fill([0, 0, CI_Q], [CI_D_INT, CI_P, CI_P], color=CS_AREA, lw=0, zorder=1)
        ax.fill([0, 0, CI_Q], [CI_P, CI_S_INT, CI_P], color=PS_AREA, lw=0, zorder=1)
        guides(ax, CI_Q, CI_P, INK)
        point(ax, CI_Q, CI_P)
        ax.text(7, 5.6, "CS $200", ha="left", va="center", fontsize=FONT - 2, color=INK,
                fontweight="bold", zorder=8)
        ax.text(7, 3.2, "PS $100", ha="left", va="center", fontsize=FONT - 2, color=INK,
                fontweight="bold", zorder=8)
        label(ax, 0, CI_P, f"P* = {money(CI_P)}", INK, 8, 8)
        label(ax, CI_Q, 0, f"Q* = {CI_Q}", INK, 8, 6)
        save(fig, out)
        return
    q = int((CI_D_INT - CARTEL_P) / CI_D_SLOPE)
    c = float(cider_mc(q))
    ax.fill([0, 0, q], [CI_D_INT, CARTEL_P, CARTEL_P], color=CS_AREA, lw=0, zorder=1)
    ax.fill([0, 0, q, q], [CARTEL_P, CI_S_INT, c, CARTEL_P], color=PS_AREA, lw=0, zorder=1)
    ax.fill([q, CI_Q, q], [CARTEL_P, CI_P, c], color=LOST, lw=0, zorder=1)
    ax.plot([0, 200], [CARTEL_P, CARTEL_P], color=INK, lw=1.8, ls=(0, (4, 3)), zorder=4)
    ax.plot([q, q], [0, c], color=GUIDE, lw=1.8, ls=(0, (4, 3)), zorder=4)
    guides(ax, CI_Q, CI_P, GUIDE)
    point(ax, CI_Q, CI_P)
    point(ax, q, CARTEL_P)
    ax.text(5, 6.45, "CS $50", ha="left", va="center", fontsize=FONT - 2, color=INK,
            fontweight="bold", zorder=8)
    ax.text(7, 4.2, "PS $175", ha="left", va="center", fontsize=FONT - 2, color=INK,
            fontweight="bold", zorder=8)
    ax.text(q + 11, 4.5, "DWL\n$75", ha="left", va="center", fontsize=FONT - 4, color=INK,
            fontweight="bold", zorder=8, linespacing=1.05)
    label(ax, q, CARTEL_P, f"Cartel price, {money(CARTEL_P)}", INK, 12, 6)
    label(ax, q, 0, f"{q} cups", INK, 8, 6)
    label(ax, CI_Q, 0, f"Q* = {CI_Q}", INK, 8, 6)
    save(fig, out)


def triangle_lost(q):
    """Surplus on the trades between q and Q* that do not happen."""
    return F(1, 2) * (Q_STAR - q) * (wtp(q) - mc(q))


def fig_elasticity(out: Path, panels, rotate: str) -> None:
    """Two panels: the rotated curve (supply or demand) steep, then flat,
    through the same equilibrium, with both surpluses shaded."""
    fs = FONT - 4
    fig, axs = plt.subplots(1, 2, figsize=PAIR, dpi=100, sharey=True)
    for ax, (title, intercept, slope) in zip(axs, panels):
        style(ax, fs)
        if rotate == "supply":
            s_int, s_slope, d_int, d_slope = intercept, slope, D_INT, D_SLOPE
        else:
            s_int, s_slope, d_int, d_slope = S_INT, S_SLOPE, intercept, slope
        assert s_int + s_slope * Q_STAR == P_STAR and d_int - d_slope * Q_STAR == P_STAR
        ax.fill([0, 0, Q_STAR], [d_int, P_STAR, P_STAR], color=CS_AREA, lw=0, zorder=1)
        ax.fill([0, 0, Q_STAR], [P_STAR, s_int, P_STAR], color=PS_AREA, lw=0, zorder=1)
        curves(ax, fs=fs, s_int=s_int, s_slope=s_slope, d_int=d_int, d_slope=d_slope, lw=3, labels=False)
        guides(ax, Q_STAR, P_STAR, INK)
        point(ax, Q_STAR, P_STAR)
        c, p = triangle(d_int), triangle(s_int)
        # Labels left-aligned at the same x, each at mid-height of its
        # triangle there, so PS sits straight under CS.
        cy = (P_STAR + float(d_int - d_slope * 60)) / 2
        py = (P_STAR + float(s_int + s_slope * 60)) / 2
        ax.text(15, cy, f"CS {money(c)}", ha="left", va="center", fontsize=fs - 2,
                color=INK, fontweight="bold", zorder=8)
        ax.text(15, py, f"PS {money(p)}", ha="left", va="center", fontsize=fs - 2,
                color=INK, fontweight="bold", zorder=8)
        label(ax, 330, float(d_int - d_slope * 330), "D", DEMAND, 8, 4, fs=fs)
        label(ax, 380, float(s_int + s_slope * 380), "S", SUPPLY, -4, 10, ha="right", fs=fs)
        ax.set_title(title, fontsize=fs, color=INK, pad=8)
        ax.set_xticks([0, 200, 400])
        ax.set_xticks(X_GRID, minor=True)
    axs[1].set_ylabel("")
    fig.subplots_adjust(left=0.09, right=0.99, top=0.9, bottom=0.17, wspace=0.08)
    save(fig, out)


def fig_worksheet(out: Path, fmt="pdf") -> None:
    """Worksheet grid: the bread demand and supply only, for students to
    mark and shade. The PDF is drawn at print size with gridlines labelled
    every 50 loaves; the SVG for Practice 17, problem 1, matches the
    solution figures' size and type, with gridlines every 50 and labels
    every 100."""
    if fmt == "pdf":
        fs = FONT - 6
        fig, ax = plt.subplots(figsize=(8.2, 5.0), dpi=100)
        style(ax, fs)
        ax.set_xticks(X_GRID)
        ax.tick_params(which="both", length=4, width=1, labelsize=fs - 4)
        curves(ax, fs=fs, lw=2.6)
        fig.subplots_adjust(left=0.13, right=0.97, top=0.97, bottom=0.17)
    else:
        fig, ax = axes()
        curves(ax)
    save(fig, out, fmt=fmt)


# ------------------------------------------------------- main -------------
def main() -> int:
    print("The bread market")
    print(f"  demand: WTP of the Qth buyer = {D_INT} - Q/{1 / D_SLOPE:.0f}; supply: MC of the Qth loaf = {S_INT} + Q/{1 / S_SLOPE:.0f}")
    assert wtp(Q_STAR) == mc(Q_STAR) == P_STAR
    assert demand(P_STAR) == supply(P_STAR) == Q_STAR
    q = ONE_LOAF
    print(f"  {q}th loaf: WTP = {D_INT} - {q}/50 = {wtp(q)}, MC = {S_INT} + {q}/100 = {mc(q)}")
    print(f"    buyer gains {wtp(q)} - {P_STAR} = {wtp(q) - P_STAR}, baker gains {P_STAR} - {mc(q)} = {P_STAR - mc(q)},"
          f" joint {wtp(q)} - {mc(q)} = {wtp(q) - mc(q)}")
    assert (wtp(q), mc(q)) == (6, 3)

    c, p = cs(P_STAR, Q_STAR), ps(P_STAR, Q_STAR)
    print(f"  CS = (1/2) x {Q_STAR} x ({D_INT} - {P_STAR}) = {c}")
    print(f"  PS = (1/2) x {Q_STAR} x ({P_STAR} - {S_INT}) = {p}")
    print(f"  total surplus = {c} + {p} = {c + p}; buyers' share {c / (c + p)}")
    assert (c, p) == (400, 200)

    q = int(supply(CAP_P))
    c2, p2 = cs(CAP_P, q), ps(CAP_P, q)
    print(f"  worksheet price cap ${CAP_P}: bakeries bake {q} loaves (supply), buyers want {demand(CAP_P):.0f}")
    print(f"    CS = {CAP_P} x {q} + (1/2) x {q} x ({D_INT} - {wtp(q)}) = {c2}")
    print(f"    PS = (1/2) x {q} x ({CAP_P} - {S_INT}) = {p2}")
    print(f"    deadweight loss = (1/2) x {Q_STAR - q} x ({wtp(q)} - {mc(q)}) = {triangle_lost(q)};"
          f" total {c2 + p2} = {c + p} - {triangle_lost(q)}")
    assert q == 100 and demand(CAP_P) == 250
    assert (c2, p2, triangle_lost(q)) == (400, 50, 150) and c2 + p2 + triangle_lost(q) == c + p

    print("\nElasticity panels (the other curve fixed, both through (200, $4))")
    for title, s_int, s_slope in SUPPLY_PANELS:
        print(f"  {title}: P = {s_int} + Q/{1 / s_slope:.0f}, PS = (1/2) x {Q_STAR} x ({P_STAR} - {s_int}) = {triangle(s_int)}, CS = {c}")
    for title, d_int, d_slope in DEMAND_PANELS:
        print(f"  {title}: P = {d_int} - Q/{1 / d_slope:.0f}, CS = (1/2) x {Q_STAR} x ({d_int} - {P_STAR}) = {triangle(d_int)}, PS = {p}")
    assert [triangle(i) for _, i, _ in SUPPLY_PANELS] == [400, 100]
    assert [triangle(i) for _, i, _ in DEMAND_PANELS] == [400, 100]
    assert triangle(D_INT) == c and triangle(S_INT) == p

    print("\nBeautiful Cars (Lecture 10's numbers)")
    print(f"  MR = MC at Q = {CAR_Q}: MR {car_mr(CAR_Q):,} = MC {CAR_MC:,}; price {car_price(CAR_Q):,};"
          f" demand meets MC at {CAR_QEFF}: {car_price(CAR_QEFF):,}")
    assert car_mr(CAR_Q) == CAR_MC and car_price(CAR_Q) == 30_000 and car_price(CAR_QEFF) == CAR_MC

    print("\nThe cartel (deck)")
    assert demand(CARTEL_P) == CARTEL_Q
    c3, p3 = cs(CARTEL_P, CARTEL_Q), ps(CARTEL_P, CARTEL_Q)
    print(f"  at ${CARTEL_P}, buyers want {demand(CARTEL_P):.0f} loaves; the {CARTEL_Q}th costs {mc(CARTEL_Q)}")
    print(f"  CS = (1/2) x {CARTEL_Q} x ({D_INT} - {CARTEL_P}) = {c3}")
    print(f"  PS = ({CARTEL_P} - {mc(CARTEL_Q)}) x {CARTEL_Q} + (1/2) x {CARTEL_Q} x ({mc(CARTEL_Q)} - {S_INT}) = {p3}")
    print(f"  total {c3 + p3}, deadweight loss {c + p - (c3 + p3)} = {triangle_lost(CARTEL_Q)}")
    assert (c3, p3, c + p - c3 - p3) == (100, 350, 150) and triangle_lost(CARTEL_Q) == 150
    print(f"  buyers lose {c - c3}, bakeries gain {p3 - p}")
    assert (c - c3, p3 - p) == (300, 150)

    print("\nPractice 17, problem 2: hot cider")
    assert cider_wtp(CI_Q) == cider_mc(CI_Q) == CI_P
    ci_cs, ci_ps = F(1, 2) * CI_Q * (CI_D_INT - CI_P), F(1, 2) * CI_Q * (CI_P - CI_S_INT)
    print(f"  8 - Q/25 = 2 + Q/50 -> 6 = 3Q/50 -> Q* = {CI_Q}, P* = {CI_P}")
    print(f"  CS = (1/2) x {CI_Q} x ({CI_D_INT} - {CI_P}) = {ci_cs}, PS = (1/2) x {CI_Q} x ({CI_P} - {CI_S_INT}) = {ci_ps},"
          f" total {ci_cs + ci_ps}")
    assert (ci_cs, ci_ps) == (200, 100)
    print(f"  50th cup: WTP {cider_wtp(50)}, MC {cider_mc(50)}: buyer gains {cider_wtp(50) - CI_P}, stand gains {CI_P - cider_mc(50)}")
    assert (cider_wtp(50), cider_mc(50)) == (6, 3)
    cq = (CI_D_INT - CARTEL_P) / CI_D_SLOPE
    cm = cider_mc(cq)
    k_cs = F(1, 2) * cq * (CI_D_INT - CARTEL_P)
    k_ps = (CARTEL_P - cm) * cq + F(1, 2) * cq * (cm - CI_S_INT)
    k_dwl = F(1, 2) * (CI_Q - cq) * (CARTEL_P - cm)
    print(f"  cartel at ${CARTEL_P}: {cq} cups; the {cq}th costs {cm}")
    print(f"    CS = (1/2) x {cq} x ({CI_D_INT} - {CARTEL_P}) = {k_cs}")
    print(f"    PS = ({CARTEL_P} - {cm}) x {cq} + (1/2) x {cq} x ({cm} - {CI_S_INT}) = {k_ps}")
    print(f"    total {k_cs + k_ps}, DWL = (1/2) x {CI_Q - cq} x ({CARTEL_P} - {cm}) = {k_dwl}")
    print(f"    buyers lose {ci_cs - k_cs}, stands gain {k_ps - ci_ps}")
    assert (cq, cm) == (50, 3) and (k_cs, k_ps, k_dwl) == (50, 175, 75)
    assert ci_cs + ci_ps - (k_cs + k_ps) == k_dwl
    assert (ci_cs - k_cs, k_ps - ci_ps) == (150, 75)

    print("\nMultiple choice")
    mq = (MC_D_INT - MC_PRICE) / MC_D_SLOPE
    print(f"  demand {MC_D_INT} - Q/5 at ${MC_PRICE}: Q = {mq}, CS = (1/2) x {mq} x ({MC_D_INT} - {MC_PRICE}) = {F(1, 2) * mq * (MC_D_INT - MC_PRICE)}")
    assert mq == 50 and F(1, 2) * mq * (MC_D_INT - MC_PRICE) == 250
    print("  one trade at $5: WTP $9, MC $3 -> buyer 4, seller 2, total 6")
    assert (9 - 5, 5 - 3, 9 - 3) == (4, 2, 6)

    fig_one_loaf(IMG / "bread-one-loaf.svg")
    fig_surplus(IMG / "bread-cs.svg", show_cs=True, show_ps=False)
    fig_surplus(IMG / "bread-ps.svg", show_cs=False, show_ps=True)
    fig_surplus(IMG / "bread-total.svg", show_cs=True, show_ps=True)
    fig_cars(IMG / "cars-mr-dwl.svg")
    fig_cartel(IMG / "bread-cartel.svg")
    fig_cap_solution(IMG / "bread-cap-solution.svg")
    fig_cider_solution(IMG / "cider-equilibrium-solution.svg", cartel=False)
    fig_cider_solution(IMG / "cider-cartel-solution.svg", cartel=True)
    fig_elasticity(IMG / "bread-supply-elasticity.svg", SUPPLY_PANELS, "supply")
    fig_elasticity(IMG / "bread-demand-elasticity.svg", DEMAND_PANELS, "demand")
    fig_worksheet(WS / "bread-cap.pdf")
    fig_worksheet(IMG / "bread-cap-grid.svg", fmt="svg")
    return 0


if __name__ == "__main__":
    sys.exit(main())
