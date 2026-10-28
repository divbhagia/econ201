"""
Numbers and figures for Lecture 18: shifts in supply and demand (CORE 8.6),
and for Worksheet 18 and Practice 18.

Run from the course root:

    python3 slides/figures/make_lecture18.py

The deck's running example is a stylized market for Andean quinoa, in
dollars per pound and million pounds a year, with the course's own numbers.
Slides read every value off the graphs; the script checks them.

Stylized numbers (Div, 2026-10-28: price 3 -> 6 -> 4.50, quantity
150 -> 250 -> 300; the nearest set with round shifts):

    demand         P = 7.5 - 3Q/100 (the local buyers, in Peru and Bolivia)
    supply         P = 3Q/100 - 1.5 (enters the plot at 50 million pounds)
    before, A      150 million pounds at $3
    foreign buyers add 200 million pounds at every price: new (total)
                   demand P = 13.5 - 3Q/100. At $3, 350 wanted and 150
                   grown: excess demand 200. New equilibrium C: 250 at $6
    who gained     at $6 locals buy 50 and 200 are exported; farmers gain
                   the strip between $3 and $6 out to the supply curve,
                   local buyers lose the strip under the local demand curve
    flatter supply the same surge with P = 1.5 + Q/100 (through A): 300 at
                   $4.50, so the price rises less and the quantity more
    growers spread 100 million pounds more at every price: supply
                   P = 3Q/100 - 4.5. At $6, 350 grown and 250 wanted:
                   excess supply 100. New equilibrium B: 300 at $4.50

Quinoa data (the opener and the later slide): FAOSTAT production and
producer prices for Peru and Bolivia, from the bulk files
Production_Crops_Livestock_E_Americas.zip and Prices_E_Americas.zip
(downloaded 2026-10-26, item "Quinoa"), cached in
slides/figures/data/quinoa_faostat.csv. The API itself now needs a key.

Practice 18 problem 1: the bread market from Lectures 16 and 17, demand
P = 8 - Q/50 and supply P = 2 + Q/100, 200 loaves at $4. Sourdough goes
viral: 150 more loaves at every price, demand P = 11 - Q/50; at $4, 350
wanted and 200 baked, excess demand 150; new equilibrium 300 at $5. A new
oven cuts marginal cost by $1.50: supply P = 0.5 + Q/100; at $4, 350 baked
and 200 wanted, excess supply 150; new equilibrium 250 at $3.

Worksheet 18 (its own market, Div): pumpkins at the fall market, pumpkins a
day. Demand P = 10 - Q/10, supply P = 2 + Q/10, equilibrium 40 pumpkins at
$6. Halloween week: 20 more wanted at every price, demand P = 12 - Q/10; at
$6, 60 wanted and 40 offered, excess demand 20; new equilibrium 50 at $7. A
bumper harvest: 20 more offered at every price, supply P = Q/10; at $6, 60
offered and 40 wanted, excess supply 20; new equilibrium 50 at $5.


Output, in slides/img/:
  quinoa-data.svg            FAOSTAT, two panels: the production-weighted
                             producer price per pound across Peru and
                             Bolivia, and their combined production in
                             million pounds a year
  quinoa-before.svg          local demand and supply, A
  quinoa-demand-shift.svg    total demand added, A
  quinoa-excess-demand.svg   the $4 line out to total demand, excess 100
  quinoa-new-equilibrium.svg A and C
  quinoa-who-gained.svg      local and total demand, producer surplus gain
                             and local consumer surplus loss shaded
  quinoa-flat-supply.svg     two panels, the surge with steep and flat supply
  quinoa-supply-shift.svg    supply shifted right, excess supply 100 at $5
  quinoa-supply-new-eq.svg   C and B
  bread-shifts-grid.svg      the worksheet grid, for Practice 18 problem 1
  bread-demand-solution.svg, bread-supply-solution.svg
                             the worksheet shocks solved, for Practice 18
and in worksheets/figures/:
  pumpkins-shifts.pdf        the worksheet grid, both curves, unmarked

Gridlines sit at every number the slides or questions refer to and stay
visible through shaded areas. Demand in Okabe-Ito blue, supply in dark
orange, the shifted curve dashed in the same colour, each labelled on the
figure; text converted to paths. Alt text lives beside each image.
"""

