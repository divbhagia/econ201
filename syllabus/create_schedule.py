import datetime as dt

# ---------------------------------------------------------------
# Semester configuration, from the CSUF Fall 2026 academic calendar
# ---------------------------------------------------------------

FIRST_DAY = dt.date(2026, 8, 22)  # first day of classes (Sat)
LAST_DAY = dt.date(2026, 12, 11)  # last day of classes (Fri)
CLASS_DAYS = (0, 2)  # Monday, Wednesday

# No-class dates -> label shown as a full-width row in the table
CLOSURES = {
    dt.date(2026, 9, 7): "Labor Day (campus closed)",
    dt.date(2026, 11, 11): "Veterans Day (campus closed)",
    dt.date(2026, 11, 23): "Fall Recess (no classes)",
    dt.date(2026, 11, 25): "Fall Recess (no classes)",
}

# From the university final exam grid for a MW 1:00 PM class.
FINAL_EXAM_DATE = "Mon 12/14"
FINAL_EXAM_TIME = "1:00--2:50 PM"

# ---------------------------------------------------------------
# Session plan: session number -> (topic, reading)
# ---------------------------------------------------------------

PLAN = {
    1: ("Introduction to the course", ""),
    2: ("The capitalist takeoff: Prosperity and its shadows", "1.1--1.5; 1.8--1.10"),
    3: (
        "Making economic decisions: Opportunity cost, rents, and incentives",
        "2.2",
    ),
    4: ("Why do markets matter? Specialization and comparative advantage", "2.3"),
    5: ("Winning brands and the price of Cheerios", "7.1--7.2"),
    6: (
        "What does it cost to make a car? Scale and the cost of production",
        "7.3--7.4",
    ),
    7: ("Who can get away with raising prices? Demand and elasticity", "7.5"),
    8: ("Steak, ramen, and recessions: Other elasticities", ""),
    9: (
        "Sweet spot: Choosing the price and quantity that maximize profit",
        "7.6",
    ),
    10: ("The surplus from a sale and who captures it", "7.7"),
    11: (
        "Standing out from the crowd: Product differentiation and competition",
        "7.8--7.9",
    ),
    12: (
        "Price wars: Strategic price setting and Nash equilibrium",
        "7.10; 4.2--4.3",
    ),
    13: (
        "Winner takes the market: Natural monopolies and competition policy",
        "7.11--7.12",
    ),
    14: (r"\textbf{Midterm 1}", ""),
    15: ("Classroom market experiment", ""),
    16: ("Cotton, war, and world markets: Supply and demand", "8.1--8.2"),
    17: (
        "Taking prices as given: Firms and consumers in competitive markets",
        "8.3--8.4",
    ),
    18: ("Who gets what: Allocation, distribution, and the gains from trade", "8.5"),
    19: ("The quinoa boom: Shifts in supply and demand", "8.6"),
    20: (
        "Oil booms and busts: Market dynamics in the short run and long run",
        "8.7--8.10",
    ),
    21: ("Salt taxes and rent control: Governments in the market", "8.12--8.13"),
    22: (r"\textbf{Midterm 2}", ""),
    23: ("Bananas, fish, and cancer: Private vs. social value wedge", "10.1--10.2"),
    24: (
        "Closing the wedge: Property rights, bargaining, and regulation",
        "10.3--10.5",
    ),
    25: ("Free riders and empty oceans: Public goods and common resources", "10.6--10.7"),
    26: ("The limits of markets", "10.8--10.11"),
    27: ("Review and Synthesis I", ""),
    28: ("Review and Synthesis II", ""),
}

# Midterms take no lecture number, so lecture numbers match the slide decks.
NON_LECTURE = {14, 22}

# Due column. Quizzes cover the previous week's material, normally on Mondays;
# Quiz 2 sits on Wed 9/9 because Labor Day removes that week's Monday. No quiz
# on the first class, on exam days, or on the Monday after an exam week.
DUE = {
    3: "Quiz 1",
    5: "Quiz 2",
    8: "Quiz 3",
    10: "Quiz 4",
    12: "Quiz 5",
    18: "Quiz 6",
    20: "Quiz 7",
    23: "Writing 1",
    25: "Quiz 8",
    27: "Writing 2",
}

