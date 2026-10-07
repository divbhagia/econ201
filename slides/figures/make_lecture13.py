"""
Figures and numbers for Lecture 13: strategic price setting (CORE 4.2 to
4.4 and 7.10).

Run from the course root:

    python3 slides/figures/make_lecture13.py

No data downloads. The running example is CORE's Wanda and Kit (Figures
7.24 and 7.25), with CORE's numbers, moved to a Southern California beach
and priced in dollars:

    cost        c = $10 per board per day
    prices      H = $36 or L = $20
    customers   60 a day, split evenly between the two activities:
                  loyal            rent their own activity at any price
                  price-sensitive  pay H for their own activity, but switch
                                   if the other is cheaper
                  price-driven     pay L but not H, their own activity first
    base case   22 loyal, 18 price-sensitive, 20 price-driven
    variations  26 loyal and 14 price-sensitive (H is dominant), and
                14 loyal and 26 price-sensitive (L is dominant: a
                prisoners' dilemma); the price-driven 20 never change.

Profit = (price - 10) x customers. main() prints every customer count and
profit, each player's best responses, and the Nash equilibria.

Output, in slides/img/:
  customer-groups.svg  each firm's 30 customers as a bar split into loyal,
                       price-sensitive, and price-driven
  who-rents.svg        for each pair of prices, each firm's customers as a
                       bar built from those groups, so 20, 30, 49, and 11
                       are visibly sums; customers keep their own firm's
                       colour wherever they rent; a key on top
  game-base.svg        the base-case pay-off matrix, no marks
  game-base-wanda.svg  the same with rings on Wanda's best responses
  game-base-nash.svg   rings for both players: two Nash equilibria
  game-loyal26.svg     26 loyal customers (13 each): (H, H)
  game-loyal14.svg     14 loyal customers (7 each): (L, L)
  game-loyal14-plain.svg  the same matrix unmarked, for the question slide
  loyalty-spectrum.svg three boxes, one per kind of game, with the range of
                       loyal customers per firm for each (computed here)
                       and an arrow: more loyal, higher prices

In each matrix Wanda (rows) is bottom left and Kit (columns) top right, as
CORE does. A blue ring marks Wanda's best response and an orange ring Kit's;
a cell with both rings is a Nash equilibrium. Players differ in position
and colour, and
customer groups in fill (solid, open, hatched) and label, so nothing rests on
colour. Text converted to paths. Alt text lives beside each image in the deck.
"""

import glob as _glob
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
SCRATCH = Path(os.environ["FIG_PREVIEW_DIR"]) if os.environ.get("FIG_PREVIEW_DIR") else None

INK = "#1a1a1a"
WANDA = "#0072B2"                # Okabe-Ito blue, 5.1:1 on white
KIT = "#8f4100"                  # dark orange, 7.7:1 on white
RULE = "#595a5b"

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

# ------------------------------------------------------- the example ------
COST = 10
PRICE = {"H": 36, "L": 20}
PRICE_DRIVEN = 20                # pay L but not H
TOTAL = 60


def customers(loyal, wanda, kit):
    """Wanda's and Kit's customers when they set prices wanda and kit."""
    sensitive = TOTAL - PRICE_DRIVEN - loyal
    l, s, d = loyal // 2, sensitive // 2, PRICE_DRIVEN // 2
    if wanda == kit == "H":
        return l + s, l + s
    if wanda == kit == "L":
        return l + s + d, l + s + d
    # One high, one low: the high-priced firm keeps only its loyal customers.
    low = l + 2 * s + 2 * d
    return (low, l) if wanda == "L" else (l, low)


def profits(loyal):
    out = {}
    for w in "HL":
        for k in "HL":
            qw, qk = customers(loyal, w, k)
            out[w, k] = ((PRICE[w] - COST) * qw, (PRICE[k] - COST) * qk)
    return out


def best_responses(pay):
    """Cells holding Wanda's best responses and Kit's (both ringed)."""
    wanda = {(max("HL", key=lambda w: pay[w, k][0]), k) for k in "HL"}
    kit = {(w, max("HL", key=lambda k: pay[w, k][1])) for w in "HL"}
    return wanda, kit


def save(fig, out: Path, tight: bool = False) -> None:
    """tight crops to the drawn content, for figures whose labels run past
    the axes limits."""
    out.parent.mkdir(parents=True, exist_ok=True)
    kw = dict(bbox_inches="tight", pad_inches=0.05) if tight else {}
    fig.savefig(out, format="svg", **kw)
    if SCRATCH:
        fig.savefig(SCRATCH / f"{out.stem}.png", format="png", dpi=110, **kw)
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