import csv
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
DATA = ROOT / "slides" / "figures" / "data"
SCRATCH = Path(os.environ["FIG_PREVIEW_DIR"]) if os.environ.get("FIG_PREVIEW_DIR") else None

INK = "#1a1a1a"
GRID = "#c8c8c8"                  # a shade darker than the earlier decks (Div, lecture 18)
DEMAND = "#0072B2"               # Okabe-Ito blue, 5.1:1 on white
SUPPLY = "#8f4100"               # dark orange, 7.7:1 on white
PERU, BOLIVIA = "#0072B2", "#8f4100"
GUIDE = "#595a5b"
RULE = "#595a5b"
CS_AREA = "#d2e7f5"
PS_AREA = "#fae2cc"
LOST = "#b8b8b8"
# Shaded areas are drawn at zorder 1, under the grid (axisbelow "line"), so
# the gridlines stay visible through them.

SIDE = (8.8, 6.0)
PAIR = (11.6, 5.4)
FONT = 26
DASH = (0, (6, 3))

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


# ------------------------------------------------------- curves ----------
# Each curve is (intercept, slope): P = intercept + slope * Q.
def price_on(curve, q):
    i, m = curve
    return i + m * q


def q_on(curve, p):
    i, m = curve
    return (p - i) / m


def cross(d, s):
    """Equilibrium of demand d and supply s: Q where the prices agree."""
    q = (d[0] - s[0]) / (s[1] - d[1])
    return q, price_on(d, q)


def triangle(q, top, bottom):
    return F(1, 2) * q * (top - bottom)


# Quinoa (the deck), in dollars per pound and million pounds a year.
QD_LOCAL = (F(15, 2), -F(3, 100))
QD_TOTAL = (F(27, 2), -F(3, 100))  # foreign buyers: +200 at every price
QS = (-F(3, 2), F(3, 100))         # enters the plot at 50 million pounds
QS_FLAT = (F(3, 2), F(1, 100))     # through A, for the flat-supply panel
QS_NEW = (-F(9, 2), F(3, 100))     # growers spread: +100 at every price
QA = cross(QD_LOCAL, QS)           # (150, 3)
QC = cross(QD_TOTAL, QS)           # (250, 6)
QC_FLAT = cross(QD_TOTAL, QS_FLAT) # (300, 4.5)
QB = cross(QD_TOTAL, QS_NEW)       # (300, 4.5)

# Bread (the worksheet).
BD0, BD1 = (8, -F(1, 50)), (11, -F(1, 50))
BS0, BS1 = (2, F(1, 100)), (F(1, 2), F(1, 100))
BA, BC, BB = cross(BD0, BS0), cross(BD1, BS0), cross(BD0, BS1)   # (200,4) (300,5) (250,3)

# Pumpkins (the worksheet).
PD0, PD1 = (10, -F(1, 10)), (12, -F(1, 10))
PS0, PS1 = (2, F(1, 10)), (0, F(1, 10))
PA, PC, PB = cross(PD0, PS0), cross(PD1, PS0), cross(PD0, PS1)   # (40,6) (50,7) (50,5)



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


def style(ax, xmax, ymax, xtick, xgrid, xlabel, ylabel="Price and cost", fs=FONT,
          ystep=1, grid=True):
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, ymax)
    ax.set_xticks(range(0, xmax + 1, xtick))
    ax.set_yticks(range(0, ymax + 1, ystep))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: money(y)))
    if grid:
        ax.set_xticks(range(0, xmax + 1, xgrid), minor=True)
        ax.grid(color=GRID, lw=1, zorder=0)
        ax.grid(which="minor", axis="x", color=GRID, lw=1, zorder=0)
        ax.set_axisbelow("line")     # grid above fills, below the curves
        ax.tick_params(which="both", length=0, labelsize=fs - 4)
    else:
        ax.tick_params(which="major", length=4, width=1, labelsize=fs - 4)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_xlabel(xlabel, fontsize=fs - 2, labelpad=8)
    ax.set_ylabel(ylabel, fontsize=fs - 2, labelpad=8)


