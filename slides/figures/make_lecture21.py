"""
Numbers and figures for Lectures 21 and 22: external effects and their
remedies (CORE 10.1 to 10.5).

Run from the course root:

    python3 slides/figures/make_lecture21.py

CORE's banana island with CORE's own numbers and curves (Figures 10.1 to
10.5), redrawn in the course's figure style (Div, lecture 21: "do as CORE").
Q is in thousand tons of bananas a year, costs in dollars a ton:

    world price   P = 400               (growers are price-takers)
    MPC           200 + 2.5 Q           (a straight line: 200 at zero, 400 at 80)
    MEC           a curve through 40 at zero, 105 at 38, and 275 at 80
    MSC           MPC + MEC             (240 at zero, 400 at 38, 675 at 80)
    A             P = MPC at 80,000 tons; MEC 275, MSC 675
    B             P = MSC at 38,000 tons; MPC 295, MEC 105
    tax           105 a ton, the MEC at B; after-tax price 295 = MPC at 38,000

The curves are CORE's, so areas are not triangles and no dollar totals are
quoted for them, as in CORE. Values CORE reads off its figure (38,000, $295,
$105, $275) are marked with guides, not ticks.

Output, in slides/img/:
  banana-market.svg        MPC, the price line, and the growers' choice A
  banana-costs.svg         the setup figure with MSC added, the total external cost
                           shaded, and the MEC at A marked
  banana-one-less.svg      A with the MEC of the last ton marked
  banana-efficient.svg     A and B
  banana-bargain.svg       lost profit, net social gain and the fishermen's gain, A to B
  banana-cap.svg           a cap on output at B and the plantations' lost profit
  banana-tax.svg           the after-tax price and the growers' new choice
  banana-compensation.svg  compensation paid at B
  banana-panels-*.svg      Lecture 22: two panels per policy (cap, tax, compensation),
                           the fishermen's pollution cost and the plantations' profit
  banana-clean-water.svg   the fishermen's right to clean water: pollution cost, net
                           social gain and the plantations' gain, C to B
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
GRID = "#c8c8c8"
RULE = "#595a5b"
PRIVATE = "#8f4100"         # MPC
SOCIAL = "#0072B2"          # MSC
EXTERNAL = "#007a59"        # MEC, Okabe-Ito green darkened to 4.5:1 on white
EXT_AREA = "#cdeee3"        # external cost
PROFIT_AREA = "#fae2cc"     # growers' profit
GAIN_AREA = "#d2e7f5"       # net social gain
SIDE = (8.8, 6.0)
FONT = 26
DASH = (0, (4, 3))

plt.rcParams.update({
    "font.family": ["Lato", "Fira Sans", "sans-serif"], "font.size": FONT,
    "svg.fonttype": "path", "pdf.fonttype": 42, "axes.edgecolor": RULE,
    "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
})

P = 400
Q_A, Q_B = 80, 38           # thousand tons: the growers' choice and the Pareto-efficient output
X_MAX, Y_MAX = 100, 900     # last ticks; the axes run a little past them
X_END = 108                 # where the horizontal axis ends; the lines run out to it

# MEC = E0 + E1 Q + E2 Q^2, through CORE's three readings: 40 at zero, 105 at B, 275 at A.
E0 = F(40)
E2 = ((275 - E0) / Q_A - (105 - E0) / Q_B) / (Q_A - Q_B)
E1 = (105 - E0) / Q_B - E2 * Q_B


def mpc(q):
    return 200 + F(5, 2) * q


def mec(q):
    return E0 + E1 * q + E2 * q * q


def msc(q):
    return mpc(q) + mec(q)


TAX = mec(Q_B)              # 105


def money(x):
    return f"${float(x):,.0f}"


def save(fig, out: Path) -> None:
    fig.savefig(out, format="svg")
    if SCRATCH:
        fig.savefig(SCRATCH / f"{out.stem}.png", format="png", dpi=110)
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


def axes():
    fig, ax = plt.subplots(figsize=SIDE, dpi=100)
    ax.set_xlim(0, X_END)
    ax.set_ylim(0, Y_MAX * 1.05)
    ax.set_xticks(range(0, X_MAX + 1, 20))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x * 1000:,.0f}"))
    ax.set_yticks(range(0, Y_MAX + 1, 100))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: money(y)))
    ax.grid(color=GRID, lw=1, zorder=0)
    ax.set_axisbelow("line")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(length=0, pad=8, labelsize=FONT - 4)
    ax.set_xlabel("Q (tons of bananas a year)", fontsize=FONT - 2, labelpad=8)
    ax.set_ylabel("Dollars a ton", fontsize=FONT - 2, labelpad=8)
    fig.subplots_adjust(left=0.16, right=0.955, top=0.97, bottom=0.16)
    return fig, ax


def label(ax, x, y, text, color, dx, dy, ha="left", va="bottom", fs=FONT):
    ax.annotate(text, xy=(float(x), float(y)), xytext=(dx, dy), textcoords="offset points",
                ha=ha, va=va, fontsize=fs, color=color, fontweight="bold", zorder=8)


def grid_q(q0, q1, n=120):
    return [q0 + (q1 - q0) * F(i, n) for i in range(n + 1)]


def curve(ax, f, color, lw=4):
    qs = grid_q(0, X_END)
    ax.plot([float(q) for q in qs], [float(f(q)) for q in qs], color=color, lw=lw,
            solid_capstyle="round", zorder=5)


def between(ax, lower, upper, q0, q1, color):
    """Shade the area between two cost curves from q0 to q1."""
    qs = grid_q(q0, q1)
    ax.fill_between([float(q) for q in qs], [float(lower(q)) for q in qs], [float(upper(q)) for q in qs],
                    color=color, lw=0, zorder=1)


def price_line(ax, p=P, text="Price", ls="-"):
    """The price line, named above its left end as in CORE's figures."""
    ax.plot([0, X_END], [p, p], color=INK, lw=2.6, ls=ls, zorder=4)
    label(ax, 3, p, text, INK, 0, 6)


