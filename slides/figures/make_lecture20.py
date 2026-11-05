"""
Numbers and figures for Lecture 20: taxes and price controls (CORE 8.12
and 8.13). Tentative draft (Div, 2026-10-28).

Run from the course root:

    python3 slides/figures/make_lecture20.py

A stylized salt market with CORE's 30% sales tax, paid by sellers, so the
taxed supply curve is 30% higher at every quantity (not parallel):

    demand        P = 17 - Q/10      (bags of salt a week, dollars a bag)
    supply        P = 8 + Q/20       (the marginal cost of the Qth bag)
    taxed supply  P = 1.3 x (8 + Q/20)
    before, A     60 bags at $11
    after, B      40 bags; buyers pay $13, sellers keep $10, tax $3 a bag
    incidence     buyers pay $2 more, sellers get $1 less: buyers bear 2/3,
                  because demand is less elastic than supply
    surplus       CS (1/2)(60)(17 - 11) = $180 -> (1/2)(40)(17 - 13) = $80
                  PS (1/2)(60)(11 - 8) = $90 -> (1/2)(40)(10 - 8) = $40
                  revenue 3 x 40 = $120; DWL (1/2)(60 - 40)(13 - 10) = $30
                  total 270 -> 80 + 40 + 120 = 240

A rent ceiling and a minimum wage, drawn as illustrations: the slides and
figures quote no numbers (Div, 2026-11-04). The rent curves behind the shapes:

    demand        P = 2100 - 3Q      supply  P = 300 + 3Q
    without it    300 apartments at $1,200
    ceiling $900  landlords offer 200, renters want 400, excess demand 200;
                  200 rented, the 200th renter would pay $1,500
    surplus       CS 135,000 -> 180,000; PS 135,000 -> 60,000; DWL 30,000
    long run      200 more apartments at every price clears the market at $900

The worksheet and the practice page use markets of their own:

    worksheet     front: gasoline, P = 8 - Q/10, P = 2 + Q/10 (thousand gallons
                  a day, dollars a gallon), 30 at $5; a 50% tax gives 20, buyers
                  pay $6, sellers keep $4, tax $2, split evenly; with the tax CS
                  20, PS 20, revenue 40, DWL 10 (at home, not on the sheet)
                  back: apartments near campus, P = 2100 - 3Q, P = 300 + 3Q, 300
                  at $1,200; a cap of $900 gives 200 offered, 400 wanted, excess
                  demand 200, 200 rented, and demand of $1,500 at 200; with the
                  cap CS 180,000, PS 60,000, DWL 30,000 (at home, not on the sheet)
    practice      cigarettes, P = 18 - 3Q/50, P = 2 + Q/50, 200 packs at $6; a $4
                  tax per pack gives 150, smokers pay $9, stores keep $5; with the
                  tax CS 675, PS 225, revenue 600, DWL 100
                  wine, P = 10 - Q/30, P = 2 + Q/30, 120 at $6; an $8 minimum
                  price gives 180 offered, 60 wanted, DWL 120

Output, in slides/img/:
  salt-tax.svg        supply, taxed supply, A and B
  salt-surplus.svg    CS, PS, tax revenue, and DWL shaded
  salt-incidence.svg  two panels: the same 30% tax with elastic and with
                      inelastic demand through A
  rent-ceiling.svg    the ceiling, the short side, and the excess demand
  rent-surplus.svg    CS, PS, and DWL with the ceiling
  min-wage.svg        the wage floor, the short side, the excess supply, and DWL
  cigarettes-grid.svg, cigarettes-solution.svg, wine-grid.svg, wine-solution.svg
                      practice page
and worksheets/figures/gasoline.pdf and apartments.pdf, the worksheet's grids.
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
PLOT_GRID = "#a0a0a0"       # darker, for the practice page's plotting grids
PRACTICE_FONT = 20          # shown at 600px, like the other practice figures: ticks 12pt, labels 14pt
PRACTICE_SIZE = (8.8, 6.0)  # the same as the other practice pages' figures
DEMAND = "#0072B2"
SUPPLY = "#8f4100"
RULE = "#595a5b"
CS_AREA = "#d2e7f5"
PS_AREA = "#fae2cc"
TAX_AREA = "#cdeee3"       # light tint of Okabe-Ito green
LOST = "#b8b8b8"
SIDE = (8.8, 6.0)
PAIR = (11.6, 5.4)
INCID_PAIR = (13.0, 5.4)
SURPLUS_PAIR = (13.6, 6.2)
SALT_SIDE = (8.8, 6.9)      # the $1 price ticks need the extra height to print at 8pt
FONT = 26
DASH = (0, (6, 3))

plt.rcParams.update({
    "font.family": ["Lato", "Fira Sans", "sans-serif"], "font.size": FONT,
    "svg.fonttype": "path", "pdf.fonttype": 42, "axes.edgecolor": RULE,
    "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
})

TAX = F(3, 10)
D = (17, -F(1, 10))
S = (8, F(1, 20))
Y_MIN = 7                  # nothing on the salt figures sits below $8, so the axis starts here
X_MAX, Y_MAX = 100, 17      # last ticks; the axes run a little past them


def price_on(c, q):
    return c[0] + c[1] * q


def taxed(c):
    return ((1 + TAX) * c[0], (1 + TAX) * c[1])


def cross(d, s):
    q = (d[0] - s[0]) / (s[1] - d[1])
    return q, price_on(d, q)


A = cross(D, S)                    # (60, 11)
B = cross(D, taxed(S))             # (40, 13)
P_SELL = price_on(S, B[0])         # 10
INCID_ELASTIC = (F(241, 20), -F(7, 400))  # through A; B at 20 bags, $11.70 and $9
INCID_INELASTIC = D                # the salt market itself; B at 40 bags, $13 and $10


def money(x):
    x = float(x)
    return f"${x:,.0f}" if x == int(x) else f"${x:,.2f}"


def save(fig, out: Path) -> None:
    fig.savefig(out, format="svg")
    if SCRATCH:
        fig.savefig(SCRATCH / f"{out.stem}.png", format="png", dpi=110)
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


def axis_break(ax):
    """Two short slashes on the price axis: it does not start at $0."""
    for dy in (0.012, 0.03):
        ax.plot([-0.012, 0.012], [dy, dy + 0.018], transform=ax.transAxes, color=RULE, lw=1.8, clip_on=False, zorder=10)


def style(ax, fs=FONT, xstep=20, ystep=1):
    ax.set_xlim(0, X_MAX * 1.05)
    ax.set_ylim(Y_MIN, Y_MAX + 0.6)
    ax.set_xticks(range(0, X_MAX + 1, xstep))
    ax.set_yticks(range(Y_MIN if ystep == 1 else Y_MIN + 1, Y_MAX + 1, ystep))
    axis_break(ax)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: money(y)))
    ax.grid(color=GRID, lw=1, zorder=0)
    ax.set_axisbelow("line")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(length=0, pad=8, labelsize=fs - 3)
    if ystep == 1:
        ax.tick_params(axis="y", labelsize=22)
    ax.set_xlabel("Q (bags of salt a week)", fontsize=fs - 2, labelpad=8)
    ax.set_ylabel("P (dollars a bag)", fontsize=fs - 2, labelpad=8)


def axes(size=SALT_SIDE):
    fig, ax = plt.subplots(figsize=size, dpi=100)
    style(ax)
    if size == SALT_SIDE:
        fig.subplots_adjust(left=0.15, right=0.97, top=0.97, bottom=0.14)
    else:
        ax.tick_params(axis="y", labelsize=FONT - 3)
        fig.subplots_adjust(left=0.135, right=0.97, top=0.97, bottom=0.135)
    return fig, ax


def label(ax, x, y, text, color, dx, dy, ha="left", va="bottom", fs=FONT):
    ax.annotate(text, xy=(float(x), float(y)), xytext=(dx, dy), textcoords="offset points",
                ha=ha, va=va, fontsize=fs, color=color, fontweight="bold", zorder=8)


def line(ax, c, color, lw=4, ls="-"):
    x1 = X_MAX
    if c[1] > 0 and price_on(c, X_MAX) > Y_MAX:
        x1 = float((Y_MAX - c[0]) / c[1])
    ax.plot([0, x1], [float(c[0]), float(price_on(c, x1))], color=color, lw=lw, ls=ls,
            solid_capstyle="round", zorder=5)


def guides(ax, q, p):
    q, p = float(q), float(p)
    ax.plot([0, q], [p, p], color=INK, lw=2.2, ls=(0, (4, 3)), zorder=4)
    ax.plot([q, q], [0, p], color=INK, lw=2.2, ls=(0, (4, 3)), zorder=4)


def point(ax, q, p, text="", dx=10, dy=6, ha="left", va="bottom", fs=FONT):
    ax.plot(float(q), float(p), marker="o", ms=12, color=INK, zorder=9)
    if text:
        label(ax, q, p, text, INK, dx, dy, ha=ha, va=va, fs=fs)


def curve_label(ax, x, y, text, color, side, fs=FONT):
    """A curve's name, right beside it. Every curve name is the same size."""
    dx, dy, ha, va = {"above-right": (5, 5, "left", "bottom"), "below-right": (6, -6, "left", "top"),
                      "above-left": (-6, 6, "right", "bottom"), "below-left": (-5, -5, "right", "top")}[side]
    ax.annotate(text, xy=(float(x), float(y)), xytext=(dx, dy), textcoords="offset points", ha=ha, va=va,
                fontsize=fs, color=color, fontweight="bold", zorder=8)