# ---------------------------------------------------------------
# Modules: label -> sessions. Rendered as one merged cell per run of
# consecutive rows; closures inside a module stay inside its merge.
# ---------------------------------------------------------------

MODULES = {
    "The Big Picture": range(1, 3),
    "The Economist's Toolkit": range(3, 5),
    "Firms as Price Setters": range(5, 14),
    "Markets with Many Buyers and Sellers": range(15, 22),
    "Market Successes and Failures": range(23, 27),
    "Review": range(27, 29),
}
SESSION_MODULE = {n: label for label, ns in MODULES.items() for n in ns}

# \multirow cannot span a page break: a merge that would straddle one is
# split before these sessions (or date labels, for closures) and continues
# unlabeled on the next page. Re-tune when pagination shifts.
SPLIT_BEFORE = {26}
BREAK_BEFORE = set()

# ---------------------------------------------------------------
# Build the table
# ---------------------------------------------------------------


def meeting_dates():
    """Every Mon/Wed in the semester, closures included."""
    out, d = [], FIRST_DAY
    while d <= LAST_DAY:
        if d.weekday() in CLASS_DAYS:
            out.append(d)
        d += dt.timedelta(days=1)
    return out


rows, session, lecture = [], 0, 0
lecture_of = {}
for d in meeting_dates():
    label = f"{d:%a} {d.month}/{d.day}"
    if d in CLOSURES:
        rows.append(
            {"kind": "closure", "Date": label, "Topics": CLOSURES[d], "module": None}
        )
        continue

    session += 1
    topic, reading = PLAN[session]
    if session in NON_LECTURE:
        rows.append(
            {
                "kind": "span",
                "session": session,
                "Date": label,
                "Topics": topic,
                "Due": DUE.get(session, ""),
                "module": None,
            }
        )
    else:
        lecture += 1
        lecture_of[session] = lecture
        rows.append(
            {
                "kind": "lecture",
                "session": session,
                "Date": label,
                "Lecture": lecture,
                "Topics": topic,
                "Reading": reading,
                "Due": DUE.get(session, ""),
                "module": SESSION_MODULE.get(session),
            }
        )

rows.append(
    {
        "kind": "span",
        "module": None,
        "Date": FINAL_EXAM_DATE,
        "Topics": rf"\textbf{{Final exam}} ({FINAL_EXAM_TIME})",
        "Due": "",
    }
)

if session != len(PLAN):
    raise SystemExit(
        f"Plan/date mismatch: {session} meeting dates vs {len(PLAN)} planned"
    )

# A closure between two rows of the same module belongs to that module's merge.
for i, r in enumerate(rows):
    if r["kind"] != "closure":
        continue
    prev = next(
        (x["module"] for x in reversed(rows[:i]) if x["kind"] == "lecture"), None
    )
    nxt = next((x["module"] for x in rows[i + 1 :] if x["kind"] == "lecture"), None)
    if prev is not None and prev == nxt:
        r["module"] = prev

# Consecutive rows sharing a module form one merge group.
group_len = [0] * len(rows)
i = 0
while i < len(rows):
    m = rows[i]["module"]
    j = i + 1
    if m is not None:
        while (
            j < len(rows)
            and rows[j]["module"] == m
            and rows[j].get("session") not in SPLIT_BEFORE
            and rows[j]["Date"] not in SPLIT_BEFORE
        ):
            j += 1
    group_len[i] = j - i
    i = j

# ---------------------------------------------------------------
# Emit LaTeX rows
# ---------------------------------------------------------------

