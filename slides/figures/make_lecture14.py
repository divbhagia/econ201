"""
Numbers, cards, and figures for Lecture 14: the classroom market experiment
(a pit market for half a dozen tamales from a home cook; one card is one order).

Run from the course root:

    python3 slides/figures/make_lecture14.py

No data downloads. Everything comes from one card schedule, CARDS: pair k
is a buyer card and a seller card, values $2 to $10 as in Holt's
playing-card version. The cards come in identical bundles of six, one
sheet each: buyers 10, 9, 8, 7, 4, 3 and sellers 2, 3, 4, 5, 8, 9, top
to bottom. Deal whole bundles, or the top k of a buyer bundle with the
top k of a seller bundle; either way every bundle is balanced around $6:
four pairs trade and the last two should not, whatever the headcount, so
the curves cross two thirds of the way across. The clearing price is $5
to $7 for any number of pairs from 1 to 30, and the quantity is about four
fifths of the pairs dealt. main() verifies this
for every headcount. Rounds repeat with the same cards reshuffled; how
many is decided in class.

A buyer's value is the most they will pay; a seller's cost is the least
they will accept (CORE's WTP and WTA). Buyers earn value minus price,
sellers price minus cost. One trade per
round, never at a loss.

Output:
  experiment/cards-buyers.html, cards-sellers.html  the cards, printed to PDF by experiment/print_cards.py
  experiment/market-data.json   the schedule for the live price board
  slides/img/market-demand.svg  the 10-pair demand steps, buyers ranked
  slides/img/market-supply.svg  the 10-pair supply steps, sellers ranked
  slides/img/market-equilibrium.svg  both, clearing range and quantity
  slides/img/market-surplus.svg  the same with each trade's gain shaded

Figures are the 10-pair case (20 students), the deck's worked example;
the live board draws the real one. Demand in Okabe-Ito blue, supply in
dark orange, each labelled on the figure; text converted to paths. Alt
text lives beside each image in the deck.
"""

import glob as _glob
import json
import os
import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle

matplotlib.use("Agg")

for f in Path.home().glob("Library/Fonts/FiraSans-*.otf"):
    font_manager.fontManager.addfont(str(f))
for pat in ("/usr/local/texlive/*/texmf-dist/fonts/truetype/typoland/lato/*.ttf",
            str(Path.home() / "Library/Fonts/Lato-*.ttf")):
    for f in _glob.glob(pat):
        font_manager.fontManager.addfont(f)

ROOT = Path(__file__).resolve().parents[2]
IMG = ROOT / "slides" / "img"
EXP = ROOT / "experiment"
SCRATCH = Path(os.environ["FIG_PREVIEW_DIR"]) if os.environ.get("FIG_PREVIEW_DIR") else None

INK = "#1a1a1a"
DEMAND = "#0072B2"               # Okabe-Ito blue, 5.1:1 on white
SUPPLY = "#8f4100"               # dark orange, 7.7:1 on white
RULE = "#595a5b"
SHADE_D = "#0072B2"
SHADE_S = "#E69F00"

SIDE = (8.8, 6.0)
FONT = 32

plt.rcParams.update(
    {
        "font.family": ["Lato", "Fira Sans", "sans-serif"],
        "font.size": FONT,
        "svg.fonttype": "path",
        "pdf.fonttype": 42,
    }
)

# ------------------------------------------------------- the schedule -----
GOOD = "half a dozen tamales"        # one card is one order
GOOD_PLURAL = "Orders of tamales"        # axis label
SCALE = 1                                # dollars per step
BUNDLE = [(10, 2), (9, 3), (8, 4), (7, 5), (4, 8), (3, 9)]   # one sheet of buyers, one of sellers
CARDS = [(v * SCALE, c * SCALE) for v, c in BUNDLE * 5]   # 30 pairs, five bundles
EXAMPLE_PAIRS = 12                       # the deck's worked case, 24 students (two bundles)
PRICE_TOP = 12 * SCALE
TICK = 2 * SCALE


def buyers(n, shift=0):
    return [v + shift for v, _ in CARDS[:n]]


def sellers(n):
    return [c for _, c in CARDS[:n]]


def demand(values, p):
    return sum(v >= p for v in values)


def supply(costs, p):
    return sum(c <= p for c in costs)


def clearing(values, costs):
    """Whole-dollar prices at which demand equals supply, and the quantity."""
    prices = [p for p in range(1, PRICE_TOP + 1) if demand(values, p) == supply(costs, p)]
    return prices, demand(values, prices[0])


def total_surplus(values, costs):
    """Highest-value buyers matched with lowest-cost sellers, while the
    match gains."""
    return sum(v - c for v, c in zip(sorted(values, reverse=True), sorted(costs)) if v > c)