def curves(ax, tax=True):
    line(ax, D, DEMAND)
    line(ax, S, SUPPLY)
    curve_label(ax, 78, price_on(D, 78), "Demand", DEMAND, "above-right")
    curve_label(ax, 82, price_on(S, 82), "Supply", SUPPLY, "below-right")
    if tax:
        line(ax, taxed(S), SUPPLY, ls=DASH)
        curve_label(ax, 62, price_on(taxed(S), 62), "Supply with tax", SUPPLY, "below-right")


def pointer(ax, text, at, frm, fs=FONT - 4, ha="left"):
    """A label set in open space, with a thin arrow to the area or point it names."""
    ax.annotate(text, xy=(float(at[0]), float(at[1])), xytext=(float(frm[0]), float(frm[1])), fontsize=fs, fontweight="bold", color=INK,
                ha=ha, va="center", zorder=9, arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.6, shrinkA=2, shrinkB=0, mutation_scale=16))


def move(ax, start, end):
    """A grey arrow beside the curve, showing which way the market moves."""
    ax.annotate("", xy=(float(end[0]), float(end[1])), xytext=(float(start[0]), float(start[1])), zorder=8,
                arrowprops=dict(arrowstyle="-|>", color="#6b6b6b", lw=2.6, shrinkA=12, shrinkB=12, mutation_scale=22))


