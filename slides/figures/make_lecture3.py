"""
Figures for Lecture 3: opportunity cost, economic rent, incentives, and models.

Run from the course root:

    python3 slides/figures/make_lecture3.py

No data downloads. Every number belongs to the free-Saturday example, CORE
Unit 2.2's decision model with a Saturday shift as the outside option,
kept here in one place so the slides, the notes, and the worksheet agree.

Output, in slides/img/:
  rent.svg            net benefit of each option, and the rent as the gap
  econ-cost.svg       benefit against economic cost = direct + opportunity,
                      no rent annotation
  model-box.svg       exogenous in, endogenous out, cf. CORE Section 2.8
  looking-at-less.svg the tangle of real decisions beside a two-box model

Accessibility: Okabe-Ito derived tints, light enough that the labels inside
each bar keep well above 4.5:1 against them; every quantity is written on the
figure as well as encoded in a length, so nothing depends on reading a colour
or comparing two bar heights by eye; text converted to paths so the SVG looks
the same on any machine. Alt text lives in the slide file beside each image.
"""

import argparse
import os
import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

matplotlib.use("Agg")

# matplotlib's font cache does not see fonts installed in ~/Library/Fonts,
# so register the Fira Sans files directly. Falls back to sans-serif.
for f in Path.home().glob("Library/Fonts/FiraSans-*.otf"):
    font_manager.fontManager.addfont(str(f))

ROOT = Path(__file__).resolve().parents[2]
IMG = ROOT / "slides" / "img"
# PDF copies of the figures the worksheets use, so slides and handouts share
# one source. Real text (Type 42) so the PDF stays searchable and taggable.
PDF_DIR = ROOT / "worksheets" / "figures"
# Add a figure's stem here when a worksheet starts using it.
WORKSHEET_FIGS = set()
SCRATCH = Path(os.environ["FIG_PREVIEW_DIR"]) if os.environ.get("FIG_PREVIEW_DIR") else None

INK = "#1a1a1a"
GRID = "#d9d9d9"
# Light tints of the course accent and of Okabe-Ito blue. Dark text on these
# clears 4.5:1 comfortably; the strong versions are kept for edges and rules.
NET = "#f0b27f"      # net benefit
DIRECT = "#dcdcdc"   # direct cost
OPP = "#9ccbea"      # opportunity cost
ACCENT = "#BF5700"

# Beside text on a slide the image fits the column width, so a squarer shape
# makes it taller; type is scaled up because the image is drawn smaller.
SIDE = (8.2, 5.9)
FULL = (11.2, 6.0)
FONT = 22

