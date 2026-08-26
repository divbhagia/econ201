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
\documentclass[frame-title-arg, font-size = 14pt]{ltx-talk}
\usepackage{amsmath,graphicx}
% pandoc sets tables as longtable with booktabs rules
\usepackage{longtable,booktabs,array}
\providecommand{\tightlist}{}
\providecommand{\note}[1]{}
\setmainfont{Lato}
\setsansfont{Lato}
\newfontfamily\headingfont{Fira Sans Condensed}
\DeclareColor{accent}[HTML]{BF5700}
\DeclareColor{ink}[HTML]{1A1A1A}
\DeclareColor{structure}[HTML]{1A1A1A}
\color{ink}
% The frame title is the running head. ltx-talk's geometry (top 10mm, header
% 10mm, headsep 2mm) starts that box above the paper edge, so the title sits
% jammed against the top; a deeper top margin moves the whole header down.
\geometry{tmargin=16mm}
\EditInstance{header}{std}{color = accent, font = \Large\bfseries\headingfont, height = 1.8cm}
\EditInstance{frametitle}{header}{color = accent, font = \Large\bfseries\headingfont}
\EditInstance{titlepage-element}{title}{color = accent, font = \LARGE\bfseries\headingfont}
\EditInstance{titlepage-element}{subtitle}{color = ink, font = \large\bfseries}
\EditInstance{footer}{std}{element-order = {framenumber}}
\date{}
\ExplSyntaxOn
\keys_set:nn { talk / frame } { vertical-alignment = top }
\ExplSyntaxOff
\renewcommand{\emph}[1]{\textcolor{accent}{\textbf{#1}}}
"""

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
        # Top-aligned frames start flush under the header; give the body the
        # same breathing room the web decks have below the title.
        body = re.sub(r"(\\begin\{frame\}\{[^}]*\})(?!\\maketitle)", r"\1\\vspace*{0.9em}", body)
        body = re.sub(r"\[<\+\+?->?\]", "", body)          # itemize[<+->]
        body = re.sub(r"<\d+(-\d*)?>", "", body)           # \item<2-> etc.
        doc = PREAMBLE + meta_from_qmd(qmd.read_text()) + "\\begin{document}\n" + body + "\n\\end{document}\n"
        (tdp / "deck.tex").write_text(doc)
        for _ in range(2):
            subprocess.run(["lualatex", "-interaction=nonstopmode", "deck.tex"],
                           cwd=td, capture_output=True)
        pdf = tdp / "deck.pdf"
        if not pdf.exists():
            log = (tdp / "deck.log").read_text(errors="replace")
            errs = [l for l in log.splitlines() if l.startswith("!")]
            shutil.copy(tdp / "deck.tex", ROOT / "scripts" / f"failed-deck{n}.tex")
            sys.exit(f"lecture {n}: compile failed (kept scripts/failed-deck{n}.tex):\n"
                     + "\n".join(errs[:6]))
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
