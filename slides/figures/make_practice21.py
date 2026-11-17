"""Figures and numbers for practice 21 (CORE 10.1 to 10.3): trawlers and the sea floor.

Run from the econ201 root:  python3 slides/figures/make_practice21.py

Problems 1 and 2 follow a small fleet of trawl boats at a California port and
a conservation group that values the sea floor the nets damage. The story is
hypothetical, in the spirit of a real 2006 buyout in Morro Bay, California,
where a conservation group bought trawl permits and boats from fishermen. The
fleet sells its catch at a dock price of $600 a ton. Its marginal private
cost rises in a straight line from $200 to $600 at 200 tons a year. Each
extra ton trawled damages more sea floor than the last, so the marginal
social cost starts at the same $200 and rises twice as fast, to $600 at 100
tons and $1,000 at 200. The fleet catches 200 tons (P = MPC, point A); the
Pareto-efficient catch is 100 tons (P = MSC, point B).

Every number the practice page quotes is computed and printed here.

  trawl-grid.svg        MPC, MSC and the price line on a plotting grid
  trawl-external.svg    the total external cost at A, shaded
  trawl-permits.svg     the fleet holds trawl permits: lost profit, net social
                        gain and the group's gain, A to B

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
EXT_AREA = "#cdeee3"        # the group's habitat cost
PROFIT_AREA = "#fae2cc"     # the fleet's lost profit
GAIN_AREA = "#d2e7f5"       # net social gain
SIZE = (8.8, 6.0)           # the same as the other practice pages' figures
FONT = 20                   # shown at 600px: ticks 12pt, labels 14pt
DASH = (0, (4, 3))

plt.rcParams.update({
    "font.family": ["Lato", "Fira Sans", "sans-serif"], "font.size": FONT,
    "svg.fonttype": "path", "pdf.fonttype": 42, "axes.edgecolor": RULE,
    "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
})

P = 600                     # the dock price of a ton of fish
Q_A, Q_B = 200, 100         # the fleet's catch and the Pareto-efficient catch
X_MAX, Y_MAX = 300, 1200    # last ticks; the axes run a little past them
X_END, Y_END = 315, 1260


def mpc(q):
    return 200 + 2 * F(q)


def msc(q):
    return 200 + 4 * F(q)


def mec(q):
    return msc(q) - mpc(q)


def triangle(base, height):
    return F(base) * F(height) / 2


EXTERNAL_AT_A = triangle(Q_A, mec(Q_A))                  # the MEC of every ton up to A
LOST_PROFIT = triangle(Q_A - Q_B, P - mpc(Q_B))          # P - MPC on each ton from B to A
GAIN_PERMITS = triangle(Q_A - Q_B, msc(Q_A) - P)         # net social gain, A to B
GROUP_GAIN = LOST_PROFIT + GAIN_PERMITS                  # the MEC of each ton from B to A


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
    ax.set_xticks(range(0, X_MAX + 1, 50))
    ax.set_yticks(range(0, Y_MAX + 1, 200))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"${y:,.0f}"))
    ax.grid(color=PLOT_GRID, lw=1, zorder=0)
    ax.set_axisbelow("line")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(length=0, labelsize=FONT - 3)
    ax.set_xlabel("Q (tons of fish a year)", fontsize=FONT, labelpad=6)
    ax.set_ylabel("Dollars a ton", fontsize=FONT, labelpad=6)
    fig.subplots_adjust(left=0.15, right=0.97, top=0.97, bottom=0.15)
    return fig, ax


def tag(ax, x, y, text, color=INK, ha="left", va="center", font=FONT):
    ax.text(x, y, text, color=color, fontsize=font, fontweight="bold", ha=ha, va=va, zorder=8)


def curves(ax):
    q_top = (Y_END - 200) / F(4)                           # MSC leaves through the top of the plot
    ax.plot([0, X_END], [float(mpc(0)), float(mpc(X_END))], color=PRIVATE, lw=3,
            solid_capstyle="round", zorder=5)
    ax.plot([0, float(q_top)], [float(msc(0)), float(msc(q_top))], color=SOCIAL, lw=3,
            solid_capstyle="round", zorder=5)
    ax.plot([0, X_END], [P, P], color=INK, lw=2, zorder=4)
    tag(ax, 285, float(mpc(285)) + 88, "MPC", PRIVATE, ha="center")       # clear of the price line
    tag(ax, 248, 1100, "MSC", SOCIAL, ha="left")                          # beside the line, inside the plot


def guide(ax, q, p):
    ax.plot([q, q], [0, float(p)], color=INK, lw=1.6, ls=DASH, zorder=4)


def point(ax, q, p, name, dx, dy):
    ax.plot(q, float(p), marker="o", ms=8, color=INK, zorder=9, clip_on=False)
    tag(ax, q + dx, float(p) + dy, name)


def pointer(ax, text, at, frm, ha="left"):
    """A label set in open space, with a thin arrow to the area it names."""
    ax.annotate(text, xy=at, xytext=frm, fontsize=FONT - 2, fontweight="bold", color=INK, ha=ha,
                va="center", linespacing=1.15, zorder=9,
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4, shrinkA=2, shrinkB=0, mutation_scale=14))


def both(ax, text, at, *targets):
    """One label with an arrow to each of the two areas that together make it up."""
    for target in targets:
        ax.annotate("", xy=target, xytext=(at[0], at[1] - 52), zorder=9,
                    arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4, shrinkA=0, shrinkB=0, mutation_scale=14))
    ax.text(at[0], at[1], text, fontsize=FONT - 2, fontweight="bold", color=INK, ha="center", va="center",
            zorder=9)


def fig_grid(out: Path) -> None:
    fig, ax = axes()
    curves(ax)
    tag(ax, 10, P + 52, "Price")
    save(fig, out)


def fig_external(out: Path) -> None:
    """The total external cost at A: the MEC of every ton, the area between MSC and MPC."""
    fig, ax = axes()
    ax.fill([0, Q_A, Q_A], [float(mpc(0)), float(mpc(Q_A)), float(msc(Q_A))], color=EXT_AREA, lw=0, zorder=1)
    curves(ax)
    tag(ax, 10, P + 52, "Price")
    guide(ax, Q_A, msc(Q_A))
    point(ax, Q_A, P, "A", 6, -60)
    pointer(ax, "Total external cost", (150, 640), (30, 1000))
    save(fig, out)


def fig_permits(out: Path) -> None:
    """The fleet holds permits: from A to B it loses profit, and the group gains both areas."""
    fig, ax = axes()
    ax.fill([Q_B, Q_A, Q_B], [P, P, float(mpc(Q_B))], color=PROFIT_AREA, lw=0, zorder=1)
    ax.fill([Q_B, Q_A, Q_A], [P, float(msc(Q_A)), P], color=GAIN_AREA, lw=0, zorder=1)
    curves(ax)
    tag(ax, 10, P + 52, "Price")
    guide(ax, Q_A, msc(Q_A))
    guide(ax, Q_B, P)
    point(ax, Q_A, P, "A", 6, -60)
    point(ax, Q_B, P, "B", -15, 60)
    both(ax, "Group’s gain", (72, 1060), (160, 760), (120, 552))
    pointer(ax, "Net social\ngain", (184, 800), (210, 890))
    pointer(ax, "Lost profit", (132, 524), (116, 240))
    save(fig, out)


def main() -> int:
    print("Q      MPC    MSC    MEC")
    for q in (0, Q_B, Q_A, 250):
        print(f"{q:>3}   {float(mpc(q)):>5.0f}  {float(msc(q)):>5.0f}  {float(mec(q)):>5.0f}")
    assert (mpc(0), mpc(Q_B), mpc(Q_A)) == (200, 400, 600)
    assert (msc(0), msc(Q_B), msc(Q_A)) == (200, 600, 1000)
    assert (mec(0), mec(Q_B), mec(Q_A)) == (0, 200, 400)
    assert mpc(Q_A) == P and msc(Q_B) == P                 # A: P = MPC; B: P = MSC
    print(f"A: {Q_A} tons where P = MPC; B: {Q_B} tons where P = MSC")
    print(f"MEC at A: {mec(Q_A)}, at B: {mec(Q_B)}; total external cost at A: {EXTERNAL_AT_A}")
    assert EXTERNAL_AT_A == 40000
    # one ton less at A: the cost saved is the area under MPC from 199 to 200
    saved = (mpc(Q_A - 1) + mpc(Q_A)) / 2
    print(f"one ton less at A: revenue down {P}, cost down {float(saved)}, profit down {float(P - saved)}")
    assert 0 < P - saved < 2
    print("the fleet holds trawl permits, A to B:")
    print(f"  lost profit {LOST_PROFIT}, group's gain {GROUP_GAIN}, net social gain {GAIN_PERMITS}")
    assert (LOST_PROFIT, GROUP_GAIN, GAIN_PERMITS) == (10000, 30000, 20000)
    # the group's gain as a trapezoid between MSC and MPC from B to A
    assert GROUP_GAIN == (mec(Q_B) + mec(Q_A)) / 2 * (Q_A - Q_B)
    # every value read off the graph sits on a labelled tick
    for q in (0, Q_B, Q_A):
        assert q % 50 == 0 and mpc(q) % 200 == 0 and msc(q) % 200 == 0
    fig_grid(IMG / "trawl-grid.svg")
    fig_external(IMG / "trawl-external.svg")
    fig_permits(IMG / "trawl-permits.svg")
    return 0


if __name__ == "__main__":
    sys.exit(main())
