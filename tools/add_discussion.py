"""
add_discussion.py - writes 00_docs/27_discussion_draft.md and 00_docs/28_final_checklist.md (13 Nov 2026).
Run from the project3 folder:  python tools/add_discussion.py
Existing files are never overwritten.
"""
import sys
from pathlib import Path

docs = Path.cwd() / "00_docs"
if not docs.exists():
    sys.exit("Run from the project3 folder.")

DISCUSSION = """# 27_discussion_draft.md - discussion section (draft, 13 Nov 2026)

Every number below comes from `10_results_writeup.md` or the literature notes in `25_topic_literature_review.md`. Statements marked (hypothesis) are
explanations that were not tested. Check each citation against the full paper before submission.

## Principal findings
After controlling for county population, lagged within-county mortality deviations did not improve out-of-sample prediction of next-year
infectious-disease up-transitions in California counties (change in AUC +0.001, 95% CI -0.028 to +0.034; 81 scored events). Context features gave
+0.003 (-0.005 to +0.013) and the combined model +0.003 (-0.028 to +0.037). Placebo, held-out-disease, spatial-block, lead-time, gradient-boosting,
decision-curve and proper-scoring analyses agreed. The 90% interval for mortality lay inside +/-0.03 AUC, and the minimum detectable gain was about 0.045.
The group of sexually transmitted infections, the diseases most plausibly linked to drug use, gave B - A of +0.001. An earlier apparent gain
(+0.025) was explained by county size.

## Why mortality may add so little (hypotheses)
1. The baseline already carries the signal. Own disease history and population capture persistence and size; mortality deviations add little beyond them.
2. Detectability. An up-transition needs the posterior probability of a rise to reach 0.80. Posterior-probability rules have low sensitivity for modest
   excess risk or small expected counts (Richardson et al., 2004), so small counties rarely register events, and small counties are where mortality is
   most often suppressed (43% of drug-overdose and suicide rows and 66% of homicide rows missing).
3. Exposure variation. The steepest rise in California drug-related mortality came after 2019, after fentanyl reached western markets late
   (Shover et al., 2020), mostly beyond the scored test years.
4. Proxy mismatch. For syphilis, individual-level links are strongest for methamphetamine and injection drug use (Kidd et al., 2019), so an opioid-heavy
   county mortality series may be a weak proxy.
5. Power. With 81 events, gains below about 0.045 AUC could not be reliably detected.

## Relation to earlier work
Vulnerability assessments rely on overdose mortality as an indicator (Van Handel et al., 2016) but were fitted and scored on the same data without validation
(Marks et al., 2021), and the California assessment for the same 58 counties states that its results are not predictive. Area-level studies report
positive associations (Sumetsky et al., 2019; Gezer et al., 2024, which also validated predictions on a later year) or mixed ones (Drewes et al., 2021,
significant only for urban gonorrhoea; Gonsalves et al., 2021 and 2023, local but not statewide). None tested whether mortality adds predictive value
beyond a population-adjusted baseline. Our result is compatible with earlier associations: an association can exist without adding predictive value.
Whether county size or detectability partly explains earlier associations is a hypothesis.

## What the result does and does not cover
It covers next-year county up-transitions in 16 notifiable diseases, including chlamydia, gonorrhoea and early syphilis, in California. It does not
cover hepatitis C or HIV outbreaks, other states, shorter lags, finer geography, or operational early warning (the mortality series is published one to
two years late). Small effects below the detection limit are not excluded.

## Implications
Overdose mortality should not be assumed to improve prediction of county infection transitions without out-of-sample testing. Baselines should include
population, and placebo tests should be able to separate the hypothesis from county size.

## Future work
Add hepatitis C and HIV series; test finer geography; extend the window beyond 2020 when events can be scored; use stimulant-specific and opioid-specific
mortality; pre-specify an urban-county stratum (Drewes et al.) with enough events; repeat with a decision-analytic endpoint.
"""

CHECKLIST = """# 28_final_checklist.md - what is done and what is left (13 Nov 2026)

## State of the project
- Analysis, results and both advanced layers: finished and frozen. Tag `advanced-freeze` stays on commit 1f9dc41.
- Write-up `10_results_writeup.md` sections 1-12 current. Literature: `24_novelty_search_log.md`, `25_topic_literature_review.md`.
- Drafts: `26_abstract_draft.md` (your abstract, check it), `27_discussion_draft.md`.

## Final commands (from the project3 folder)
1. python -m pytest 04_scripts -q            (expect 9 passed)
2. python tools/make_manifest.py             (refresh manifest.csv)
3. git status                                 (tree clean after commit)
4. git tag writeup-v1                         (marks the finished write-up)
5. git archive --format=zip -o ..\\project3_final.zip HEAD   (clean copy of tracked files only)

## For you to do
1. Open Gezer 2024 on PMC in a browser: read the Table 2 footnote (is mortality mutually adjusted?) and the accuracy method; update 24 and 25.
2. Read in full: Sumetsky 2019, Gonsalves 2021 and 2023, Gizamba 2025 synthesis. Verify Cohen 2003, Abara 2019, Bauer 2023, Patton 2025.
3. If your library allows, run the PubMed strings in Embase, Web of Science and Scopus; record strings, dates and hit counts in `24_novelty_search_log.md`.
4. Run a looser PubMed string (drop the forecasting block; add "risk" and "vulnerab*") and record the hit count.
5. Check the abstract draft: every number must match the write-up; wording "no evidence of gain within the detectable range".
6. Complete `06_paper/references.bib` from the verified papers only.
7. Ask your supervisor to review the framing (stress test of the overdose-indicator assumption) and the limits.
8. Before any submission, repeat the novelty search and update the dates.
9. Do not move the `advanced-freeze` tag; add new tags for later versions.
"""

for name, body in (("27_discussion_draft.md", DISCUSSION), ("28_final_checklist.md", CHECKLIST)):
    p = docs / name
    if p.exists():
        print(f"SKIPPED {name}: already exists")
    else:
        p.write_text(body, encoding="utf-8", newline="\r\n")
        print(f"Wrote {name}")