def fig_tax(out: Path, size=SALT_SIDE) -> None:
    fig, ax = axes(size)
    curves(ax)
    guides(ax, *A)
    guides(ax, *B)
    ax.plot([0, float(B[0])], [float(P_SELL)] * 2, color=INK, lw=2.2, ls=(0, (4, 3)), zorder=4)
    point(ax, *A, "A", dx=0, dy=14, ha="center")
    point(ax, *B, "B", dx=0, dy=14, ha="center")
    point(ax, B[0], P_SELL)
    save(fig, out)


def fig_surplus(out: Path) -> None:
    """CORE's Figure 8.24 layout: the surplus without the tax beside the surplus with it."""
    fs = FONT - 3
    (cs0, ps0), (cs1, ps1, rev, dwl) = surplus()
    q0, p0, q, pb, ps = float(A[0]), float(A[1]), float(B[0]), float(B[1]), float(P_SELL)
    fig, (left, right) = plt.subplots(1, 2, figsize=SURPLUS_PAIR, dpi=100)

    def area_label(ax, x, y, text):
        ax.text(x, y, text, ha="left", va="center", fontsize=FONT - 4, color=INK, fontweight="bold", zorder=8)

    for ax, title in ((left, "Without the tax"), (right, "With the tax")):
        style(ax, fs)
        ax.set_title(title, fontsize=FONT, color="#BF5700", fontweight="bold", pad=8)
        line(ax, D, DEMAND, lw=3)
        line(ax, S, SUPPLY, lw=3)

    left.fill([0, 0, q0], [float(D[0]), p0, p0], color=CS_AREA, lw=0, zorder=1)
    left.fill([0, 0, q0], [float(S[0]), p0, p0], color=PS_AREA, lw=0, zorder=1)
    guides(left, *A)
    point(left, *A, "A", dx=0, dy=12, ha="center", fs=fs)
    area_label(left, 4, 12.4, f"CS {money(cs0)}")
    area_label(left, 4, 10.1, f"PS {money(ps0)}")

    right.fill([0, 0, q], [float(D[0]), pb, pb], color=CS_AREA, lw=0, zorder=1)
    right.fill([0, 0, q, q], [ps, pb, pb, ps], color=TAX_AREA, lw=0, zorder=1)
    right.fill([0, 0, q], [float(S[0]), ps, ps], color=PS_AREA, lw=0, zorder=1)
    right.fill([q, q, q0], [ps, pb, p0], color=LOST, lw=0, zorder=1)
    line(right, taxed(S), SUPPLY, lw=3, ls=DASH)
    guides(right, *B)
    right.plot([0, q], [ps, ps], color=INK, lw=2, ls=(0, (4, 3)), zorder=4)
    point(right, *B, "B", dx=0, dy=12, ha="center", fs=fs)
    point(right, *A, "A", dx=0, dy=12, ha="center", fs=fs)
    area_label(right, 3, 14.1, f"CS {money(cs1)}")
    area_label(right, 3, 12.45, f"Tax {money(rev)}")
    area_label(right, 2, 9.55, f"PS {money(ps1)}")
    pointer(right, f"DWL {money(dwl)}", (46, 11.5), (52, 8.2))
    assert cs0 + ps0 == 270 and cs1 + ps1 + rev == 240
    totals = ((left, f"Total surplus = {money(cs0)} + {money(ps0)} = {money(cs0 + ps0)}"),
              (right, f"Total surplus = {money(cs1)} + {money(ps1)} + {money(rev)} = {money(cs1 + ps1 + rev)}"))
    for ax, text in totals:
        ax.text(-0.14, -0.31, text.replace("$", r"\$"), transform=ax.transAxes, ha="left", va="center", fontsize=FONT - 1, color=INK, fontweight="bold")
    fig.subplots_adjust(left=0.085, right=0.985, top=0.92, bottom=0.26, wspace=0.26)
    save(fig, out)


