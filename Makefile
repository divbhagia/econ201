# ECON 201 build. Run from the econ201 folder.
#
#   make syllabus    regenerate the schedule, rebuild the syllabus PDF (slow: tagged compile)
#   make schedule    regenerate schedule.qmd and the module content pages only
#   make worksheets  tagged worksheet PDFs (lualatex), veraPDF-gated
#   make slides-pdf  tagged-PDF decks (ltx-talk) from the same slide sources
#   make site        rebuild the website into docs/
#   make audit       WCAG 2.1 AA check of docs/ (axe-core + reflow + veraPDF); run before pushing
#   make verify      confirm docs/ still matches the last render; run right before git add
#   make             schedule, slides-pdf, site
#
# The site renders in a temp copy outside Dropbox, then docs/ is synced to it
# and compared, repeatedly, until they match: Dropbox restores files that are
# overwritten or deleted in place a few seconds later, which silently left
# stale pages in docs/. The build fails rather than publish a mismatch.

SHELL := /bin/bash
# Published lectures; keep in step with MATERIALS in syllabus/create_schedule.py.
# A deck not listed here is neither built as PDF nor rendered into the site, so
# a lecture can be drafted in slides/ without appearing anywhere public.
LECTURES := 1 2 3 4
PUBLISHED_DECKS := $(foreach n,$(LECTURES),--include=slides/lecture$(n).qmd --include=slides/lecture$(n).pdf)
# Published practice pages, same idea: a page absent from this list is not
# rendered, so it is in the repo but nowhere on the site, not even site search.
# Keep in step with MATERIALS in syllabus/create_schedule.py.
PRACTICE := 02 03 04
PUBLISHED_PRACTICE := $(foreach n,$(PRACTICE),--include=practice/practice$(n).qmd)
# Consolidated module practice PDFs ride along with the published pages.
PUBLISHED_PRACTICE += --include=practice/practice-*.pdf
TMP := $(TMPDIR)econ201-build
AUX := aux,log,out,fls,fdb_latexmk,xdv,toc,synctex.gz

.PHONY: all syllabus schedule worksheets slides-pdf site audit verify

all: schedule worksheets slides-pdf site

schedule:
	@echo "==> schedule table and module pages"
	@python3 syllabus/create_schedule.py

# Tagged compile of the syllabus takes several minutes; batch edits, build once.
syllabus: schedule
	@echo "==> syllabus PDF (lualatex, tagged)"
	@(cd syllabus && lualatex -interaction=nonstopmode Econ201-Syllabus.tex >/dev/null 2>&1; \
	                lualatex -interaction=nonstopmode Econ201-Syllabus.tex >/dev/null 2>&1; \
	  rm -f Econ201-Syllabus.{$(AUX)})
	@pdfinfo syllabus/Econ201-Syllabus.pdf | awk '/^Pages/{print "    pages: " $$2}'
	@verapdf --flavour ua2 --format text syllabus/Econ201-Syllabus.pdf 2>/dev/null | grep -E "^(PASS|FAIL)" | sed 's|/.*/||; s/^/    /'