plt.rcParams.update(
    {
        "font.family": ["Fira Sans", "sans-serif"],
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
# CORE Section 2.2's decision model, on a free Saturday: a Dodgers game or a
# four-hour campus shift. Two mutually exclusive uses of the same day.
#
# In class the two benefits come from Mentimeter polls, so they differ for
# every student. These are the canonical answers the worked slides use.
GAME_BENEFIT = 200   # polled: the most you would pay for the whole day
GAME_COST = 100      # the total quoted on the slide; itemised below
SHIFT_PAY = 120      # four hours at $30
SHIFT_COST = 80      # polled: the least you would take to give up the afternoon

GAME_NET = GAME_BENEFIT - GAME_COST       # 100
SHIFT_NET = SHIFT_PAY - SHIFT_COST        # 40
OPP_COST = SHIFT_NET                      # the outside option
ECON_COST = GAME_COST + OPP_COST          # 140
RENT = GAME_NET - SHIFT_NET               # 60
TOP = 244                                 # room above the taller bar
TICKS = range(0, 201, 50)

# Where the $130 comes from, at 2026 Orange County prices. The slides quote
# only the total, since itemising it in class pulls attention onto the price
# of a Dodger dog. Kept here, and checked by main(), as the record that the
# total is a real one.
OUTING = (
    ("Ticket, upper reserve", 45),
    ("Parking", 30),
    ("Food and a drink", 15),
    ("Gas, Fullerton and back", 10),
)


def dollars(x, _pos=None) -> str:
    return f"${x:,.0f}"


def new_axes(figsize=SIDE, font=FONT, bottom=0.10):
    plt.rcParams.update({"font.size": font, "xtick.labelsize": font, "ytick.labelsize": font})
    fig, ax = plt.subplots(figsize=figsize, dpi=100)
    fig.subplots_adjust(left=0.155, right=0.98, top=0.99, bottom=bottom)
    ax.grid(axis="y", color=GRID, lw=1, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", length=0, pad=10)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(dollars))
    return fig, ax


def segment(ax, x, bottom, height, color, label, width=0.52, font=FONT - 4,
            label_y=None):
    """One piece of a stacked bar, with its own label written inside it.

    label_y overrides the centred position, for the one segment a dashed
    reference line would otherwise cut straight through.
    """
    ax.bar(x, height, bottom=bottom, width=width, color=color, edgecolor="white",
           linewidth=1.5, zorder=5)
    ax.text(x, bottom + height / 2 if label_y is None else label_y, label,
            ha="center", va="center", fontsize=font, color=INK, zorder=8,
            linespacing=1.15)


def bracket(ax, x, low, high, text=None, font=FONT - 4):
    """A double-headed arrow spanning [low, high].

    With text, it is set to the right of the arrow, which only fits when the
    span is tall enough to hold a line of type. A short span passes text=None
    and gets its label from callout() instead.
    """
    ax.add_patch(FancyArrowPatch((x, low), (x, high), arrowstyle="<|-|>",
                                 mutation_scale=14, lw=1.8, color=ACCENT,
                                 shrinkA=0, shrinkB=0, zorder=9))
    if text:
        ax.text(x + 0.06, (low + high) / 2, text, ha="left", va="center",
                fontsize=font, color=ACCENT, zorder=9, linespacing=1.15)


def callout(ax, text, xy, xytext, font=FONT - 4):
    """A label parked in clear space, with a leader down to what it names."""
    ax.annotate(text, xy=xy, xytext=xytext, ha="center", va="center",
                fontsize=font, color=ACCENT, zorder=9,
                arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=1.6,
                                shrinkA=6, shrinkB=3))


def save(fig, out: Path) -> None:
    IMG.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format="svg")
    if out.stem in WORKSHEET_FIGS:
        PDF_DIR.mkdir(parents=True, exist_ok=True)
        fig.savefig(PDF_DIR / f"{out.stem}.pdf", format="pdf")
    if SCRATCH:
        fig.savefig(SCRATCH / f"{out.stem}.png", format="png", dpi=110)
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


# ----------------------------------------------------------- drawing ------

def draw_rent(out: Path) -> None:
    """Net benefit sits at the bottom of each bar so the two are comparable.

    Stacking the direct cost on top keeps every bar's full height equal to the
    benefit, and puts both net benefits on the same baseline, which is what
    makes the rent readable as the gap between them.
    """
    fig, ax = new_axes()
    # Label pushed low: the dashed line marking the shift's net benefit
    # crosses this segment at the height it would otherwise sit.
    segment(ax, 0, 0, GAME_NET, NET, f"Net benefit\n${GAME_NET}",
            label_y=SHIFT_NET / 2 - 4)
    segment(ax, 0, GAME_NET, GAME_COST, DIRECT, f"The day out\n${GAME_COST}")
    segment(ax, 1, 0, SHIFT_NET, NET, f"Net benefit\n${SHIFT_NET}")
    segment(ax, 1, SHIFT_NET, SHIFT_COST, DIRECT, f"Giving up the\nafternoon ${SHIFT_COST}")

    ax.text(0, GAME_BENEFIT + 4, f"Worth ${GAME_BENEFIT}", ha="center",
            va="bottom", fontsize=FONT - 4, color=INK)
    ax.text(1, SHIFT_PAY + 4, f"Pays ${SHIFT_PAY}", ha="center",
            va="bottom", fontsize=FONT - 4, color=INK)

    ax.plot([-0.42, 1.42], [SHIFT_NET, SHIFT_NET], ls=(0, (4, 3)), lw=1.6,
            color=ACCENT, zorder=7)
    bracket(ax, 0.31, SHIFT_NET, GAME_NET, f"Economic\nrent ${RENT}")

    ax.set_xticks([0, 1], ["Go to the game", "Work the shift"])
    ax.set_xlim(-0.6, 1.6)
    ax.set_ylim(0, TOP)
    ax.set_yticks(TICKS)
    save(fig, out)


def draw_econ_cost(out: Path) -> None:
    """The same decision the other way round: benefit against economic cost."""
    # Two-line tick labels below the axis, so the bottom margin is deeper.
    fig, ax = new_axes(bottom=0.175)
    segment(ax, 0, 0, GAME_BENEFIT, NET, f"Worth\n${GAME_BENEFIT}")
    segment(ax, 1, 0, GAME_COST, DIRECT, f"The day out\n${GAME_COST}")
    segment(ax, 1, GAME_COST, OPP_COST, OPP, f"Opportunity\ncost ${OPP_COST}")

    # No rent annotation here: this figure appears on the opportunity cost
    # slide, before rent has been defined. rent.svg carries that.

    ax.set_xticks([0, 1], [f"Benefit\n${GAME_BENEFIT}",
                           f"Economic cost\n${ECON_COST}"])
    ax.set_xlim(-0.6, 1.6)
    ax.set_ylim(0, TOP)
    ax.set_yticks(TICKS)
    save(fig, out)


def draw_model_box(out: Path) -> None:
    """What a model takes in, what it explains, and what it holds fixed."""
    fig, ax = plt.subplots(figsize=(10.6, 5.7), dpi=100)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    ax.set_xlim(0, 10.6)
    ax.set_ylim(0, 5.7)
    ax.axis("off")

    ax.add_patch(FancyBboxPatch((3.55, 1.55), 3.5, 2.7,
                                boxstyle="round,pad=0.12,rounding_size=0.22",
                                fc="#f4f4f4", ec=INK, lw=2.2, zorder=4))
    ax.text(5.3, 3.62, "The model", ha="center", va="center", fontsize=25,
            color=INK, fontweight="bold", zorder=6)
    ax.text(5.3, 2.55, "the decision rule:\nnet benefit against\nopportunity cost", ha="center",
            va="center", fontsize=19, color=INK, zorder=6, linespacing=1.35)

    # \$ keeps matplotlib's mathtext from treating the dollar amounts as math.
    for term, gloss, x, ha, colour in (
        ("Exogenous", "Set from outside\ne.g. the \$100 day out,\nthe \$120 shift pay", 0.15, "left", "#0072B2"),
        ("Endogenous", "Explained by the model\ne.g. Sam's choice:\ngo to the game",
         10.45, "right", ACCENT),
    ):
        ax.text(x, 3.45, term, ha=ha, va="center", fontsize=21, color=colour,
                fontweight="bold", zorder=6)
        ax.text(x, 2.55, gloss, ha=ha, va="center", fontsize=19, color=colour,
                zorder=6, linespacing=1.35)

    for x0, x1 in ((3.0, 3.45), (7.15, 7.6)):
        ax.add_patch(FancyArrowPatch((x0, 2.9), (x1, 2.9), arrowstyle="-|>",
                                     mutation_scale=26, lw=2.4, color=INK, zorder=5))

    ax.text(5.3, 0.75, "Everything else is held fixed: "
            r"$\it{ceteris}$ $\it{paribus}$", ha="center", va="center",
            fontsize=19, color="#595a5b", zorder=6)
    ax.text(5.3, 5.1, "Equilibrium: nothing changes\nuntil something outside does",
            ha="center", va="center", fontsize=19, color="#595a5b", zorder=6,
            linespacing=1.3)
    save(fig, out)


def draw_looking_at_less(out: Path) -> None:
    """The point of Section 2.8, as a picture: detail on the left, model right.

    The left panel is deliberately unreadable. It is not data, and the slide's
    alt text says so.
    """
    rng = np.random.default_rng(201)
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 5.4), dpi=100)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.97, bottom=0.02, wspace=0.10)

    left, right = axes
    for ax in axes:
        ax.set_xlim(0, 10)
        ax.set_ylim(-1.9, 10)
        ax.set_aspect("equal")
        ax.axis("off")

    pts = rng.uniform(0.6, 9.4, size=(150, 2))
    for i, j in rng.integers(0, len(pts), size=(240, 2)):
        if i != j:
            left.plot(*zip(pts[i], pts[j]), color="#b8b8b8", lw=0.6, zorder=2)
    left.scatter(pts[:, 0], pts[:, 1], s=26, color="#595a5b", zorder=3)
    left.text(5, -1.1, "Millions of decisions,\nall at once", ha="center", va="center",
              fontsize=21, color=INK, fontweight="bold", linespacing=1.25)

    boxes = (("Households", 1.5, 6.9, "#cfe4f4"), ("Firms", 1.5, 1.9, "#f0b27f"))
    for label, x, y, colour in boxes:
        right.add_patch(FancyBboxPatch((x, y), 7.0, 2.1,
                                       boxstyle="round,pad=0.1,rounding_size=0.2",
                                       fc=colour, ec=INK, lw=2.2, zorder=4))
        right.text(x + 3.5, y + 1.05, label, ha="center", va="center", fontsize=24,
                   color=INK, zorder=6)
    right.add_patch(FancyArrowPatch((3.6, 6.8), (3.6, 4.1), arrowstyle="-|>",
                                    mutation_scale=24, lw=2.2, color=INK, zorder=5))
    right.add_patch(FancyArrowPatch((6.4, 4.1), (6.4, 6.8), arrowstyle="-|>",
                                    mutation_scale=24, lw=2.2, color=INK, zorder=5))
    right.text(3.4, 5.45, "work", ha="right", va="center", fontsize=19, color="#595a5b")
    right.text(6.6, 5.45, "wages,\ngoods", ha="left", va="center", fontsize=19,
               color="#595a5b", linespacing=1.2)
    right.text(5, -1.1, "The few that matter\nfor the question at hand", ha="center",
               va="center", fontsize=21, color=INK, fontweight="bold", linespacing=1.25)
    save(fig, out)


