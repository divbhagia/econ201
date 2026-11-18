"""
Numbers and the figure for Worksheet 22: regulation, a Pigouvian tax, and
compensation (CORE 10.4), with the worksheet's own example.

Run from the course root:

    python3 slides/figures/make_worksheet22.py

A warehouse next to a neighborhood, in truck trips a day and dollars a trip.
The warehouse is paid a fixed $60 for every trip it handles, and each trip's
exhaust and noise fall on the neighbors. Straight lines, so every area is a
triangle or a rectangle:

    price          $60 a trip
    MPC            20 + Q/5
    MEC            Q/5 (the harm grows with every extra trip)
    MSC            20 + 2Q/5
    A              200 trips, where P = MPC
    B              100 trips, where P = MSC; MPC there is $40
    MEC at B       60 - 40 = $20, the Pigouvian tax; after-tax price $40
    cap at B       the warehouse loses 1/2 x 100 x 20 = $1,000 a day
    tax            the same lost profit, plus 20 x 100 = $2,000 a day in tax
    compensation   the same lost profit, plus the harm from the 100 trips
                   still made, 1/2 x 100 x 20 = $1,000 a day
    neighbors      pollution costs fall by (20 + 40)/2 x 100 = $3,000 a day

Every value a student reads sits on a labelled tick: trips every 50, dollars
every 20. Writes worksheets/figures/warehouse-grid.pdf, the unmarked grid
students draw on. With FIG_PREVIEW_DIR set, a PNG is also written there.
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
WS = ROOT / "worksheets" / "figures"
SCRATCH = Path(os.environ["FIG_PREVIEW_DIR"]) if os.environ.get("FIG_PREVIEW_DIR") else None

INK = "#1a1a1a"
GRID = "#c8c8c8"
RULE = "#595a5b"
PRIVATE = "#8f4100"         # MPC, dark orange, 7.7:1 on white
SOCIAL = "#0072B2"          # MSC, Okabe-Ito blue, 5.1:1 on white
SIZE = (8.2, 5.6)           # the same as the other worksheet grids
FONT = 20                   # set at 0.6 of the text width: labels 10pt, ticks 9pt

plt.rcParams.update({
    "font.family": ["Lato", "Fira Sans", "sans-serif"], "font.size": FONT,
    "svg.fonttype": "path", "pdf.fonttype": 42, "axes.edgecolor": RULE,
    "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
})

P = 60                      # what the warehouse is paid for a trip
X_MAX, Y_MAX = 250, 120     # last ticks; the axes run a little past them
X_END, Y_END = 260, 126


def mpc(q):
    return 20 + F(1, 5) * q


def mec(q):
    return F(1, 5) * q


def msc(q):
    return mpc(q) + mec(q)


Q_A = (P - 20) * 5                      # P = MPC
Q_B = F(P - 20, 2) * 5                  # P = MSC
TAX = mec(Q_B)
LOST_PROFIT = F(1, 2) * (Q_A - Q_B) * (P - mpc(Q_B))
TAX_REVENUE = TAX * Q_B
COMPENSATION = F(1, 2) * Q_B * mec(Q_B)
NEIGHBORS_GAIN = (mec(Q_B) + mec(Q_A)) / 2 * (Q_A - Q_B)


def save(fig, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format="pdf")
    if SCRATCH:
        fig.savefig(SCRATCH / f"{out.stem}.png", format="png", dpi=110)
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


def tag(ax, x, y, text, color=INK, ha="center", va="bottom"):
    ax.text(x, y, text, color=color, fontsize=FONT, fontweight="bold", ha=ha, va=va, zorder=8)


def fig_grid(out: Path, solution: bool = False) -> None:
    """The worksheet grid: MPC, MSC and the price, unmarked, big enough to draw on.

    With solution=True, the answers are drawn in: A, B, the MEC at B, and the
    profit the warehouse loses under a cap at B.
    """
    fig, ax = plt.subplots(figsize=SIZE, dpi=100)
    ax.set_xlim(0, X_END)
    ax.set_ylim(0, Y_END)
    ax.set_xticks(range(0, X_MAX + 1, 50))
    ax.set_yticks(range(0, Y_MAX + 1, 20))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"${y:.0f}"))
    ax.grid(color=GRID, lw=1, zorder=0)
    ax.set_axisbelow("line")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(length=4, width=1, labelsize=FONT - 2)
    ax.set_xlabel("Q (truck trips a day)", fontsize=FONT, labelpad=6)
    ax.set_ylabel("Dollars a trip", fontsize=FONT, labelpad=6)
    for f, color in ((mpc, PRIVATE), (msc, SOCIAL)):
        ax.plot([0, X_END], [float(f(0)), float(f(X_END))], color=color, lw=2.6,
                solid_capstyle="round", zorder=5)
    ax.plot([0, X_END], [P, P], color=INK, lw=2, zorder=4)
    tag(ax, 232, float(mpc(232)) + 3, "MPC", PRIVATE)
    tag(ax, 222, float(msc(222)) + 3, "MSC", SOCIAL, ha="right")
    tag(ax, 8, P + 2, "Price", INK, ha="left")
    if solution:
        qa, qb, low = float(Q_A), float(Q_B), float(mpc(Q_B))
        ax.fill([qb, qa, qb], [P, P, low], color="#fae2cc", lw=0, zorder=1)
        for q, name, dx in ((qa, "A", 6), (qb, "B", -6)):
            ax.plot([q, q], [0, P], color=INK, lw=1.6, ls=(0, (4, 3)), zorder=4)
            ax.plot(q, P, marker="o", ms=9, color=INK, zorder=9)
            tag(ax, q + dx, P + 2, name, INK, ha="left" if dx > 0 else "right")
        ax.plot(qb, low, marker="o", ms=7, color=INK, zorder=9)
        ax.annotate("", xy=(qb - 6, P), xytext=(qb - 6, low), zorder=8,
                    arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=1.6, shrinkA=0, shrinkB=0))
        ax.annotate(f"MEC = ${int(TAX)}", xy=(qb - 8, (P + low) / 2 + 4), xytext=(22, 88), fontsize=FONT - 4,
                    fontweight="bold", color=INK, ha="left", va="center", zorder=9,
                    arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4))
        after = float(P - TAX)                  # what the warehouse keeps per trip with the tax
        ax.plot([0, X_END], [after, after], color=INK, lw=2, ls=(0, (4, 3)), zorder=4)
        ax.text(Q_A + 5, after - 2.5, "After-tax price", fontsize=FONT - 4, fontweight="bold",
                color=INK, ha="left", va="top", zorder=9)
        ax.annotate("Lost profit", xy=(128, 52), xytext=(128, 12), fontsize=FONT - 4, fontweight="bold",
                    color=INK, ha="left", va="center", zorder=9,
                    arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4))
    fig.subplots_adjust(left=0.13, right=0.97, top=0.97, bottom=0.15)
    save(fig, out)


def main() -> int:
    print("Q (trips)   MPC    MEC    MSC")
    for q in (0, Q_B, Q_A, X_MAX):
        print(f"  {str(q):>4}      {float(mpc(q)):>4.0f}   {float(mec(q)):>4.0f}   {float(msc(q)):>4.0f}")
    assert (Q_A, Q_B) == (200, 100)
    assert (mpc(0), mpc(Q_B), mpc(Q_A)) == (20, 40, 60)
    assert (msc(0), msc(Q_B), msc(Q_A)) == (20, 60, 100)
    assert TAX == 20 and P - TAX == mpc(Q_B)
    assert (LOST_PROFIT, TAX_REVENUE, COMPENSATION, NEIGHBORS_GAIN) == (1000, 2000, 1000, 3000)
    # every value a student reads is on a labelled tick
    assert all(v % 50 == 0 for v in (Q_A, Q_B))
    assert all(v % 20 == 0 for v in (P, mpc(Q_B), msc(Q_A), mpc(0), P - TAX))
    print(f"A: {Q_A} trips where P = MPC. B: {Q_B} trips where P = MSC.")
    print(f"MEC at B = tax = ${TAX}; after-tax price ${P - TAX} = MPC at B")
    print(f"cap: warehouse loses ${int(LOST_PROFIT):,} a day; neighbors' pollution costs fall ${int(NEIGHBORS_GAIN):,}")
    print(f"tax: the same lost profit, plus ${int(TAX_REVENUE):,} a day in tax")
    print(f"compensation: the same lost profit, plus ${int(COMPENSATION):,} a day paid to the neighbors")
    fig_grid(WS / "warehouse-grid.pdf")
    fig_grid(ROOT / "worksheets" / "solutions" / "warehouse-solution.pdf", solution=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
