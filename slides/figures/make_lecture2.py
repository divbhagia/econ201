"""
Figures for Lecture 2: history's hockey stick, and the other hockey stick.

Run from the course root:

    python3 slides/figures/make_lecture2.py            # uses cached data
    python3 slides/figures/make_lecture2.py --refresh  # re-download first

Data, both served by Our World in Data and cached in slides/figures/data/
so the figures rebuild offline and the numbers behind them live in the repo:
  maddison.csv   Maddison Project Database 2023, GDP per capita in 2011
                 international dollars, five countries
  co2-world.csv  Global Carbon Budget 2024, world CO2 emissions from fossil
                 fuels and industry, tonnes per year

Output, in slides/img/:
  hockey.svg        GDP per person, 1000 to 2022, in the spirit of CORE Fig 1.1
  hockey-side.svg   the same, squarer and with larger type, for a 60% column
  hockey-1600.svg   the same from 1600
  co2.svg           world CO2 emissions, 1750 to 2024, cf. CORE Fig 1.2a
  temperature.svg   Northern Hemisphere temperature since 1700, cf. CORE Fig 1.2b
  germanies.svg     GDP per capita, East and West Germany 1950 to 1989, CORE Fig 1.16
  biosphere.svg     economy inside society inside the biosphere, cf. CORE Figs 1.20 and 1.21
  capitalism.svg    private property, markets, firms as nested circles, cf. CORE Fig 1.14

The GDP series are smoothed with a centred 10-year moving average. The 2023
Maddison release has annual English GDP from 1253 (Broadberry et al.), and
plotted raw the harvest-to-harvest swings turn the medieval stretch into a
fuzzy band. Sparse series are filled by linear interpolation before
averaging, which leaves them unchanged.

Accessibility: Okabe-Ito colours with the pair for the two lines that end
closest together (China, Mexico) chosen for the largest separation under
simulated colour-vision deficiency; every line labelled at its end so nothing
depends on matching a colour to a legend; heavy lines and large type for a
projector; text converted to paths so the SVG looks the same on any machine.
Alt text lives in the slide file beside each image.
"""

import argparse
import sys
import urllib.request
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter

matplotlib.use("Agg")

# matplotlib's font cache does not see fonts installed in ~/Library/Fonts,
# so register the Fira Sans files directly. Falls back to sans-serif.
for f in Path.home().glob("Library/Fonts/FiraSans-*.otf"):
    font_manager.fontManager.addfont(str(f))

ROOT = Path(__file__).resolve().parents[2]
# PDF copies of the figures the worksheets use, so slides and handouts share
# one source. Real text (Type 42) so the PDF stays searchable and taggable.
PDF_DIR = ROOT / "worksheets" / "figures"
# Optional: also drop PNG previews here for quick viewing (set by env var).
import os
SCRATCH = Path(os.environ["FIG_PREVIEW_DIR"]) if os.environ.get("FIG_PREVIEW_DIR") else None
DATA = ROOT / "slides" / "figures" / "data"
IMG = ROOT / "slides" / "img"

MADDISON_URL = (
    "https://ourworldindata.org/grapher/gdp-per-capita-maddison-project-database.csv"
    "?v=1&csvType=full&useColumnShortNames=true"
)
CO2_URL = (
    "https://ourworldindata.org/grapher/annual-co2-emissions-per-country.csv"
    "?v=1&csvType=filtered&useColumnShortNames=true&country=OWID_WRL"
)
# Northern Hemisphere temperature, deviation from the 1951 to 1990 average,
# the series behind CORE Figure 1.2b.
TEMP_URL = (
    "https://ourworldindata.org/grapher/"
    "northern-hemisphere-temperatures-over-the-long-run-deviation-from-1951-1990-mean-temperature-c.csv"
    "?v=1&csvType=full&useColumnShortNames=true"
)
# Our World in Data's reproduction of CORE Figure 1.16 (Conference Board,
# Total Economy Database 2015; 1990 international dollars, 1950 to 1989).
GERMANY_URL = (
    "https://ourworldindata.org/grapher/the-two-germanies-planning-and-capitalism.csv"
    "?v=1&csvType=full&useColumnShortNames=true"
)

# Entity name in the data -> label on the chart.
COUNTRIES = {
    "United Kingdom": "UK",
    "United States": "US",
    "China": "China",
    "India": "India",
    "Mexico": "Mexico",
}

