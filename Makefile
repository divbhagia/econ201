# ECON 201 build. Run from the econ201 folder.
#
#   make syllabus    regenerate the schedule, rebuild the syllabus PDF (slow: tagged compile)
#   make schedule    regenerate schedule.qmd and the module content pages only
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
LECTURES := 1
PUBLISHED_DECKS := $(foreach n,$(LECTURES),--include=slides/lecture$(n).qmd --include=slides/lecture$(n).pdf)
TMP := $(TMPDIR)econ201-build
AUX := aux,log,out,fls,fdb_latexmk,xdv,toc,synctex.gz

.PHONY: all syllabus schedule slides-pdf site audit verify

all: schedule slides-pdf site

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
	          --exclude 'slides/*_files' --exclude 'slides/figures' ./ $(TMP)/
	@cd $(TMP) && quarto render
	@# Dropbox restores files that are overwritten or deleted in place, a few
	@# seconds after the fact, which used to leave stale pages in docs/. So the
	@# copy is converged: sync, wait, compare against the render, repeat until
	@# nothing differs. The comparison is what makes the result trustworthy.
	@mkdir -p docs; ok=0; \
	for i in 1 2 3 4 5 6; do \
	  rsync -a --delete --checksum $(TMP)/docs/ docs/; sleep 12; \
	  if diff -rq $(TMP)/docs docs >/dev/null; then ok=1; break; fi; \
	  echo "    pass $$i: docs/ still differs from the render, syncing again"; \
	done; \
	[ $$ok = 1 ] || { echo "    docs/ never matched the render; Dropbox kept interfering. Run make site again."; exit 1; }
	@# Dropbox has brought a deleted file back as late as 20 s after a clean
	@# diff, so a passing check is confirmed once more after a longer wait.
	@sleep 30; diff -rq $(TMP)/docs docs >/dev/null || { echo "    docs/ changed again after verifying; Dropbox restored something. Run make site again."; exit 1; }
	@find docs -name "*conflicted copy*" -exec rm -rf {} + 2>/dev/null || true
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
	@diff -rq $(TMP)/docs docs && echo "docs/ matches the last render"