def label(ax, x, y, text, color, dx, dy, ha="left", va="bottom", fs=FONT, bold=True):
    ax.annotate(text, xy=(float(x), float(y)), xytext=(dx, dy), textcoords="offset points",
                ha=ha, va=va, fontsize=fs, color=color,
                fontweight="bold" if bold else "normal", zorder=8)


def line(ax, curve, xmax, color, lw=4, ls="-"):
    """Draw P = intercept + slope Q over the part of [0, xmax] where P >= 0."""
    i, m = curve
    x0 = 0 if i >= 0 else float(q_on(curve, 0))
    x1 = xmax if m >= 0 or price_on(curve, xmax) >= 0 else float(q_on(curve, 0))
    ax.plot([x0, x1], [float(price_on(curve, x0)), float(price_on(curve, x1))], color=color,
            lw=lw, ls=ls, solid_capstyle="round", zorder=5)


def guides(ax, q, p, color=INK):
    """Dashed guides to both axes; dark enough to read the values off (Div)."""
    q, p = float(q), float(p)
    ax.plot([0, q], [p, p], color=color, lw=2.2, ls=(0, (4, 3)), zorder=4)
    ax.plot([q, q], [0, p], color=color, lw=2.2, ls=(0, (4, 3)), zorder=4)


def point(ax, q, p, text="", dx=10, dy=6, ha="left", va="bottom", fs=FONT):
    ax.plot(float(q), float(p), marker="o", ms=12, color=INK, zorder=9)
    if text:
        label(ax, q, p, text, INK, dx, dy, ha=ha, va=va, fs=fs)


def hline_to(ax, q, p, color=INK):
    ax.plot([0, float(q)], [float(p), float(p)], color=color, lw=2.2, ls=(0, (4, 3)), zorder=4)


def bracket(ax, q0, q1, p, color, above=True):
    """A horizontal bracket from q0 to q1 at price p (label placed separately)."""
    q0, q1, p = float(q0), float(q1), float(p)
    tick = ax.get_ylim()[1] / 40 * (1 if above else -1)
    ax.plot([q0, q1], [p, p], color=color, lw=2.2, zorder=6)
    ax.plot([q0, q0], [p, p + tick], color=color, lw=2.2, zorder=6)
    ax.plot([q1, q1], [p, p + tick], color=color, lw=2.2, zorder=6)


# ------------------------------------------------------- quinoa figures --
Q_X, Q_Y = 500, 12                 # million pounds; dollars per pound
Q_XLABEL = "Million pounds a year, Q"


def quinoa_style(ax, fs=FONT):
    """Gridlines every 50 million pounds and every dollar (Div: a denser
    grid looked ugly); dashed guides mark 225 and $4.50 on the panel."""
    ax.set_xlim(0, Q_X)
    ax.set_ylim(0, Q_Y)
    ax.set_xticks(range(0, 501, 100))
    ax.set_xticks(range(0, Q_X + 1, 50), minor=True)
    ax.set_yticks(range(0, Q_Y + 1, 1))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: money(y)))
    ax.grid(color=GRID, lw=1, zorder=0)
    ax.grid(which="minor", axis="x", color=GRID, lw=1, zorder=0)
    ax.set_axisbelow("line")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(which="both", length=0, labelsize=fs - 4)
    ax.set_xlabel(Q_XLABEL, fontsize=fs - 2, labelpad=8)
    ax.set_ylabel("Dollars per pound", fontsize=fs - 2, labelpad=8)


def quinoa_axes(size=SIDE, fs=FONT):
    fig, ax = plt.subplots(figsize=size, dpi=100)
    quinoa_style(ax, fs)
    fig.subplots_adjust(left=0.16, right=0.97, top=0.96, bottom=0.16)
    return fig, ax