# ------------------------------------------------------- cards ------------
CARD_CSS = """
@page { size: letter; margin: 0.5in; }
@font-face { font-family: "Fira Sans"; src: local("Fira Sans"), local("FiraSans-Regular"); }
@font-face { font-family: "Fira Sans"; font-weight: 700; src: local("Fira Sans Bold"), local("FiraSans-Bold"); }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; font-family: "Fira Sans", "Helvetica Neue", Arial, sans-serif; color: #000; }
/* Six cards per page in a 2 by 3 grid. Every cell draws all four of its
   borders, pulled together by a negative gap, so the cut lines are single
   and the outer lines sit inside the printable area. */
.page { width: 7.5in; height: 10in; display: grid; grid-template-columns: repeat(2, 1fr);
        grid-template-rows: repeat(3, 1fr); grid-auto-flow: column; gap: 0; break-after: page; }
.page:last-child { break-after: auto; }
.card { border: 0.7pt solid #000; margin: 0 -0.35pt -0.35pt 0; padding: 0.22in 0.32in 0.24in;
        display: flex; flex-direction: column; justify-content: flex-end; }
.mid { flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; }
.side { font-size: 22pt; font-weight: 700; letter-spacing: 0.16em; text-transform: uppercase; }
.value { font-size: 46pt; font-weight: 700; line-height: 1.05; margin-top: 2pt; }
.note { font-size: 11pt; line-height: 1.35; margin: 0; padding: 8pt 0 0 1.1em; border-top: 0.6pt solid #000; }
.note li { margin: 0 0 3pt; }
.back .side { font-size: 36pt; letter-spacing: 0.22em; }
.blank { border: none; }
"""


def card_html(side, value):
    """Generic wording, so the same cards serve any good."""
    if side == "Buyer":
        items = ["The number above is your value for the good. Keep it private.",
                 "Find a seller who will take less than your value. Your gain is value minus price."]
    else:
        items = ["The number above is your cost for the good. Keep it private.",
                 "Find a buyer who will pay more than your cost. Your gain is price minus cost."]
    return (f'<div class="card"><div class="mid"><div class="side">{side}</div>'
            f'<div class="value">${value}</div></div>'
            '<ul class="note">' + "".join(f"<li>{i}</li>" for i in items) + "</ul></div>")


def back_html(side):
    return f'<div class="card back"><div class="mid"><div class="side">{side}</div></div></div>'


def write_cards():
    """experiment/cards-buyers.html and cards-sellers.html: two pages
    each, one bundle of six cards (filling down the left column, then the
    right) and its page of backs. Every bundle is identical, so print as
    many copies as the class needs (double-sided, flip on the long edge).
    experiment/print_cards.py turns them into PDFs."""
    EXP.mkdir(exist_ok=True)
    for side, cards in (("Buyer", [card_html("Buyer", v) for v, _ in BUNDLE]),
                        ("Seller", [card_html("Seller", c) for _, c in BUNDLE])):
        pages = ['<div class="page">' + "".join(cards) + "</div>",
                 '<div class="page">' + back_html(side) * len(cards) + "</div>"]
        html = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
                f"<title>ECON 201 Market Experiment: {side} Cards</title>"
                "<!-- Written by slides/figures/make_lecture14.py. Do not edit. -->"
                f"<style>{CARD_CSS}</style></head><body>\n" + "\n".join(pages) + "\n</body></html>\n")
        name = f"cards-{side.lower()}s"
        (EXP / f"{name}.html").write_text(html)
        print(f"wrote experiment/{name}.html")

    data = {"good": GOOD, "plural": GOOD_PLURAL, "scale": SCALE, "top": PRICE_TOP, "tick": TICK,
            "buyers": [v for v, _ in CARDS], "sellers": [c for _, c in CARDS]}
    (EXP / "market-data.json").write_text(json.dumps(data, indent=1) + "\n")
    print("wrote experiment/market-data.json")


# ------------------------------------------------------- figures ----------
def save(fig, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format="svg")
    if SCRATCH:
        fig.savefig(SCRATCH / f"{out.stem}.png", format="png", dpi=110)
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


def axes(n):
    fig, ax = plt.subplots(figsize=SIDE, dpi=100)
    fig.subplots_adjust(left=0.14, right=0.97, top=0.96, bottom=0.17)
    ax.set_xlim(0, n + 0.6)
    ax.set_ylim(0, PRICE_TOP)
    ax.set_xticks(range(0, n + 1))
    ax.set_yticks(range(0, PRICE_TOP + 1, TICK))
    ax.set_yticklabels([f"${p}" for p in range(0, PRICE_TOP + 1, TICK)])
    ax.set_xlabel(GOOD_PLURAL, labelpad=8)
    ax.set_ylabel("Price", labelpad=8)
    ax.grid(True, color="#d9d9d9", linewidth=1)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(RULE)
    ax.tick_params(colors=INK, length=0)
    return fig, ax


