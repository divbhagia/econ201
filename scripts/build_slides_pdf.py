r"""Tagged-PDF slide decks from the same .qmd sources as the web decks.

Usage (from the econ201 folder):  python3 scripts/build_slides_pdf.py 1 2

Route: pandoc's beamer writer emits the frames, then the beamer template is
discarded and the body is compiled under ltx-talk, the LaTeX team's
tagging-aware presentation class (beamer itself refuses \DocumentMetadata).
The output must pass veraPDF PDF/UA-2; the build fails if it does not.

Deliberate choices:
  - Overlay specs are stripped: the PDF is the downloadable study artifact,
    complete slides, one page per frame.
  - fig-alt survives via assets/beamer-deck.lua (pandoc's writers drop it).
  - Speaker notes, if any, are dropped.
"""
import pathlib, re, shutil, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SLIDES = ROOT / "slides"

# Theme: as close to the web decks (assets/slides.scss) as ltx-talk allows.
# Burnt orange accent, near-black ink, Lato body, Fira Sans Condensed headings,
# *term* as orange bold. Fira Sans Condensed is a system font (fontspec finds
# it by name); Lato comes from the TeX tree. ltx-talk's template keys are
# experimental, so if a tlmgr update breaks an \EditInstance line, the visual
# theme is all that is lost; tagging does not depend on it.
PREAMBLE = r"""\DocumentMetadata{pdfstandard=UA-2,pdfversion=2.0,lang=en-US,tagging=on}
\documentclass[frame-title-arg, font-size = 13pt]{ltx-talk}
\usepackage{amsmath,graphicx}
% pandoc sets tables as longtable with booktabs rules
\usepackage{longtable,booktabs,array}
\providecommand{\tightlist}{}
\providecommand{\note}[1]{}
% Ligatures=TeX on every family: without it -- prints as two hyphens rather
% than an en dash, which is what the heading font was doing.
\setmainfont{Lato}[Ligatures=TeX]
\setsansfont{Lato}[Ligatures=TeX]
\newfontfamily\headingfont{Fira Sans Condensed}[Ligatures=TeX]
\DeclareColor{accent}[HTML]{BF5700}
\DeclareColor{ink}[HTML]{1A1A1A}
\DeclareColor{muted}[HTML]{595A5B}
\DeclareColor{structure}[HTML]{1A1A1A}
\color{ink}
% The web deck spaces consecutive statements (.plain p, 0.6em); LaTeX runs
% them together, so a slide of short paragraphs reads as one block of text.
\setlength{\parindent}{0pt}
% Kept as its own length because ltx-talk's column environment runs
% \@parboxrestore, which zeroes \parskip; the filter restores it from this.
\newlength{\bodyparskip}
\setlength{\bodyparskip}{0.6em}
\setlength{\parskip}{\bodyparskip}
% Space above and below a list or a quotation. \parskip does not reach inside a
% list item, so this is the only thing separating a bullet from a quotation
% nested under it. Zero here closes that gap up entirely.
\setlength{\topsep}{0.5em}
\setlength{\partopsep}{0pt}
% Air between top-level list items, as a length so a crowded frame can tighten
% it (assets/beamer-deck.lua emits \global\itemsep=\listsep).
\newlength{\listsep}
\setlength{\listsep}{0.9em}
% The frame title is the running head. ltx-talk's geometry (top 10mm, header
% 10mm, headsep 2mm) starts that box above the paper edge, so the title sits
% jammed against the top; a deeper top margin moves the whole header down.
\geometry{tmargin=15mm, bmargin=7mm}
\EditInstance{header}{std}{color = accent, font = \Large\bfseries\headingfont, height = 1.7cm}
\EditInstance{frametitle}{header}{color = accent, font = \Large\bfseries\headingfont}
\EditInstance{titlepage-element}{title}{color = accent, font = \LARGE\bfseries\headingfont}
\EditInstance{titlepage-element}{subtitle}{color = ink, font = \large\bfseries}
% Slide number: readable, and out of the way at the bottom right. The footer
% box is left-aligned with a trailing \hfil, so the way to move its one
% element right is to start the box there.
\EditInstance{footer}{std}{element-order = {framenumber}, font = \small,
  color = muted, left-hspace = 0.93\paperwidth}
% How tall a figure may be. The body is ~78mm of a 100mm frame, so for any
% chart wider than it is tall this, not \linewidth, sets the size on screen.
\newlength{\figmaxht}
\setlength{\figmaxht}{0.88\textheight}
\date{}
\ExplSyntaxOn
\keys_set:nn { talk / frame } { vertical-alignment = top }
\ExplSyntaxOff
\renewcommand{\emph}[1]{\textcolor{accent}{\textbf{#1}}}
% Quotations are italic on the web deck. A switch rather than \textit so the
% tagging code is not handed an argument-taking command around a paragraph.
% \parskip does not reach inside a list item, so a quotation nested under a
% bullet gets only \topsep above it and reads as jammed against the bullet.
% The extra goes on quote alone: center is a list too, and widening \topsep
% globally pads every figure on the deck.
\AddToHook{env/quote/before}{\addvspace{0.35em}}
\AddToHook{env/quote/begin}{\itshape}
"""