HLINE = r"\Xhline{1.75\arrayrulewidth}"
# Light rule inside a merge stops short of the module column; at a
# page-break split the merge has ended, so the rule runs full width and
# closes the module cell at the bottom of the page. These are \cmidrule,
# not \cline: PDF tagging (tagging=on) errors out on \cline.
CLINE = r"\arrayrulecolor{black!25}\cmidrule{2-6}" r"\arrayrulecolor{black}"
CLINE_FULL = r"\arrayrulecolor{black!25}\cmidrule{1-6}" r"\arrayrulecolor{black}"
lines = []
i = 0
while i < len(rows):
    n_grp = group_len[i]
    first = rows[i]
    if (
        first["kind"] == "lecture"
        and lecture_of
        and first.get("Lecture")
        in {lecture_of[s_] for s_ in BREAK_BEFORE if s_ in lecture_of}
    ):
        lines.append(r"\pagebreak")
    # A group that continues the previous row's module is the tail of a
    # page-break split; its label already appeared, so it stays blank.
    continued = i > 0 and first["module"] is not None and (
        rows[i - 1]["module"] == first["module"]
    )
    for k in range(max(n_grp, 1)):
        r = rows[i + k]
        if r["module"] is not None and k == 0 and not continued:
            if n_grp == 1:
                mod = rf"{r['module']}"
            else:
                mod = rf"\multirow{{{n_grp}}}{{=}}{{\centering {r['module']}}}"
        else:
            mod = ""

        if r["kind"] == "lecture":
            line = (
                f"{mod} & {r['Date']} & {r['Lecture']} & {r['Topics']} "
                f"& {r['Reading']} & {r['Due']} \\\\"
            )
        elif r["kind"] == "closure":
            line = (
                f"{mod} & {r['Date']} & "
                f"\\multicolumn{{3}}{{l}}{{{r['Topics']}}} &  \\\\"
            )
        elif r["kind"] == "span":
            line = (
                f" & {r['Date']} & "
                f"\\multicolumn{{3}}{{l}}{{{r['Topics']}}} "
                f"& {r['Due']} \\\\"
            )
        # Heavy rules only where a module ends or begins; light everywhere
        # else. The closing rule lives in the wrapper's \endlastfoot.
        idx = i + k
        nxt = rows[idx + 1] if idx + 1 < len(rows) else None
        last_in_grp = k == max(n_grp, 1) - 1
        if nxt is None:
            rule = ""
        elif not last_in_grp:
            rule = CLINE
        else:
            r_mod, nxt_mod = r.get("module"), nxt.get("module")
            if (r_mod is not None and nxt_mod != r_mod) or (
                nxt_mod is not None and nxt_mod != r_mod
            ):
                rule = HLINE
            elif r_mod is not None:  # same module resumes: page-break split
                rule = CLINE_FULL
            else:
                rule = CLINE
        line += rule
        lines.append(line)
    i += max(n_grp, 1)

# A trailing \\ before \end{xltabular} would render a phantom empty row.
if lines[-1].rstrip().endswith("\\\\"):
    lines[-1] = lines[-1].rstrip()[:-2]

with open("syllabus/schedule.tex", "w") as f:
    f.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------
# Website: schedule page and per-module content pages
#
# Same plan, same numbers, three outputs. The LaTeX table above is the
# printed syllabus; what follows is the web schedule and the module pages
# students actually click through during the semester.
# ---------------------------------------------------------------

import pathlib

MODULE_SLUG = {
    "The Big Picture": "the-big-picture",
    "The Economist's Toolkit": "economists-toolkit",
    "Firms as Price Setters": "firms-as-price-setters",
    "Markets with Many Buyers and Sellers": "markets-with-many-buyers-and-sellers",
    "Market Successes and Failures": "market-successes-and-failures",
    "Review": "review",
}

# Materials go live only once they are written and checked. Add a lecture
# number here, with whatever it has, and both the schedule and the module
# page pick it up on the next run.
MATERIALS = {
    # slides_pdf is the tagged-PDF copy of the deck (make slides-pdf), which
    # the accessibility statement promises for every published deck.
    1: {"slides": "slides/lecture1.html", "slides_pdf": "slides/lecture1.pdf"},
    2: {"slides": "slides/lecture2.html", "slides_pdf": "slides/lecture2.pdf",
        "notes": "notes/notes02.pdf",
        "practice": "practice/practice02.html",
        "worksheet": "worksheets/worksheet02.pdf"},
    3: {"slides": "slides/lecture3.html", "slides_pdf": "slides/lecture3.pdf",
        "practice": "practice/practice03.html",
        "worksheet": "worksheets/worksheet03.pdf"},
    4: {"slides": "slides/lecture4.html", "slides_pdf": "slides/lecture4.pdf",
        "practice": "practice/practice04.html",
        "worksheet": "worksheets/worksheet04.pdf"},
}