def fig_incidence(out: Path) -> None:
    fs = FONT - 1
    panels = [("Elastic demand", INCID_ELASTIC), ("Inelastic demand", INCID_INELASTIC)]
    fig, axs = plt.subplots(1, 2, figsize=INCID_PAIR, dpi=100)
    low = 8
    for ax, (title, d) in zip(axs, panels):
        assert price_on(d, A[0]) == A[1]
        style(ax, fs, xstep=20, ystep=2)
        b = cross(d, taxed(S))
        q1, q0, pb, p0, pn = float(b[0]), float(A[0]), float(b[1]), float(A[1]), float(price_on(S, b[0]))
        # only the values that matter here, in place of the even grid (Div, lecture 20)
        ax.grid(False)
        ax.set_ylim(low, 15)
        ax.set_xticks([0, q1, q0], ["0", f"{q1:.0f}", f"{q0:.0f}"])
        ax.set_yticks([pn, p0, pb], [money(pn), money(p0), money(pb)])
        line(ax, d, DEMAND, lw=3)
        line(ax, S, SUPPLY, lw=3)
        line(ax, taxed(S), SUPPLY, lw=3, ls=DASH)
        ax.axhline(p0, color=INK, lw=2, zorder=4)
        ax.plot([0, q1], [pb, pb], color=INK, lw=1.8, ls=(0, (4, 3)), zorder=4)
        ax.plot([0, q1], [pn, pn], color=INK, lw=1.8, ls=(0, (4, 3)), zorder=4)
        for q in (q1, q0):
            ax.plot([q, q], [low, min(pn, p0) if q == q1 else p0], color=INK, lw=1.8, ls=(0, (4, 3)), zorder=4)
        # the same three marks, in the same colours, in both panels
        ax.plot([q1, q1], [p0, pb], color=DEMAND, lw=7, solid_capstyle="butt", zorder=6)
        ax.plot([q1, q1], [pn, p0], color=SUPPLY, lw=7, solid_capstyle="butt", zorder=6)
        ax.plot([q1, q0], [low, low], color=RULE, lw=8, solid_capstyle="butt", clip_on=False, zorder=6)
        point(ax, q0, p0)
        point(ax, q1, pb)
        point(ax, q1, pn)
        if d == INCID_ELASTIC:
            label(ax, q0, p0, "A", INK, 12, -8, va="top", fs=fs)
            label(ax, q1, pb, "B", INK, 0, 12, ha="center", fs=fs)
        else:
            label(ax, q0, p0, "A", INK, 6, 12, fs=fs)
            label(ax, q1, pb, "B", INK, 6, 16, fs=fs)
        ax.set_title(title, fontsize=fs, color=INK, pad=8)
    axs[1].set_ylabel("")
    fig.subplots_adjust(left=0.08, right=0.985, top=0.9, bottom=0.17, wspace=0.13)
    save(fig, out)


# ------------------------------------------------------------ the rent ceiling
RD, RS, CAP = (2100, -3), (300, 3), 900
R_A = cross(RD, RS)
R_OFFER, R_WANT = F(CAP - RS[0], RS[1]), F(RD[0] - CAP, -RD[1])
R_WTP = price_on(RD, R_OFFER)
RS2 = (RS[0] - RS[1] * 200, RS[1])     # 200 more apartments at every price


def rent_axes(ylabel="P (rent)", xlabel="Q (apartments)"):
    fig, ax = plt.subplots(figsize=SIDE, dpi=100)
    ax.set_xlim(0, 630)
    ax.set_ylim(0, 2190)
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(length=0, pad=8, labelsize=FONT - 3)
    ax.set_xlabel(xlabel, fontsize=FONT - 2, labelpad=8)
    ax.set_ylabel(ylabel, fontsize=FONT - 2, labelpad=8)
    fig.subplots_adjust(left=0.19, right=0.97, top=0.96, bottom=0.16)
    return fig, ax


def named(ax, xs=(), ys=()):
    """Axis marks with names in place of numbers."""
    ax.set_xticks([float(q) for q, _ in xs], [t for _, t in xs])
    ax.set_yticks([float(p) for p, _ in ys], [t for _, t in ys])


def hguide(ax, q, p):
    ax.plot([0, float(q)], [float(p)] * 2, color=INK, lw=2.2, ls=(0, (4, 3)), zorder=4)


def vguide(ax, q, p):
    ax.plot([float(q)] * 2, [0, float(p)], color=INK, lw=2.2, ls=(0, (4, 3)), zorder=4)


def rent_curves(ax, demand_side="above-right"):
    ax.plot([0, 600], [RD[0], price_on(RD, 600)], color=DEMAND, lw=4, zorder=5)
    ax.plot([0, 600], [RS[0], price_on(RS, 600)], color=SUPPLY, lw=4, zorder=5)
    x = 470 if demand_side == "above-right" else 540
    curve_label(ax, x, price_on(RD, x), "Demand", DEMAND, demand_side)
    curve_label(ax, 480, price_on(RS, 480), "Supply", SUPPLY, "below-right")


def fig_rent_ceiling(out: Path) -> None:
    fig, ax = rent_axes()
    rent_curves(ax)
    ax.plot([0, float(R_WANT)], [CAP, CAP], color=INK, lw=2.6, zorder=4)
    ax.plot([float(R_OFFER), float(R_WANT)], [CAP - 4, CAP - 4], color="#7fb6d9", lw=5, zorder=4)
    ax.text(float(R_OFFER + R_WANT) / 2, CAP - 60, "Excess\ndemand", color=DEMAND, fontsize=FONT - 2, ha="center", va="top", zorder=9)
    hguide(ax, *R_A)
    vguide(ax, R_OFFER, CAP)
    vguide(ax, R_WANT, CAP)
    point(ax, *R_A, "A", dx=0, dy=14, ha="center")
    point(ax, R_OFFER, CAP)
    point(ax, R_WANT, CAP)
    named(ax, [(R_OFFER, "Offered"), (R_WANT, "Wanted")], [(CAP, "Ceiling"), (R_A[1], "Market")])
    save(fig, out)