# Steps a frame is taken down by when its content does not fit. The figure cap
# comes down with the type: on a figure slide the picture is what overflows.
SHRINK_STEPS = [
    r"\setlength{\bodyparskip}{0.35em}\setlength{\parskip}{\bodyparskip}\setlength{\listsep}{0.35em}"
    r"\setlength{\figmaxht}{0.95\figmaxht}",
    r"\setlength{\bodyparskip}{0.2em}\setlength{\parskip}{\bodyparskip}\setlength{\listsep}{0.2em}"
    r"\setlength{\figmaxht}{0.90\figmaxht}\linespread{0.97}\selectfont",
    r"\setlength{\bodyparskip}{0.12em}\setlength{\parskip}{\bodyparskip}\setlength{\listsep}{0.12em}"
    r"\setlength{\figmaxht}{0.82\figmaxht}\linespread{0.94}\selectfont",
]

# Frame opening, through the two setup lines the writer and the filter put at
# the top of a frame, so a size change lands after \figmaxht is set, not before.
FRAME_TOP = re.compile(
    r"\\begin\{frame\}(?:\[[^\]]*\])?\{[^}]*\}"
    r"(?:\\vspace\*\{[^}]*\})?"
    r"(?:\s*\\phantomsection\\label\{[^}]*\})?"
    r"(?:\s*\\setlength\{\\figmaxht\}\{[^}]*\})?")

def apply_shrink(body, shrink):
    """Insert a size command at the top of the frames listed in `shrink`."""
    i = [0]
    def rep(m):
        i[0] += 1
        return m.group(0) + shrink.get(i[0], "")
    return FRAME_TOP.sub(rep, body)

def frame_titles(doc):
    return [m.group(1) for m in
            re.finditer(r"\\begin\{frame\}(?:\[[^\]]*\])?\{([^}]*)\}", doc)]

def overfull_frames(doc, log):
    """(frame number, title, points over) for every frame taller than the body."""
    lines, titles, out = doc.split("\n"), frame_titles(doc), []
    for pt, ln in re.findall(r"Overfull \\vbox \(([\d.]+)pt too high\) "
                             r"detected at line (\d+)", log):
        i = sum(l.count(r"\begin{frame}") for l in lines[:int(ln)])
        if 1 <= i <= len(titles):
            out.append((i, titles[i - 1], float(pt)))
    return out

def meta_from_qmd(text):
    def grab(key):
        m = re.search(r'^%s:\s*"?(.*?)"?\s*$' % key, text, re.M)
        return m.group(1).replace("<br>", r"\\") if m else None
    title = grab("title") or "Slides"
    subtitle = grab("subtitle") or ""
    author = grab("author") or ""
    out = f"\\title{{{title}}}\n"
    if subtitle: out += f"\\subtitle{{{subtitle}}}\n"
    if author: out += f"\\author{{{author}}}\n"
    # The line break in the displayed title would otherwise close up the words
    # in the document title a reader's title bar and a screen reader announce.
    out += "\\hypersetup{pdftitle={%s}}\n" % title.replace(r"\\", " ").strip()
    return out