def quinoa_curves(ax, total=False, supply=QS, new_supply=None, fs=FONT,
                  names=("Demand", "New demand")):
    """Demand (and the shifted curve, dashed) plus supply. The local versus
    total naming appears only where the slide needs it (Div)."""
    line(ax, QD_LOCAL, Q_X, DEMAND)
    if total:
        line(ax, QD_TOTAL, Q_X, DEMAND, ls=DASH)
        label(ax, 150, price_on(QD_TOTAL, 150), names[1], DEMAND, 12, 2, fs=fs)
        label(ax, 200, price_on(QD_LOCAL, 200), names[0], DEMAND, -12, -6, ha="right", va="top", fs=fs - 4)
    else:
        label(ax, 200, price_on(QD_LOCAL, 200), names[0], DEMAND, 12, 4, fs=fs)
    line(ax, supply, Q_X, SUPPLY)
    label(ax, 400, price_on(supply, 400), "Supply", SUPPLY, -6, 10, ha="right", fs=fs)
    if new_supply is not None:
        line(ax, new_supply, Q_X, SUPPLY, ls=DASH)
        label(ax, 400, price_on(new_supply, 400), "New\nsupply", SUPPLY, 12, -4, va="top", fs=fs)


def fig_quinoa_before(out: Path) -> None:
    fig, ax = quinoa_axes()
    quinoa_curves(ax)
    guides(ax, *QA)
    point(ax, *QA, "A", dx=0, dy=10, ha="center")
    save(fig, out)


def fig_quinoa_demand_shift(out: Path) -> None:
    fig, ax = quinoa_axes()
    quinoa_curves(ax, total=True)
    guides(ax, *QA)
    point(ax, *QA, "A", dx=0, dy=10, ha="center")
    save(fig, out)


def fig_quinoa_excess_demand(out: Path) -> None:
    fig, ax = quinoa_axes()
    quinoa_curves(ax, total=True)
    qd = q_on(QD_TOTAL, QA[1])
    hline_to(ax, qd, QA[1])
    point(ax, *QA, "A", dx=0, dy=10, ha="center")
    point(ax, qd, QA[1], "D", dx=0, dy=-10, ha="center", va="top")
    bracket(ax, QA[0], qd, QA[1], DEMAND)
    label(ax, qd, QA[1], f"Excess demand,\n{float(qd - QA[0]):.0f}", DEMAND, 12, 6, fs=FONT - 4)
    save(fig, out)


def fig_quinoa_new_equilibrium(out: Path) -> None:
    fig, ax = quinoa_axes()
    quinoa_curves(ax, total=True)
    guides(ax, *QA)
    guides(ax, *QC)
    point(ax, *QA, "A", dx=0, dy=10, ha="center")
    point(ax, *QC, "C", dx=0, dy=12, ha="center")
    save(fig, out)


def fig_quinoa_who_gained(out: Path) -> None:
    """At C: the producer surplus gain (between $4 and $5, out to the supply
    curve) and the local consumer surplus loss (between $4 and $5, under
    local demand) shaded."""
    fig, ax = quinoa_axes()
    q_local = q_on(QD_LOCAL, QC[1])                     # 100
    # Producer surplus gain: the strip between the two prices left of supply.
    ax.fill([0, 0, float(QC[0]), float(QA[0])], [QA[1], QC[1], QC[1], QA[1]],
            color=PS_AREA, lw=0, zorder=1)
    # Local consumer surplus loss: the strip between the two prices under
    # local demand, hatched because it overlaps the farmers' strip.
    ax.fill([0, 0, float(q_local), float(QA[0])], [QA[1], QC[1], QC[1], QA[1]],
            facecolor="none", edgecolor=DEMAND, hatch="//", lw=0, zorder=2)
    quinoa_curves(ax, total=True, names=("Local demand", "Total demand"), fs=FONT - 4)
    guides(ax, *QA)
    guides(ax, *QC)
    ax.plot([float(q_local)] * 2, [0, float(QC[1])], color=GUIDE, lw=1.8, ls=(0, (4, 3)), zorder=4)
    point(ax, *QA, "A", dx=0, dy=10, ha="center")
    point(ax, *QC, "C", dx=0, dy=12, ha="center")
    point(ax, q_local, QC[1])
    save(fig, out)


