"""
Figures and numbers for Lecture 12: the markup rule and the sources of
market power (CORE 7.6, 7.8, 7.9, 7.11, 7.12).

Run from the course root:

    python3 slides/figures/make_lecture12.py

No data downloads. The running example is the scooter company from
worksheets 10 and 11 and Quiz 5 (make_lecture10.py draws the worksheet
graph), so the lecture picks up where the quiz left off:

    demand           P = 1,200 - 20 Q, so the slope is -20
    MC               400 a scooter
    E                Q* = 20, P* = 800 (MR = 1,200 - 40 Q = 400)
    surplus at E     CS 4,000, PS 8,000, DWL 4,000 (the quiz answers)
    markup           (800 - 400) / 800 = 1/2
    elasticity at E  -(P/Q) x (1/slope) = (800/20) x (1/20) = 2
    markup rule      1 / 2 = 1/2

The car table on the slides is CORE Figure 7.22 (Berry, Levinsohn, and
Pakes, 1995); main() checks that each markup is close to 1 / elasticity.

Output, in slides/img/:
  scooters-quiz.svg    the quiz graph: demand, MC, and E, with consumer
                       surplus, producer surplus, and deadweight loss shaded
                       and labelled with their values
  film-price.svg       a film's average cost (100 million fixed, 1 dollar per
                       stream) falling toward MC, marked at 5, 10, 25, and 50
                       million viewers, with a dotted line at the 5 dollar
                       price: break-even at 25 million, loss left, profit right
  generics.svg         median generic price as a share of the brand's price
                       before generic entry, by number of generic makers,
                       redrawn from the FDA report's appendix table (AMP)

Accessibility: Okabe-Ito derived colours, every curve and point labelled
on the figure itself; text converted to paths. Alt text lives beside the
image in the deck.
"""

import glob as _glob
import os
import sys
from fractions import Fraction
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

ROOT = Path(__file__).resolve().parents[2]
IMG = ROOT / "slides" / "img"
SCRATCH = Path(os.environ["FIG_PREVIEW_DIR"]) if os.environ.get("FIG_PREVIEW_DIR") else None

INK = "#1a1a1a"
GRID = "#d9d9d9"
ACCENT = "#BF5700"
DEMAND = "#0072B2"
CS_AREA = "#d2e7f5"
PS_AREA = "#fae2cc"
DWL_AREA = "#e8e8e8"
MARGINAL = "#595a5b"
GUIDE = "#595a5b"

SIDE = (8.8, 6.0)                # beside a 38% text column
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
FIXED = 4_000
MC = 400
INTERCEPT = 1_200                # demand: P = INTERCEPT - SLOPE Q
SLOPE = 20
Q_STAR = 20
Q_EFF = 40
Q_MAX = 50
AC_MARKS = (10, 20)

# CORE Figure 7.22: price, P - MC, markup (%), elasticity, 1983 dollars.
CARS = {
    "Mazda 323": (5_049, 801, 16, 6.3),
    "Nissan Sentra": (5_661, 880, 16, 6.4),
    "Lexus LS400": (27_544, 9_030, 33, 3.1),
    "BMW 735i": (37_490, 10_975, 29, 3.4),
}


def price(q):
    return INTERCEPT - SLOPE * q


def average_cost(q):
    return FIXED / q + MC


P_STAR = INTERCEPT - SLOPE * Q_STAR
CS = Q_STAR * (INTERCEPT - P_STAR) // 2
PS = (P_STAR - MC) * Q_STAR
DWL = (Q_EFF - Q_STAR) * (P_STAR - MC) // 2


def money(x):
    sign = "−" if x < 0 else ""
    return f"{sign}${abs(x):,.0f}"


def save(fig, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format="svg")
    if SCRATCH:
        fig.savefig(SCRATCH / f"{out.stem}.png", format="png", dpi=110)
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


def base_axes(ylabel, yticks, ylim):
    fig, ax = plt.subplots(figsize=SIDE, dpi=100)
    ax.grid(color=GRID, lw=1, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=5, width=1, labelsize=FONT)
    ax.set_xlim(0, Q_MAX)
    ax.set_ylim(0, ylim)
    ax.set_xticks([0, 10, 20, 30, 40, 50])
    ax.set_yticks(yticks)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: money(y)))
    ax.set_xlabel("Scooters per day, Q", fontsize=FONT, labelpad=8)
    ax.set_ylabel(ylabel, fontsize=FONT, labelpad=8)
    fig.subplots_adjust(left=0.2, right=0.965, top=0.96, bottom=0.15)
    return fig, ax


