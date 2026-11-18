"""Figures and numbers for practice 22 (CORE 10.4 to 10.5): an airport and its neighbors.

Run from the econ201 root:  python3 slides/figures/make_practice22.py

Problem 1 follows a hypothetical airport and the neighborhood under its flight
path, in the spirit of John Wayne Airport in Orange County, where a 1985
settlement with Newport Beach residents set a night curfew and a cap on
passengers. The airport earns $800 in fees from each flight. Its marginal
private cost rises in a straight line from $400 to $800 at 400 flights a day.
Each extra flight costs the neighbors more in noise than the last, so the
marginal social cost starts at the same $400 and rises twice as fast, to $800
at 200 flights and $1,200 at 400. The airport runs 400 flights (P = MPC,
point A); the Pareto-efficient number is 200 (P = MSC, point B).

Every number the practice page quotes is computed and printed here.

  airport-grid.svg          MPC, MSC and the price line on a plotting grid
  airport-cap.svg           a cap at B and the airport's lost profit
  airport-tax.svg           the Pigouvian tax and the after-tax price
  airport-compensation.svg  total compensation at B, shaded

With FIG_PREVIEW_DIR set, a PNG of each figure is also written there.
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
SCRATCH = Path(os.environ["FIG_PREVIEW_DIR"]) if os.environ.get("FIG_PREVIEW_DIR") else None

INK = "#1a1a1a"
PLOT_GRID = "#c6c6c6"       # light enough that the lines and shaded areas stand out
RULE = "#595a5b"
PRIVATE = "#8f4100"         # MPC
SOCIAL = "#0072B2"          # MSC
POLICY = "#007a59"          # the cap and the tax, green at 4.5:1 on white
EXT_AREA = "#cdeee3"        # the neighbors' noise cost
PROFIT_AREA = "#fae2cc"     # the airport's lost profit
SIZE = (8.8, 6.0)           # the same as the other practice pages' figures
FONT = 20                   # shown at 600px: ticks 12pt, labels 14pt
DASH = (0, (4, 3))

plt.rcParams.update({
    "font.family": ["Lato", "Fira Sans", "sans-serif"], "font.size": FONT,
    "svg.fonttype": "path", "pdf.fonttype": 42, "axes.edgecolor": RULE,
    "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
})

P = 800                     # what the airport earns from a flight
Q_A, Q_B = 400, 200         # the airport's choice and the Pareto-efficient number
X_MAX, Y_MAX = 500, 1400    # last ticks; the axes run a little past them
X_END, Y_END = 525, 1470


def mpc(q):
    return 400 + F(q)


def msc(q):
    return 400 + 2 * F(q)


def mec(q):
    return msc(q) - mpc(q)


def triangle(base, height):
    return F(base) * F(height) / 2


TAX = mec(Q_B)                                           # the Pigouvian tax: the MEC at B
KEEPS = P - TAX                                          # the after-tax price of a flight
LOST_PROFIT = triangle(Q_A - Q_B, P - mpc(Q_B))          # P - MPC on each flight from B to A
REVENUE = TAX * Q_B                                      # the government's revenue from the tax
COMPENSATION = triangle(Q_B, mec(Q_B))                   # the MEC of every flight up to B
NOISE_AT_A = triangle(Q_A, mec(Q_A))                     # the MEC of every flight up to A


def save(fig, out: Path) -> None:
    fig.savefig(out, format="svg")
    if SCRATCH:
        fig.savefig(SCRATCH / f"{out.stem}.png", format="png", dpi=110)
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


def axes():
    fig, ax = plt.subplots(figsize=SIZE, dpi=100)
    ax.set_xlim(0, X_END)
    ax.set_ylim(0, Y_END)
    ax.set_xticks(range(0, X_MAX + 1, 100))
    ax.set_yticks(range(0, Y_MAX + 1, 200))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"${y:,.0f}"))
    ax.grid(color=PLOT_GRID, lw=1, zorder=0)
    ax.set_axisbelow("line")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(length=0, labelsize=FONT - 3)
    ax.set_xlabel("Q (flights a day)", fontsize=FONT, labelpad=6)
    ax.set_ylabel("Dollars a flight", fontsize=FONT, labelpad=6)
    fig.subplots_adjust(left=0.15, right=0.97, top=0.97, bottom=0.15)
    return fig, ax


def tag(ax, x, y, text, color=INK, ha="left", va="center", font=FONT):
    ax.text(x, y, text, color=color, fontsize=font, fontweight="bold", ha=ha, va=va, zorder=8)


def curves(ax):
    for f, color in ((mpc, PRIVATE), (msc, SOCIAL)):
        ax.plot([0, X_END], [float(f(0)), float(f(X_END))], color=color, lw=3, solid_capstyle="round", zorder=5)
    ax.plot([0, X_END], [P, P], color=INK, lw=2, zorder=4)
    tag(ax, 478, float(mpc(478)) + 78, "MPC", PRIVATE, ha="center")       # clear of the price line
    tag(ax, 408, 1130, "MSC", SOCIAL, ha="left")                          # beside the line, inside the plot
    tag(ax, 12, P + 58, "Price")


def guide(ax, q, p):
    ax.plot([q, q], [0, float(p)], color=INK, lw=1.6, ls=DASH, zorder=4)


def point(ax, q, p, name="", dx=0, dy=0):
    ax.plot(q, float(p), marker="o", ms=8, color=INK, zorder=9, clip_on=False)
    if name:
        tag(ax, q + dx, float(p) + dy, name)


def pointer(ax, text, at, frm, ha="left"):
    """A label set in open space, with a thin arrow to the area it names."""
    ax.annotate(text, xy=at, xytext=frm, fontsize=FONT - 2, fontweight="bold", color=INK, ha=ha,
                va="center", linespacing=1.15, zorder=9,
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4, shrinkA=2, shrinkB=0, mutation_scale=14))


def fig_grid(out: Path) -> None:
    fig, ax = axes()
    curves(ax)
    save(fig, out)


def fig_cap(out: Path) -> None:
    """Regulation: flights capped at B, and the profit the airport loses between B and A."""
    fig, ax = axes()
    ax.fill([Q_B, Q_A, Q_B], [P, P, float(mpc(Q_B))], color=PROFIT_AREA, lw=0, zorder=1)
    curves(ax)
    ax.plot([Q_B, Q_B], [0, 1290], color=POLICY, lw=4, solid_capstyle="butt", zorder=6)
    tag(ax, Q_B, 1345, "Cap", POLICY, ha="center")
    guide(ax, Q_A, P)
    point(ax, Q_A, P, "A", 9, -62)
    point(ax, Q_B, P, "B", -30, 62)
    pointer(ax, "Lost profit", (262, 724), (255, 470))
    save(fig, out)


def fig_tax(out: Path) -> None:
    """The Pigouvian tax: the MEC at B, and the after-tax price of a flight."""
    fig, ax = axes()
    curves(ax)
    ax.plot([0, X_END], [float(KEEPS)] * 2, color=INK, lw=2, ls=DASH, zorder=4)
    tag(ax, X_END - 6, float(KEEPS) - 56, "After-tax price", ha="right", font=FONT - 2)
    guide(ax, Q_B, KEEPS)
    ax.plot([Q_B, Q_B], [float(KEEPS), P], color=POLICY, lw=6, solid_capstyle="butt", zorder=6)
    point(ax, Q_B, P, "B", -30, 62)
    point(ax, Q_B, KEEPS)
    pointer(ax, f"Tax = ${TAX}", (206, 690), (245, 400))
    save(fig, out)


def fig_compensation(out: Path) -> None:
    """Compensation: the MEC of every flight up to B, the area between MSC and MPC."""
    fig, ax = axes()
    ax.fill([0, Q_B, Q_B], [float(mpc(0)), float(mpc(Q_B)), float(msc(Q_B))], color=EXT_AREA, lw=0, zorder=1)
    curves(ax)
    guide(ax, Q_B, P)
    point(ax, Q_B, P, "B", -30, 62)
    point(ax, Q_B, mpc(Q_B))
    pointer(ax, "Total\ncompensation", (140, 592), (40, 300))
    save(fig, out)


def main() -> int:
    print("Q      MPC    MSC    MEC")
    for q in (0, Q_B, Q_A, 500):
        print(f"{q:>3}   {float(mpc(q)):>5.0f}  {float(msc(q)):>5.0f}  {float(mec(q)):>5.0f}")
    assert (mpc(0), mpc(Q_B), mpc(Q_A)) == (400, 600, 800)
    assert (msc(0), msc(Q_B), msc(Q_A)) == (400, 800, 1200)
    assert (mec(0), mec(Q_B), mec(Q_A)) == (0, 200, 400)
    assert mpc(Q_A) == P and msc(Q_B) == P                 # A: P = MPC; B: P = MSC
    print(f"A: {Q_A} flights where P = MPC; B: {Q_B} flights where P = MSC")
    print(f"cap at B: lost profit {LOST_PROFIT}")
    assert LOST_PROFIT == 20000
    print(f"tax {TAX} a flight, after-tax price {KEEPS} = MPC at {Q_B}; revenue {REVENUE}")
    assert (TAX, KEEPS, REVENUE) == (200, 600, 40000)
    assert KEEPS == mpc(Q_B)                               # with the tax, the airport stops at B
    print(f"compensation at B: {COMPENSATION}; noise cost at A: {NOISE_AT_A}")
    assert (COMPENSATION, NOISE_AT_A) == (20000, 80000)
    # what each policy costs the airport, and what noise the neighbors are left with
    print(f"airport worse off: cap {LOST_PROFIT}, tax {LOST_PROFIT + REVENUE}, "
          f"compensation {LOST_PROFIT + COMPENSATION}")
    assert (LOST_PROFIT + REVENUE, LOST_PROFIT + COMPENSATION) == (60000, 40000)
    print(f"neighbors: noise cost falls by {NOISE_AT_A - COMPENSATION}, {COMPENSATION} remains at B")
    assert NOISE_AT_A - COMPENSATION == 60000
    # every value read off the graph sits on a labelled tick
    for q in (0, Q_B, Q_A):
        assert q % 100 == 0 and mpc(q) % 200 == 0 and msc(q) % 200 == 0
    assert KEEPS % 200 == 0
    fig_grid(IMG / "airport-grid.svg")
    fig_cap(IMG / "airport-cap.svg")
    fig_tax(IMG / "airport-tax.svg")
    fig_compensation(IMG / "airport-compensation.svg")
    return 0


if __name__ == "__main__":
    sys.exit(main())