def fig_quinoa_flat_supply(out: Path) -> None:
    fs = FONT - 4
    fig, axs = plt.subplots(1, 2, figsize=PAIR, dpi=100, sharey=True)
    for ax, (title, s, c) in zip(axs, (("Steep supply", QS, QC), ("Flat supply", QS_FLAT, QC_FLAT))):
        quinoa_style(ax, fs)
        line(ax, QD_LOCAL, Q_X, DEMAND)
        line(ax, QD_TOTAL, Q_X, DEMAND, ls=DASH)
        line(ax, s, Q_X, SUPPLY)
        label(ax, 60, price_on(QD_LOCAL, 60), "D", DEMAND, -8, -8, ha="right", va="top", fs=fs - 4)
        label(ax, 330, price_on(QD_TOTAL, 330), "D'", DEMAND, 10, 2, fs=fs - 4)
        label(ax, 395, price_on(s, 395), "Supply", SUPPLY, -4, 8, ha="right", fs=fs - 4)
        guides(ax, *QA)
        guides(ax, *c)
        point(ax, *QA, "A", dx=0, dy=10, ha="center", fs=fs)
        point(ax, *c, "C", dx=0, dy=12, ha="center", fs=fs)
        ax.set_title(title, fontsize=fs, color=INK, pad=8)
        ax.set_xlim(0, 400)
        ax.set_xticks([0, 200, 400])
    axs[1].set_ylabel("")
    fig.subplots_adjust(left=0.09, right=0.99, top=0.9, bottom=0.17, wspace=0.08)
    save(fig, out)


def fig_quinoa_supply_shift(out: Path) -> None:
    fig, ax = quinoa_axes()
    quinoa_curves(ax, total=True, new_supply=QS_NEW)
    qs = q_on(QS_NEW, QC[1])
    hline_to(ax, qs, QC[1])
    point(ax, *QC, "C", dx=0, dy=12, ha="center")
    point(ax, qs, QC[1])
    bracket(ax, QC[0], qs, QC[1], SUPPLY, above=False)
    label(ax, qs, QC[1], f"Excess supply,\n{float(qs - QC[0]):.0f}", SUPPLY, 12, -8, va="top", fs=FONT - 4)
    save(fig, out)


def fig_quinoa_supply_new_eq(out: Path) -> None:
    fig, ax = quinoa_axes()
    quinoa_curves(ax, total=True, new_supply=QS_NEW)
    guides(ax, *QC)
    guides(ax, *QB)
    point(ax, *QC, "C", dx=0, dy=12, ha="center")
    point(ax, *QB, "B", dx=10, dy=-8, va="top")
    save(fig, out)


# ------------------------------------------------------- quinoa data -----
def quinoa():
    out = {}
    with open(DATA / "quinoa_faostat.csv", newline="") as fh:
        for row in csv.DictReader(fh):
            c, y = row["country"], int(row["year"])
            out.setdefault(c, {})[y] = (
                float(row["production_tonnes"]) if row["production_tonnes"] else None,
                float(row["producer_price_usd_per_tonne"]) if row["producer_price_usd_per_tonne"] else None,
            )
    return out


Q_YEARS = (2000, 2022)             # the latest year in the FAOSTAT file
LB_PER_TONNE = 2204.62
SMOOTH_YEARS = 3                   # centred moving average on the data charts (Div)


def smooth(values, k=SMOOTH_YEARS):
    """Centred k-year moving average; the ends use the years available."""
    h = k // 2
    return [sum(values[max(0, i - h):i + h + 1]) / len(values[max(0, i - h):i + h + 1])
            for i in range(len(values))]


