"""
Figures and numbers for the Midterm 1 materials: the formula sheet's
reference graph and the study guide's surplus example and its twin.

Run from the course root:

    python3 exams/midterm1/figures/make_midterm1.py

Same drawing style as slides/figures/make_lecture10.py (Okabe-Ito colours,
Lato or Fira Sans, thick lines, a tick at every number a question uses).
The guide's examples use their own firms and numbers, not the lectures'.

    Luma Lamps (worked)   P = 100 - 2 Q, MC = 20, F = 300
                          MR = 100 - 4 Q = 20 at Q* = 20, P* = 60
                          CS = 1/2 x 20 x 40 = 400, PS = 40 x 20 = 800
                          profit = 800 - 300 = 500
                          demand meets MC at Q = 40, DWL = 1/2 x 20 x 40 = 400
                          30th buyer: WTP = 40
    Pine Desks (twin)     P = 60 - Q, MC = 12, F = 200
                          MR = 60 - 2 Q = 12 at Q* = 24, P* = 36
                          CS = 1/2 x 24 x 24 = 288, PS = 24 x 24 = 576
                          profit = 576 - 200 = 376
                          demand meets MC at Q = 48, DWL = 1/2 x 24 x 24 = 288

    Lakeside Smoothies (practice exam, Part 3)
                          Q = 120 - 5 P, i.e. P = 24 - Q/5, MC = 4, F = 150
                          MR = 24 - 2Q/5 = 4 at Q* = 50, P* = 14
                          CS = 1/2 x 50 x 10 = 250, PS = 10 x 50 = 500
                          profit = 500 - 150 = 350 (the table's best row)
                          demand meets MC at Q = 100, DWL = 1/2 x 50 x 10 = 250
                          operate while F <= 500

Output, in exams/midterm1/figures/:
  reference.pdf     help sheet: demand, MR, MC with the CS, PS, and DWL regions
                    labelled and the axes marked P0, P*, MC, Q*, Q_F; no numbers
  lamps.pdf         worked example, with CS, PS, and DWL shaded and labelled
  juice.pdf         the juice stand's demand curve with the 10th buyer marked,
                    for the study guide's demand-and-costs worked example
  juice-profit.pdf  the same stand's demand, MR, and MC with E and E'
  smoothies.pdf     practice exam, Part 3: Lakeside Smoothies' demand, MR,
                    and MC on a grid, nothing marked; smoothies-key.pdf adds
                    the $14 price line, E, and the three shaded regions
  desks.pdf         twin: demand and MC on a grid, nothing marked, for the
                    student to work on
"""
import glob as _glob
import os
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

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "exams" / "midterm1" / "figures"
SCRATCH = Path(os.environ["FIG_PREVIEW_DIR"]) if os.environ.get("FIG_PREVIEW_DIR") else None

INK = "#1a1a1a"
GRID = "#d9d9d9"
# Demand in the course orange (Div, 2026-10-06), MR dashed in the same colour.
ACCENT = "#BF5700"
DEMAND = ACCENT
AC_LINE = "#0072B2"
MARGINAL = "#595a5b"
CS_AREA = "#fae2cc"
PS_AREA = "#e3edf6"
DWL_AREA = "#e8e8e8"

FONT = 15
SIZE = (7.2, 4.6)

plt.rcParams.update(
    {
        "font.family": ["Lato", "Fira Sans", "sans-serif"],
        "font.size": FONT,
        "pdf.fonttype": 42,
        "axes.edgecolor": INK,
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
    }
)


def save(fig, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format="pdf")
    if SCRATCH:
        fig.savefig(SCRATCH / f"{out.stem}.png", format="png", dpi=110)
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


def axes(qmax, pmax, qstep, pstep, xlabel, ylabel, dollars=True, size=SIZE):
    fig, ax = plt.subplots(figsize=size, dpi=100)
    ax.grid(color=GRID, lw=1, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=5, width=1, labelsize=FONT - 2)
    ax.set_xlim(0, qmax)
    ax.set_ylim(0, pmax)
    ax.set_xticks(range(0, qmax + 1, qstep))
    ax.set_yticks(range(0, pmax + 1, pstep))
    if dollars:
        ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"${y:,.0f}"))
    ax.set_xlabel(xlabel, fontsize=FONT, labelpad=6)
    ax.set_ylabel(ylabel, fontsize=FONT, labelpad=6)
    fig.subplots_adjust(left=0.13, right=0.97, top=0.96, bottom=0.17)
    return fig, ax


