"""
Figures for Lecture 4: comparative advantage, specialization, and trade.

Run from the course root:

    python3 slides/figures/make_lecture4.py

No data downloads. Every number is the lecture's Pablo-and-Lin example (two
neighbors, one eight-hour Sunday of baking bread and making cheese), defined
once at the top so the slides, the notes, and the worksheet quote the same
figures, and so the opportunity costs and the gains are computed rather than
typed. The textbook's section 2.3 runs the same argument with its own pair,
Greta and Carlos.

The numbers are engineered so that the story works: Pablo has the absolute
advantage in both foods, Lin the comparative advantage in cheese, and complete
specialization raises the total of BOTH foods. That last part requires Lin's
cheese ceiling (4 lb) to exceed what the two consume under self-sufficiency
(2.5 lb); a Lin who is too small in cheese would make total cheese fall.

Output, in slides/img/:
  ppf-side.svg     the two production lines, at column size so the slide can
                   explain the picture beside it
  ppf-trade.svg    the same at full-slide size, plus what each produces alone
                   and what each consumes after specializing and trading,
                   which lies outside both lines

Accessibility: Okabe-Ito derived colours, and every series labelled on the
figure itself rather than in a legend keyed by colour; each bar carries its
value as text, so no comparison rests on judging two heights by eye; text
converted to paths so the SVG looks the same on any machine. Alt text lives
in the slide file beside each image.
"""

import argparse
import os
import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager

matplotlib.use("Agg")

# matplotlib's font cache does not see fonts installed in ~/Library/Fonts,
# so register the Fira Sans files directly. Lato, the deck's body font, ships
# inside TeX Live (the PDF build uses it from there), so register those TTFs
# too; the figures then match the slide typography. Falls back to sans-serif.
for f in Path.home().glob("Library/Fonts/FiraSans-*.otf"):
    font_manager.fontManager.addfont(str(f))
import glob as _glob
for pat in ("/usr/local/texlive/*/texmf-dist/fonts/truetype/typoland/lato/*.ttf",
            str(Path.home() / "Library/Fonts/Lato-*.ttf")):
    for f in _glob.glob(pat):
        font_manager.fontManager.addfont(f)

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
PABLO = "#0072B2"
LIN = "#BF5700"
BEFORE = "#d9d9d9"
AFTER = "#f0b27f"

FULL = (11.2, 6.0)
# Beside text in a column, as in make_lecture3.py.
SIDE = (8.2, 5.9)
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
# Output if the whole eight-hour Sunday goes into one food.
MAX = {
    "Pablo": {"cheese": 6, "bread": 12},
    "Lin": {"cheese": 4, "bread": 2},
}
# Self-sufficiency: each spends six of the eight hours on bread, two on cheese.
SHARE_ON_BREAD = {"Pablo": 0.75, "Lin": 0.75}
# The bargain they strike once they specialize: Lin sells cheese for bread.
CHEESE_SOLD, BREAD_PAID = 2, 2

PEOPLE = ("Pablo", "Lin")
GOODS = ("cheese", "bread")
COLOR = {"Pablo": PABLO, "Lin": LIN}


def alone(who: str) -> dict:
    """What each produces, and so consumes, with no one to trade with."""
    s = SHARE_ON_BREAD[who]
    return {"bread": MAX[who]["bread"] * s, "cheese": MAX[who]["cheese"] * (1 - s)}


def opportunity_cost(who: str, good: str) -> float:
    """Units of the other good given up per unit of this one."""
    other = "bread" if good == "cheese" else "cheese"
    return MAX[who][other] / MAX[who][good]


# Specialize completely in the food of comparative advantage, then trade.
SPECIALIST = {"Pablo": "bread", "Lin": "cheese"}
AFTER_TRADE = {
    "Pablo": {"cheese": CHEESE_SOLD, "bread": MAX["Pablo"]["bread"] - BREAD_PAID},
    "Lin": {"cheese": MAX["Lin"]["cheese"] - CHEESE_SOLD, "bread": BREAD_PAID},
}


def fmt(v: float) -> str:
    """1.5 as 1.5, 2.0 as 2."""
    return f"{v:g}"


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