def guide(ax, q, p):
    """A dashed drop from a point to the quantity axis."""
    ax.plot([float(q)] * 2, [0, float(p)], color=INK, lw=2.2, ls=DASH, zorder=4)


def point(ax, q, p, text="", dx=0, dy=14, ha="center", va="bottom"):
    ax.plot(float(q), float(p), marker="o", ms=12, color=INK, zorder=9)
    if text:
        label(ax, q, p, text, INK, dx, dy, ha=ha, va=va)


def point_a(ax):
    point(ax, Q_A, P, "A", dx=12, dy=-10, ha="left", va="top")


def point_b(ax):
    point(ax, Q_B, P, "B", dx=-8, dy=12, ha="right")


def pointer(ax, text, at, frm, ha="left"):
    """A label set in open space, with a thin arrow to the area it names."""
    ax.annotate(text, xy=(float(at[0]), float(at[1])), xytext=(float(frm[0]), float(frm[1])),
                fontsize=FONT - 4, fontweight="bold", color=INK, ha=ha, va="center", zorder=9,
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.6, shrinkA=2, shrinkB=0, mutation_scale=16))


def both(ax, text, at, *targets):
    """One label with an arrow to each of the areas that together make it up."""
    for tx, ty in targets:
        ax.annotate("", xy=(float(tx), float(ty)), xytext=(float(at[0]), float(at[1]) - 34), zorder=9,
                    arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.6, shrinkA=0, shrinkB=0, mutation_scale=16))
    ax.text(float(at[0]), float(at[1]), text, fontsize=FONT - 4, fontweight="bold", color=INK,
            ha="center", va="center", zorder=9)


def cost_lines(ax, social=True):
    curve(ax, mpc, PRIVATE)
    label(ax, 95, mpc(95), "MPC", PRIVATE, 0, 8, ha="center")       # clear of the price line
    if social:
        curve(ax, msc, SOCIAL)
        label(ax, 84, msc(84), "MSC", SOCIAL, -12, 6, ha="right")


def fig_market(out: Path) -> None:
    fig, ax = axes()
    cost_lines(ax, social=False)
    price_line(ax)
    guide(ax, Q_A, P)
    point_a(ax)
    save(fig, out)


def mec_arrow(ax):
    """CORE's Figure 10.2 marks the gap between MSC and MPC at A with an arrow and its size."""
    x = Q_A + 1.6
    ax.annotate("", xy=(x, float(msc(Q_A)) - 4), xytext=(x, P + 4), zorder=8,
                arrowprops=dict(arrowstyle="<|-|>", color=EXTERNAL, lw=2.6, shrinkA=0, shrinkB=0, mutation_scale=18))
    label(ax, x, 610, money(mec(Q_A)), EXTERNAL, 8, 0, va="center")       # above the MPC label