def firm(ax, a, b, mc, qmax, label_at, shade=True, mark=True, mr=True, mc_label=True, eff=True):
    """Linear demand P = a - bQ with constant MC. Returns Q*, P*, Q_eff."""
    q_star = (a - mc) / (2 * b)
    p_star = a - b * q_star
    q_eff = (a - mc) / b
    q = np.array([0.0, min(qmax, a / b)])
    if shade:
        qs = np.linspace(0, q_star, 50)
        # Below the gridlines (axes sit at zorder 0.5 with set_axisbelow), so
        # the grid shows through the shading (Div, 2026-10-06).
        ax.fill_between(qs, p_star, a - b * qs, color=CS_AREA, zorder=0.3)
        ax.fill_between([0, q_star], mc, p_star, color=PS_AREA, zorder=0.3)
        qd = np.linspace(q_star, q_eff, 50)
        ax.fill_between(qd, mc, a - b * qd, color=DWL_AREA, zorder=0.3)
        ax.text(q_star * 0.42, p_star + (a - p_star) * 0.3, "CS", ha="center",
                va="center", fontsize=FONT, color=ACCENT, fontweight="bold", zorder=8)
        ax.text(q_star * 0.5, (p_star + mc) / 2, "PS", ha="center", va="center",
                fontsize=FONT, color=AC_LINE, fontweight="bold", zorder=8)
        ax.text(q_star + (q_eff - q_star) * 0.3, mc + (p_star - mc) * 0.3, "DWL",
                ha="center", va="center", fontsize=FONT, color=INK,
                fontweight="bold", zorder=8)
    ax.plot(q, a - b * q, color=DEMAND, lw=2.6, solid_capstyle="round", zorder=5)
    ax.annotate("Demand", xy=(label_at, a - b * label_at), xytext=(8, 6),
                textcoords="offset points", ha="left", va="bottom",
                fontsize=FONT, color=DEMAND, fontweight="bold", zorder=8)
    if mr:
        qm = np.array([0.0, min(qmax, a / (2 * b))])
        ax.plot(qm, a - 2 * b * qm, color=DEMAND, lw=2, ls=(0, (6, 3)), zorder=5)
        qlab = a / (2 * b) * 0.97
        ax.annotate("MR", xy=(qlab, a - 2 * b * qlab), xytext=(6, -2),
                    textcoords="offset points", ha="left", va="center",
                    fontsize=FONT, color=DEMAND, fontweight="bold", zorder=8)
    ax.axhline(mc, color=MARGINAL, lw=2, ls=(0, (5, 3)), zorder=4)
    if mc_label:
        ax.annotate("MC", xy=(qmax * 0.02, mc), xytext=(0, -7),
                    textcoords="offset points", ha="left", va="top",
                    fontsize=FONT, color=MARGINAL, fontweight="bold", zorder=8)
    if mark:
        ax.plot([q_star, q_star], [0, p_star], color=INK, lw=1, ls=":", zorder=6)
        ax.plot([0, q_star], [p_star, p_star], color=INK, lw=1, ls=":", zorder=6)
        ax.plot(q_star, p_star, "o", ms=9, color=INK, zorder=9)
        ax.annotate("E", xy=(q_star, p_star), xytext=(7, 7), textcoords="offset points",
                    fontsize=FONT, color=INK, fontweight="bold", zorder=10)
        ax.plot(q_star, mc, "o", ms=9, color=INK, zorder=9)
        ax.annotate("E′", xy=(q_star, mc), xytext=(7, -14), textcoords="offset points",
                    fontsize=FONT, color=INK, fontweight="bold", zorder=10)
    if mark and eff:
        ax.plot(q_eff, mc, "o", ms=9, color=INK, zorder=9)
        ax.annotate("F", xy=(q_eff, mc), xytext=(7, 7), textcoords="offset points",
                    fontsize=FONT, color=INK, fontweight="bold", zorder=10)
    return q_star, p_star, q_eff


def draw_reference(out: Path) -> None:
    """Help sheet: demand, MR, and MC with CS, PS, and DWL shaded and labelled,
    the axes marked with the symbols the surplus formulas use (P0, P*, MC;
    Q*, Q_F) and no points marked (Div, 2026-10-06)."""
    with plt.rc_context({"mathtext.fontset": "custom", "mathtext.rm": "Lato",
                         "mathtext.it": "Lato:italic", "mathtext.default": "it"}):
        fig, ax = axes(50, 100, 10, 20, "Quantity, Q", "Price", dollars=False, size=(4.6, 3.4))
        fig.subplots_adjust(left=0.16, right=0.97, top=0.96, bottom=0.2)
        ax.set_xticks([20, 40])
        ax.set_xticklabels([r"$Q^*$", r"$Q_F$"])
        ax.set_yticks([20, 60, 100])
        ax.set_yticklabels([r"$\mathrm{MC}$", r"$P^*$", r"$P_0$"])
        ax.tick_params(labelsize=FONT)
        ax.grid(False)
        firm(ax, 100, 2, 20, 50, 8, mark=False, mc_label=False)
        ax.plot([20, 20], [0, 60], color=INK, lw=1, ls=":", zorder=6)
        ax.plot([0, 20], [60, 60], color=INK, lw=1, ls=":", zorder=6)
        ax.plot([40, 40], [0, 20], color=INK, lw=1, ls=":", zorder=6)
        save(fig, out)


