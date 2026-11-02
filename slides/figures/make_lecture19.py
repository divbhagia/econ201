"""
Numbers and figures for Lecture 19: market dynamics in the short run and
long run (CORE 8.7 to 8.10).

Run from the course root:

    python3 slides/figures/make_lecture19.py

The lecture's quinoa figures come from slides/figures/make_lecture18.py.

Oil data, cached in slides/figures/data/ (gitignored):
    oil-prices.csv   Our World in Data, "Crude oil prices" (Energy Institute,
                     Statistical Review of World Energy 2026), current US$
                     per cubic meter, 1861 to 2025; divided by 6.2898 for
                     dollars per barrel
    oil-consumption.csv  Our World in Data, "Oil consumption" (Energy Institute,
                     Statistical Review of World Energy 2026), TWh a year
    cpi-us.csv       FRED series CPIAUCNS (US CPI, all items, not seasonally
                     adjusted), monthly; annual averages over complete years.
                     October 2025 was never published (federal shutdown), so
                     the base year is 2024.

OPEC (stylized, the course's own numbers, CORE Figure 8.19's shape), in
million barrels a day and dollars a barrel:
    supply    flat at marginal cost $20 up to capacity 80, then P = 20 + 3(Q - 80)
    demand    P = 120 - Q
    before    85 at $35
    OPEC cuts 20 of capacity: flat at $20 up to 60, then P = 20 + 3(Q - 60)
    after     70 at $50

Output, in slides/img/:
  oil-prices.svg   real oil price and world consumption, 1965 to 2024, with events
  opec-cut.svg     world supply before and after OPEC's cut, with demand
"""

import csv
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
DATA = ROOT / "slides" / "figures" / "data"
SCRATCH = Path(os.environ["FIG_PREVIEW_DIR"]) if os.environ.get("FIG_PREVIEW_DIR") else None

INK = "#1a1a1a"
GRID = "#c8c8c8"
DEMAND = "#0072B2"
SUPPLY = "#8f4100"
RULE = "#595a5b"
SIDE = (8.8, 6.0)
FONT = 26
DASH = (0, (6, 3))

plt.rcParams.update({
    "font.family": ["Lato", "Fira Sans", "sans-serif"], "font.size": FONT,
    "svg.fonttype": "path", "pdf.fonttype": 42, "axes.edgecolor": RULE,
    "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
})

LITRES = 6.2898            # barrels per cubic meter
BASE = 2024
FIRST = 1965


def save(fig, out: Path) -> None:
    fig.savefig(out, format="svg")
    if SCRATCH:
        fig.savefig(SCRATCH / f"{out.stem}.png", format="png", dpi=110)
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


def label(ax, x, y, text, color, dx, dy, ha="left", va="bottom", fs=FONT):
    ax.annotate(text, xy=(float(x), float(y)), xytext=(dx, dy), textcoords="offset points",
                ha=ha, va=va, fontsize=fs, color=color, fontweight="bold", zorder=8)


# ------------------------------------------------------- oil prices -------
def real_oil():
    cpi = {}
    with open(DATA / "cpi-us.csv", newline="") as fh:
        for r in csv.DictReader(fh):
            k = list(r)
            v = r[k[1]]
            if v not in ("", "."):
                cpi.setdefault(int(r[k[0]][:4]), []).append(float(v))
    cpi = {y: sum(v) / len(v) for y, v in cpi.items() if len(v) == 12}
    out = {}
    with open(DATA / "oil-prices.csv", newline="") as fh:
        for r in csv.DictReader(fh):
            y = int(r["Year"])
            if y in cpi:
                out[y] = float(r["Oil price - Crude prices since 1861"]) / LITRES * cpi[BASE] / cpi[y]
    return out