# Okabe-Ito, colour-blind safe, with the course accent (close to Okabe-Ito
# vermillion) for Britain. China and Mexico end within $1,000 of each other,
# so they get the pair with the largest separation under simulated
# protanopia, deuteranopia, and tritanopia (black and amber; Machado 2009
# matrices, CIE76 distance). All lines share one weight.
COLOR = {
    "UK": "#BF5700",
    "US": "#0072B2",
    "China": "#000000",
    "India": "#56B4E9",
    "Mexico": "#E69F00",
    "World": "#1a1a1a",
    "West Germany": "#0072B2",
    "East Germany": "#BF5700",
}
LW = 2.6
INK = "#1a1a1a"
GRID = "#d9d9d9"
FIRST_YEAR = 1000
WINDOW = 10

# Alone on a slide Reveal fits the image to the free height under the title,
# unless the full slide width (1280) binds first; it does not know about the
# side padding. Keep the aspect ratio under about 1.9 so height binds and
# the figure stays inside the padded area.
FULL = (11.2, 6.0)
# Beside text the image fits the column width instead, so a squarer shape
# makes it taller; type is scaled up because the image is drawn smaller.
SIDE = (8.2, 5.9)
FONT = 22

plt.rcParams.update(
    {
        "font.family": ["Fira Sans", "sans-serif"],
        "font.size": 19,
        "svg.fonttype": "path",
        "pdf.fonttype": 42,
        "axes.edgecolor": INK,
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "xtick.labelsize": 19,
        "ytick.labelsize": 19,
    }
)


# ----------------------------------------------------------------- data ---

def fetch(url: str) -> pd.DataFrame:
    print(f"downloading {url}")
    # OWID answers 403 to urllib's default user agent.
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (econ201 figures)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return pd.read_csv(r)


def load_maddison(refresh: bool) -> pd.DataFrame:
    path = DATA / "maddison.csv"
    if refresh or not path.exists():
        raw = fetch(MADDISON_URL)
        df = raw[raw["entity"].isin(COUNTRIES)].dropna(subset=["gdp_per_capita"])
        df = df[df["year"] >= FIRST_YEAR]
        df = df.assign(country=df["entity"].map(COUNTRIES))
        df = df[["country", "year", "gdp_per_capita"]].sort_values(["country", "year"])
        DATA.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        print(f"cached {len(df)} rows to {path.relative_to(ROOT)}")
    return pd.read_csv(path)


def load_co2(refresh: bool) -> pd.Series:
    path = DATA / "co2-world.csv"
    if refresh or not path.exists():
        raw = fetch(CO2_URL)
        df = raw[["year", "emissions_total"]].dropna()
        DATA.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        print(f"cached {len(df)} rows to {path.relative_to(ROOT)}")
    df = pd.read_csv(path)
    return df.set_index("year")["emissions_total"] / 1e9  # billion tonnes


def load_germany(refresh: bool) -> pd.DataFrame:
    path = DATA / "germanies.csv"
    if refresh or not path.exists():
        raw = fetch(GERMANY_URL)
        df = raw[raw["entity"].isin(["East Germany", "West Germany"])]
        df = df.rename(columns={"gdp_per_capita__1990_dollar": "gdp_per_capita"})
        df = df[["entity", "year", "gdp_per_capita"]].dropna().sort_values(["entity", "year"])
        DATA.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        print(f"cached {len(df)} rows to {path.relative_to(ROOT)}")
    return pd.read_csv(path)


def load_temperature(refresh: bool) -> pd.Series:
    path = DATA / "temperature-nh.csv"
    if refresh or not path.exists():
        raw = fetch(TEMP_URL)
        df = raw.rename(columns={"deviation_from_1951_1990_average_temperature": "anomaly"})
        df = df[["year", "anomaly"]].dropna()
        DATA.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        print(f"cached {len(df)} rows to {path.relative_to(ROOT)}")
    df = pd.read_csv(path)
    return df.set_index("year")["anomaly"]


def annual(g: pd.DataFrame) -> pd.Series:
    """One value per year, linearly interpolated between the points we have."""
    y = g.set_index("year")["gdp_per_capita"]
    return y.reindex(range(int(y.index.min()), int(y.index.max()) + 1)).interpolate()


def smooth(g: pd.DataFrame, window: int = WINDOW) -> pd.Series:
    """Centred moving average; sparse stretches come through unchanged."""
    return annual(g).rolling(window, center=True, min_periods=1).mean()


# -------------------------------------------------------------- drawing ---

def dollars(x, _pos=None) -> str:
    return f"${x:,.0f}"