def draw_lamps(out: Path) -> None:
    fig, ax = axes(50, 100, 10, 10, "Lamps per day, Q", "Price and cost")
    q_star, p_star, q_eff = firm(ax, 100, 2, 20, 50, 8)
    assert (q_star, p_star, q_eff) == (20, 60, 40)
    save(fig, out)


def draw_desks(out: Path) -> None:
    fig, ax = axes(60, 60, 6, 6, "Desks per week, Q", "Price and cost")
    q_star, p_star, q_eff = firm(ax, 60, 1, 12, 60, 10, shade=False, mark=False, mr=False)
    assert (q_star, p_star, q_eff) == (24, 36, 48)
    save(fig, out)


def draw_juice(out: Path) -> None:
    """Study guide worked example: the juice stand's demand curve, P = 20 - Q/5,
    with the 10th buyer's willingness to pay. No intercept labels (Div)."""
    fig, ax = axes(100, 20, 10, 2, "Cups per day, Q", "Price per cup", size=(6.4, 4.2))
    ax.plot([0, 100], [20, 0], color=DEMAND, lw=2.6, solid_capstyle="round", zorder=5)
    ax.annotate("Demand", xy=(55, 9), xytext=(8, 6), textcoords="offset points",
                fontsize=FONT, color=DEMAND, fontweight="bold", zorder=8)
    ax.plot([10, 10], [0, 18], color=INK, lw=1, ls=":", zorder=6)
    ax.plot([0, 10], [18, 18], color=INK, lw=1, ls=":", zorder=6)
    ax.plot(10, 18, "o", ms=7, color=INK, zorder=9)
    ax.annotate("10th buyer: $18", xy=(10, 18), xytext=(12, 4), textcoords="offset points",
                fontsize=FONT - 2, color=INK, zorder=10, va="bottom")
    fig.subplots_adjust(left=0.15, right=0.96, top=0.93, bottom=0.18)
    save(fig, out)


def draw_juice_profit(out: Path) -> None:
    """Study guide worked example, second figure: the juice stand's demand,
    MR, and MC with E and E' marked (no AC: Div, 2026-10-06), and the table's
    MR values marked at Q = 20, 30, 50. Axes run a little past the
    intercepts (Div)."""
    fig, ax = axes(100, 20, 10, 2, "Cups per day, Q", "Price and cost", size=(6.4, 4.2))
    ax.set_xlim(0, 110)
    ax.set_ylim(-2, 22)
    ax.set_yticks(range(0, 23, 2))
    ax.axhline(0, color=INK, lw=0.8, zorder=3)
    q_star, p_star, _ = firm(ax, 20, 0.2, 4, 110, 62, shade=False, mark=True, eff=False)
    assert (q_star, p_star) == (40, 12)
    # The table's rows: P and MR at Q = 20, 30, 40, 50, so the student sees
    # where the MR line comes from (Div, 2026-10-06).
    # Only the table's MR values are marked, as dark points with their values,
    # so the student sees where the MR line comes from; the demand curve was
    # drawn in the step before (Div, 2026-10-06: no dots on demand, no
    # squares, no legend).
    for q in (20, 30, 50):
        mr = (20 - (q + 1) / 5) * (q + 1) - (20 - q / 5) * q
        ax.plot(q, mr, "o", ms=8, color=INK, mec="white", mew=1, zorder=9)
        left = q < 50  # label clear of the dashed MR line
        ax.annotate(f"MR {mr:.2f}".replace("-", "\u2212"), xy=(q, mr),
                    xytext=(-9, -3) if left else (8, -3), textcoords="offset points",
                    fontsize=FONT - 2, color=INK, ha="right" if left else "left",
                    va="top", zorder=10)
    fig.subplots_adjust(left=0.15, right=0.96, top=0.93, bottom=0.18)
    save(fig, out)


def draw_exam(out: Path, a, b, mc, qmax, pmax, qstep, pstep, xlabel, solution, shade=True, eff=True):
    fig, ax = axes(qmax, pmax, qstep, pstep, xlabel, "Price and cost")
    if qmax >= 1000:
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:,.0f}"))
    firm(ax, a, b, mc, qmax, qmax * 0.16, shade=solution and shade, mark=solution, eff=eff)
    save(fig, out)


