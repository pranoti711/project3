# 28_final_checklist.md - what is done and what is left (13 Nov 2026)

## State of the project
- Analysis, results and both advanced layers: finished and frozen. Tag `advanced-freeze` stays on commit 1f9dc41.
- Write-up `10_results_writeup.md` sections 1-12 current. Literature: `24_novelty_search_log.md`, `25_topic_literature_review.md`.
- Drafts: `26_abstract_draft.md` (your abstract, check it), `27_discussion_draft.md`.

## Final commands (from the project3 folder)
1. python -m pytest 04_scripts -q            (expect 9 passed)
2. python tools/make_manifest.py             (refresh manifest.csv)
3. git status                                 (tree clean after commit)
4. git tag writeup-v1                         (marks the finished write-up)
5. git archive --format=zip -o ..\project3_final.zip HEAD   (clean copy of tracked files only)

## For you to do
1. Gezer 2024: Table 2 and the accuracy definition were read on 14 Nov 2026 (see 25, section 9); only the appendix (page 3, accuracy formula) is unread.
2. Read in full: Sumetsky 2019, Gonsalves 2021, Gizamba 2025 synthesis. Verify Patton 2025 (Abara 2019, Bauer 2023, Cohen 2003 and Gonsalves 2023 checked 14 Nov 2026).
3. If your library allows, run the PubMed strings in Embase, Web of Science and Scopus; record strings, dates and hit counts in `24_novelty_search_log.md`.
4. Run a looser PubMed string (drop the forecasting block; add "risk" and "vulnerab*") and record the hit count.
5. Check the abstract draft: every number must match the write-up; wording "no evidence of gain within the detectable range".
6. Complete `06_paper/references.bib` from the verified papers only.
7. Ask your supervisor to review the framing (stress test of the overdose-indicator assumption) and the limits.
8. Before any submission, repeat the novelty search and update the dates.
9. Do not move the `advanced-freeze` tag; add new tags for later versions.

- [x] HIV exploratory extension run, committed (a1b6688, tag hiv-ext) and written up
- [x] Missingness handling in p3_common.R checked and reported as a limitation
- [x] Old HCV/HIV limitation reworded (3ce98e2, tag writeup-v5)
- [x] Manifest refreshed after the HIV additions
- [x] HIV sentence and missingness limitation merged into abstract and discussion
- [ ] Missingness percentages in discussion section "Why mortality may add so little" match the n=3712 table
- [x] Drewes et al. wording (urban gonorrhoea vs rural 2016-2017) checked against the full paper
- [ ] Push to GitHub