def fig_costs(out: Path) -> None:
    """CORE's Figure 10.2 without B: the total external cost shaded and the MEC at A marked."""
    fig, ax = axes()
    between(ax, mpc, msc, 0, Q_A, EXT_AREA)
    cost_lines(ax)
    price_line(ax)
    guide(ax, Q_A, msc(Q_A))
    point_a(ax)
    mec_arrow(ax)
    save(fig, out)


def fig_one_less(out: Path) -> None:
    fig, ax = axes()
    cost_lines(ax)
    price_line(ax)
    guide(ax, Q_A, msc(Q_A))
    point_a(ax)
    mec_arrow(ax)
    save(fig, out)


def fig_efficient(out: Path) -> None:
    fig, ax = axes()
    cost_lines(ax)
    price_line(ax)
    guide(ax, Q_A, P)
    guide(ax, Q_B, P)
    point_a(ax)
    point_b(ax)
    save(fig, out)


def fig_bargain(out: Path) -> None:
    fig, ax = axes()
    between(ax, mpc, lambda q: P, Q_B, Q_A, PROFIT_AREA)
    between(ax, lambda q: P, msc, Q_B, Q_A, GAIN_AREA)
    cost_lines(ax)
    price_line(ax)
    guide(ax, Q_A, msc(Q_A))
    guide(ax, Q_B, P)
    point_a(ax)
    point_b(ax)
    both(ax, "Fishermen’s gain", (36, 700), (64, 500), (48, 365))
    pointer(ax, "Net social\ngain", (74, 540), (84, 600))
    pointer(ax, "Lost profit", (62, 375), (50, 225))
    save(fig, out)


def fig_cap(out: Path) -> None:
    """Regulation: output capped at B, and the surplus the plantations lose between B and A."""
    fig, ax = axes()
    between(ax, mpc, lambda q: P, Q_B, Q_A, PROFIT_AREA)
    cost_lines(ax)
    price_line(ax)
    ax.plot([Q_B, Q_B], [0, 860], color=EXTERNAL, lw=5, solid_capstyle="butt", zorder=6)
    label(ax, Q_B, 860, "Cap", EXTERNAL, 0, 6, ha="center")
    guide(ax, Q_A, P)
    point_a(ax)
    point_b(ax)
    pointer(ax, "Lost profit", (58, 368), (46, 225))
    save(fig, out)


def fig_tax(out: Path) -> None:
    fig, ax = axes()
    cost_lines(ax)
    price_line(ax)
    after = P - TAX
    price_line(ax, after, "", ls=DASH)
    label(ax, 68, after, "After-tax price", INK, 0, -8, va="top", fs=FONT - 3)
    guide(ax, Q_B, P)
    ax.plot([Q_B, Q_B], [float(after), P], color=EXTERNAL, lw=7, solid_capstyle="butt", zorder=6)
    point_b(ax)
    point(ax, Q_B, after)
    pointer(ax, f"Tax = {money(TAX)}", (Q_B + 1, 345), (43, 150))
    save(fig, out)


def fig_compensation(out: Path) -> None:
    fig, ax = axes()
    between(ax, mpc, msc, 0, Q_B, EXT_AREA)
    cost_lines(ax)
    price_line(ax)
    guide(ax, Q_B, P)
    point_b(ax)
    point(ax, Q_B, mpc(Q_B))
    pointer(ax, "Compensation", (20, 282), (3, 130))
    save(fig, out)


def fig_clean_water(out: Path) -> None:
    """The other allocation of rights: from no bananas at all, the plantations pay to grow up to B."""
    fig, ax = axes()
    between(ax, mpc, msc, 0, Q_B, EXT_AREA)
    between(ax, msc, lambda q: P, 0, Q_B, GAIN_AREA)
    cost_lines(ax)
    price_line(ax, text="")
    label(ax, X_END, P, "Price", INK, -6, -6, ha="right", va="top")       # C sits at its usual place
    guide(ax, Q_B, P)
    point(ax, Q_B, P, "B", dx=12, dy=-10, ha="left", va="top")       # clear of the arrows above
    ax.plot(0, P, marker="o", ms=12, color=INK, zorder=9, clip_on=False)       # C: no bananas grown
    label(ax, 0, P, "C", INK, 12, 12)
    both(ax, "Plantations’ gain", (22, 560), (9, 340), (22, 285))
    pointer(ax, "Net social\ngain", (29, 380), (47, 600))
    pointer(ax, "Pollution cost", (14, 262), (3, 130))
    save(fig, out)