# Lecture 2's practice page bundles guided reading; from lecture 3 on the
# pages are practice problems only, so the links say what each page is.
def _practice_label(lec):
    if lec == 2:
        return ("Guided reading and practice",
                "guided reading questions and practice problems")
    return ("Practice problems", "practice problems")


def _icons(lec):
    """Emoji links for one lecture, or empty if nothing is published yet."""
    m = MATERIALS.get(lec)
    if not m:
        return ""
    out = []
    if m.get("slides"):
        out.append(
            f'<a href="{m["slides"]}" target="_blank" rel="noopener" '
            f'aria-label="Lecture {lec} slides (opens in a new tab)">'
            f'<span aria-hidden="true">\U0001F5A5\uFE0F</span></a>'
        )
    if m.get("worksheet"):
        out.append(
            f'<a href="{m["worksheet"]}" target="_blank" rel="noopener" '
            f'aria-label="Lecture {lec} worksheet, PDF (opens in a new tab)">'
            f'<span aria-hidden="true">\U0001F5D2\uFE0F</span></a>'
        )
    if m.get("notes"):
        out.append(
            f'<a href="{m["notes"]}" target="_blank" rel="noopener" '
            f'aria-label="Lecture {lec} notes, PDF (opens in a new tab)">'
            f'<span aria-hidden="true">\U0001F4C4</span></a>'
        )
    if m.get("practice"):
        out.append(
            f'<a href="{m["practice"]}" target="_blank" rel="noopener" '
            f'aria-label="Lecture {lec} {_practice_label(lec)[1]} (opens in a new tab)">'
            f'<span aria-hidden="true">\u270D\uFE0F</span></a>'
        )
    return " ".join(out)


def _web(text):
    """LaTeX conventions out, HTML in."""
    return (text.replace("--", "&ndash;")
                .replace(r"\textbf{", "<strong>").replace("}", "}")
                .replace("&", "&amp;") if False else
            text.replace("--", "&ndash;")
                .replace(r"\textbf{Midterm 1}", "Midterm 1")
                .replace(r"\textbf{Midterm 2}", "Midterm 2")
                .replace(r"\textbf{Final exam}", "Final exam"))


# How many table rows each module spans, closures included.
span = {}
for r in rows:
    if r["module"]:
        span[r["module"]] = span.get(r["module"], 0) + 1

html_rows, seen_mod, prev_mod = [], set(), object()
for r in rows:
    mod = r["module"]
    starts = mod != prev_mod
    prev_mod = mod
    date = r["Date"]

    if mod and mod not in seen_mod:
        seen_mod.add(mod)
        slug = MODULE_SLUG.get(mod)
        label = f'<a href="content/{slug}.html">{mod}</a>' if slug else mod
        mod_cell = (f'<th scope="rowgroup" rowspan="{span[mod]}">{label}</th>')
    elif mod:
        mod_cell = ""
    else:
        mod_cell = "<td></td>"

    edge = " module-start" if starts else ""
    date_cell = f'<th scope="row">{date}</th>'

    if r["kind"] == "closure":
        html_rows.append(f'<tr class="recess{edge}">{mod_cell}{date_cell}'
                         f'<td colspan="3">{_web(r["Topics"])}</td></tr>')
    elif r["kind"] == "span":
        due = f' &mdash; {r["Due"]}' if r.get("Due") else ""
        html_rows.append(f'<tr class="assessment{edge}">{mod_cell}{date_cell}'
                         f'<td colspan="3"><strong>{_web(r["Topics"])}</strong>'
                         f'{due}</td></tr>')
    else:
        lec = r["Lecture"]
        due = (f'<strong>{r["Due"]}</strong>; ' if r.get("Due") else "")
        html_rows.append(
            f'<tr class="{edge.strip()}">{mod_cell}{date_cell}'
            f'<td class="topics">{due}{_web(r["Topics"])}</td>'
            f'<td class="refs">{_web(r["Reading"])}</td>'
            f'<td class="mat">{_icons(lec)}</td></tr>'
        )