def fig_quinoa_data(out: Path) -> None:
    """Two panels from FAOSTAT, in the stylized market's units: the
    production-weighted producer price per pound across Peru and Bolivia,
    and their combined production in million pounds a year."""
    data = quinoa()
    fs = FONT + 2                      # larger type: the figure fills its slide
    fig, axs = plt.subplots(1, 2, figsize=(16.0, 6.4), dpi=100)   # wide: the PDF frame is height-limited
    for ax in axs:
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.grid(color=GRID, lw=1, zorder=0)
        ax.set_axisbelow(True)
        ax.tick_params(length=0, labelsize=fs - 4)
        ax.set_xlim(Q_YEARS[0] - 1.2, Q_YEARS[1] + 0.5)   # keep "2000" off the "0" at the corner
        ax.set_xticks(range(Q_YEARS[0], Q_YEARS[1] + 1, 4))
        ax.set_xticks(range(Q_YEARS[0], Q_YEARS[1] + 1, 2), minor=True)
        ax.grid(which="minor", axis="x", color=GRID, lw=1, zorder=0)
        ax.set_xlabel("Year", fontsize=fs - 2, labelpad=8)
    ax = axs[0]
    # One price line: the two countries' producer prices weighted by their
    # production each year (Peru alone where Bolivia reports no price).
    years, avg = [], []
    for y in range(Q_YEARS[0], Q_YEARS[1] + 1):
        pairs = [(data[c][y][1], data[c][y][0]) for c in ("Peru", "Bolivia")
                 if y in data[c] and data[c][y][1] is not None and data[c][y][0] is not None]
        if pairs:
            years.append(y)
            avg.append(sum(p * q for p, q in pairs) / sum(q for _, q in pairs) / LB_PER_TONNE)
    sm = smooth(avg)
    ax.plot(years, sm, color=DEMAND, lw=4, solid_capstyle="round", zorder=5)
    ax.set_ylim(0, 1.0)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"${y:.2f}"))
    ax.set_ylabel("Dollars per pound", fontsize=fs - 2, labelpad=8)
    ax.set_title("Price paid to farmers", fontsize=fs, color=INK, pad=8)
    ax.set_ylabel("Dollars per pound", fontsize=fs - 2, labelpad=8)
    ax = axs[1]
    years = [y for y in range(Q_YEARS[0], Q_YEARS[1] + 1)
             if data["Peru"].get(y, (None,))[0] is not None and data["Bolivia"].get(y, (None,))[0] is not None]
    total = [(data["Peru"][y][0] + data["Bolivia"][y][0]) * LB_PER_TONNE / 1e6 for y in years]
    ax.plot(years, smooth(total), color=SUPPLY, lw=4, solid_capstyle="round", zorder=5)
    ax.set_ylim(0, 450)
    ax.set_yticks(range(0, 451, 100))
    ax.set_ylabel("Million pounds a year", fontsize=fs - 2, labelpad=8)
    ax.set_title("Production", fontsize=fs, color=INK, pad=8)
    fig.subplots_adjust(left=0.1, right=0.99, top=0.92, bottom=0.15, wspace=0.25)
    save(fig, out)


# ------------------------------------------------------- bread (worksheet)
B_X, B_Y = 500, 12