def world_consumption():
    out = {}
    with open(DATA / "oil-consumption.csv", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["Entity"] == "World":
                out[int(r["Year"])] = float(r["Oil"]) / 1000   # thousand TWh
    return out


# Events on the chart: year, label, label's x and y on the price axis, and
# the horizontal alignment of the label over that x.
EVENTS = [
    (1974, "OPEC cuts supply", 1971.5, 112, "center"),
    (1980, "Iranian Revolution", 1980, 172, "center"),
    (1986, "Low growth, demand falls", 1985, 10, "left"),
    (2003, "Iraq War", 1999, 118, "center"),
    (2009, "Financial crisis", 2004.5, 27, "center"),
    (2011, "Arab Spring", 2011, 182, "center"),
    (2016, "Shale oil", 2014, 11, "center"),
    (2020, "Covid-19", 2021, 11, "center"),
    (2022, "Ukraine war", 2019, 150, "center"),
]


def fig_oil(out: Path) -> None:
    oil = real_oil()
    con = world_consumption()
    years = [y for y in sorted(oil) if FIRST <= y <= BASE]
    cyears = [y for y in sorted(con) if FIRST <= y <= BASE]
    fig, ax = plt.subplots(figsize=(13.0, 6.4), dpi=100)
    fs = FONT - 4
    ax2 = ax.twinx()
    ax.set_zorder(ax2.get_zorder() + 1)   # price and its events sit over consumption
    ax.patch.set_visible(False)
    ax2.plot(cyears, [con[y] for y in cyears], color=SUPPLY, lw=4, solid_capstyle="round", zorder=4)
    ax.plot(years, [oil[y] for y in years], color=DEMAND, lw=4, solid_capstyle="round", zorder=5)
    ax.set_ylim(0, 195)
    ax.set_yticks(range(0, 161, 40))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"${y:.0f}"))
    ax.set_ylabel(f"Price, dollars a barrel ({BASE} prices)", fontsize=fs, labelpad=8, color=DEMAND)
    ax2.set_ylim(0, 97.5)                 # $40 on the left lines up with 20 on the right
    ax2.set_yticks(range(0, 81, 20))
    ax2.set_ylabel("World consumption, thousand TWh a year", fontsize=fs, labelpad=10, color=SUPPLY)
    ax.set_xlim(FIRST - 1, BASE + 1)
    ax.set_xticks(range(1970, BASE + 1, 10))
    ax.grid(color=GRID, lw=1, zorder=0)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax2.spines["top"].set_visible(False)
    ax.tick_params(length=0, labelsize=fs)
    ax2.tick_params(length=0, labelsize=fs)
    ax.text(1984.5, 122, "Price", color=DEMAND, fontsize=fs, fontweight="bold", ha="left", va="center", zorder=8)
    ax.text(1992, 92, "Consumption", color=SUPPLY, fontsize=fs, fontweight="bold", ha="center", va="center", zorder=8)
    for year, text, lx, ly, ha in EVENTS:
        ax.annotate(text, xy=(year, oil[year]), xytext=(lx, ly), fontsize=fs - 1, color=INK,
                    ha=ha, va="center", zorder=8,
                    arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4, shrinkA=3, shrinkB=4))
    fig.subplots_adjust(left=0.095, right=0.915, top=0.98, bottom=0.08)
    save(fig, out)


# ------------------------------------------------------- OPEC -------------
C, CAP, CUT, STEEP = 20, 80, 20, 3
D_INT = 120


def world_supply(q, cap):
    return C if q <= cap else C + STEEP * (q - cap)


def cross(cap):
    q = (D_INT - C + STEEP * cap) / F(1 + STEEP)
    return q, D_INT - q


def fig_opec(out: Path) -> None:
    fig, ax = plt.subplots(figsize=SIDE, dpi=100)
    ax.set_xlim(0, 120)
    ax.set_ylim(0, 120)
    ax.set_xticks(range(0, 121, 20))
    ax.set_xticks(range(0, 121, 10), minor=True)
    ax.set_yticks(range(0, 121, 20))
    ax.set_yticks(range(0, 121, 10), minor=True)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"${y:.0f}"))
    ax.grid(which="both", color=GRID, lw=1, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(which="both", length=0, labelsize=FONT - 4)
    ax.set_xlabel("Million barrels a day, Q", fontsize=FONT - 2, labelpad=8)
    ax.set_ylabel("Dollars a barrel", fontsize=FONT - 2, labelpad=8)
    fig.subplots_adjust(left=0.16, right=0.97, top=0.96, bottom=0.16)
    ax.plot([0, 120], [D_INT, 0], color=DEMAND, lw=4, solid_capstyle="round", zorder=5)
    label(ax, 95, D_INT - 95, "Demand", DEMAND, 8, 6)
    for cap, ls, name in ((CAP, "-", "Supply"), (CAP - CUT, DASH, "After OPEC's cut")):
        top = cap + (120 - C) / STEEP
        ax.plot([0, cap, top], [C, C, 120], color=SUPPLY, lw=4, ls=ls, solid_capstyle="round", zorder=5)
    label(ax, 100, world_supply(100, CAP), "Supply", SUPPLY, -12, 0, ha="right", va="center")
    label(ax, 82, 92, "After OPEC's cut", SUPPLY, -6, 0, ha="right", va="center", fs=FONT - 4)
    for cap in (CAP, CAP - CUT):
        q, p = cross(cap)
        ax.plot([0, float(q)], [float(p)] * 2, color=INK, lw=2.2, ls=(0, (4, 3)), zorder=4)
        ax.plot([float(q)] * 2, [0, float(p)], color=INK, lw=2.2, ls=(0, (4, 3)), zorder=4)
        ax.plot(float(q), float(p), marker="o", ms=12, color=INK, zorder=9)
    q0, p0 = cross(CAP)
    q1, p1 = cross(CAP - CUT)
    label(ax, q0, p0, "A", INK, 10, 2)
    label(ax, q1, p1, "B", INK, -10, 6, ha="right")
    save(fig, out)


def main() -> int:
    oil = real_oil()
    print(f"Real oil prices, {BASE} dollars a barrel")
    for y in (1965, 1972, 1974, 1980, 1986, 1998, 2008, 2014, 2016, 2020, 2022, 2024):
        print(f"  {y}: ${oil[y]:.0f}")
    q0, p0 = cross(CAP)
    q1, p1 = cross(CAP - CUT)
    print(f"OPEC: before {q0} at ${p0}; after cutting {CUT}: {q1} at ${p1}")
    assert (q0, p0) == (85, 35) and (q1, p1) == (70, 50)
    assert world_supply(q0, CAP) == p0 and world_supply(q1, CAP - CUT) == p1
    fig_oil(IMG / "oil-prices.svg")
    fig_opec(IMG / "opec-cut.svg")
    return 0


if __name__ == "__main__":
    sys.exit(main())