def spread(ax, points, gap_pt):
    """Nudge end labels apart vertically so none overlap.

    points: list of (label, y_data). Returns {label: y_data_for_label}.
    Works in display pixels, so it is scale-agnostic.
    """
    fig = ax.figure
    gap = gap_pt / 72 * fig.dpi
    to_disp = lambda y: ax.transData.transform((0, y))[1]
    to_data = lambda p: ax.transData.inverted().transform((0, p))[1]
    order = sorted(points, key=lambda t: t[1])
    disp = [to_disp(y) for _, y in order]
    for i in range(1, len(disp)):
        if disp[i] - disp[i - 1] < gap:
            disp[i] = disp[i - 1] + gap
    top = ax.transAxes.transform((0, 1))[1]
    overflow = disp[-1] - top
    if overflow > 0:
        disp = [d - overflow for d in disp]
    return {label: to_data(d) for (label, _), d in zip(order, disp)}


def new_axes(figsize=FULL, font=FONT, right=None):
    plt.rcParams.update({"font.size": font, "xtick.labelsize": font, "ytick.labelsize": font})
    fig, ax = plt.subplots(figsize=figsize, dpi=100)
    left = 0.15 if figsize[0] > 9 else 0.185
    if right is None:
        right = 0.88 if figsize[0] > 9 else 0.865
    fig.subplots_adjust(left=left, right=right, top=0.99, bottom=0.09 if figsize[0] <= 9 else 0.105)
    ax.grid(axis="y", color=GRID, lw=1, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", length=5, width=1)
    return fig, ax


def finish(fig, ax, series, ylabel, out: Path, font=FONT):
    """Draw lines with an end marker and a direct label, then save.

    series: dict label -> pd.Series indexed by year.
    """
    last_year = max(int(s.index.max()) for s in series.values())
    ends = []
    for label, s in series.items():
        c = COLOR[label]
        ax.plot(s.index, s.values, color=c, lw=LW, solid_capstyle="round", zorder=5)
        ax.plot(s.index[-1], s.values[-1], marker="o", ms=8, color=c, zorder=7, clip_on=False)
        ends.append((label, float(s.values[-1])))

    fig.canvas.draw()  # transforms must be final before spreading labels
    where = spread(ax, ends, gap_pt=22)
    for label, _ in ends:
        ax.annotate(
            label,
            xy=(last_year, where[label]),
            xytext=(11, 0),
            textcoords="offset points",
            ha="left",
            va="center",
            fontsize=font,
            color=COLOR[label],
            annotation_clip=False,
        )
    ax.set_ylabel(ylabel, color=INK, fontsize=font - 2, labelpad=6)
    IMG.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format="svg")
    if out.stem in ("hockey", "germanies"):
        PDF_DIR.mkdir(parents=True, exist_ok=True)
        fig.savefig(PDF_DIR / f"{out.stem}.pdf", format="pdf")
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


def draw_gdp(df: pd.DataFrame, out: Path, start: int = FIRST_YEAR,
             figsize=FULL, font=FONT) -> None:
    series = {}
    for label, g in df.groupby("country"):
        s = smooth(g)
        series[label] = s[s.index >= start]
    last_year = int(df["year"].max())

    fig, ax = new_axes(figsize, font)
    ax.set_xlim(start, last_year)
    span = last_year - start
    step = 200 if span > 700 else 50
    # On the zoomed chart, skip the first tick: it sits on top of the $0
    # label at the origin.
    first = start if start == FIRST_YEAR else start + step
    ticks = list(range(first, last_year + 1, step))
    ax.set_xticks(ticks)
    ax.set_xticklabels([str(t) for t in ticks])
    ax.set_ylim(0, 66000)
    ax.set_yticks(list(range(0, 60001, 10000)))
    ax.yaxis.set_major_formatter(FuncFormatter(dollars))
    finish(fig, ax, series, "GDP per capita (2011 international $)", out, font)


def draw_co2(s: pd.Series, out: Path) -> None:
    first, last = int(s.index.min()), int(s.index.max())
    fig, ax = new_axes()
    ax.set_xlim(first, last)
    ticks = list(range(1750, last + 1, 50))
    ax.set_xticks(ticks)
    ax.set_xticklabels([str(t) for t in ticks])
    ax.set_ylim(0, 44)
    ax.set_yticks(list(range(0, 41, 10)))
    finish(fig, ax, {"World": s}, "Billion tonnes of CO$_2$ per year", out)


def draw_germany(df: pd.DataFrame, out: Path) -> None:
    series = {e: g.set_index("year")["gdp_per_capita"] for e, g in df.groupby("entity")}
    fig, ax = new_axes(right=0.79)  # room for the long end labels
    ax.set_xlim(1950, 1989)
    ax.set_xticks(list(range(1955, 1990, 5)))  # skip 1950: it collides with the $0 label
    ax.set_ylim(0, 20000)
    ax.set_yticks(list(range(0, 20001, 5000)))
    ax.yaxis.set_major_formatter(FuncFormatter(dollars))
    finish(fig, ax, series, "GDP per capita (1990 international $)", out)


