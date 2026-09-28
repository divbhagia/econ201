"""
Figures and numbers for Lecture 10: the surplus from a sale and who
captures it (CORE 7.7).

Run from the course root:

    python3 slides/figures/make_lecture10.py

No data downloads. The running example is CORE's Beautiful Cars with the
course's numbers: lecture 6's cost function and the demand curve of the
practice 9 questions, so the profit-maximizing point is the one students
have already found.

    demand           P = 50,000 - 1,000 Q, cars a day (the k-th buyer in
                     line, highest first, is willing to pay 50,000 - 1,000 k)
    cost             C(Q) = 60,000 + 10,000 Q, so MC = 10,000
    MR = MC          MR = 50,000 - 2,000 Q = 10,000 at Q* = 20, P* = 30,000
    profit at Q*     = 600,000 - 260,000 = 340,000
    consumer surplus = 1/2 x 20 x (50,000 - 30,000) = 200,000
    producer surplus = (30,000 - 10,000) x 20 = 400,000
                       and profit = 400,000 - 60,000 = 340,000
    efficient point  demand meets MC where 50,000 - 1,000 Q = 10,000, Q = 40
    deadweight loss  = 1/2 x (40 - 20) x (30,000 - 10,000) = 200,000
    total surplus    = 1/2 x 40 x (50,000 - 10,000) = 800,000

Surpluses are measured as areas, as CORE does in Figure 7.19. Adding the
buyer-by-buyer surpluses one car at a time gives a slightly different
number (the triangle is a staircase), so the slides use the areas only.

Output, in slides/img/:
  cars-wtp.svg         the demand curve read as willingness to pay: the 5th
                       and 15th buyers marked with coloured dotted guides, and
                       E, the MR = MC choice, in heavier dashes
  cars-best.svg        demand, marginal revenue, and marginal cost, with E
                       and E-prime labelled, at column size
  cars-cs.svg          consumer surplus as strips: one light line per half
                       car from the price up to demand, the 5th, 10th, and
                       15th buyers' gains drawn darker and labelled
  cars-ps.svg          producer surplus the same way: light lines from MC
                       up to the price
  cars-surplus.svg     consumer and producer surplus shaded lightly and
                       labelled with their values, at column size
  cars-leftout.svg     the 30th buyer: WTP $20,000 on the demand curve, below
                       the $30,000 price, with the gap above MC split at the
                       $15,000 deal into the firm's and the buyer's $5,000
  cars-dwl.svg         the same with the deadweight loss triangle, lined like
                       the CS and PS slides, from E to
                       F shaded and labelled, at column size

  gift-receipt.svg     a joke gift receipt for grandma's $50 sweater, valued at
                       63 cents on the dollar (Waldfogel's grandparent yield,
                       62.9%), so the deadweight loss is $18.50

and in worksheets/figures/:
  scooters.pdf         the worksheet's own example: a scooter maker's demand,
                       MC, and E on a grid fine enough to read every number

Accessibility: Okabe-Ito derived colours, every curve, point, and area
labelled with its name and value on the figure itself, so nothing rests on
colour; text converted to paths. Alt text lives beside each image.
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
DEMAND = "#0072B2"
ACCENT = "#BF5700"
MARGINAL = "#595a5b"
GUIDE = "#595a5b"
CS_FILL = "#a6d1ec"   # light tint of the demand blue
PS_FILL = "#f5c9a3"   # light tint of the accent orange
DWL_FILL = "#d4d4d4"
# Lighter tints for the solid areas (surplus and DWL figures); the strips on
# the CS and PS slides keep the stronger tints above so thin lines still show.
CS_AREA = "#d2e7f5"
PS_AREA = "#fae2cc"
DWL_AREA = "#e8e8e8"
BUYER_COLOURS = ("#0072B2", "#00735A")   # Okabe-Ito blue, darkened green

SIDE = (8.8, 6.0)                # every slide figure, beside a 38% text column
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
FIXED = 60_000                   # fixed cost a day
PER_CAR = 10_000                 # cost of one more car, MC
INTERCEPT = 50_000               # demand: P = INTERCEPT - SLOPE Q
SLOPE = 1_000
Q_STAR = 20
Q_EFF = 40
Q_MAX = 50
SLIDE_BUYERS = (5, 15)           # the two buyers on the one-car slide
SLIDE_LEFT_OUT = 30              # the buyer priced out, Pareto improvement
SLIDE_DEAL = 15_000              # a price that suits both
# The worksheet's own example, read off a printed graph: a scooter maker
# with demand P = 1,200 - 20 Q and MC = 400, so MR = 1,200 - 40 Q = 400 at
# Q* = 20, P* = 800, and demand meets MC at 40.
SC_INTERCEPT, SC_SLOPE, SC_MC = 1_200, 20, 400
SC_Q, SC_QEFF, SC_BUYER = 20, 40, 10


def price(q):
    return INTERCEPT - SLOPE * q


def wtp(k):
    """Willingness to pay of the k-th buyer in line, highest first."""
    return price(k)


def revenue(q):
    return price(q) * q


def total_cost(q):
    return FIXED + PER_CAR * q


def average_cost(q):
    return total_cost(q) / q


def profit(q):
    return revenue(q) - total_cost(q)


def marginal_revenue(q):
    return INTERCEPT - 2 * SLOPE * q


P_STAR = price(Q_STAR)
CS = Q_STAR * (INTERCEPT - P_STAR) // 2
PS = (P_STAR - PER_CAR) * Q_STAR
DWL = (Q_EFF - Q_STAR) * (P_STAR - PER_CAR) // 2
TS_MAX = Q_EFF * (INTERCEPT - PER_CAR) // 2


def money(x):
    """$30,000, -$10,000."""
    sign = "−" if x < 0 else ""
    return f"{sign}${abs(x):,.0f}"


def save(fig, out: Path, fmt="svg") -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format=fmt)
    if SCRATCH:
        fig.savefig(SCRATCH / f"{out.stem}.png", format="png", dpi=110)
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


# ----------------------------------------------------------- drawing ------

def axes(size=SIDE, fs=FONT, ymin=0):
    fig, ax = plt.subplots(figsize=size, dpi=100)
    ax.grid(color=GRID, lw=1, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=5, width=1, labelsize=fs)
    ax.set_xlim(0, Q_MAX)
    ax.set_ylim(ymin, 52_000)
    ax.set_xticks(range(0, Q_MAX + 1, 10))
    ax.set_yticks(range(ymin, 50_001, 10_000))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: money(y)))
    ax.set_xlabel("Cars per day, Q", fontsize=fs, labelpad=8)
    ax.set_ylabel("Price and cost", fontsize=fs, labelpad=8)
    fig.subplots_adjust(left=0.22, right=0.965, top=0.96, bottom=0.15)
    return fig, ax


def demand_and_mc(ax, fs=FONT, lw=3, label_at=32):
    q = np.array([0, Q_MAX])
    ax.plot(q, price(q), color=DEMAND, lw=lw, solid_capstyle="round", zorder=5)
    ax.annotate("Demand", xy=(label_at, price(label_at)), xytext=(10, 8),
                textcoords="offset points", ha="left", va="bottom",
                fontsize=fs, color=DEMAND, fontweight="bold", zorder=8)
    ax.axhline(PER_CAR, color=MARGINAL, lw=lw - 0.6, ls=(0, (5, 3)), zorder=4)
    ax.annotate(f"MC = {money(PER_CAR)}", xy=(0.6, PER_CAR),
                xytext=(0, -10), textcoords="offset points", ha="left",
                va="top", fontsize=fs, color=MARGINAL, fontweight="bold",
                zorder=8)


def point(ax, q, p, label, dx, dy, ha, va):
    ax.plot(q, p, marker="o", ms=13, color=INK, zorder=9)
    ax.annotate(label, xy=(q, p), xytext=(dx, dy), textcoords="offset points",
                ha=ha, va=va, fontsize=FONT, color=INK, fontweight="bold",
                zorder=10)


def draw_wtp(out: Path) -> None:
    """Demand as willingness to pay, one series, so the accent colour."""
    fig, ax = axes()
    ax.set_xticks([0, 5, 10, 15, 20, 30, 40, 50])
    ax.set_yticks([0, 10_000, 20_000, 30_000, 35_000, 45_000, 50_000])
    q = np.array([0, Q_MAX])
    ax.plot(q, price(q), color=ACCENT, lw=3, solid_capstyle="round", zorder=5)
    ax.set_ylabel("Willingness to pay", fontsize=FONT, labelpad=8)
    # One colour per buyer, dark enough for 4.5:1 text on white; the labels
    # name each buyer, so the colours only help tell the guides apart.
    for k, col in zip(SLIDE_BUYERS, BUYER_COLOURS):
        ax.plot([k, k], [0, wtp(k)], color=col, lw=2.2, ls=(0, (2, 2)), zorder=6)
        ax.plot([0, k], [wtp(k), wtp(k)], color=col, lw=2.2, ls=(0, (2, 2)), zorder=6)
        ax.plot(k, wtp(k), marker="o", ms=13, color=col, zorder=9)
        ax.annotate(f"{k}th buyer: {money(wtp(k))}", xy=(k, wtp(k)),
                    xytext=(12, 6), textcoords="offset points", ha="left",
                    va="bottom", fontsize=FONT - 2, color=col,
                    fontweight="bold", zorder=10)
    # E, the firm's choice from MR = MC: long dashes in ink, heavier than
    # the buyers' dotted guides, so it reads as a different kind of point.
    for xs, ys in (([0, Q_STAR], [P_STAR, P_STAR]), ([Q_STAR, Q_STAR], [0, P_STAR])):
        ax.plot(xs, ys, color=INK, lw=2.6, ls=(0, (6, 3)), zorder=6)
    ax.plot(Q_STAR, P_STAR, marker="o", ms=15, mfc="white", mec=INK, mew=3,
            zorder=9)
    ax.annotate("E (MR = MC)", xy=(Q_STAR, P_STAR), xytext=(14, 4),
                textcoords="offset points", ha="left", va="bottom",
                fontsize=FONT - 2, color=INK, fontweight="bold", zorder=10)
    ax.annotate("Demand", xy=(38, price(38)), xytext=(10, 8),
                textcoords="offset points", ha="left", va="bottom",
                fontsize=FONT, color=ACCENT, fontweight="bold", zorder=8)
    save(fig, out)


def draw_best(out: Path) -> None:
    """Demand, marginal revenue, and marginal cost, with E and E-prime."""
    fig, ax = axes()
    demand_and_mc(ax)
    q = np.array([0, 25])
    ax.plot(q, marginal_revenue(q), color=ACCENT, lw=3,
            solid_capstyle="round", zorder=5)
    ax.annotate("MR", xy=(23, marginal_revenue(23)), xytext=(12, 0),
                textcoords="offset points", ha="left", va="center",
                fontsize=FONT, color=ACCENT, fontweight="bold", zorder=8)
    ax.plot([Q_STAR, Q_STAR], [0, P_STAR], color=GUIDE, lw=1.6,
            ls=(0, (4, 3)), zorder=4)
    ax.plot([0, Q_STAR], [P_STAR, P_STAR], color=GUIDE, lw=1.6,
            ls=(0, (4, 3)), zorder=4)
    point(ax, Q_STAR, P_STAR, f"E: {money(P_STAR)}", 14, 8, "left", "bottom")
    point(ax, Q_STAR, PER_CAR, "E′", 12, 8, "left", "bottom")
    save(fig, out)


def draw_strips(out: Path, kind: str) -> None:
    """Consumer or producer surplus as a sum of one-car gains.

    Light lines every half car fill the area, so the shape reads as the sum
    of the gains; on the consumer side the 5th, 10th, and 15th buyers are
    drawn darker and labelled. Demand and
    MC are both drawn, and the price line runs out to Q*.
    """
    fig, ax = axes()
    light, dark = (CS_FILL, DEMAND) if kind == "cs" else (PS_FILL, ACCENT)
    for x in np.arange(0.5, Q_STAR + 0.01, 0.5):
        lo, hi = (P_STAR, price(x)) if kind == "cs" else (PER_CAR, P_STAR)
        ax.plot([x, x], [lo, hi], color=light, lw=2.2, zorder=2,
                solid_capstyle="butt")
    for k in ((5, 10, 15) if kind == "cs" else ()):
        lo, hi = P_STAR, wtp(k)
        ax.plot([k, k], [lo, hi], color=dark, lw=3.4, zorder=6,
                solid_capstyle="butt")
        if kind == "cs":
            ax.annotate(f"{k}th: {money(hi - lo)}", xy=(k, hi), xytext=(8, 4),
                        textcoords="offset points", ha="left", va="bottom",
                        fontsize=FONT - 4, color=dark, fontweight="bold",
                        zorder=10)
    ax.plot([0, Q_STAR], [P_STAR, P_STAR], color=INK, lw=1.6, zorder=4)
    ax.plot([Q_STAR, Q_STAR], [0, P_STAR], color=GUIDE, lw=1.6,
            ls=(0, (4, 3)), zorder=4)
    demand_and_mc(ax)
    point(ax, Q_STAR, P_STAR, "E", 12, 6, "left", "bottom")
    save(fig, out)


def draw_left_out(out: Path) -> None:
    """The 30th buyer, priced out, and the deal that helps both sides."""
    fig, ax = axes()
    ax.set_yticks([0, 10_000, 15_000, 20_000, 30_000, 40_000, 50_000])
    ax.set_xticks([0, 10, 20, 30, 40, 50])
    ax.plot([0, Q_STAR], [P_STAR, P_STAR], color=INK, lw=1.6, zorder=4)
    ax.plot([Q_STAR, Q_STAR], [0, P_STAR], color=GUIDE, lw=1.6, ls=(0, (4, 3)), zorder=4)
    demand_and_mc(ax, label_at=40)
    k, w = SLIDE_LEFT_OUT, wtp(SLIDE_LEFT_OUT)
    # The gap between MC and WTP, split at the deal price: the firm's part in
    # the producer-surplus orange, the buyer's in the consumer-surplus blue.
    ax.plot([k, k], [PER_CAR, SLIDE_DEAL], color=ACCENT, lw=7, zorder=6,
            solid_capstyle="butt")
    ax.plot([k, k], [SLIDE_DEAL, w], color=DEMAND, lw=7, zorder=6,
            solid_capstyle="butt")
    ax.plot([0, k], [SLIDE_DEAL, SLIDE_DEAL], color=GUIDE, lw=1.4,
            ls=(0, (2, 2)), zorder=4)
    ax.plot([0, k], [w, w], color=GUIDE, lw=1.4, ls=(0, (2, 2)), zorder=4)
    ax.plot(k, w, marker="o", ms=12, color=INK, zorder=9)
    ax.annotate(f"{k}th buyer: {money(w)}", xy=(k, w), xytext=(10, 6),
                textcoords="offset points", ha="left", va="bottom",
                fontsize=FONT - 4, color=INK, fontweight="bold", zorder=10)
    ax.annotate(f"Buyer gains {money(w - SLIDE_DEAL)}", xy=(k, (w + SLIDE_DEAL) / 2),
                xytext=(-12, 0), textcoords="offset points", ha="right", va="center",
                fontsize=FONT - 4, color=DEMAND, fontweight="bold", zorder=10)
    ax.annotate(f"Firm gains {money(SLIDE_DEAL - PER_CAR)}", xy=(k, (SLIDE_DEAL + PER_CAR) / 2),
                xytext=(-12, 0), textcoords="offset points", ha="right", va="center",
                fontsize=FONT - 4, color="#8f4100", fontweight="bold", zorder=10)
    point(ax, Q_STAR, P_STAR, "E", 12, 6, "left", "bottom")
    save(fig, out)


def draw_gift_receipt(out: Path) -> None:
    """A gift receipt whose last line is the deadweight loss."""
    price_paid, cents = 50.00, 0.63
    value = round(price_paid * cents, 2)
    loss = round(price_paid - value, 2)
    fig = plt.figure(figsize=(4.6, 6.0), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 13)
    ax.axis("off")
    # Paper with a torn (zigzag) bottom edge.
    zig_x = np.linspace(0.6, 9.4, 23)
    zig_y = np.where(np.arange(23) % 2 == 0, 0.9, 0.5)
    xs = np.concatenate([[0.6, 0.6], zig_x, [9.4, 9.4]])
    ys = np.concatenate([[12.6, 0.9], zig_y, [0.9, 12.6]])
    ax.fill(xs, ys, color="#fbfaf6", zorder=1)
    ax.plot(np.append(xs, xs[0]), np.append(ys, ys[0]), color=GUIDE, lw=1.4, zorder=2)
    mono = {"family": "DejaVu Sans Mono", "color": INK}
    ax.text(5, 11.7, "GIFT RECEIPT", ha="center", va="center", fontsize=21,
            fontweight="bold", **mono)
    ax.text(5, 10.8, "From: Grandma", ha="center", va="center", fontsize=15, **mono)
    rule = "-" * 26
    ax.text(5, 10.0, rule, ha="center", va="center", fontsize=14, **mono)
    rows = [("1 ugly sweater", ""), ("Price paid", f"${price_paid:.2f}"),
            ("Value to you", f"${value:.2f}")]
    y = 9.0
    for left, right in rows:
        ax.text(1.2, y, left, ha="left", va="center", fontsize=15, **mono)
        ax.text(8.8, y, right, ha="right", va="center", fontsize=15, **mono)
        y -= 1.1
    ax.text(5, y + 0.2, rule, ha="center", va="center", fontsize=14, **mono)
    y -= 0.8
    ax.text(1.2, y, "Deadweight", ha="left", va="center", fontsize=16,
            fontweight="bold", family="DejaVu Sans Mono", color="#8f4100")
    ax.text(1.2, y - 0.8, "loss", ha="left", va="center", fontsize=16,
            fontweight="bold", family="DejaVu Sans Mono", color="#8f4100")
    ax.text(8.8, y - 0.8, f"${loss:.2f}", ha="right", va="center", fontsize=16,
            fontweight="bold", family="DejaVu Sans Mono", color="#8f4100")
    ax.text(5, 2.2, "No returns. No exchanges.", ha="center", va="center",
            fontsize=12, **mono)
    ax.text(5, 1.5, "Thank you for your love.", ha="center", va="center",
            fontsize=12, **mono)
    save(fig, out)
    print(f"  gift receipt: price {money(price_paid)}, value {value:.2f}, loss {loss:.2f}")


def draw_surplus(out: Path, with_dwl: bool) -> None:
    """CS triangle and PS rectangle at E, and the DWL triangle if asked."""
    fig, ax = axes()
    ax.fill([0, 0, Q_STAR], [INTERCEPT, P_STAR, P_STAR], color=CS_AREA,
            lw=0, zorder=2)
    ax.fill([0, 0, Q_STAR, Q_STAR], [P_STAR, PER_CAR, PER_CAR, P_STAR],
            color=PS_AREA, lw=0, zorder=2)
    ax.plot([0, Q_STAR], [P_STAR, P_STAR], color=INK, lw=1.6, zorder=4)
    ax.plot([Q_STAR, Q_STAR], [0, P_STAR], color=GUIDE, lw=1.6,
            ls=(0, (4, 3)), zorder=4)
    demand_and_mc(ax, label_at=8 if with_dwl else 32)
    ax.text(6.5, 36_800, f"CS\n{money(CS)}", ha="center", va="center",
            fontsize=FONT - 4, color=INK, fontweight="bold", zorder=8,
            linespacing=1.05)
    ax.text(10, 20_000, f"PS\n{money(PS)}", ha="center", va="center",
            fontsize=FONT - 2, color=INK, fontweight="bold", zorder=8,
            linespacing=1.1)
    if with_dwl:
        # One light line per half car from MC up to demand, as on the CS and
        # PS slides: each is the WTP - MC lost on a sale that does not happen.
        for x in np.arange(Q_STAR + 0.5, Q_EFF, 0.5):
            ax.plot([x, x], [PER_CAR, price(x)], color="#b8b8b8", lw=2.2,
                    zorder=2, solid_capstyle="butt")
        # The 30th buyer's lost sale, drawn darker and labelled, as the CS
        # slide does for the 5th, 10th, and 15th buyers.
        k = SLIDE_LEFT_OUT
        ax.plot([k, k], [PER_CAR, wtp(k)], color=MARGINAL, lw=3.4, zorder=6,
                solid_capstyle="butt")
        ax.annotate(f"{k}th: {money(wtp(k) - PER_CAR)} lost", xy=(k, wtp(k)),
                    xytext=(8, 4), textcoords="offset points", ha="left",
                    va="bottom", fontsize=FONT - 4, color=MARGINAL,
                    fontweight="bold", zorder=10)
        ax.plot([Q_EFF, Q_EFF], [0, PER_CAR], color=GUIDE, lw=1.6,
                ls=(0, (4, 3)), zorder=4)
        point(ax, Q_EFF, PER_CAR, "F", 0, 12, "center", "bottom")
    point(ax, Q_STAR, P_STAR, "E", 12, 6, "left", "bottom")
    save(fig, out)


def draw_worksheet_scooters(out: Path) -> None:
    """The worksheet example: demand, MC, and E, gridlines at every number."""
    fs = FONT - 4
    sp = lambda q: SC_INTERCEPT - SC_SLOPE * q
    p_star = sp(SC_Q)
    fig, ax = plt.subplots(figsize=(8.2, 4.6), dpi=100)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_xlim(0, 50)
    ax.set_ylim(0, 1_240)
    ax.set_xticks(range(0, 51, 10))
    ax.set_xticks(range(0, 51, 5), minor=True)
    ax.set_yticks(range(0, 1_201, 200))
    ax.set_yticks(range(0, 1_201, 100), minor=True)
    ax.grid(which="major", color=GRID, lw=1, zorder=0)
    ax.grid(which="minor", color="#ececec", lw=0.7, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(length=5, width=1, labelsize=fs)
    ax.tick_params(which="minor", length=0)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: money(y)))
    ax.set_xlabel("Scooters per day, Q", fontsize=fs, labelpad=6)
    ax.set_ylabel("Price and cost", fontsize=fs, labelpad=6)
    fig.subplots_adjust(left=0.16, right=0.97, top=0.97, bottom=0.16)
    q = np.array([0, 50])
    ax.plot(q, sp(q), color=DEMAND, lw=2.6, zorder=5)
    ax.annotate("Demand", xy=(32, sp(32)), xytext=(10, 8),
                textcoords="offset points", ha="left", va="bottom",
                fontsize=fs, color=DEMAND, fontweight="bold", zorder=8)
    ax.axhline(SC_MC, color=MARGINAL, lw=2.2, ls=(0, (5, 3)), zorder=4)
    ax.annotate(f"MC = {money(SC_MC)}", xy=(0.5, SC_MC), xytext=(0, -8),
                textcoords="offset points", ha="left", va="top",
                fontsize=fs, color=MARGINAL, fontweight="bold", zorder=8)
    ax.plot([0, SC_Q], [p_star, p_star], color=GUIDE, lw=1.6, ls=(0, (4, 3)), zorder=4)
    ax.plot([SC_Q, SC_Q], [0, p_star], color=GUIDE, lw=1.6, ls=(0, (4, 3)), zorder=4)
    ax.plot(SC_Q, p_star, marker="o", ms=11, color=INK, zorder=9)
    ax.annotate("E", xy=(SC_Q, p_star), xytext=(10, 6), textcoords="offset points",
                ha="left", va="bottom", fontsize=fs, color=INK,
                fontweight="bold", zorder=10)
    save(fig, out, fmt="pdf")


# -------------------------------------------------------------- main ------

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.parse_args()

    draw_best(IMG / "cars-best.svg")
    draw_wtp(IMG / "cars-wtp.svg")
    draw_strips(IMG / "cars-cs.svg", "cs")
    draw_strips(IMG / "cars-ps.svg", "ps")
    draw_surplus(IMG / "cars-surplus.svg", with_dwl=False)
    draw_left_out(IMG / "cars-leftout.svg")
    draw_surplus(IMG / "cars-dwl.svg", with_dwl=True)
    draw_gift_receipt(IMG / "gift-receipt.svg")
    draw_worksheet_scooters(WS / "scooters.pdf")

    print("\nvalues used in slide and worksheet text")
    print(f"  C(Q) = {FIXED:,} + {PER_CAR:,} Q      P = {INTERCEPT:,} - {SLOPE:,} Q")
    print(f"  E: Q* = {Q_STAR}, P* = {money(P_STAR)}, MR at Q* = {money(marginal_revenue(Q_STAR))}")
    print(f"    the 20th car adds {money(revenue(20) - revenue(19))},"
          f" the 21st adds {money(revenue(21) - revenue(20))}")
    print(f"    R = {money(revenue(Q_STAR))}, C = {money(total_cost(Q_STAR))},"
          f" profit = {money(profit(Q_STAR))}, AC = {money(average_cost(Q_STAR))}")
    print("  one buyer at a time (WTP, joint WTP - MC, buyer WTP - P, firm P - MC):")
    for k in SLIDE_BUYERS:
        w = wtp(k)
        print(f"    buyer {k}: WTP {money(w)}, joint {money(w - PER_CAR)},"
              f" buyer {money(w - P_STAR)}, firm {money(P_STAR - PER_CAR)}")
    for k, deal in ((SLIDE_LEFT_OUT, SLIDE_DEAL),):
        w = wtp(k)
        print(f"    buyer {k}: WTP {money(w)}, joint {money(w - PER_CAR)}, priced out at {money(P_STAR)};"
              f" at {money(deal)}: buyer {money(w - deal)}, firm {money(deal - PER_CAR)}")
    k = SLIDE_LEFT_OUT
    print(f"  single price to reach buyer {k}: P = {money(price(k))} for all {k},"
          f" profit = {k} x ({price(k):,} - {PER_CAR:,}) - {FIXED:,} = {money(profit(k))}"
          f" vs {money(profit(Q_STAR))} at Q*")
    print(f"  CS = 1/2 x {Q_STAR} x ({INTERCEPT:,} - {P_STAR:,}) = {money(CS)}")
    print(f"  PS = ({P_STAR:,} - {PER_CAR:,}) x {Q_STAR} = {money(PS)}")
    print(f"  profit = PS - fixed = {money(PS)} - {money(FIXED)} = {money(PS - FIXED)}"
          f" = (P - AC) Q = ({P_STAR:,} - {average_cost(Q_STAR):,.0f}) x {Q_STAR}"
          f" = {money((P_STAR - average_cost(Q_STAR)) * Q_STAR)}")
    print(f"  efficient Q where P = MC: {Q_EFF}")
    print(f"  DWL = 1/2 x ({Q_EFF} - {Q_STAR}) x ({P_STAR:,} - {PER_CAR:,}) = {money(DWL)}")
    print(f"  max total surplus = 1/2 x {Q_EFF} x ({INTERCEPT:,} - {PER_CAR:,}) = {money(TS_MAX)};"
          f" at E: {money(CS + PS)}")
    assert CS + PS + DWL == TS_MAX and marginal_revenue(Q_STAR) == PER_CAR
    assert price(Q_EFF) == PER_CAR

    # Worksheet: the scooter maker, every answer a gridline reading.
    sp = lambda q: SC_INTERCEPT - SC_SLOPE * q
    assert SC_INTERCEPT - 2 * SC_SLOPE * SC_Q == SC_MC and sp(SC_QEFF) == SC_MC
    ps_ = sp(SC_Q)
    w = sp(SC_BUYER)
    print("\nworksheet, scooters: P = 1,200 - 20 Q, MC = 400")
    print(f"  E: Q* = {SC_Q}, P* = {money(ps_)}; buyer {SC_BUYER}: WTP {money(w)},"
          f" buyer gains {money(w - ps_)}, firm gains {money(ps_ - SC_MC)},"
          f" joint {money(w - SC_MC)}")
    print(f"  CS = 1/2 x {SC_Q} x {SC_INTERCEPT - ps_} = {money(SC_Q * (SC_INTERCEPT - ps_) // 2)},"
          f" PS = {ps_ - SC_MC} x {SC_Q} = {money((ps_ - SC_MC) * SC_Q)},"
          f" DWL = 1/2 x {SC_QEFF - SC_Q} x {ps_ - SC_MC} = {money((SC_QEFF - SC_Q) * (ps_ - SC_MC) // 2)}")

    # Practice page, problem 1: Sierra Bikes, continued from practice 9.
    sp = lambda q: 1_200 - 10 * q
    s_mc, s_f, sq, seff = 200, 2_000, 50, 100
    assert 1_200 - 20 * sq == s_mc and sp(seff) == s_mc
    s_cs, s_ps = sq * (1_200 - sp(sq)) // 2, (sp(sq) - s_mc) * sq
    s_dwl = (seff - sq) * (sp(sq) - s_mc) // 2
    print("\npractice page, Sierra Bikes: P = 1,200 - 10 Q, C(Q) = 2,000 + 200 Q")
    print(f"  Q* = {sq}, P* = {money(sp(sq))}; CS = {money(s_cs)}, PS = {money(s_ps)},"
          f" profit = {money(s_ps - s_f)}; efficient Q = {seff}, DWL = {money(s_dwl)},"
          f" max TS = {money(seff * (1_200 - s_mc) // 2)}")
    for k in (10, 30, 70):
        w = sp(k)
        print(f"  buyer {k}: WTP {money(w)}, joint {money(w - s_mc)},"
              f" buyer {money(w - sp(sq))}, firm {money(sp(sq) - s_mc)}")

    print(f"  rent rises to 3,000: PS still {money(s_ps)}, profit {money(s_ps - 3_000)}")
    w70, deal70 = sp(70), 350
    print(f"  buyer 70 at {money(deal70)}: buyer gains {money(w70 - deal70)},"
          f" firm gains {money(deal70 - s_mc)}")

    # Practice page, multiple choice.
    print("\npractice MCQs")
    print(f"  WTP 120, P 80, MC 50: buyer {120 - 80}, firm {80 - 50}, joint {120 - 50}")
    print(f"  PS 5,000 - fixed 1,500 = profit {5_000 - 1_500:,}")
    for pr in (700, 650):
        print(f"  WTP 1,100, MC 200, P {pr}: buyer {1_100 - pr}, firm {pr - 200}, joint {1_100 - 200}")
    dq, dmc, dqs = 100, 20, 40            # P = 100 - Q, MC = 20, sells 40 at 60
    assert 100 - 2 * dqs == dmc
    dps = 100 - dqs
    print(f"  P = 100 - Q, MC = 20: Q* = {dqs}, P* = {dps}, CS = {dqs * (100 - dps) // 2},"
          f" PS = {(dps - dmc) * dqs}, efficient Q = {100 - dmc},"
          f" DWL = {(100 - dmc - dqs) * (dps - dmc) // 2}")

    # Practice page, problem 2: Nadia's mugs, one shopper per row.
    wtps, mc = (30, 26, 22, 18, 14, 10), 12
    print("\npractice page, Nadia's mugs: MC = 12, WTP", wtps)
    for pr in wtps:
        sold = [w for w in wtps if w >= pr]
        ps, cs = (pr - mc) * len(sold), sum(w - pr for w in sold)
        print(f"  P = {pr}: sells {len(sold)}, PS = {ps}, CS = {cs}, total = {ps + cs}")
    eff = [w - mc for w in wtps if w > mc]
    print(f"  worth making: {len(eff)} mugs, max total surplus = {sum(eff)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