def fig_rent_surplus(out: Path) -> None:
    fig, ax = rent_axes()
    q, w = float(R_OFFER), float(R_WTP)
    ax.fill([0, 0, q, q], [CAP, RD[0], w, CAP], color=CS_AREA, lw=0, zorder=1)
    ax.fill([0, 0, q], [RS[0], CAP, CAP], color=PS_AREA, lw=0, zorder=1)
    ax.fill([q, q, float(R_A[0])], [CAP, w, float(R_A[1])], color=LOST, lw=0, zorder=1)
    rent_curves(ax)
    ax.plot([0, q], [CAP, CAP], color=INK, lw=2.6, zorder=4)
    vguide(ax, q, w)
    hguide(ax, *R_A)
    point(ax, *R_A, "A", dx=0, dy=14, ha="center")
    point(ax, q, w)
    point(ax, q, CAP)
    ax.text(90, 1400, "CS", color=INK, fontsize=FONT - 2, fontweight="bold", ha="center", va="center", zorder=8)
    ax.text(50, 760, "PS", color=INK, fontsize=FONT - 2, fontweight="bold", ha="center", va="center", zorder=8)
    pointer(ax, "DWL", (242, 1080), (330, 560), fs=FONT - 2)
    named(ax, [(q, "Rented")], [(CAP, "Ceiling"), (R_A[1], "Market")])
    save(fig, out)


def fig_min_wage(out: Path) -> None:
    fig, ax = rent_axes("P (wage)", "Q (workers)")
    floor = 1500
    hired, seeking = F(RD[0] - floor, -RD[1]), F(floor - RS[0], RS[1])
    low = price_on(RS, hired)
    ax.fill([float(hired)] * 2 + [float(R_A[0])], [floor, float(low), float(R_A[1])], color=LOST, lw=0, zorder=1)
    rent_curves(ax)
    ax.plot([0, float(seeking)], [floor, floor], color=INK, lw=2.6, zorder=4)
    ax.plot([float(hired), float(seeking)], [floor + 4, floor + 4], color="#d9a77f", lw=5, zorder=4)
    ax.text(float(hired + seeking) / 2, floor + 60, "Excess\nsupply", color=SUPPLY, fontsize=FONT - 2, ha="center", va="bottom", zorder=9)
    hguide(ax, *R_A)
    vguide(ax, hired, floor)
    vguide(ax, seeking, floor)
    point(ax, *R_A, "A", dx=26, dy=0, va="center")
    point(ax, hired, floor)
    point(ax, seeking, floor)
    pointer(ax, "DWL", (232, 1180), (300, 560), fs=FONT - 2)
    named(ax, [(hired, "Hired"), (seeking, "Want work")], [(floor, "Minimum"), (R_A[1], "Market")])
    fig.subplots_adjust(left=0.22)
    save(fig, out)


def rent_numbers():
    assert R_A == (300, 1200) and (R_OFFER, R_WANT, R_WTP) == (200, 400, 1500)
    cs0 = F(1, 2) * R_A[0] * (RD[0] - R_A[1])
    ps0 = F(1, 2) * R_A[0] * (R_A[1] - RS[0])
    cs1 = F(1, 2) * R_OFFER * (RD[0] - R_WTP) + (R_WTP - CAP) * R_OFFER
    ps1 = F(1, 2) * R_OFFER * (CAP - RS[0])
    dwl = F(1, 2) * (R_A[0] - R_OFFER) * (R_WTP - CAP)
    assert (cs0, ps0, cs1, ps1, dwl) == (135000, 135000, 180000, 60000, 30000) and cs0 + ps0 == cs1 + ps1 + dwl
    assert cross(RD, RS2) == (400, 900)
    print(f"rent: A {R_A}; ceiling {CAP}: offered {R_OFFER}, wanted {R_WANT}; CS {cs0}->{cs1}; PS {ps0}->{ps1}; DWL {dwl}; long run {cross(RD, RS2)}")


# --------------------------------------------- worksheet and practice markets
def grid_axes(qmax, qstep, pmax, xlabel, ylabel, out_size=(7.2, 4.8), font=15):
    fig, ax = plt.subplots(figsize=out_size, dpi=100)
    ax.set_xlim(0, qmax)
    ax.set_ylim(0, pmax)
    ax.set_xticks(range(0, qmax + 1, qstep))
    ax.set_yticks(range(0, pmax + 1))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"${y:.0f}"))
    ax.grid(color=PLOT_GRID, lw=1, zorder=0)
    ax.set_axisbelow("line")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(length=0, labelsize=font - 3)
    ax.set_xlabel(xlabel, fontsize=font, labelpad=6)
    ax.set_ylabel(ylabel, fontsize=font, labelpad=6)
    fig.subplots_adjust(left=0.11, right=0.96, top=0.97, bottom=0.15)
    return fig, ax