def draw_temperature(t: pd.Series, out: Path, start: int = 1700) -> None:
    """Annual series in light grey, ten-year moving average in the accent."""
    t = t[t.index >= start]
    smooth_t = t.rolling(WINDOW, center=True, min_periods=1).mean()
    last = int(t.index.max())
    fig, ax = new_axes(right=0.80)  # room for the end label
    ax.set_xlim(start, last)
    ax.set_xticks(list(range(1750, last + 1, 50)))
    ax.set_ylim(-1.0, 1.2)
    ax.set_yticks([-1.0, -0.5, 0, 0.5, 1.0])
    ax.axhline(0, color=INK, lw=1, ls=(0, (4, 3)), zorder=2)
    ax.plot(t.index, t.values, color="#bbbbbb", lw=1.2, zorder=3)
    ax.plot(smooth_t.index, smooth_t.values, color=COLOR["UK"], lw=LW, zorder=5)
    ax.plot(smooth_t.index[-1], smooth_t.values[-1], marker="o", ms=8, color=COLOR["UK"],
            zorder=7, clip_on=False)
    ax.annotate("10-year average", xy=(last, smooth_t.values[-1]), xytext=(11, 0),
                textcoords="offset points", ha="left", va="center", fontsize=FONT - 2,
                color=COLOR["UK"], annotation_clip=False)
    ax.set_ylabel("Temperature vs. 1951 to 1990 average (°C)", color=INK, fontsize=FONT - 2, labelpad=6)
    IMG.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format="svg")
    fig.savefig(SCRATCH / "temperature.png", format="png", dpi=110) if SCRATCH else None
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


def draw_biosphere(out: Path) -> None:
    """The economy sits inside society, which sits inside the biosphere.

    Cleaner take on CORE Figures 1.20 and 1.21: three nested layers, with the
    economy drawn as households and firms exchanging with each other, drawing
    energy and materials from the biosphere and sending waste back to it.
    """
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

    fig, ax = plt.subplots(figsize=(11.2, 6.0), dpi=100)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    ax.set_xlim(0, 112); ax.set_ylim(0, 60); ax.axis("off")

    GREEN, BROWN, BLUE = "#1b5e3b", "#7a3b00", "#1f3b73"

    def layer(x, y, w, h, fc, ec, label, r=3):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                    fc=fc, ec=ec, lw=2.2))
        ax.text(x + 2.4, y + h - 2.2, label, ha="left", va="top", fontsize=22,
                color=ec, fontweight="bold")

    layer(1, 1, 110, 58, "#e6f2ea", GREEN, "Biosphere: air, water, land, climate, all living things")
    layer(12, 13, 88, 38, "#fff4e6", BROWN, "Society: families, communities, governments, rules")
    layer(30, 17, 52, 26, "#eef2fb", BLUE, "The economy")

    hx, fx, by, bw, bh = 33, 61, 22, 18, 12
    for x, name in ((hx, "Households"), (fx, "Firms")):
        ax.add_patch(FancyBboxPatch((x, by), bw, bh, boxstyle="round,pad=0,rounding_size=2",
                                    fc="white", ec=BLUE, lw=2.2))
        ax.text(x + bw / 2, by + bh / 2, name, ha="center", va="center", fontsize=21,
                color=BLUE, fontweight="bold")

    def arrow(p, q, color, rad=0.0):
        ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=22, lw=2.4,
                                     color=color, connectionstyle=f"arc3,rad={rad}"))

    # Exchange inside the economy; labels sit clear of the two boxes.
    arrow((hx + bw, by + bh - 2.5), (fx, by + bh - 2.5), BLUE)
    ax.text((hx + bw + fx) / 2, by + bh + 0.8, "work, savings", ha="center", va="bottom",
            fontsize=18, color=BLUE)
    arrow((fx, by + 2.5), (hx + bw, by + 2.5), BLUE)
    ax.text((hx + bw + fx) / 2, by - 0.8, "goods, services, wages", ha="center", va="top",
            fontsize=18, color=BLUE)

    # Flows between the biosphere and the economy, routed through the blank
    # side channels of the society layer down to the biosphere's bottom band.
    arrow((18, 6), (30, 26), GREEN, rad=0.25)
    ax.text(4, 4.2, "energy, materials, food", ha="left", va="center", fontsize=19, color=GREEN)
    arrow((82, 26), (94, 6), BROWN, rad=0.25)
    ax.text(108, 4.2, "waste, emissions, heat", ha="right", va="center", fontsize=19, color=BROWN)

    IMG.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format="svg")
    fig.savefig(SCRATCH / "biosphere.png", format="png", dpi=110) if SCRATCH else None
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


