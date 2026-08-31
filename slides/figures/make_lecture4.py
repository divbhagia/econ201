"""
Figures for Lecture 4: comparative advantage, specialization, and trade.

Run from the course root:

    python3 slides/figures/make_lecture4.py

No data downloads. Every number is CORE Unit 2.3's Greta-and-Carlos example,
defined once at the top so the slides, the notes, and the worksheet quote the
same figures, and so the opportunity costs and the gains are computed rather
than typed.

Output, in slides/img/:
  ppf-side.svg     the two production lines, at column size so the slide can
                   explain the picture beside it
  ppf-trade-side.svg
                   the same, plus what each produces alone and what each
                   consumes after specializing and trading, which lies
                   outside both lines
  gains-trade.svg  before and after, apples and wheat, for each and in total
  price-range.svg  the prices of a ton of wheat, in apples, at which both gain:
                   between the two opportunity costs, with the deal marked

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
GRETA = "#0072B2"
CARLOS = "#BF5700"
BEFORE = "#d9d9d9"
AFTER = "#f0b27f"

FULL = (11.2, 6.0)
# Beside text in a column, as in make_lecture3.py.
SIDE = (8.2, 5.9)
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
# CORE Section 2.3. Output if all of the year goes into one crop.
MAX = {
    "Greta": {"apples": 1250, "wheat": 50},
    "Carlos": {"apples": 1000, "wheat": 20},
}
# Self-sufficiency: Greta spends 40% of her time on apples, Carlos 30%.
SHARE_ON_APPLES = {"Greta": 0.40, "Carlos": 0.30}
# The bargain they strike once they specialize: Greta sells wheat for apples.
WHEAT_SOLD, APPLES_BOUGHT = 15, 600

PEOPLE = ("Greta", "Carlos")
GOODS = ("apples", "wheat")
COLOR = {"Greta": GRETA, "Carlos": CARLOS}


def alone(who: str) -> dict:
    """What each produces, and so consumes, with no one to trade with."""
    s = SHARE_ON_APPLES[who]
    return {"apples": MAX[who]["apples"] * s, "wheat": MAX[who]["wheat"] * (1 - s)}


def opportunity_cost(who: str, good: str) -> float:
    """Units of the other good given up per unit of this one."""
    other = "wheat" if good == "apples" else "apples"
    return MAX[who][other] / MAX[who][good]


# Specialize completely in the good of comparative advantage, then trade.
SPECIALIST = {"Greta": "wheat", "Carlos": "apples"}
AFTER_TRADE = {
    "Greta": {"apples": APPLES_BOUGHT, "wheat": MAX["Greta"]["wheat"] - WHEAT_SOLD},
    "Carlos": {"apples": MAX["Carlos"]["apples"] - APPLES_BOUGHT, "wheat": WHEAT_SOLD},
}


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
    """Both production lines on one pair of axes.

    Sharing the axes is the whole point: Greta's line is above Carlos's
    everywhere, which is absolute advantage, while Carlos's is flatter, which
    is his comparative advantage in apples. On the second version the two
    consumption points sit above both lines, outside what either could reach
    alone.
    """
    fig, ax = plt.subplots(figsize=figsize, dpi=100)
    side = figsize == SIDE
    fig.subplots_adjust(left=0.155 if side else 0.115, right=0.975 if side else 0.985,
                        top=0.97, bottom=0.15 if side else 0.145)
    ax.grid(color=GRID, lw=1, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.tick_params(length=5, width=1)

    for who in PEOPLE:
        ax.plot([0, MAX[who]["apples"]], [MAX[who]["wheat"], 0], color=COLOR[who],
                lw=2.6, solid_capstyle="round", zorder=5)
        ax.annotate(who, xy=(28, MAX[who]["wheat"] - 2.6), ha="left", va="top",
                    fontsize=FONT, color=COLOR[who], fontweight="bold", zorder=8)

    if with_trade:
        for who in PEOPLE:
            a = alone(who)
            ax.plot(a["apples"], a["wheat"], marker="o", ms=13, color=COLOR[who], zorder=7)
            # Below and left of the point, which keeps it clear of the
            # after-trade label that sits above and right of it.
            ax.annotate(f"{who} alone", xy=(a["apples"], a["wheat"]), xytext=(-13, -12),
                        textcoords="offset points", ha="right", va="top",
                        fontsize=FONT - 4, color=COLOR[who], zorder=8)
        for who, (dx, dy) in zip(PEOPLE, ((14, 8), (14, 8))):
            t = AFTER_TRADE[who]
            ax.plot(t["apples"], t["wheat"], marker="D", ms=13, mfc="white",
                    mec=COLOR[who], mew=2.6, zorder=7)
            ax.annotate(f"{who} after trade", xy=(t["apples"], t["wheat"]),
                        xytext=(dx, dy), textcoords="offset points", ha="left",
                        va="bottom", fontsize=FONT - 4, color=COLOR[who],
                        fontweight="bold", zorder=8)

    ax.set_xlabel("Apples", fontsize=FONT, labelpad=8)
    ax.set_ylabel("Tons of wheat", fontsize=FONT, labelpad=8)
    ax.set_xlim(0, 1330)
    ax.set_ylim(0, 56)
    ax.set_xticks(range(0, 1301, 250))
    ax.set_yticks(range(0, 56, 10))
    save(fig, out)


def draw_price_range(out: Path) -> None:
    """The prices of a ton of wheat, in apples, that leave both better off.

    A number line: Greta will not sell a ton for fewer apples than it costs
    her to grow (25), Carlos will not pay more than growing a ton costs him
    (50). Between the two both gain; the deal on the slides, 40, sits inside.
    Each region is labelled in words, so nothing rests on the shading alone.
    """
    lo = opportunity_cost("Greta", "wheat")     # 25 apples per ton
    hi = opportunity_cost("Carlos", "wheat")    # 50 apples per ton
    deal = APPLES_BOUGHT / WHEAT_SOLD           # 40 apples per ton

    fig, ax = plt.subplots(figsize=(11.2, 3.4), dpi=100)
    fig.subplots_adjust(left=0.03, right=0.97, top=0.98, bottom=0.26)
    ax.axvspan(lo, hi, color="#FDF3EA", zorder=0)
    ax.axhline(0, color=INK, lw=1.6, zorder=3)
    for x, who, txt in ((lo, "Greta", f"Greta's cost of a ton:\n{lo:.0f} apples"),
                        (hi, "Carlos", f"Carlos's cost of a ton:\n{hi:.0f} apples")):
        ax.plot([x, x], [-0.18, 0.18], color=COLOR[who], lw=3, zorder=4)
        ax.annotate(txt, xy=(x, 0.22), ha="center", va="bottom", fontsize=FONT - 4,
                    color=COLOR[who], fontweight="bold", zorder=8)
    ax.plot(deal, 0, marker="D", ms=14, mfc="white", mec=INK, mew=2.4, zorder=6)
    ax.annotate(f"The deal: {deal:.0f} apples per ton", xy=(deal, -0.22), ha="center",
                va="top", fontsize=FONT - 4, color=INK, zorder=8)
    for x, txt in (((lo + 12) / 2, "Greta refuses:\nshe could grow it for less"),
                   ((hi + 63) / 2, "Carlos refuses:\nhe could grow it for less"),
                   ((lo + hi) / 2, "both gain")):
        ax.annotate(txt, xy=(x, 0.78), ha="center", va="center", fontsize=FONT - 5,
                    color="#595a5b", zorder=8)
    ax.set_xlim(12, 63)
    ax.set_ylim(-0.75, 1.0)
    ax.set_xticks(range(15, 61, 5))
    ax.set_yticks([])
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_position(("data", -0.55))
    ax.tick_params(length=5, width=1, labelsize=FONT - 4)
    ax.set_xlabel("Apples per ton of wheat", fontsize=FONT - 2, labelpad=6)
    save(fig, out)


def draw_gains(out: Path) -> None:
    """Before and after, side by side, for each good.

    Two panels because apples and wheat are not on the same scale. Every bar
    is labelled, so the point (every number goes up) does not depend on
    comparing bar heights across a gap.
    """
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 6.0), dpi=100)
    fig.subplots_adjust(left=0.075, right=0.985, top=0.82, bottom=0.115, wspace=0.22)

    groups = [*PEOPLE, "Together"]
    x = range(len(groups))
    w = 0.36

    for ax, good in zip(axes, GOODS):
        before = [alone(p)[good] for p in PEOPLE]
        after = [AFTER_TRADE[p][good] for p in PEOPLE]
        before.append(sum(before))
        after.append(sum(after))

        for i, (b, a) in enumerate(zip(before, after)):
            for off, val, colour in ((-w / 2 - 0.02, b, BEFORE), (w / 2 + 0.02, a, AFTER)):
                ax.bar(i + off, val, width=w, color=colour, edgecolor=INK, lw=1.2, zorder=5)
                ax.text(i + off, val, f"{val:,.0f}", ha="center", va="bottom",
                        fontsize=FONT - 6, color=INK, zorder=8)

        top = max(after) * 1.22
        ax.set_ylim(0, top)
        ax.set_xticks(list(x), groups, fontsize=FONT - 3)
        ax.set_title("Apples" if good == "apples" else "Tons of wheat",
                     fontsize=FONT, color=INK, pad=12)
        ax.grid(axis="y", color=GRID, lw=1, zorder=0)
        ax.set_axisbelow(True)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
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
    draw_ppf(IMG / "ppf-trade-side.svg", with_trade=True)
    draw_gains(IMG / "gains-trade.svg")
    draw_price_range(IMG / "price-range.svg")

    # Numbers quoted on the slides and in the tables, printed so they can be
    # checked against what is written in the deck.
    print("\nvalues used in slide text")
    for who in PEOPLE:
        print(f"  {who}: {MAX[who]['apples']:,} apples or {MAX[who]['wheat']} t wheat; "
              f"1 t wheat costs {opportunity_cost(who, 'wheat'):,.0f} apples, "
              f"1 apple costs {opportunity_cost(who, 'apples'):.2f} t wheat")
    lower = min(PEOPLE, key=lambda w: opportunity_cost(w, "apples"))
    print(f"  comparative advantage in apples: {lower} "
          f"(and so in wheat: {[p for p in PEOPLE if p != lower][0]})")
    for good in GOODS:
        b = sum(alone(p)[good] for p in PEOPLE)
        a = sum(AFTER_TRADE[p][good] for p in PEOPLE)
        print(f"  total {good}: {b:,.0f} alone -> {a:,.0f} with trade (+{a - b:,.0f})")
    for who in PEOPLE:
        d = {g: AFTER_TRADE[who][g] - alone(who)[g] for g in GOODS}
        print(f"  {who} gains {d['apples']:,.0f} apples and {d['wheat']:,.0f} t wheat")
    return 0


if __name__ == "__main__":
    sys.exit(main())