def seg(ax, c, q0, q1, color, ls="-", lw=3):
    ax.plot([q0, q1], [float(price_on(c, q0)), float(price_on(c, q1))], color=color, lw=lw, ls=ls, zorder=5)


def tag(ax, x, y, text, color=INK, ha="left", va="center", font=15):
    ax.text(x, y, text, color=color, fontsize=font, fontweight="bold", ha=ha, va=va, zorder=8)


def market(d, s, t):
    """Before and after a percentage tax t on sellers."""
    q0, p0 = cross(d, s)
    q1, pb = cross(d, ((1 + t) * s[0], (1 + t) * s[1]))
    return q0, p0, q1, pb, price_on(s, q1)


G_D, G_S, G_T = (8, -F(1, 10)), (2, F(1, 10)), F(1, 2)
A_D, A_S, A_CAP = (2100, -3), (300, 3), 900
C_D, C_S, C_T = (18, -F(3, 50)), (2, F(1, 50)), 4
V_D, V_S, V_MIN = (10, -F(1, 30)), (2, F(1, 30)), 8


def fig_gasoline(out: Path) -> None:
    # Placed at 0.74\textwidth = 5.18in, so this 7.2in figure prints at 0.72:
    # tick labels 12pt -> 8.6pt, axis labels and curve names 15pt -> 10.8pt.
    fig, ax = grid_axes(60, 10, 8, "Q (thousand gallons a day)", "P (dollars a gallon)")
    ax.set_xlim(0, 63)
    ax.set_ylim(0, 8.4)
    ax.tick_params(pad=7)       # keeps $0 and 0 apart at the origin
    seg(ax, G_D, 0, 60, DEMAND)
    seg(ax, G_S, 0, 60, SUPPLY)
    taxed_g = ((1 + G_T) * G_S[0], (1 + G_T) * G_S[1])
    seg(ax, taxed_g, 0, F(8 - taxed_g[0]) / taxed_g[1], SUPPLY, ls=DASH)
    tag(ax, 51, 3.5, "Demand", DEMAND)
    tag(ax, 52, 6.5, "Supply", SUPPLY)
    tag(ax, 33, 7.5, "Supply with tax", SUPPLY)
    ax.texts[-1].set_bbox(dict(fc="white", ec="none", pad=1.5))     # wider than a grid cell
    fig.savefig(out, format="pdf")
    if SCRATCH:
        fig.savefig(SCRATCH / f"{out.stem}.png", format="png", dpi=110)
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


def fig_apartments(out: Path) -> None:
    # Same 7.2in figure at 0.74\textwidth as fig_gasoline, so the same print sizes.
    fig, ax = grid_axes(600, 100, 2100, "Q (apartments)", "P (rent, dollars a month)")
    ax.set_xlim(0, 630)
    ax.set_ylim(0, 2190)
    ax.set_yticks(range(0, 2101, 300))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"${y:,.0f}"))
    ax.tick_params(pad=7)       # keeps $0 and 0 apart at the origin
    fig.subplots_adjust(left=0.15)     # room for the wider $2,100 labels
    seg(ax, A_D, 0, 600, DEMAND)
    seg(ax, A_S, 0, 600, SUPPLY)
    tag(ax, 510, 750, "Demand", DEMAND)
    tag(ax, 520, 1650, "Supply", SUPPLY)
    fig.savefig(out, format="pdf")
    if SCRATCH:
        fig.savefig(SCRATCH / f"{out.stem}.png", format="png", dpi=110)
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