def draw_matrix(out: Path, loyal: int, marks: str) -> None:
    """Pay-off matrix; marks is '', 'wanda', or 'both'."""
    pay = profits(loyal)
    br_w, br_k = best_responses(pay)
    fig, ax = plt.subplots(figsize=SIDE, dpi=100)
    ax.set_xlim(-1.25, 2.05)
    ax.set_ylim(-0.05, 2.75)
    ax.axis("off")
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)

    ax.text(1.0, 2.6, "Kit's price", ha="center", va="center",
            fontsize=FONT, color=KIT, fontweight="bold")
    ax.text(-1.15, 1.0, "Wanda's price", ha="center", va="center",
            fontsize=FONT, color=WANDA, fontweight="bold", rotation=90)
    cols = {"H": 0, "L": 1}
    rows = {"H": 1, "L": 0}
    for k, c in cols.items():
        ax.text(c + 0.5, 2.22, f"{k} = ${PRICE[k]}", ha="center", va="center",
                fontsize=FONT, color=INK)
    for w, r in rows.items():
        ax.text(-0.4, r + 0.5, f"{w} = ${PRICE[w]}", ha="center", va="center",
                fontsize=FONT, color=INK)

    for w, r in rows.items():
        for k, c in cols.items():
            ax.add_patch(Rectangle((c, r), 1, 1, fill=False, ec=RULE, lw=2))
            pw, pk = pay[w, k]
            # Wanda bottom left, Kit top right, as in CORE.
            ax.text(c + 0.3, r + 0.28, f"{pw}", ha="center", va="center",
                    fontsize=FONT + 2, color=WANDA, fontweight="bold")
            ax.text(c + 0.7, r + 0.72, f"{pk}", ha="center", va="center",
                    fontsize=FONT + 2, color=KIT, fontweight="bold")
            if marks in ("wanda", "both") and (w, k) in br_w:
                ax.plot(c + 0.3, r + 0.28, marker="o", ms=74, mfc="none",
                        mec=WANDA, mew=2.6)
            if marks == "both" and (w, k) in br_k:
                ax.plot(c + 0.7, r + 0.72, marker="o", ms=74, mfc="none",
                        mec=KIT, mew=2.6)
    save(fig, out)


# --------------------------------------------- customers as segmented bars --
GROUPS = ("loyal", "price-sensitive", "price-driven")


def firm_groups(loyal):
    """Per-firm loyal, price-sensitive, and price-driven customers."""
    return {"loyal": loyal // 2,
            "price-sensitive": (TOTAL - PRICE_DRIVEN - loyal) // 2,
            "price-driven": PRICE_DRIVEN // 2}


def segment(ax, x, y, w, h, group, col, label, fs, grey=False):
    """One bar segment: solid for loyal, open for price-sensitive, hatched
    for price-driven, so the group never rests on colour alone."""
    if grey:
        col = RULE
    face = {"loyal": col, "price-sensitive": "white", "price-driven": "white"}[group]
    rect = ax.add_patch(Rectangle((x, y), w, h, fc=face, ec=col, lw=2.4,
                                  hatch="///" if group == "price-driven" else None,
                                  ls=(0, (4, 3)) if grey else "-", zorder=3))
    txt = "white" if group == "loyal" else col
    box = dict(fc="white", ec="none", pad=1.5) if group == "price-driven" else None
    lab = ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=fs,
                  color=txt, fontweight="bold", bbox=box, zorder=4)
    return [rect, lab]


def draw_groups(out: Path, loyal: int = 22) -> None:
    """Slide 3: each firm's 30 customers, by group."""
    g = firm_groups(loyal)
    fig, ax = plt.subplots(figsize=(10.0, 2.3), dpi=100)
    ax.set_xlim(-7.6, 30.3)
    ax.set_ylim(-0.1, 3.05)
    ax.axis("off")
    fig.subplots_adjust(left=0.005, right=0.995, top=0.99, bottom=0.01)
    fs = 20
    x = 0
    for grp in GROUPS:
        ax.text(x + g[grp] / 2, 2.62, grp, ha="center", va="center",
                fontsize=fs, color=INK, fontweight="bold")
        x += g[grp]
    for name, col, y in (("Wanda's 30", WANDA, 1.25), ("Kit's 30", KIT, 0.0)):
        ax.text(-0.6, y + 0.5, name, ha="right", va="center", fontsize=fs,
                color=col, fontweight="bold")
        x = 0
        for grp in GROUPS:
            n = g[grp]
            segment(ax, x, y, n, 1.0, grp, col, f"{n}", fs)
            x += n
    save(fig, out)