def draw_capitalism(out: Path) -> None:
    """Our version of CORE Figure 1.14: the three institutions, nested.

    Three panels. Each adds one institution inside the last, so capitalism
    reads as private property plus markets plus firms.
    """
    from matplotlib.patches import Circle

    fig, axes = plt.subplots(1, 3, figsize=(11.2, 5.6), dpi=100)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.98, bottom=0.02, wspace=0.05)

    # Three tints of one blue, dark text throughout.
    layers = [
        ("Private\nProperty", "#cfe4f4", INK),
        ("Markets", "#9ccbea", INK),
        ("Firms", "#5aaee0", INK),
    ]
    titles = [
        "Self-sufficient\nfamily production",
        "Market economy with\nfamily production",
        "Capitalist\neconomic system",
    ]
    radii = [1.0, 0.64, 0.34]
    # Inner circles sit low, so each outer ring keeps a thick band at the top
    # for its label.
    centres = [0.0] + [-(radii[0] - r) * 0.8 for r in radii[1:]]

    for k, ax in enumerate(axes):
        ax.set_aspect("equal"); ax.axis("off")
        ax.set_xlim(-1.15, 1.15); ax.set_ylim(-1.85, 1.15)
        n = k + 1
        for i in range(n):
            label, color, tc = layers[i]
            r, cy = radii[i], centres[i]
            ax.add_patch(Circle((0, cy), r, fc=color, ec="white", lw=2.5, zorder=i))
            if i == n - 1:
                y = cy  # innermost: label at the centre
                label = label.replace("\n", " ")
            else:
                # midpoint of the band between this circle's top and the next one's top
                y = ((cy + r) + (centres[i + 1] + radii[i + 1])) / 2
            ax.text(0, y, label, ha="center", va="center", fontsize=18 if i < n - 1 else 21,
                    color=tc, fontweight="bold", zorder=10, linespacing=1.05)
        ax.text(0, -1.45, titles[k], ha="center", va="center", fontsize=22,
                color="#1a1a1a", fontweight="bold")

    IMG.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format="svg")
    fig.savefig(SCRATCH / "capitalism.png", format="png", dpi=110) if SCRATCH else None
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


# ----------------------------------------------------------------- main ---

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--refresh", action="store_true", help="re-download the data")
    args = p.parse_args()

    gdp = load_maddison(args.refresh)
    co2 = load_co2(args.refresh)
    ger = load_germany(args.refresh)
    temp = load_temperature(args.refresh)

    draw_gdp(gdp, IMG / "hockey.svg")
    draw_gdp(gdp, IMG / "hockey-side.svg", figsize=SIDE)
    draw_gdp(gdp, IMG / "hockey-1600.svg", start=1600)
    draw_co2(co2, IMG / "co2.svg")
    draw_temperature(temp, IMG / "temperature.svg")
    draw_germany(ger, IMG / "germanies.svg")
    draw_biosphere(IMG / "biosphere.svg")
    draw_capitalism(IMG / "capitalism.svg")

    # Numbers quoted on the slides, printed so the text can be checked.
    print("\nraw values used in slide text")
    for c in COUNTRIES.values():
        g = gdp[gdp["country"] == c].set_index("year")["gdp_per_capita"]
        yrs = [y for y in (1800, 1870, 1950, 1980, 2022) if y in g.index]
        print(f"  {c:7s}", "  ".join(f"{y}: ${g[y]:,.0f}" for y in yrs))
    uk = gdp[gdp["country"] == "UK"].set_index("year")["gdp_per_capita"]
    ch = gdp[gdp["country"] == "China"].set_index("year")["gdp_per_capita"]
    g_uk = (uk[2022] / uk[1800]) ** (1 / 222) - 1
    g_ch = (ch[2022] / ch[1980]) ** (1 / 42) - 1
    print(f"  UK 1800-2022: total {(uk[2022]/uk[1800]-1)*100:,.0f}%, {g_uk*100:.2f}% a year")
    print(f"  China 1980-2022: total {(ch[2022]/ch[1980]-1)*100:,.0f}%, {g_ch*100:.2f}% a year")
    print(f"  CO2 {int(co2.index.min())}: {co2.iloc[0]:.3f} bn t;  {int(co2.index.max())}: {co2.iloc[-1]:.1f} bn t")
    return 0


if __name__ == "__main__":
    sys.exit(main())