def cigarettes(out: Path, key: bool) -> None:
    fig, ax = grid_axes(250, 50, 19, "Q (packs a day)", "P (dollars a pack)", out_size=PRACTICE_SIZE, font=PRACTICE_FONT)
    ax.set_xlim(0, 258)
    taxed_c = (C_S[0] + C_T, C_S[1])
    q0, p0 = cross(C_D, C_S)
    q1, pb = cross(C_D, taxed_c)
    ps = price_on(C_S, q1)
    if key:
        ax.fill([0, 0, float(q1)], [C_D[0], float(pb), float(pb)], color=CS_AREA, lw=0, zorder=1)
        ax.fill([0, 0, float(q1), float(q1)], [float(ps), float(pb), float(pb), float(ps)], color=TAX_AREA, lw=0, zorder=1)
        ax.fill([0, 0, float(q1)], [C_S[0], float(ps), float(ps)], color=PS_AREA, lw=0, zorder=1)
        ax.fill([float(q1), float(q1), float(q0)], [float(ps), float(pb), float(p0)], color=LOST, lw=0, zorder=1)
    seg(ax, C_D, 0, 250, DEMAND)
    seg(ax, C_S, 0, 250, SUPPLY)
    seg(ax, taxed_c, 0, 250, SUPPLY, ls=DASH)
    tag(ax, 62, 15.4, "Demand", DEMAND, font=PRACTICE_FONT)
    tag(ax, 256, 8.0, "Supply", SUPPLY, ha="right", font=PRACTICE_FONT)
    tag(ax, 248, 12.0, "Supply with tax", SUPPLY, ha="right", font=PRACTICE_FONT)
    if key:
        for (q, p, name, dx, dy) in ((q0, p0, "A", 5, 0.95), (q1, pb, "B", -3, 1.05)):
            ax.plot([0, float(q)], [float(p), float(p)], color=INK, lw=1.6, ls=(0, (4, 3)), zorder=4)
            ax.plot([float(q), float(q)], [0, float(p)], color=INK, lw=1.6, ls=(0, (4, 3)), zorder=4)
            ax.plot(float(q), float(p), marker="o", ms=8, color=INK, zorder=9)
            tag(ax, float(q) + dx, float(p) + dy, name, font=PRACTICE_FONT)
        ax.plot([0, float(q1)], [float(ps), float(ps)], color=INK, lw=1.6, ls=(0, (4, 3)), zorder=4)
        ax.plot(float(q1), float(ps), marker="o", ms=8, color=INK, zorder=9)
        tag(ax, 18, 11, "CS", font=PRACTICE_FONT - 2)
        tag(ax, 25, 7.95, "Tax", font=PRACTICE_FONT - 2)
        tag(ax, 14, 4, "PS", font=PRACTICE_FONT - 2)
        tag(ax, 165, 6.6, "DWL", ha="center", font=PRACTICE_FONT - 2)
    fig.savefig(out, format="svg")
    if SCRATCH:
        fig.savefig(SCRATCH / f"{out.stem}.png", format="png", dpi=110)
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


def wine(out: Path, key: bool) -> None:
    fig, ax = grid_axes(240, 60, 12, "Q (bottles a day)", "P (dollars a bottle)", out_size=PRACTICE_SIZE, font=PRACTICE_FONT)
    ax.set_yticks(range(0, 13, 2))
    q0, p0 = cross(V_D, V_S)
    sold, offered = F(V_D[0] - V_MIN) / -V_D[1], F(V_MIN - V_S[0]) / V_S[1]
    low = price_on(V_S, sold)
    if key:
        ax.fill([0, 0, float(sold)], [V_D[0], V_MIN, V_MIN], color=CS_AREA, lw=0, zorder=1)
        ax.fill([0, 0, float(sold), float(sold)], [V_S[0], V_MIN, V_MIN, float(low)], color=PS_AREA, lw=0, zorder=1)
        ax.fill([float(sold), float(sold), float(q0)], [V_MIN, float(low), float(p0)], color=LOST, lw=0, zorder=1)
    seg(ax, V_D, 0, 240, DEMAND)
    seg(ax, V_S, 0, 240, SUPPLY)
    tag(ax, 48, 10.7, "Demand", DEMAND, font=PRACTICE_FONT)
    tag(ax, 240, 7.2, "Supply", SUPPLY, ha="right", font=PRACTICE_FONT)
    ax.plot([0, 240], [V_MIN, V_MIN], color=INK, lw=2, zorder=4)
    tag(ax, 126, 8.72, "Minimum price", ha="center", font=PRACTICE_FONT)
    if key:
        for (q, p) in ((q0, p0), (sold, V_MIN), (sold, low), (offered, V_MIN)):
            ax.plot([float(q), float(q)], [0, float(p)], color=INK, lw=1.6, ls=(0, (4, 3)), zorder=4)
            ax.plot(float(q), float(p), marker="o", ms=8, color=INK, zorder=9)
        ax.plot([0, float(q0)], [float(p0), float(p0)], color=INK, lw=1.6, ls=(0, (4, 3)), zorder=4)
        tag(ax, float(q0) + 14, float(p0), "A", font=PRACTICE_FONT)
        tag(ax, 8, 8.65, "CS", font=PRACTICE_FONT - 2)
        tag(ax, 26, 5.4, "PS", font=PRACTICE_FONT - 2)
        tag(ax, 77, 6.75, "DWL", ha="center", font=PRACTICE_FONT - 2)
    fig.savefig(out, format="svg")
    if SCRATCH:
        fig.savefig(SCRATCH / f"{out.stem}.png", format="png", dpi=110)
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