def stand_parts(loyal, my_p, their_p, col, other_col):
    """The groups renting from a firm at price my_p when its rival charges
    their_p, each tagged with the colour of the firm whose customers they are."""
    parts = [("loyal", col)]
    if my_p == "H" and their_p == "H":
        parts += [("price-sensitive", col)]
    elif my_p == "L" and their_p == "L":
        parts += [("price-sensitive", col), ("price-driven", col)]
    elif my_p == "L":
        parts += [("price-sensitive", col), ("price-driven", col),
                  ("price-sensitive", other_col), ("price-driven", other_col)]
    return parts


def draw_who_rents(out: Path, loyal: int = 22) -> None:
    """Slide 4: whose customers rent where, for each pair of prices, with a
    key on top so the slide reads without slide 3."""
    g = firm_groups(loyal)
    fig, ax = plt.subplots(figsize=(7.0, 5.4), dpi=100)
    ax.set_xlim(-1, 50)
    fs = 23
    bar_h, gap_in, gap_out = 0.82, 0.16, 0.62
    cases = (("H", "H"), ("L", "L"), ("L", "H"), ("H", "L"))
    top = len(cases) * (2 * bar_h + gap_in) + (len(cases) - 1) * gap_out
    key_y = top + 1.45
    ax.set_ylim(-0.1, key_y + 0.75)
    ax.axis("off")
    fig.subplots_adjust(left=0.005, right=0.995, top=0.99, bottom=0.01)
    # Key: the three groups by fill, then whose customers by colour and word.
    for grp, x in (("loyal", 0), ("price-sensitive", 12.5), ("price-driven", 33)):
        segment(ax, x, key_y, 3.5, bar_h * 0.8, grp, INK, "", fs)
        ax.text(x + 4.2, key_y + bar_h * 0.4, grp, ha="left", va="center",
                fontsize=fs - 2, color=INK)
    ax.text(0, key_y - 0.62, "Wanda's customers are blue, Kit's are orange",
            ha="left", va="center", fontsize=fs - 2, color=INK)
    frames = []
    y = top
    for pw, pk in cases:
        arts = []
        y -= bar_h
        y_w = y
        y -= gap_in + bar_h
        y_k = y
        y -= gap_out
        for me, my_p, their_p, col, other_col, yy in (
                ("Wanda", pw, pk, WANDA, KIT, y_w), ("Kit", pk, pw, KIT, WANDA, y_k)):
            arts.append(ax.text(-0.6, yy + bar_h / 2, f"{me} at {my_p}", ha="right",
                                va="center", fontsize=fs, color=col, fontweight="bold"))
            parts = stand_parts(loyal, my_p, their_p, col, other_col)
            x = 0
            for grp, c in parts:
                arts += segment(ax, x, yy, g[grp], bar_h, grp, c, f"{g[grp]}", fs)
                x += g[grp]
            total = x
            assert total == customers(loyal, pw, pk)[0 if me == "Wanda" else 1]
            incoming = sum(g[grp] for grp, c in parts if c != col)
            other = "Kit" if me == "Wanda" else "Wanda"
            note = f"= {total}" + (f"  ({incoming} from {other})" if incoming else "")
            arts.append(ax.text(x + 0.8, yy + bar_h / 2, note, ha="left", va="center",
                                fontsize=fs + 1, color=INK, fontweight="bold"))
            if my_p == "H" and their_p == "H":
                xs = x + 7.5
                arts += segment(ax, xs, yy, g["price-driven"], bar_h, "price-driven", col,
                                f"{g['price-driven']}", fs, grey=True)
                arts.append(ax.text(xs + g["price-driven"] + 0.8, yy + bar_h / 2,
                                    "do not rent", ha="left", va="center", fontsize=fs,
                                    color=RULE))
        frames.append(arts)
    save(fig, out, tight=True)


# ------------------------------------------------------ loyalty spectrum ----
def game_type(loyal):
    pay = profits(loyal)
    br_w, br_k = best_responses(pay)
    rows_w = {w for w, _ in br_w}
    nash = sorted(br_w & br_k)
    if rows_w == {"H"}:
        return "H dominant", nash
    if rows_w == {"L"}:
        return "L dominant", nash
    return "two equilibria", nash


def spectrum():
    """Game type for each number of loyal customers per firm, 0 to 20."""
    return {l: game_type(2 * l) for l in range(0, 21)}