# Worksheets compile in place; Quarto copies the PDFs into docs/ via the
# resources list in _quarto.yml. Each one is veraPDF-gated: a worksheet that
# fails PDF/UA-2 is deleted rather than published.
worksheets:
	@echo "==> worksheets (lualatex, tagged)"
	@for f in worksheets/*.tex; do \
	  b=$$(basename "$$f" .tex); \
	  (cd worksheets && lualatex -interaction=nonstopmode "$$b.tex" >/dev/null 2>&1; \
	                   lualatex -interaction=nonstopmode "$$b.tex" >/dev/null 2>&1; \
	   rm -f "$$b".{$(AUX)}); \
	  r=$$(verapdf --flavour ua2 --format text "worksheets/$$b.pdf" 2>/dev/null | grep -oE "^(PASS|FAIL)"); \
	  echo "    $$b.pdf: $$r (PDF/UA-2)"; \
	  [ "$$r" = PASS ] || { rm -f "worksheets/$$b.pdf"; exit 1; }; \
	done

# Tagged-PDF slide decks from the same .qmd sources as the web decks, compiled
# under ltx-talk (beamer refuses tagging). Each build veraPDF-gates its output.
slides-pdf:
	@echo "==> slide decks as tagged PDF (ltx-talk)"
	@python3 scripts/build_slides_pdf.py $(LECTURES)

site: schedule
	@echo "==> website"
	@rm -rf $(TMP)
	@rsync -a --exclude .git --exclude grades --exclude quizzes --exclude references \
	          --exclude canvas --exclude docs --exclude .quarto --exclude _freeze \
	          $(PUBLISHED_DECKS) --exclude 'slides/lecture*.qmd' --exclude 'slides/lecture*.pdf' \
	          --exclude 'slides/*_files' --exclude 'slides/figures' \
	          $(PUBLISHED_PRACTICE) --exclude 'practice/*' ./ $(TMP)/
	@cd $(TMP) && quarto render
	@# Dropbox restores files that are overwritten or deleted in place, a few
	@# seconds after the fact, which used to leave stale pages in docs/. So the
	@# copy is converged: sync, wait, compare against the render, repeat until
	@# nothing differs. The comparison is what makes the result trustworthy.
	@mkdir -p docs; ok=0; \
	for i in 1 2 3 4 5 6; do \
	  rsync -a --delete --checksum $(TMP)/docs/ docs/; sleep 12; \
	  if diff -rq -x .DS_Store $(TMP)/docs docs >/dev/null; then ok=1; break; fi; \
	  echo "    pass $$i: docs/ still differs from the render, syncing again"; \
	done; \
	[ $$ok = 1 ] || { echo "    docs/ never matched the render; Dropbox kept interfering. Run make site again."; exit 1; }
	@# Dropbox has brought a deleted file back as late as 20 s after a clean
	@# diff, so a passing check is confirmed once more after a longer wait.
	@sleep 30; diff -rq -x .DS_Store $(TMP)/docs docs >/dev/null || { echo "    docs/ changed again after verifying; Dropbox restored something. Run make site again."; exit 1; }
	@find docs \( -name "*conflicted copy*" -o -name .DS_Store \) -exec rm -rf {} + 2>/dev/null || true
	@echo "    pages: $$(find $(TMP)/docs -name '*.html' ! -path '*site_libs*' | wc -l | tr -d ' ')"
	@echo "    pdfs:  $$(find $(TMP)/docs -name '*.pdf' | wc -l | tr -d ' ')"
	@echo "    docs/ verified identical to the render"

# Every page and PDF must meet WCAG 2.1 AA / PDF/UA-2 (DOJ Title II rule,
# 28 CFR 35.200; CSUF deadline 2027-04-26). Separate from `site` because it
# takes several minutes: run it before pushing, and after any new material.
audit:
	@echo "==> accessibility audit (WCAG 2.1 AA + PDF/UA-2)"
	@python3 scripts/audit_a11y.py

# Dropbox has restored deleted files into docs/ minutes after a clean build,
# once between an audit and a git add. Cheap to run, so run it every time.
verify:
	@diff -rq -x .DS_Store $(TMP)/docs docs && echo "docs/ matches the last render"

# Consolidated module practice PDFs (441-style), generated from the practice
# pages by scripts/build_module_practice.py; rerun after editing any
# practice/practiceNN.qmd in a listed module.
module-practice:
	@echo "==> module practice PDFs (lualatex, tagged)"
	@python3 scripts/build_module_practice.py economists-toolkit 03 04
	@cd practice && for f in practice-economists-toolkit practice-economists-toolkit_solutions; do \
	  lualatex -interaction=nonstopmode $$f.tex >/dev/null 2>&1; \
	  lualatex -interaction=nonstopmode $$f.tex >/dev/null 2>&1; \
	  verapdf --flavour ua2 --format text $$f.pdf 2>/dev/null | grep -q "^PASS" \
	    && echo "    $$f.pdf: PASS (PDF/UA-2)" \
	    || { echo "    $$f.pdf: FAIL (PDF/UA-2)"; exit 1; }; \
	  rm -f $$f.aux $$f.log $$f.out; done

.PHONY: module-practice