def other_numbers():
    q0, p0, q1, pb, ps = market(G_D, G_S, G_T)
    assert (q0, p0, q1, pb, ps) == (30, 5, 20, 6, 4) and pb == (1 + G_T) * ps
    assert pb - ps == 2 and pb - p0 == 1 and p0 - ps == 1
    assert price_on(((1 + G_T) * G_S[0], (1 + G_T) * G_S[1]), 20) == 6 and (1 + G_T) * G_S[0] == 3 and (1 + G_T) * G_S[1] == F(3, 20)
    a_offer, a_want = F(A_CAP - A_S[0], A_S[1]), F(A_D[0] - A_CAP, -A_D[1])
    assert cross(A_D, A_S) == (300, 1200)
    assert (a_offer, a_want, a_want - a_offer, min(a_offer, a_want)) == (200, 400, 200, 200)
    assert price_on(A_D, a_offer) == 1500
    q0, p0, q1, pb, ps = market(G_D, G_S, G_T)
    cs1, ps1, rev, dwl = F(1, 2) * q1 * (G_D[0] - pb), F(1, 2) * q1 * (ps - G_S[0]), (pb - ps) * q1, F(1, 2) * (q0 - q1) * (pb - ps)
    assert (cs1, ps1, rev, dwl) == (20, 20, 40, 10) and F(1, 2) * q0 * (G_D[0] - G_S[0]) == cs1 + ps1 + rev + dwl
    a_wtp = price_on(A_D, a_offer)
    cs1 = F(1, 2) * a_offer * (A_D[0] - a_wtp) + a_offer * (a_wtp - A_CAP)
    ps1, dwl = F(1, 2) * a_offer * (A_CAP - A_S[0]), F(1, 2) * (300 - a_offer) * (a_wtp - A_CAP)
    assert (cs1, ps1, dwl) == (180000, 60000, 30000) and F(1, 2) * 300 * (A_D[0] - A_S[0]) == cs1 + ps1 + dwl
    assert cross(C_D, C_S) == (200, 6) and cross(C_D, (C_S[0] + C_T, C_S[1])) == (150, 9) and price_on(C_S, 150) == 5
    cs0, ps0 = F(1, 2) * 200 * (18 - 6), F(1, 2) * 200 * (6 - 2)
    cs1, ps1, rev, dwl = F(1, 2) * 150 * (18 - 9), F(1, 2) * 150 * (5 - 2), C_T * 150, F(1, 2) * 50 * C_T
    assert (cs0, ps0, cs1, ps1, rev, dwl) == (1200, 400, 675, 225, 600, 100) and cs0 + ps0 == cs1 + ps1 + rev + dwl
    assert cross(V_D, V_S) == (120, 6)
    assert F(V_D[0] - V_MIN) / -V_D[1] == 60 and F(V_MIN - V_S[0]) / V_S[1] == 180 and price_on(V_S, 60) == 4
    cs0, ps0 = F(1, 2) * 120 * (10 - 6), F(1, 2) * 120 * (6 - 2)
    cs1, ps1, dwl = F(1, 2) * 60 * (10 - 8), F(1, 2) * 60 * ((8 - 2) + (8 - 4)), F(1, 2) * 60 * (8 - 4)
    assert (cs0, ps0, cs1, ps1, dwl) == (240, 240, 60, 300, 120) and cs0 + ps0 == cs1 + ps1 + dwl
    print("worksheet and practice numbers check")


def surplus():
    q0, p0 = A
    q1, pb = B
    before = (F(1, 2) * q0 * (D[0] - p0), F(1, 2) * q0 * (p0 - S[0]))
    after = (F(1, 2) * q1 * (D[0] - pb), F(1, 2) * q1 * (P_SELL - S[0]),
             (pb - P_SELL) * q1, F(1, 2) * (q0 - q1) * (pb - P_SELL))
    return before, after


def main() -> int:
    print(f"A: {A[0]} bags at {money(A[1])}")
    print(f"B: {B[0]} bags; buyers pay {money(B[1])}, sellers keep {money(P_SELL)}, tax {money(B[1] - P_SELL)} a bag")
    assert A == (60, 11) and B == (40, 13) and P_SELL == 10
    assert B[1] == (1 + TAX) * P_SELL
    (cs0, ps0), (cs1, ps1, rev, dwl) = surplus()
    print(f"CS {cs0} -> {cs1}; PS {ps0} -> {ps1}; revenue {rev}; DWL {dwl}")
    print(f"total {cs0 + ps0} -> {cs1 + ps1 + rev} (+ DWL {dwl})")
    assert (cs0, ps0, cs1, ps1, rev, dwl) == (180, 90, 80, 40, 120, 30)
    assert cs0 + ps0 == cs1 + ps1 + rev + dwl
    print(f"incidence: buyers +{B[1] - A[1]}, sellers -{A[1] - P_SELL}")
    for title, d in (("elastic", INCID_ELASTIC), ("inelastic", INCID_INELASTIC)):
        b = cross(d, taxed(S)); pn = price_on(S, b[0])
        print(f"  {title} demand: buyers +{float(b[1] - A[1]):.2f}, sellers -{float(A[1] - pn):.2f}")
    fig_tax(IMG / "salt-tax.svg")
    fig_surplus(IMG / "salt-surplus.svg")
    fig_incidence(IMG / "salt-incidence.svg")
    rent_numbers()
    other_numbers()
    fig_rent_ceiling(IMG / "rent-ceiling.svg")
    fig_rent_surplus(IMG / "rent-surplus.svg")
    fig_min_wage(IMG / "min-wage.svg")
    fig_gasoline(ROOT / "worksheets" / "figures" / "gasoline.pdf")
    fig_apartments(ROOT / "worksheets" / "figures" / "apartments.pdf")
    cigarettes(IMG / "cigarettes-grid.svg", key=False)
    cigarettes(IMG / "cigarettes-solution.svg", key=True)
    wine(IMG / "wine-grid.svg", key=False)
    wine(IMG / "wine-solution.svg", key=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