def draw_quiz(out: Path) -> None:
    """The quiz graph with CS, PS, and DWL shaded and labelled."""
    p = price(Q_STAR)
    fig, ax = base_axes("Price and cost", [0, MC, p, INTERCEPT], 1_250)
    ax.fill([0, 0, Q_STAR], [INTERCEPT, p, p], color=CS_AREA, lw=0, zorder=2)
    ax.fill([0, 0, Q_STAR, Q_STAR], [p, MC, MC, p], color=PS_AREA, lw=0,
            zorder=2)
    ax.fill([Q_STAR, Q_STAR, Q_EFF], [p, MC, MC], color=DWL_AREA, lw=0,
            zorder=2)
    q = np.array([0, Q_MAX])
    ax.plot(q, price(q), color=DEMAND, lw=3, solid_capstyle="round", zorder=5)
    ax.annotate("Demand", xy=(31, price(31)), xytext=(10, 8),
                textcoords="offset points", ha="left", va="bottom",
                fontsize=FONT, color=DEMAND, fontweight="bold", zorder=8)
    ax.axhline(MC, color=MARGINAL, lw=2.4, ls=(0, (5, 3)), zorder=4)
    ax.annotate(f"MC = {money(MC)}", xy=(0.6, MC), xytext=(0, -10),
                textcoords="offset points", ha="left", va="top",
                fontsize=FONT, color=MARGINAL, fontweight="bold", zorder=8)
    ax.plot([0, Q_STAR], [p, p], color=INK, lw=1.6, zorder=4)
    ax.plot([Q_STAR, Q_STAR], [0, p], color=GUIDE, lw=1.6, ls=(0, (4, 3)),
            zorder=4)
    for x, y, lab in ((5.5, 930, f"CS\n{money(CS)}"), (10, 600, f"PS\n{money(PS)}"),
                      (25.5, 520, f"DWL\n{money(DWL)}")):
        ax.text(x, y, lab, ha="center", va="center", fontsize=FONT - 4,
                color=INK, fontweight="bold", zorder=8, linespacing=1.05)
    ax.plot(Q_STAR, p, marker="o", ms=13, color=INK, zorder=9)
    ax.annotate("E", xy=(Q_STAR, p), xytext=(12, 6), textcoords="offset points",
                ha="left", va="bottom", fontsize=FONT, color=INK,
                fontweight="bold", zorder=10)
    save(fig, out)


def draw_ac(out: Path) -> None:
    """Average cost falling toward marginal cost; one curve, so the accent."""
    fig, ax = base_axes("Cost per scooter",
                        [0, MC, average_cost(20), average_cost(10), 1_200], 1_250)
    q = np.linspace(3.5, Q_MAX, 300)
    ax.plot(q, average_cost(q), color=ACCENT, lw=3, solid_capstyle="round",
            zorder=5)
    ax.annotate("AC", xy=(40, average_cost(40)), xytext=(0, 12),
                textcoords="offset points", ha="center", va="bottom",
                fontsize=FONT, color=ACCENT, fontweight="bold", zorder=8)
    ax.axhline(MC, color=MARGINAL, lw=2.4, ls=(0, (5, 3)), zorder=4)
    ax.annotate(f"MC = {money(MC)}", xy=(Q_MAX - 0.5, MC), xytext=(0, -10),
                textcoords="offset points", ha="right", va="top",
                fontsize=FONT, color=MARGINAL, fontweight="bold", zorder=8)
    for k in AC_MARKS:
        ac = average_cost(k)
        ax.plot([k, k], [0, ac], color=GUIDE, lw=1.6, ls=(0, (4, 3)), zorder=4)
        ax.plot([0, k], [ac, ac], color=GUIDE, lw=1.6, ls=(0, (4, 3)), zorder=4)
        ax.plot(k, ac, marker="o", ms=13, color=INK, zorder=9)
        ax.annotate(money(ac), xy=(k, ac), xytext=(12, 6),
                    textcoords="offset points", ha="left", va="bottom",
                    fontsize=FONT, color=INK, fontweight="bold", zorder=10)
    save(fig, out)


# FDA (Conrad and Lutter, 2019), appendix table "Generic-to-Brand Price
# Ratios in the Main Figure", average manufacturer price, median.
GENERICS = [("1", 0.614), ("2", 0.465), ("3", 0.322), ("4", 0.212),
            ("5", 0.144), ("6", 0.061), ("7", 0.040), ("8", 0.049),
            ("9", 0.012), ("10+", 0.010)]
GENERIC_LABELS = ("1", "2", "4", "6")