def draw_spectrum(out: Path) -> None:
    """Three boxes, one per kind of game, with the range of loyal customers
    per firm for each (computed from the model), and an arrow underneath."""
    kinds = spectrum()
    runs = []
    for l in range(0, 21):
        k = kinds[l][0]
        if runs and runs[-1][0] == k:
            runs[-1][2] = l
        else:
            runs.append([k, l, l])
    assert [r[0] for r in runs] == ["L dominant", "two equilibria", "H dominant"]
    rng = {k: (lo, hi) for k, lo, hi in runs}
    head = {"L dominant": f"{rng['L dominant'][1]} or fewer loyal",
            "two equilibria": f"{rng['two equilibria'][0]} to {rng['two equilibria'][1]} loyal",
            "H dominant": f"{rng['H dominant'][0]} or more loyal"}
    body = {"L dominant": "Both price low\n(prisoners' dilemma)",
            "two equilibria": "Two equilibria:\nhigh or low",
            "H dominant": "Both price high\n(H is dominant)"}
    case = {"L dominant": "fewer loyal case: 7", "two equilibria": "first case: 11",
            "H dominant": "more loyal case: 13"}
    for k, l in (("L dominant", 7), ("two equilibria", 11), ("H dominant", 13)):
        assert kinds[l][0] == k
    fig, ax = plt.subplots(figsize=(10.0, 3.1), dpi=100)
    ax.set_xlim(0, 30)
    ax.set_ylim(0, 3.75)
    ax.axis("off")
    fig.subplots_adjust(left=0.005, right=0.995, top=0.99, bottom=0.01)
    fs = 21
    w, gap = 9.6, 0.6
    for i, k in enumerate(("L dominant", "two equilibria", "H dominant")):
        x0 = i * (w + gap)
        ax.add_patch(Rectangle((x0, 1.0), w, 2.7, fc="white", ec=RULE, lw=2))
        ax.text(x0 + w / 2, 3.32, head[k], ha="center", va="center",
                fontsize=fs, color=KIT, fontweight="bold")
        ax.text(x0 + w / 2, 2.3, body[k], ha="center", va="center",
                fontsize=fs, color=INK, fontweight="bold", linespacing=1.2)
        ax.text(x0 + w / 2, 1.32, case[k], ha="center", va="center",
                fontsize=fs - 4, color=RULE)
    ax.annotate("", xy=(29.8, 0.62), xytext=(0.2, 0.62),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=2.4,
                                mutation_scale=28))
    ax.text(15, 0.22, "More loyal customers: less elastic demand, higher prices",
            ha="center", va="center", fontsize=fs - 2, color=INK)
    save(fig, out)


def report(loyal):
    pay = profits(loyal)
    dots, rings = best_responses(pay)
    print(f"\n{loyal} loyal customers:")
    for w in "HL":
        for k in "HL":
            qw, qk = customers(loyal, w, k)
            print(f"  Wanda {w}, Kit {k}: customers {qw}, {qk};"
                  f" profits ({PRICE[w]} - 10) x {qw} = {pay[w, k][0]},"
                  f" ({PRICE[k]} - 10) x {qk} = {pay[w, k][1]}")
    for k in "HL":
        print(f"  if Kit picks {k}: Wanda gets H {pay['H', k][0]} or L {pay['L', k][0]}")
    nash = sorted(dots & rings)
    dominant = {w for w, _ in dots} if len({w for w, _ in dots}) == 1 else None
    print(f"  Wanda's best responses {sorted(dots)}; dominant: {dominant}")
    print(f"  Nash equilibria: {nash}")
    return pay, nash


def main() -> int:
    pay, nash = report(22)
    assert pay["L", "H"] == (490, 286) and nash == [("H", "H"), ("L", "L")]
    pay, nash = report(26)
    assert pay["H", "L"] == (338, 470) and nash == [("H", "H")]
    pay, nash = report(14)
    assert pay["L", "H"] == (530, 182) and nash == [("L", "L")]

    # Practice 13, problem 2: Maya's and Leo's food trucks (row Maya).
    food = {("H", "H"): (600, 500), ("H", "L"): (300, 450),
            ("L", "H"): (650, 250), ("L", "L"): (400, 300)}
    d, r = best_responses(food)
    print(f"\npractice 13, food trucks: Maya's best responses {sorted(d)},"
          f" Leo's {sorted(r)}, Nash {sorted(d & r)}")

    kinds = spectrum()
    print("\nloyal per firm -> game:")
    for l in range(0, 21):
        print(f"  {l:2d}: {kinds[l][0]}, Nash {kinds[l][1]}")
    assert kinds[7][0] == "L dominant" and kinds[11][0] == "two equilibria"
    assert kinds[13][0] == "H dominant"

    draw_groups(IMG / "customer-groups.svg")
    draw_who_rents(IMG / "who-rents.svg")
    draw_spectrum(IMG / "loyalty-spectrum.svg")
    draw_matrix(IMG / "game-base.svg", 22, "")
    draw_matrix(IMG / "game-base-wanda.svg", 22, "wanda")
    draw_matrix(IMG / "game-base-nash.svg", 22, "both")
    draw_matrix(IMG / "game-loyal26.svg", 26, "both")
    draw_matrix(IMG / "game-loyal14.svg", 14, "both")
    draw_matrix(IMG / "game-loyal14-plain.svg", 14, "")
    return 0


if __name__ == "__main__":
    sys.exit(main())
