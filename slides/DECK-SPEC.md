# ECON 201 slide deck spec

Standing instructions for drafting any `slides/lectureN.qmd`, its figures,
and the matching worksheet. Distilled from Div's corrections on lectures 1
to 5 (August and September 2026). Read this in full before drafting a deck,
and check the draft against it before handing it over. Div edits this file;
nothing here is a suggestion.

## Source and accuracy

1. Build every slide from the assigned CORE 2.0 sections only. Read them in
   full first (the site is `books.core-econ.org/the-economy/microeconomics/`;
   fetch the HTML and convert it locally, the summarizer drops details).
2. Take every definition near verbatim from CORE, with the term in
   `*italics*` (renders orange). Do not paraphrase a definition or the
   statement of a rule. Comparing options means comparing net benefits.
3. Use CORE's notation and terms: $R$, $C(Q)$, AC, MC, outside option. No
   symbols or names the book does not use (no TR/TC, no reservation option).
4. No facts, anecdotes, statistics, company details, quotations, or examples
   from outside the assigned sections unless Div supplied them. If one is
   needed, ask, or flag it clearly in the hand-over as not from CORE.
5. Every real-world number has a source Div can check, credited on a closing
   `## Sources {.smaller}` slide. No captions or source lines under figures.
6. Check every arithmetic step and every direction of an opportunity-cost or
   comparative-advantage claim before handing over.

## Structure

7. Follow Div's sketch or dictated slide order exactly. Do not reorder,
   insert, merge, or drop slides on your own. If he sketches the deck in
   chat, that sketch is the outline.
8. Open by picking up where the last class ended, in his words: a short
   recap or the debrief of last class's worksheet, then a `.plain` roadmap
   naming today's terms as `[term]{.book}`. On a quiz day (see `DUE` in
   `syllabus/create_schedule.py`) the standing quiz-instructions slide
   comes first.
9. Concept before story. Pose the general question, define the tool in
   CORE's words, then bring in the real-firm numbers. Company anecdotes
   illustrate a concept already on the table; they never open the lecture.
10. One running example per lecture, built step by step in the book's
    order, numbers computed once in `slides/figures/make_lectureN.py` and
    printed so slides and worksheet quote the same values. Show the
    arithmetic on the slide (224,000 / 10 = 22,400). Tables grow across
    slides with earlier columns kept.
11. Hand off to the worksheet near the end on one slide that asks the
    question and names the activity ("Worksheet, Activity 2: ... then
    compare with a neighbor"). Discussion prompts and menti questions live
    on the slides themselves, with their context; menti text under 150
    characters.
12. A model gets a "What the Model Leaves Out" slide.
13. Close with one "What to Do Next" slide: reading, slides and worksheet,
    practice problems, quiz date in `*emphasis*`, one sentence on next
    class. No "posted on the course website", no lecture-notes line.
14. No section-break slides, no `.takeaway` boxes (Div places those
    himself), no `.figcap` captions, no speaker notes, no presenter copies.
15. Reveals (`::: fragment`, `::: incremental`) only after a question put
    to the class, or where Div asks. Not on ordinary lists.

## Voice and wording

16. Every bullet is a complete sentence a teacher would say aloud, and every
    bullet ends with a period, single-sentence and fragment bullets
    included. Sweep after every edit.
17. No aphorisms, punchline closers, "not X but Y" reversals, triple
    parallels, presentational openers ("Here is how much..."), grand
    framing ("a model small enough to reuse all semester"), or filler
    clauses ("whether or not anyone writes it down"). If a line would not
    be said in class, cut it.
18. No back-references to earlier lectures or to Adam Smith unless Div asks.
19. Titles are topical noun phrases or plain questions ("Average Cost",
    "Why Do Firms Get So Big?"). No assertion sentences, no jokes unless
    requested.
20. Keep slides short: at most four or five bullets, one idea each, nothing
    bleeding past the footer in the PDF. Split rather than shrink.
21. Lists of brands or examples are names only; Div talks to them in class.
22. Emphasis is `*italics*` only. No bold in prose. No em dashes anywhere.
23. Everyday-versus-technical usage is worth a line ("In everyday language,
    'technology' refers to...").

## Examples and numbers

24. Examples are US-based where the book's are not, in dollars, at a scale
    students recognize, and not politically charged (no polarizing public
    figures).
25. Comparisons are like with like: same industry, same year, same profit
    line (Ford vs Ferrari, not Kroger vs Ferrari).
26. Hypothetical people get invented names that fit the setting (Sam, Lena,
    Pablo and Lin); vary names and goods across problems; never make Div
    the example.

## Figures and tables

27. Figures come from `slides/figures/make_lectureN.py`: Okabe-Ito colours,
    labels on the figure for every marked point, thick lines, Lato/Fira
    fonts, SVG text as paths, `fig-alt` on every image. Column figures use
    `SIDE` size beside `46%/54%` columns; full-slide figures use `FULL`.
28. Figures fill their space with no empty band above; text in a column
    sits level with the figure. Keep tick labels clear of the origin and of
    each other. Never bold a single series.
29. Tables have a rule at top and bottom and before totals, right-aligned or
    centered numbers, even spacing above and below. Highlight a cell only
    where Div names it, and only in the way he names (bold or orange, not
    both).
30. Worksheet tables students write in are ruled grids with tall blank
    rows, variables named in the header ($P$, $Q$, $R$, $C$), and an empty
    plotting grid when they are asked to draw.

## Worksheets and practice

31. The worksheet opens with the definitions used, then mirrors the slide
    example exactly (same table, blank cells, parts a to e), then one
    similar problem on the back. Do not add further problems.
32. Practice problem 1 reuses the worksheet problem; long-form problems
    first, MCQs last; MCQ feedback is one "Correct! ..." sentence.

33. The definitions panel on a worksheet is an itemized list, bullets flush
    with the panel's left edge, one item per definition. Nest each
    classification under the definition it belongs to (normal and inferior
    goods under the income elasticity, substitutes and complements under the
    cross-price elasticity) rather than collecting them under a heading of
    their own. Do not restate a definition students met in an earlier lecture.
34. A worksheet fits on one page. When it overruns, cut or tighten the prose,
    never the rows students write in, and restore full-height rows once it
    fits.
35. Every part of a practice problem should be liftable onto a quiz. Cut
    conceptual "why is it written this way" parts.

## Process

36. Before writing a deck, agree the slide-by-slide plan in chat if Div has
    not already sketched one. When asked to improve a sentence, offer two or
    three options in chat and implement only the one he picks.
37. The qmd is co-edited. Re-read the file before every edit, apply changes
    on top of his, and never touch a slide he has just fixed. If a slide was
    already right, restore it rather than re-edit it.
38. Change only what was asked. A layout fix never alters content. If a fix
    is not possible, say so and leave the original.
39. Build for review (HTML in a scratch copy, tagged PDF via
    `scripts/build_slides_pdf.py N`, screenshots) but do not render into
    `docs/`, run the audit, commit, or push until Div says so. Ask about
    committing once.
40. After every edit: sweep bullet periods, check for bleeding slides in the
    PDF, stray blank lines in the qmd, table rules, figure alignment, and
    em dashes; rebuild HTML and PDF; report anything not from CORE and
    anything not verified.