def build(n):
    qmd = SLIDES / f"lecture{n}.qmd"
    if not qmd.exists():
        sys.exit(f"no {qmd.relative_to(ROOT)}")
    with tempfile.TemporaryDirectory() as td:
        tdp = pathlib.Path(td)
        # figures: svg -> pdf, raster copied, under img/ relative to the tex
        idir = tdp / "img"; idir.mkdir()
        for f in (SLIDES / "img").iterdir():
            if f.suffix == ".svg":
                subprocess.run(["rsvg-convert", "-f", "pdf", "-o",
                                str(idir / f.with_suffix(".pdf").name), str(f)], check=True)
            elif f.suffix.lower() in (".png", ".jpg", ".jpeg"):
                shutil.copy(f, idir / f.name)
        # frames from pandoc's beamer writer (body only; template discarded)
        r = subprocess.run(["quarto", "pandoc", str(qmd), "-t", "beamer",
                            "--lua-filter", str(ROOT / "assets" / "beamer-deck.lua"),
                            "--standalone"], capture_output=True, text=True, check=True)
        tex = r.stdout
        body = tex.split(r"\begin{document}", 1)[1].rsplit(r"\end{document}", 1)[0]
        # With frame-title-arg every frame must carry a title argument, and a
        # bare \maketitle gets wrapped in an argument-less frame that then eats
        # the *next* frame as its argument (veraPDF: Hn shall not contain Sect).
        # So the title page is an explicit frame; the wallpaper style keeps the
        # header from printing the title twice.
        qtitle = meta_from_qmd(qmd.read_text()).split("\n")[0][7:-1]
        body = body.replace("\\frame{\\titlepage}",
                            "\\begin{frame}[vertical-alignment = center]{%s}\\maketitle[framestyle = wallpaper]\\end{frame}" % qtitle)
        body = re.sub(r"\\begin\{columns\}\[[^\]]*\]", r"\\begin{columns}", body)
        # ltx-talk sets the columns row to \textwidth and puts \hfil between
        # the columns, so a gutter only appears if the widths leave slack.
        # Pandoc's widths sum to 1, which butts the text right against the
        # figure; shaving 5% off each opens the gap the web deck has.
        body = re.sub(r"\\begin\{column\}\{([\d.]+)\\linewidth\}",
                      lambda m: r"\begin{column}{%.4f\linewidth}" % (float(m.group(1)) * 0.95),
                      body)
        # Top-aligned frames start flush under the header; give the body the
        # same breathing room the web decks have below the title.
        body = re.sub(r"(\\begin\{frame\}\{[^}]*\})(?!\\maketitle)", r"\1\\vspace*{0.5em}", body)
        body = re.sub(r"\[<\+\+?->?\]", "", body)          # itemize[<+->]
        body = re.sub(r"<\d+(-\d*)?>", "", body)           # \item<2-> etc.
        # A frame whose content is taller than the body silently loses its last
        # line; nothing else in the pipeline catches that, so the deck is
        # compiled, the log read for overfull frames, and just those frames
        # re-set a step smaller. Everything else keeps the full size.
        head = PREAMBLE + meta_from_qmd(qmd.read_text()) + "\\begin{document}\n"
        level, over = {}, []
        for attempt in range(len(SHRINK_STEPS) + 1):
            shrink = {i: SHRINK_STEPS[k] for i, k in level.items()}
            doc = head + apply_shrink(body, shrink) + "\n\\end{document}\n"
            (tdp / "deck.tex").write_text(doc)
            subprocess.run(["lualatex", "-interaction=nonstopmode", "deck.tex"],
                           cwd=td, capture_output=True)
            if not (tdp / "deck.log").exists():
                break
            over = overfull_frames(doc, (tdp / "deck.log").read_text(errors="replace"))
            if not over or attempt == len(SHRINK_STEPS):
                break
            for i, _, _ in over:
                level[i] = min(level.get(i, -1) + 1, len(SHRINK_STEPS) - 1)
        # a second pass so the frame count in the footer is right
        subprocess.run(["lualatex", "-interaction=nonstopmode", "deck.tex"],
                       cwd=td, capture_output=True)
        pdf = tdp / "deck.pdf"
        if not pdf.exists():
            log = (tdp / "deck.log").read_text(errors="replace")
            errs = [l for l in log.splitlines() if l.startswith("!")]
            shutil.copy(tdp / "deck.tex", ROOT / "scripts" / f"failed-deck{n}.tex")
            sys.exit(f"lecture {n}: compile failed (kept scripts/failed-deck{n}.tex):\n"
                     + "\n".join(errs[:6]))
        if level:
            titles = frame_titles(doc)
            print(f"    lecture {n}: tightened to fit: " + ", ".join(sorted(
                f"{titles[i - 1]} (step {k + 1})" for i, k in level.items()
                if 1 <= i <= len(titles))))
        if over:
            print(f"    lecture {n}: STILL runs off the bottom: "
                  + "; ".join(f"{t} ({pt:.0f}pt)" for _, t, pt in over))
        v = subprocess.run(["verapdf", "--flavour", "ua2", "--format", "xml", str(pdf)],
                           capture_output=True, text=True)
        fails = re.findall(r'clause="([^"]*)"[^>]*testNumber="[^"]*"[^>]*status="failed"'
                           r'[^>]*failedChecks="([^"]*)"', v.stdout)
        if fails:
            keep = ROOT / "scripts" / f"failed-deck{n}.pdf"
            shutil.copy(pdf, keep)
            sys.exit(f"lecture {n}: deck does not pass veraPDF UA-2 "
                     f"({', '.join(f'{c} x{k}' for c, k in fails)}); kept {keep.name} for inspection")
        dest = SLIDES / f"lecture{n}.pdf"
        shutil.copy(pdf, dest)
        pages = subprocess.run(["pdfinfo", str(dest)], capture_output=True, text=True)
        np = re.search(r"Pages:\s+(\d+)", pages.stdout).group(1)
        print(f"    lecture {n}: {np} pages, tagged, veraPDF ua2 PASS -> {dest.relative_to(ROOT)}")

if __name__ == "__main__":
    for n in sys.argv[1:]:
        build(n)