def draw_generics(out: Path) -> None:
    """One series, so the accent; values labelled at the points the slide uses."""
    fig, ax = plt.subplots(figsize=SIDE, dpi=100)
    ax.grid(axis="y", color=GRID, lw=1, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=5, width=1, labelsize=FONT)
    xs = range(len(GENERICS))
    ys = [100 * r for _, r in GENERICS]
    ax.plot(xs, ys, color=ACCENT, lw=3, marker="o", ms=12, zorder=5)
    for x, (n, r) in zip(xs, GENERICS):
        if n in GENERIC_LABELS:
            ax.annotate(f"{100 * r:.0f}%", xy=(x, 100 * r), xytext=(12, 8),
                        textcoords="offset points", ha="left", va="bottom",
                        fontsize=FONT, color=INK, fontweight="bold", zorder=8)
    ax.set_xticks(list(xs), [n for n, _ in GENERICS])
    ax.set_xlim(-0.4, len(GENERICS) - 0.6)
    ax.set_ylim(0, 72)
    ax.set_yticks([0, 20, 40, 60])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.set_xlabel("Number of generic makers", fontsize=FONT, labelpad=8)
    ax.set_ylabel("Generic price, % of brand's", fontsize=FONT, labelpad=8)
    fig.subplots_adjust(left=0.17, right=0.97, top=0.96, bottom=0.15)
    save(fig, out)


FILM_F, FILM_MC = 100, 1         # millions of dollars; dollars per stream
FILM_MARKS = (5, 10, 25, 50)      # millions of viewers
FILM_PRICE = 5                   # what viewers will pay, so break-even at 25


def film_ac(q):
    return FILM_F / q + FILM_MC


def draw_film(out: Path, price=None) -> None:
    """AC = 100 / Q + 1 (Q in millions), one curve, so the accent.

    With price, a dotted line at what viewers pay: the AC curve crosses it
    at the break-even quantity, above it the studio loses money.
    """
    fig, ax = plt.subplots(figsize=SIDE, dpi=100)
    ax.grid(axis="y", color=GRID, lw=1, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=5, width=1, labelsize=FONT)
    ax.set_xlim(0, 55)
    ax.set_ylim(0, 25)
    ax.set_xticks([0] + list(FILM_MARKS))
    ax.set_yticks([0, 5, 10, 15, 20, 25])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"${y:.0f}"))
    ax.set_xlabel("Viewers (millions)", fontsize=FONT, labelpad=8)
    ax.set_ylabel("Cost per viewer", fontsize=FONT, labelpad=8)
    fig.subplots_adjust(left=0.15, right=0.965, top=0.96, bottom=0.15)
    q = np.linspace(100 / 24, 55, 400)
    ax.plot(q, film_ac(q), color=ACCENT, lw=3.4, solid_capstyle="round", zorder=5)
    if price is None:
        ac_xy, ac_off, ac_ha = (38, film_ac(38)), (0, 14), "center"
    else:
        ac_xy, ac_off, ac_ha = (16, film_ac(16)), (14, 10), "left"
    ax.annotate("Average cost", xy=ac_xy, xytext=ac_off,
                textcoords="offset points", ha=ac_ha, va="bottom",
                fontsize=FONT, color=ACCENT, fontweight="bold", zorder=8)
    ax.axhline(FILM_MC, color=MARGINAL, lw=2.6, ls=(0, (5, 3)), zorder=4)
    ax.annotate(f"Marginal cost = ${FILM_MC}", xy=(37.5, FILM_MC), xytext=(0, 5),
                textcoords="offset points", ha="center", va="bottom",
                fontsize=FONT - 2, color=MARGINAL, fontweight="bold", zorder=8)
    if price is not None:
        ax.axhline(price, color=DEMAND, lw=2.6, ls=(0, (1.5, 2.5)), zorder=4)
        ax.annotate(f"Price = ${price}", xy=(54.5, price), xytext=(0, 6),
                    textcoords="offset points", ha="right", va="bottom",
                    fontsize=FONT - 2, color=DEMAND, fontweight="bold", zorder=8)
        ax.set_yticks([0, price, 10, 15, 20, 25])
    for k in FILM_MARKS:
        y = film_ac(k)
        ax.plot([k, k], [0, y], color=GUIDE, lw=1.4, ls=(0, (4, 3)), zorder=3)
        ax.plot(k, y, marker="o", ms=13, color=INK, zorder=9)
        label = f"${y:.0f}"
        if price is not None and abs(y - price) < 1e-9:
            label = f"${y:.0f}: breaks even"
        elif price is not None:
            label = f"${y:.0f}: " + ("loss" if y > price else "profit")
        last = k == FILM_MARKS[-1]
        ax.annotate(label, xy=(k, y), xytext=(-10, 8) if last else (10, 8),
                    textcoords="offset points", ha="right" if last else "left",
                    va="bottom",
                    fontsize=FONT - (2 if price is not None else 0), color=INK,
                    fontweight="bold", zorder=10)
    save(fig, out)