table = (
    '<div class="table-scroll" tabindex="0" role="region" '
    'aria-label="Semester schedule table">\n'
    '<table class="schedule-table">\n'
    '<thead>\n<tr>\n'
    '  <th scope="col" style="width:7.4em">Module</th>\n'
    '  <th scope="col" style="width:5.6em">Date</th>\n'
    '  <th scope="col">Topic</th>\n'
    '  <th scope="col" style="width:5.2em">Reading</th>\n'
    '  <th scope="col" style="width:5.4em">Materials</th>\n'
    '</tr>\n</thead>\n<tbody>\n' + "\n".join(html_rows) + '\n</tbody>\n</table>\n</div>\n'
)

first_slug = MODULE_SLUG[next(iter(MODULES))]
schedule_page = f'''---
title: "Schedule"
sidebar: false
toc: false
format: html
---

Materials appear here as we reach each lecture. For materials grouped by
module, see the
[Content](content/{first_slug}.qmd) pages. Readings refer to sections of
[*The Economy 2.0: Microeconomics*](https://books.core-econ.org/the-economy/microeconomics).
Quizzes are given at the start of class on the dates marked below.

<p class="materials-legend">
<span aria-hidden="true">🖥️</span> Slides &nbsp;
<span aria-hidden="true">🗒️</span> Worksheet (PDF) &nbsp;
<span aria-hidden="true">📄</span> Notes (PDF) &nbsp;
<span aria-hidden="true">✍️</span> Practice
</p>

```{{=html}}
{table}```
'''
pathlib.Path("schedule.qmd").write_text(schedule_page)

# ---- one content page per module -------------------------------------------

ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"]
content_dir = pathlib.Path("content")
content_dir.mkdir(exist_ok=True)

for idx, (label, sessions) in enumerate(MODULES.items()):
    slug = MODULE_SLUG[label]
    blocks = []
    for s in sessions:
        if s in NON_LECTURE:
            continue
        lec = lecture_of[s]
        topic, reading = PLAN[s]
        m = MATERIALS.get(lec, {})
        links = []
        # `what`, not `label`: `label` is the module name this page is titled
        # after, and shadowing it here silently retitled every module page.
        for key, text, what in (
                ("slides", "Slides", "slides"),
                ("slides_pdf", "Slides (PDF)", "slides as a tagged PDF"),
                ("notes", "Notes", "notes as a PDF"),
                ("practice", *_practice_label(lec)),
                ("worksheet", "Worksheet", "worksheet")):
            if m.get(key):
                links.append(
                    f'<a class="btn btn-outline-primary" href="../{m[key]}" '
                    f'target="_blank" rel="noopener" role="button" '
                    f'aria-label="Lecture {lec} {what} '
                    f'(opens in a new tab)">{text}</a>'
                )
        link_html = ('<p class="lecture-links">' + "\n".join(links) + '</p>'
                     if links else
                     '<p class="lecture-links dim">Materials posted closer to the date.</p>')
        reading_html = (f'<p><strong>Reading:</strong> {_web(reading)}</p>'
                        if reading else "")
        blocks.append(
            f'::: {{.lecture}}\n'
            f'<h2>Lecture {lec}: {_web(topic)}</h2>\n\n'
            f'{reading_html}\n'
            f'{link_html}\n'
            f':::\n'
        )
    # The module pages carry the Modules sidebar from _quarto.yml, so a
    # student can move between modules without going back to the navbar.
    page = (f'---\ntitle: "{label}"\nsubtitle: "Module {ROMAN[idx]}"\n'
            f'toc: false\nformat: html\n---\n\n'
            f'Materials are posted as we go. See the [Schedule](../schedule.qmd) '
            f'for dates and assessments.\n\n'
            + "\n".join(blocks))
    (content_dir / f"{slug}.qmd").write_text(page)

print(f"schedule.qmd written: {len(html_rows)} rows")
print(f"content pages written: {len(MODULES)}")