def draw_ppf(out: Path, with_trade: bool, figsize=SIDE) -> None:
    """Both production lines on one pair of axes: cheese across, bread up.

    Sharing the axes is the whole point: Pablo's line is above Lin's
    everywhere, which is absolute advantage, while Lin's is flatter, which
    is her comparative advantage in cheese. The first version is the bare
    lines, shown before self-sufficiency comes up; the second adds what each
    produces alone and the two consumption points, which sit above both
    lines, outside what either could reach alone.
    """
    fig, ax = plt.subplots(figsize=figsize, dpi=100)
    side = figsize == SIDE
    fig.subplots_adjust(left=0.125 if side else 0.10, right=0.975 if side else 0.985,
                        top=0.97, bottom=0.15 if side else 0.145)
    ax.grid(color=GRID, lw=1, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=5, width=1)

    for who in PEOPLE:
        ax.plot([0, MAX[who]["cheese"]], [MAX[who]["bread"], 0], color=COLOR[who],
                lw=2.6, solid_capstyle="round", zorder=5)
    # Name labels sit just above each line, clear of the line itself and of
    # the alone/after-trade annotations on the with_trade version.
    ax.annotate("Pablo", xy=(4.3, 3.55), ha="left", va="bottom",
                fontsize=FONT, color=PABLO, fontweight="bold", zorder=8)
    ax.annotate("Lin", xy=(3.0, 0.62), ha="left", va="bottom",
                fontsize=FONT, color=LIN, fontweight="bold", zorder=8)

    if with_trade:
        for who in PEOPLE:
            a = alone(who)
            ax.plot(a["cheese"], a["bread"], marker="o", ms=13, color=COLOR[who], zorder=7)
            # Below and left of the point, which keeps it clear of the
            # after-trade label that sits above and right of it.
            ax.annotate(f"{who} alone", xy=(a["cheese"], a["bread"]), xytext=(-13, -12),
                        textcoords="offset points", ha="right", va="top",
                        fontsize=FONT, color=COLOR[who], zorder=8)
        for who in PEOPLE:
            t = AFTER_TRADE[who]
            ax.plot(t["cheese"], t["bread"], marker="D", ms=13, mfc="white",
                    mec=COLOR[who], mew=2.6, zorder=7)
            ax.annotate(f"{who} after trade", xy=(t["cheese"], t["bread"]),
                        xytext=(14, 8), textcoords="offset points", ha="left",
                        va="bottom", fontsize=FONT, color=COLOR[who], zorder=8)

    ax.set_xlabel("Pounds of cheese", fontsize=FONT, labelpad=8)
    ax.set_ylabel("Loaves of bread", fontsize=FONT, labelpad=8)
    ax.set_xlim(0, 6.5)
    ax.set_ylim(0, 13)
    ax.set_xticks(range(0, 7))
    ax.set_yticks(range(0, 13, 2))
    save(fig, out)


def draw_gains(out: Path) -> None:
    """Before and after, side by side, for each food.

    Two panels because loaves and pounds are not on the same scale. Every bar
    is labelled, so the point (every number goes up) does not depend on
    comparing bar heights across a gap.
    """
    fig, axes = plt.subplots(1, 2, figsize=FULL, dpi=100)
    fig.subplots_adjust(left=0.06, right=0.985, top=0.82, bottom=0.115, wspace=0.22)

    groups = [*PEOPLE, "Together"]
    x = range(len(groups))
    w = 0.36

    for ax, good in zip(axes, ("bread", "cheese")):
        before = [alone(p)[good] for p in PEOPLE]
        after = [AFTER_TRADE[p][good] for p in PEOPLE]
        before.append(sum(before))
        after.append(sum(after))

        for i, (b, a) in enumerate(zip(before, after)):
            for off, val, colour in ((-w / 2 - 0.02, b, BEFORE), (w / 2 + 0.02, a, AFTER)):
                ax.bar(i + off, val, width=w, color=colour, edgecolor=INK, lw=1.2, zorder=5)
                ax.text(i + off, val, fmt(val), ha="center", va="bottom",
                        fontsize=FONT - 6, color=INK, zorder=8)

        top = max(after) * 1.22
        ax.set_ylim(0, top)
        ax.set_xticks(list(x), groups, fontsize=FONT - 3)
        ax.set_title("Loaves of bread" if good == "bread" else "Pounds of cheese",
                     fontsize=FONT, color=INK, pad=12)
        ax.grid(axis="y", color=GRID, lw=1, zorder=0)
        ax.set_axisbelow(True)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.tick_params(axis="y", labelsize=FONT - 4, length=0)
        ax.tick_params(axis="x", length=0, pad=8)

    # One legend for both panels, above them, as text rather than a colour key
    # alone: the swatch is there, but each bar also carries its number.
    handles = [plt.Rectangle((0, 0), 1, 1, fc=BEFORE, ec=INK, lw=1.2),
               plt.Rectangle((0, 0), 1, 1, fc=AFTER, ec=INK, lw=1.2)]
    fig.legend(handles, ["On their own", "Specialize, then trade"],
               loc="upper center", ncol=2, frameon=False, fontsize=FONT - 3,
               bbox_to_anchor=(0.5, 1.005), handlelength=1.4, columnspacing=2.2)
    save(fig, out)


# -------------------------------------------------------------- main ------

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.parse_args()

    draw_ppf(IMG / "ppf-side.svg", with_trade=False)
    draw_ppf(IMG / "ppf-trade.svg", with_trade=True, figsize=FULL)

    # Numbers quoted on the slides and in the tables, printed so they can be
    # checked against what is written in the deck.
    print("\nvalues used in slide text")
    for who in PEOPLE:
        print(f"  {who}: {MAX[who]['bread']:g} loaves or {MAX[who]['cheese']:g} lb cheese; "
              f"1 lb cheese costs {opportunity_cost(who, 'cheese'):g} loaves, "
              f"1 loaf costs {opportunity_cost(who, 'bread'):g} lb")
    lower = min(PEOPLE, key=lambda w: opportunity_cost(w, "cheese"))
    print(f"  comparative advantage in cheese: {lower} "
          f"(and so in bread: {[p for p in PEOPLE if p != lower][0]})")
    for good in GOODS:
        b = sum(alone(p)[good] for p in PEOPLE)
        a = sum(AFTER_TRADE[p][good] for p in PEOPLE)
        print(f"  total {good}: {b:g} alone -> {a:g} with trade (+{a - b:g})")
    for who in PEOPLE:
        d = {g: AFTER_TRADE[who][g] - alone(who)[g] for g in GOODS}
        print(f"  {who} gains {d['bread']:g} loaves and {d['cheese']:g} lb cheese")
    return 0


if __name__ == "__main__":
    sys.exit(main())