def main() -> int:
    p = price(Q_STAR)
    markup = Fraction(p - MC, p)
    eps = Fraction(p, Q_STAR) * Fraction(1, SLOPE)
    assert INTERCEPT - 2 * SLOPE * Q_STAR == MC and price(Q_EFF) == MC
    assert (CS, PS, DWL) == (4_000, 8_000, 4_000)
    assert markup == 1 / eps == Fraction(1, 2)
    print(f"Scooters at E: CS {CS:,}, PS {PS:,}, DWL {DWL:,}")
    print(f"Scooters at E: Q = {Q_STAR}, P = {p:,}, MC = {MC:,}")
    print(f"  markup = ({p:,} - {MC:,}) / {p:,} = {markup} = {float(markup):.1%}")
    print(f"  elasticity = ({p:,} / {Q_STAR}) x (1 / {SLOPE:,}) = {eps} = {float(eps)}")
    print(f"  1 / elasticity = {1 / eps}")
    for k in AC_MARKS:
        print(f"  AC at {k} scooters = {FIXED:,} / {k} + {MC:,} = {average_cost(k):,.0f}")

    print("\nCORE Figure 7.22, markup against 1 / elasticity:")
    for name, (pr, margin, mk, e) in CARS.items():
        print(f"  {name:14s} margin/price = {margin / pr:.1%} (table {mk}%),"
              f" 1/e = {1 / e:.1%}")
        assert abs(100 * margin / pr - mk) < 0.6

    # Source 2: a film (CORE 7.11's example) with illustrative round numbers.
    print(f"\nfilm: fixed {FILM_F} million, {FILM_MC} dollar per stream")
    for k in FILM_MARKS:
        print(f"  AC at {k} million viewers = {FILM_F}/{k} + {FILM_MC} = {film_ac(k):.0f}")
    q_be = FILM_F / (FILM_PRICE - FILM_MC)
    print(f"  at P = {FILM_PRICE}: break even at {q_be:.0f} million viewers;"
          f" two studios splitting 50 million each break even, three each lose")

    # Generic drugs: FDA (Conrad and Lutter, 2019), generic AMP below the
    # pre-entry brand price, by number of generic makers.
    print("\nFDA generic prices below the brand's: 1 maker 39%, 2 makers 54%,"
          " 4 makers 79%, 6+ makers over 95%")
    # De Loecker, Eeckhout, and Unger (2020) report P / MC: 1.21 in 1980 and
    # 1.61 in 2016. In CORE's measure, markup = (P - MC) / P = 1 - MC / P.
    for year, mu in ((1980, 1.21), (2016, 1.61)):
        print(f"  {year}: P/MC = {mu}, price {mu - 1:.0%} above MC,"
              f" (P - MC)/P = {(mu - 1) / mu:.1%}")

    # Practice 12, problem 3: Pixel Forge, a game studio, 60 million fixed,
    # 2 dollars a download, 5 dollar price, 60 million buyers at that price.
    gf, gmc, gp, gmkt = 60, 2, 5, 60
    print("\npractice 12, Pixel Forge: AC at 10, 20, 60 million =",
          [f"{gf / q + gmc:.0f}" for q in (10, 20, 60)],
          f"; break even at P = {gp}: {gf / (gp - gmc):.0f} million")
    for n in (1, 3, 6):
        q = gmkt / n
        print(f"  {n} studio(s), {q:.0f} million each: profit {(gp - (gf / q + gmc)) * q:.0f} million each")

    # Practice 12, problem 1: Canyon Kayaks, P = 80 - 2Q, MC = 20.
    ki, ks, kmc = 80, 2, 20
    kq = (ki - kmc) // (2 * ks)                  # MR = 80 - 4Q = 20
    kp = ki - ks * kq
    kmark = Fraction(kp - kmc, kp)
    keps = Fraction(kp, kq) * Fraction(1, ks)
    assert ki - 2 * ks * kq == kmc and kmark == 1 / keps
    print(f"\npractice 12, Canyon Kayaks: Q* = {kq}, P* = {kp},"
          f" markup = {kp - kmc}/{kp} = {kmark} = {float(kmark):.0%},"
          f" elasticity = ({kp}/{kq}) x (1/{ks}) = {keps} = {float(keps):.3f}")

    # Practice 12, problem 2: the markup rule run backwards,
    # (P - MC) / P = 1 / e, so P = MC x e / (e - 1).
    for mc, e in ((15, 4), (15, 6)):
        pr = Fraction(mc * e, e - 1)
        print(f"  phone cases: MC = {mc}, e = {e}: P = {mc} x {e} / {e - 1} = {pr}"
              f" (markup {float(Fraction(pr - mc, pr)):.1%})")
    # MCQ: elasticity 5, price 50.
    print(f"  MCQ: e = 5, P = 50: markup 1/5, MC = 50 x (1 - 1/5) = {50 * 4 // 5}")

    draw_quiz(IMG / "scooters-quiz.svg")
    draw_generics(IMG / "generics.svg")
    draw_film(IMG / "film-price.svg", price=FILM_PRICE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