def fig_bread(out: Path, shock: str) -> None:
    """The worksheet grid (shock 'none', PDF) or a shock solved (SVG)."""
    fs = FONT - 6 if shock == "none" else FONT
    size = (8.2, 5.0) if shock == "none" else SIDE
    fig, ax = plt.subplots(figsize=size, dpi=100)
    style(ax, B_X, B_Y, 100, 50, "Loaves a day, Q", fs=fs)
    if shock == "none":
        ax.set_xticks(range(0, B_X + 1, 50))
        ax.tick_params(which="both", length=4, width=1, labelsize=fs - 4)
    lw = 2.6 if shock == "none" else 4
    line(ax, BD0, B_X, DEMAND, lw=lw)
    line(ax, BS0, B_X, SUPPLY, lw=lw)
    if shock in ("none", "grid"):
        label(ax, 300, price_on(BD0, 300), "Demand", DEMAND, 10, 4, fs=fs)
        label(ax, 495, price_on(BS0, 495), "Supply", SUPPLY, -4, 10, ha="right", fs=fs)
        if shock == "grid":            # the web copy for Practice 18, problem 1
            fig.subplots_adjust(left=0.15, right=0.97, top=0.96, bottom=0.16)
            save(fig, out)
            return
        fig.subplots_adjust(left=0.13, right=0.97, top=0.97, bottom=0.17)
        save(fig, out, fmt="pdf")
        return
    fig.subplots_adjust(left=0.15, right=0.97, top=0.96, bottom=0.16)
    label(ax, 495, price_on(BS0, 495), "Supply", SUPPLY, -4, 10, ha="right", fs=fs)
    if shock == "demand":
        label(ax, 250, price_on(BD0, 250), "Demand", DEMAND, -8, -8, ha="right", va="top", fs=fs)
        line(ax, BD1, B_X, DEMAND, ls=DASH)
        label(ax, 100, price_on(BD1, 100), "New demand", DEMAND, 10, 8, fs=fs)
        old_p, qd, new = BA[1], q_on(BD1, BA[1]), BC
        hline_to(ax, qd, old_p)
        point(ax, qd, old_p)
        bracket(ax, BA[0], qd, old_p, DEMAND)
        label(ax, qd, old_p, f"Excess demand,\n{float(qd - BA[0]):.0f}", DEMAND, 12, 6, fs=FONT - 4)
        guides(ax, *new, INK)
        point(ax, *BA, "A", dx=-8, dy=-10, ha="right", va="top")
        point(ax, *new, "B")
        label(ax, 0, new[1], f"P = {money(new[1])}", INK, 8, 8)
    else:
        label(ax, 330, price_on(BD0, 330), "Demand", DEMAND, 12, 4, fs=fs)
        line(ax, BS1, B_X, SUPPLY, ls=DASH)
        label(ax, 60, price_on(BS1, 60), "New supply", SUPPLY, 10, 8, fs=fs)
        old_p, qs, new = BA[1], q_on(BS1, BA[1]), BB
        hline_to(ax, qs, old_p)
        point(ax, qs, old_p)
        bracket(ax, BA[0], qs, old_p, SUPPLY, above=False)
        label(ax, qs, old_p, f"Excess supply,\n{float(qs - BA[0]):.0f}", SUPPLY, 12, -8, va="top", fs=FONT - 4)
        guides(ax, *new, INK)
        point(ax, *BA, "A", dx=-8, dy=8, ha="right")
        point(ax, *new, "B", dx=10, dy=-8, va="top")
        label(ax, 0, new[1], f"P = {money(new[1])}", INK, 8, -8, va="top")
    label(ax, new[0], 0, f"Q = {float(new[0]):.0f}", INK, 8, 6)
    save(fig, out)


# ------------------------------------------------------- pumpkins (worksheet)
def fig_pumpkins(out: Path) -> None:
    """The worksheet grid: demand and supply only, gridlines every 10
    pumpkins and every dollar, big enough to draw on."""
    fs = FONT - 6
    fig, ax = plt.subplots(figsize=(8.2, 5.6), dpi=100)
    style(ax, 100, 12, 10, 10, "Pumpkins a day, Q", fs=fs)
    ax.tick_params(which="both", length=4, width=1, labelsize=fs - 4)
    line(ax, PD0, 100, DEMAND, lw=2.6)
    line(ax, PS0, 100, SUPPLY, lw=2.6)
    label(ax, 75, price_on(PD0, 75), "Demand", DEMAND, 10, 4, fs=fs)
    label(ax, 88, price_on(PS0, 88), "Supply", SUPPLY, -6, -6, ha="right", va="top", fs=fs)
    fig.subplots_adjust(left=0.13, right=0.97, top=0.97, bottom=0.15)
    save(fig, out, fmt="pdf")