# The Lecture 22 policy slides: two panels side by side, the fishermen's
# pollution cost and the plantations' profit, each showing what is left at B
# (solid) and what the move from A to B takes away (hatched). Set across the
# full slide width, so the type is sized for a 15 inch figure.
PANELS = (15, 5.5)         # fills the PDF frame's width and height with only the explanation above
PF = 26                     # panel type, large for a full-width figure: titles 29pt, ticks 23pt, key 21pt
COST_LEFT, COST_GONE = "#7fcfb4", "#d9f2ea"
PROFIT_LEFT, PROFIT_GONE = "#f0b27a", "#fbe6d3"
TAX_PAID = "#cbbbe6"
TITLE = "#8f4100"
PANEL_TOP = 700             # last tick on the panels' price axis


def panel_axes(ax, policy, ylabel=True):
    ax.set_xlim(0, X_END)
    ax.set_ylim(0, PANEL_TOP * 1.07)             # everything of interest is below MSC at A, $675
    ax.set_xticks(range(0, X_MAX + 1, 20))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.0f}K" if x else "0"))   # 38K, as on the slides
    ax.set_yticks(range(0, PANEL_TOP + 1, 100))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: money(y)))
    ax.grid(color=GRID, lw=1, zorder=0)
    ax.set_axisbelow("line")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(length=0, pad=6, labelsize=PF - 3)
    qs = grid_q(0, X_END)
    for f, color in ((mpc, PRIVATE), (msc, SOCIAL)):
        ax.plot([float(q) for q in qs], [float(f(q)) for q in qs], color=color, lw=3.4,
                solid_capstyle="round", zorder=5)
    ax.plot([0, X_END], [P, P], color=INK, lw=2.4, zorder=4)
    ax.text(97, float(mpc(97)) + 22, "MPC", color=PRIVATE, fontsize=PF, fontweight="bold", ha="center")
    ax.text(70, float(msc(70)) + 16, "MSC", color=SOCIAL, fontsize=PF, fontweight="bold", ha="right")
    ax.text(3, P + 12, "Price", color=INK, fontsize=PF, fontweight="bold", ha="left")
    for q in (Q_A, Q_B):
        ax.plot([q, q], [0, P], color=INK, lw=1.8, ls=DASH, zorder=4)
    for q, name, dx, dy in ((Q_A, "A", 2, -62), (Q_B, "B", -8, 16)):
        ax.plot(q, P, marker="o", ms=10, color=INK, zorder=9)
        ax.text(q + dx, P + dy, name, color=INK, fontsize=PF + 1, fontweight="bold")
    if policy == "cap":
        ax.plot([Q_B, Q_B], [0, PANEL_TOP - 40], color=EXTERNAL, lw=5, solid_capstyle="butt", zorder=6)
        ax.text(Q_B, PANEL_TOP - 30, "Cap", color=EXTERNAL, fontsize=PF, fontweight="bold", ha="center")
    if policy == "tax":
        after = float(P - TAX)
        ax.plot([0, X_END], [after, after], color=INK, lw=2.2, ls=DASH, zorder=4)
        ax.text(X_END - 2, after - 12, "After-tax\nprice", color=INK, fontsize=PF - 3, fontweight="bold",
                ha="right", va="top", linespacing=1.1, zorder=7,        # two lines, clear of the guide at A
                bbox=dict(facecolor="white", edgecolor="none", pad=1.5))
    ax.set_xlabel("Q (tons of bananas a year)", fontsize=PF - 2, labelpad=6)
    if ylabel:
        ax.set_ylabel("Dollars a ton", fontsize=PF - 2, labelpad=6)


def panel_area(ax, lower, upper, q0, q1, color, hatch=None, edge=None):
    qs = grid_q(q0, q1)
    ax.fill_between([float(q) for q in qs], [float(lower(q)) for q in qs], [float(upper(q)) for q in qs],
                    facecolor=color, edgecolor=edge or "none", hatch=hatch, lw=0, zorder=1)


def panel_key(ax, entries):
    """A one-row key between the panel title and the plot, so nothing sits on the graph itself."""
    from matplotlib.patches import Patch
    handles = [Patch(facecolor=c, edgecolor=(e or c), hatch=h, lw=0.8) for _, c, h, e in entries]
    ax.legend(handles, [t for t, *_ in entries], loc="lower left", bbox_to_anchor=(-0.01, 1.0),
              ncol=len(entries), fontsize=PF - 5, frameon=False, handlelength=1.4, handleheight=1.0,
              columnspacing=1.2, handletextpad=0.5, borderaxespad=0.2, borderpad=0.1)