# -------------------------------------------------------------- main ------

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.parse_args()

    draw_rent(IMG / "rent.svg")
    draw_econ_cost(IMG / "econ-cost.svg")
    draw_model_box(IMG / "model-box.svg")
    draw_looking_at_less(IMG / "looking-at-less.svg")

    # Numbers quoted on the slides, printed so the text can be checked.
    print("\nvalues used in slide text")
    for label, amount in OUTING:
        print(f"  {label:28s} ${amount}")
    total = sum(a for _, a in OUTING)
    print(f"  {'the day out':28s} ${total}"
          f"   {'OK' if total == GAME_COST else 'DOES NOT MATCH ' + str(GAME_COST)}")
    print(f"  game:  worth ${GAME_BENEFIT}, costs ${GAME_COST}, net ${GAME_NET}")
    print(f"  shift: pays ${SHIFT_PAY}, costs ${SHIFT_COST}, net ${SHIFT_NET}")
    print(f"  opportunity cost of the game  = ${OPP_COST}")
    print(f"  opportunity cost of the shift = ${GAME_NET}")
    print(f"  economic cost of the game  = ${GAME_COST} + ${OPP_COST} = ${ECON_COST}"
          f"  vs benefit ${GAME_BENEFIT}, so go")
    print(f"  economic cost of the shift = ${SHIFT_COST} + ${GAME_NET} = "
          f"${SHIFT_COST + GAME_NET}  vs benefit ${SHIFT_PAY}, so no")
    print(f"  economic rent = ${GAME_NET} - ${SHIFT_NET} = ${RENT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
