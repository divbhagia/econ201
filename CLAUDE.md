# ECON 201 course site

Quarto website (output in `docs/`, served via GitHub Pages), a LaTeX syllabus,
reveal.js slide decks, and an offline quiz-grading pipeline in `quizzes/`.
Run every command from this folder. `make site` renders in a temp copy outside
Dropbox and replaces `docs/`; never render into `docs/` directly.

## Student data

`grades/` holds everything with a student's name or CWID in it, plus the
Canvas token. Do not read it. Develop the grading code against the synthetic
data `quizzes/test_grader.py` generates. See `quizzes/README.md`.

## Accessibility is a hard requirement

Everything published must meet **WCAG 2.1 Level AA** (DOJ Title II rule,
28 CFR 35.200; CSUF's compliance deadline is 2027-04-26). The site has an
[accessibility statement](accessibility.qmd) promising this. Non-negotiable for
any new or edited material:

- **Every figure gets `fig-alt`** (markdown) or `alt` (raw HTML) describing
  what it shows. Decorative icons get `aria-hidden="true"` instead.
- **Math is authored as TeX** (rendered to MathML), never as an image of an
  equation.
- **Text contrast at least 4.5:1** on white. Safe theme colors: `#8f4100`
  (7.7:1), `#393A3B` (11.4:1), `#1a1a1a` (17.4:1), `#595a5b` (6.9:1),
  `#6b6b6b` (5.3:1), `#747576` (4.6:1). The brand orange `#BF5700` is 4.59:1
  on white, which passes, and 4.19:1 on the cream panel `#FDF3EA`, which does
  not: on a tinted background use `#8f4100` for text and keep `#BF5700` for
  rules and borders.
- **Raw HTML blocks need real semantics**: header cells with `scope`, valid
  list nesting (no `<ul>` around markdown list items), `aria-label` on
  icon-only links, `tabindex="0"` on scrollable regions.
- **PDFs are tagged AND validated**: every `.tex` starts with
  `\DocumentMetadata{pdfstandard=UA-2,pdfversion=2.0,lang=en-US,tagging=on}`,
  compiles with lualatex (tagging is silently skipped under XeLaTeX), and must
  pass `verapdf --flavour ua2` (part of `make audit`). Figures in LaTeX get
  `alt={...}` on `\includegraphics`.
- **LaTeX constructs that break tagging**: `$$...$$` display math (use
  `\[...\]`); the `tasks` package; argument-taking commands like `\textit` in
  a section font (use switches like `\itshape`); boxed constructs that put a
  paragraph inside a paragraph.
- Do not convey meaning by color alone; keep pages usable at 320px width
  (wide content scrolls in its own container, never the page).

## Audit

`make audit` checks every built page and PDF: axe-core (WCAG 2.1 A/AA), a
reflow check at 320px, and veraPDF PDF/UA-2 validation of every PDF in `docs/`.
It takes several minutes and exits nonzero on any failure. Run it after
`make site` and before pushing; nothing is published until it passes. The
script is `scripts/audit_a11y.py` (axe vendored at `scripts/axe.min.js`;
verapdf via Homebrew).

## Slide decks

Sources are `slides/lectureN.qmd`, rendered by Quarto as part of the site. No
speaker notes and no presenter copies. Only decks listed in `LECTURES` in the
Makefile are rendered or built as PDF, so a lecture can be drafted in
`slides/` without appearing anywhere public; add it to `LECTURES` and to
`MATERIALS` in `syllabus/create_schedule.py` together when it is ready. `make slides-pdf` builds a tagged-PDF
version of each deck in `LECTURES` from the same source, via pandoc's beamer
writer compiled under `ltx-talk`; `fig-alt` survives via
`assets/beamer-deck.lua`, and each deck is veraPDF-gated at build time. Keep
`LECTURES` in the Makefile in step with `MATERIALS` in
`syllabus/create_schedule.py`, and rerun `make slides-pdf` before `make site`
when a deck changes. ltx-talk is experimental: after `tlmgr update`, rebuild
and re-audit before publishing.

Gotchas that caused real failures:

- reveal.js emits `user-scalable=no` and unlabeled menu chrome; fixed at
  runtime by `assets/slides-a11y.html`, included from `_quarto.yml`. Keep it.
- Long inline equations overflow narrow viewports; `assets/site-a11y.html`,
  included site-wide, makes actual offenders scrollable and keyboard-reachable.
  Keep that too.
- Quarto's `.reveal .slide ul li` margin rules outrank simpler selectors in
  `assets/slides.scss`; match that specificity when styling slide lists.

## Pages

`_quarto.yml` declares both `html` and `revealjs` formats, so every ordinary
page must say `format: html` in its front matter or Quarto also renders it as
a slide deck and the build fails on the rename.

## Schedule and content pages

`schedule.qmd` and `content/*.qmd` are generated. Edit
`syllabus/create_schedule.py`, not the pages. The same script writes
`syllabus/schedule.tex` for the syllabus PDF, whose tagged compile takes
several minutes: batch edits and build once with `make syllabus`.

## Working conventions

- Div commits and pushes. Stage changes and hand over the commands.
- Delete LaTeX aux files after every compile.
- No em dashes anywhere: prose, comments, course materials.