# ------------------------------------------------------- main -------------
def main() -> int:
    print("Quinoa, before the boom")
    print(f"  A: demand meets supply at Q = {QA[0]}, P = {money(QA[1])}")
    assert QA == (150, 3) and q_on(QS, 0) == 50

    print("\nForeign buyers arrive: +200 at every price")
    for p in (3, 4, 6):
        assert q_on(QD_TOTAL, p) - q_on(QD_LOCAL, p) == 200
    qd, qs = q_on(QD_TOTAL, QA[1]), q_on(QS, QA[1])
    print(f"  at ${QA[1]}: wanted {qd}, grown {qs}, excess demand {qd - qs}")
    assert (qd, qs) == (350, 150)
    print(f"  C: Q = {QC[0]}, P = {money(QC[1])}")
    assert QC == (250, 6)
    q_local = q_on(QD_LOCAL, QC[1])
    print(f"  at C locals buy {q_local}, exports {QC[0] - q_local}")
    assert q_local == 50 and QC[0] - q_local == 200

    print("\nThe same surge with flat supply 1.5 + Q/100 (through A)")
    assert price_on(QS_FLAT, QA[0]) == QA[1]
    print(f"  C: Q = {QC_FLAT[0]}, P = {money(QC_FLAT[1])}; price rise {QC_FLAT[1] - QA[1]} vs {QC[1] - QA[1]}")
    assert QC_FLAT == (300, F(9, 2))

    print("\nGrowers spread: +100 at every price")
    for p in (3, 4, 6):
        assert q_on(QS_NEW, p) - q_on(QS, p) == 100
    qd, qs = q_on(QD_TOTAL, QC[1]), q_on(QS_NEW, QC[1])
    print(f"  at ${QC[1]}: grown {qs}, wanted {qd}, excess supply {qs - qd}")
    assert (qd, qs) == (250, 350)
    print(f"  B: Q = {QB[0]}, P = {money(QB[1])}")
    assert QB == (300, F(9, 2))

    print("\nQuinoa (FAOSTAT), in the deck's units")
    data = quinoa()
    for c in ("Peru", "Bolivia"):
        for y in (2000, 2013, 2014, 2016, 2022):
            v = data[c][y][1]
            print(f"  {c} {y}: ${v / LB_PER_TONNE:.2f} per pound" if v else f"  {c} {y}: no price")
    for y in (2000, 2010, 2013, 2014, 2017, 2022):
        t = (data["Peru"][y][0] + data["Bolivia"][y][0]) * LB_PER_TONNE / 1e6
        pairs = [(data[c][y][1], data[c][y][0]) for c in ("Peru", "Bolivia") if data[c][y][1] is not None]
        avg = sum(p * q for p, q in pairs) / sum(q for _, q in pairs) / LB_PER_TONNE
        print(f"  {y}: production {t:,.0f} million pounds, weighted price ${avg:.2f} per pound")

    print("\nPumpkins (worksheet 18)")
    assert PA == (40, 6)
    qd = q_on(PD1, PA[1])
    print(f"  Halloween, +20: at $6 wanted {qd}, offered {q_on(PS0, PA[1])}, excess demand {qd - PA[0]}; C: {PC[0]} at {money(PC[1])}")
    assert qd == 60 and PC == (50, 7)
    qs = q_on(PS1, PA[1])
    print(f"  bumper harvest, +20: at $6 offered {qs}, wanted {q_on(PD0, PA[1])}, excess supply {qs - PA[0]}; B: {PB[0]} at {money(PB[1])}")
    assert qs == 60 and PB == (50, 5)

    print("\nBread (practice 18 problem 1)")
    assert BA == (200, 4)
    qd = q_on(BD1, BA[1])
    print(f"  sourdough viral, +150: at $4 wanted {qd}, baked {q_on(BS0, BA[1])}, excess demand {qd - BA[0]}; C: {BC[0]} at {money(BC[1])}")
    assert qd == 350 and BC == (300, 5)
    qs = q_on(BS1, BA[1])
    print(f"  new oven, MC down $1.50: at $4 baked {qs}, wanted {q_on(BD0, BA[1])}, excess supply {qs - BA[0]}; B: {BB[0]} at {money(BB[1])}")
    assert qs == 350 and BB == (250, 3)

    fig_quinoa_data(IMG / "quinoa-data.svg")
    fig_quinoa_before(IMG / "quinoa-before.svg")
    fig_quinoa_demand_shift(IMG / "quinoa-demand-shift.svg")
    fig_quinoa_excess_demand(IMG / "quinoa-excess-demand.svg")
    fig_quinoa_new_equilibrium(IMG / "quinoa-new-equilibrium.svg")
    fig_quinoa_who_gained(IMG / "quinoa-who-gained.svg")
    fig_quinoa_flat_supply(IMG / "quinoa-flat-supply.svg")
    fig_quinoa_supply_shift(IMG / "quinoa-supply-shift.svg")
    fig_quinoa_supply_new_eq(IMG / "quinoa-supply-new-eq.svg")
    fig_pumpkins(WS / "pumpkins-shifts.pdf")
    fig_bread(IMG / "bread-shifts-grid.svg", "grid")
    fig_bread(IMG / "bread-demand-solution.svg", "demand")
    fig_bread(IMG / "bread-supply-solution.svg", "supply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