def fig_panels(policy: str, out: Path) -> None:
    """policy is "cap", "tax" or "compensation"."""
    price, after = (lambda q: P), (lambda q: P - TAX)
    gone_cost = (COST_GONE, "///", "#2a9d7c")
    gone_profit = (PROFIT_GONE, "///", "#c9742d")
    fig, (left, right) = plt.subplots(1, 2, figsize=PANELS, dpi=100)

    panel_axes(left, policy)
    left.set_title("Fishermen's pollution cost", fontsize=PF + 3, fontweight="bold", color=TITLE, pad=40)   # room for the key
    panel_area(left, mpc, msc, Q_B, Q_A, *gone_cost)
    paid = (COST_LEFT, "..", "#1f7a5f")          # the same dotted area as on the plantations' side
    if policy == "compensation":
        # The pollution at B is still there, but the plantations pay for it, so the
        # fishermen do not bear it: drawn as the payment, not as a cost they carry.
        panel_area(left, mpc, msc, 0, Q_B, *paid)
        panel_key(left, [("Compensated", *paid), ("Avoided", *gone_cost)])
    else:
        panel_area(left, mpc, msc, 0, Q_B, COST_LEFT)
        panel_key(left, [("Still borne", COST_LEFT, None, None), ("Avoided", *gone_cost)])

    panel_axes(right, policy, ylabel=False)
    right.set_title("Plantations' profit", fontsize=PF + 3, fontweight="bold", color=TITLE, pad=40)   # room for the key
    panel_area(right, mpc, price, Q_B, Q_A, *gone_profit)
    entries = [("Kept", PROFIT_LEFT, None, None)]
    if policy == "cap":
        panel_area(right, mpc, price, 0, Q_B, PROFIT_LEFT)
    elif policy == "tax":
        panel_area(right, mpc, after, 0, Q_B, PROFIT_LEFT)
        panel_area(right, after, price, 0, Q_B, TAX_PAID, "..", "#6b4fa8")
        entries.append(("Tax paid", TAX_PAID, "..", "#6b4fa8"))
    else:
        panel_area(right, msc, price, 0, Q_B, PROFIT_LEFT)
        panel_area(right, mpc, msc, 0, Q_B, *paid)
        entries.append(("Compensation paid", *paid))
    entries.append(("Lost", *gone_profit))
    panel_key(right, entries)
    fig.tight_layout(pad=0.25, w_pad=1.6)        # little margin, so the graphs fill the slide
    save(fig, out)


def main() -> int:
    print("Q (thousand tons)   MPC     MEC     MSC")
    for q in (0, Q_B, Q_A, 100):
        print(f"  {q:>3}               {float(mpc(q)):>5.0f}   {float(mec(q)):>5.0f}   {float(msc(q)):>5.0f}")
    assert (mpc(0), mpc(Q_A), mpc(Q_B)) == (200, 400, 295)
    assert (mec(0), mec(Q_B), mec(Q_A)) == (40, 105, 275)
    assert (msc(0), msc(Q_B), msc(Q_A)) == (240, 400, 675)
    assert E1 > 0 and E2 > 0                    # the harm grows, and faster, as output rises
    print(f"A: {Q_A},000 tons where P = MPC; one ton less saves the fishermen {mec(Q_A)} and costs growers {P - mpc(Q_A)}")
    print(f"B: {Q_B},000 tons where P = MSC; one ton less saves the fishermen {mec(Q_B)} and costs growers {P - mpc(Q_B)}")
    print(f"tax {TAX} a ton, after-tax price {P - TAX} = MPC at {Q_B},000 tons")
    assert P - TAX == mpc(Q_B)
    fig_market(IMG / "banana-market.svg")
    fig_costs(IMG / "banana-costs.svg")
    fig_one_less(IMG / "banana-one-less.svg")
    fig_efficient(IMG / "banana-efficient.svg")
    fig_bargain(IMG / "banana-bargain.svg")
    fig_cap(IMG / "banana-cap.svg")
    fig_tax(IMG / "banana-tax.svg")
    fig_compensation(IMG / "banana-compensation.svg")
    fig_clean_water(IMG / "banana-clean-water.svg")
    for policy in ("cap", "tax", "compensation"):
        fig_panels(policy, IMG / f"banana-panels-{policy}.svg")
    return 0


if __name__ == "__main__":
    sys.exit(main())