def draw_smoothies(out: Path, solution: bool) -> None:
    """Practice exam, Part 3: Lakeside Smoothies' demand, MR, and MC on a grid
    (Div, 2026-10-06: the problem opens with this graph; students read the
    price and Q* off it). Drawn for reading at a glance: larger type, a light
    grid, and each line labelled beside it. The key adds the $14 price line,
    E at (50, 14), and CS, PS, and DWL shaded; no E' or F labels."""
    fig, ax = plt.subplots(figsize=(7.4, 4.8), dpi=100)
    ax.grid(color="#e6e6e6", lw=0.9, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.set_xlim(0, 120)
    ax.set_ylim(0, 25)
    ax.set_xticks(range(0, 121, 10))
    ax.set_yticks(range(0, 25, 2))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"${y:,.0f}"))
    ax.tick_params(length=4, width=1, labelsize=FONT - 1)
    ax.set_xlabel("Smoothies per day, Q", fontsize=FONT + 1, labelpad=6)
    ax.set_ylabel("Price and cost", fontsize=FONT + 1, labelpad=6)
    if solution:
        qs = np.linspace(0, 50, 50)
        ax.fill_between(qs, 14, 24 - qs / 5, color=CS_AREA, zorder=0.3)
        ax.fill_between([0, 50], 4, 14, color=PS_AREA, zorder=0.3)
        qd = np.linspace(50, 100, 50)
        ax.fill_between(qd, 4, 24 - qd / 5, color=DWL_AREA, zorder=0.3)
        for x, y, t, c in ((17, 17, "CS", ACCENT), (25, 9, "PS", AC_LINE), (66, 8, "DWL", INK)):
            ax.text(x, y, t, ha="center", va="center", fontsize=FONT + 1, color=c,
                    fontweight="bold", zorder=8)
        ax.plot([0, 50], [14, 14], color=INK, lw=1.2, ls=":", zorder=6)
        ax.plot([50, 50], [0, 14], color=INK, lw=1.2, ls=":", zorder=6)
        ax.plot(50, 14, "o", ms=9, color=INK, zorder=9)
        ax.annotate("E", xy=(50, 14), xytext=(8, 6), textcoords="offset points",
                    fontsize=FONT + 1, color=INK, fontweight="bold", zorder=10)
    ax.plot([0, 120], [24, 0], color=DEMAND, lw=3, solid_capstyle="round", zorder=5)
    ax.plot([0, 60], [24, 0], color=DEMAND, lw=2.4, ls=(0, (6, 3)), zorder=5)
    ax.axhline(4, color=MARGINAL, lw=2.4, ls=(0, (6, 3)), zorder=4)
    ax.text(71, 10.6, "Demand", ha="left", va="bottom", fontsize=FONT + 1, color=DEMAND,
            fontweight="bold", zorder=8)
    ax.text(41.5, 9.3, "MR", ha="left", va="center", fontsize=FONT + 1, color=DEMAND,
            fontweight="bold", zorder=8)
    ax.text(118, 4.6, "MC", ha="right", va="bottom", fontsize=FONT + 1, color=MARGINAL,
            fontweight="bold", zorder=8)
    fig.subplots_adjust(left=0.13, right=0.97, top=0.97, bottom=0.15)
    save(fig, out)


if __name__ == "__main__":
    draw_reference(OUT / "reference.pdf")
    draw_lamps(OUT / "lamps.pdf")
    draw_desks(OUT / "desks.pdf")
    draw_juice(OUT / "juice.pdf")
    draw_juice_profit(OUT / "juice-profit.pdf")
    # Practice exam, Part 3: Lakeside Smoothies' demand, MR, and MC; the
    # student marks E, then shades CS, PS, and DWL on the same graph.
    draw_smoothies(OUT / "smoothies.pdf", False)
    draw_smoothies(OUT / "smoothies-key.pdf", True)
    for name, a, b, mc, F in (("Luma Lamps", 100, 2, 20, 300), ("Pine Desks", 60, 1, 12, 200),
                              ("Lakeside Smoothies", 24, 1 / 5, 4, 150)):
        qs = (a - mc) / (2 * b); ps = a - b * qs; qe = (a - mc) / b
        cs = 0.5 * qs * (a - ps); pss = (ps - mc) * qs; dwl = 0.5 * (qe - qs) * (ps - mc)
        print(f"{name}: Q*={qs:g} P*={ps:g} CS={cs:g} PS={pss:g} profit={pss - F:g} "
              f"Q_eff={qe:g} DWL={dwl:g}")