def steps(ax, heights, color, label, where):
    """One dot per card at (k, heights[k-1]), k = 1..n, joined by a line
    (CORE draws its few-trader curves this way too); label the curve."""
    ks = range(1, len(heights) + 1)
    ax.plot(ks, heights, color=color, linewidth=4, marker="o", markersize=11, zorder=3)
    x, y = where
    ax.text(x, y, label, color=color, fontsize=FONT, fontweight="bold",
            ha="left", va="center")


def qlabel(ax, q):
    ax.text(q, 0.25 * SCALE, f"Q = {q}", color=INK, fontsize=FONT * 0.75, ha="center", va="bottom",
            bbox=dict(facecolor="white", edgecolor="none", pad=2))


def demand_steps(n, shift=0):
    return sorted(buyers(n, shift), reverse=True)


def supply_steps(n):
    return sorted(sellers(n))


def fig_demand(n):
    fig, ax = axes(n)
    d = demand_steps(n)
    steps(ax, d, DEMAND, "Demand", (n - 2.6, 1.6 * SCALE))
    for k, v in enumerate(d):
        ax.text(k + 1, v + 0.55 * SCALE, f"{v}", color=DEMAND, fontsize=FONT * 0.6,
                ha="center", va="bottom")
    save(fig, IMG / "market-demand.svg")


def fig_supply(n):
    fig, ax = axes(n)
    s = supply_steps(n)
    steps(ax, s, SUPPLY, "Supply", (n - 2.6, 10.6 * SCALE))
    for k, c in enumerate(s):
        ax.text(k + 1, c - 0.55 * SCALE, f"{c}", color=SUPPLY, fontsize=FONT * 0.6,
                ha="center", va="top")
    save(fig, IMG / "market-supply.svg")


def fig_equilibrium(n, shade=False, out="market-equilibrium.svg"):
    fig, ax = axes(n)
    d, s = demand_steps(n), supply_steps(n)
    prices, q = clearing(buyers(n), sellers(n))
    lo, hi = prices[0], prices[-1]
    if shade:
        mid = 6 * SCALE
        ks = list(range(1, q + 1))
        ax.fill_between(ks, [mid] * q, d[:q], color=SHADE_D, alpha=0.25, linewidth=0)
        ax.fill_between(ks, s[:q], [mid] * q, color=SHADE_S, alpha=0.35, linewidth=0)
    ax.axhspan(lo, hi, xmin=0, xmax=1, color="#bbbbbb", alpha=0.35, linewidth=0)
    steps(ax, d, DEMAND, "Demand", (n - 2.6, 1.6 * SCALE))
    steps(ax, s, SUPPLY, "Supply", (n - 2.6, 10.6 * SCALE))
    ax.vlines(q, 0, 6 * SCALE, color=INK, linewidth=2, linestyle=(0, (4, 4)))
    qlabel(ax, q)
    ax.text(0.15, hi + 0.25 * SCALE, f"P = \\${lo} to \\${hi}", color=INK, fontsize=FONT * 0.75,
            ha="left", va="bottom")
    if shade:
        ax.text(2.6, 8.4 * SCALE, "Buyers' gains", color="#005f94", fontsize=FONT * 0.65, ha="center")
        ax.text(2.6, 3.6 * SCALE, "Sellers' gains", color=SUPPLY, fontsize=FONT * 0.65, ha="center")
    save(fig, IMG / out)


# ------------------------------------------------------- main -------------
def main() -> int:
    bad = []
    for n in range(1, len(CARDS) + 1):
        p, q = clearing(buyers(n), sellers(n))
        if 6 * SCALE not in p or q != total_surplus_q(n):
            bad.append(n)
        print(f"{n:2d} pairs: clears at ${p[0]} to ${p[-1]}, Q = {q}, surplus ${total_surplus(buyers(n), sellers(n))}")
    if bad:
        print("schedule is NOT balanced at", bad)
        return 1

    n = EXAMPLE_PAIRS
    print(f"\nDeck example, {n} pairs:")
    print("  buyers ranked:", demand_steps(n))
    print("  sellers ranked:", supply_steps(n))
    for k, (v, c) in enumerate(zip(demand_steps(n), supply_steps(n)), 1):
        tag = "trades" if v > c else "does not trade"
        print(f"  unit {k:2d}: value {v:2d}, cost {c:2d}, gain {v - c:3d}  {tag}")
    print("  total surplus:", total_surplus(buyers(n), sellers(n)))

    write_cards()
    fig_demand(n)
    fig_supply(n)
    fig_equilibrium(n)
    fig_equilibrium(n, shade=True, out="market-surplus.svg")
    return 0


def total_surplus_q(n):
    """Units whose matched gain is positive: the efficient quantity."""
    return sum(v > c for v, c in zip(sorted(buyers(n), reverse=True), sorted(sellers(n))))


if __name__ == "__main__":
    sys.exit(main())
