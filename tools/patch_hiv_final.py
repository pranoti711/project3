from pathlib import Path
D = Path("00_docs"); M = "<!-- hiv-final-patch -->"
ADD = {
"26_abstract_draft.md": """
**Suggested sentence to insert in the results or conclusion:** An exploratory extension adding HIV
(Office of AIDS county series, 2012-2023; 4 test events) gave the same null result (pooled B-A -0.007,
95% CI -0.039 to +0.023).
""",
"27_discussion_draft.md": """
**Limitations paragraph - add:** HIV was included only as an exploratory group (4 test events in the
leave-future-out window) and HCV is absent (county data for 2014-2016 only). County mortality deviations
were missing in 19% (all-cause), 57% (drug overdose), 57% (suicide) and 74% (homicide) of county-years
because of small-count suppression; missing values were mean-imputed with no missing indicator, which
probably biases model B toward the null. The null result therefore applies to publicly available,
suppressed county-level data and does not show that mortality has no predictive value in principle.
""",
"28_final_checklist.md": """
- [x] HIV exploratory extension run, committed (a1b6688, tag hiv-ext) and written up
- [x] Missingness handling in p3_common.R checked and reported as a limitation
- [x] Old HCV/HIV limitation reworded (3ce98e2, tag writeup-v5)
- [ ] Manifest refreshed after the HIV additions
- [ ] Abstract and discussion: HIV sentence and missingness limitation moved into the text
""",
}
for name, text in ADD.items():
    p = D / name; s = p.read_text(encoding="utf-8")
    if M in s: print("[skip]", name); continue
    p.write_text(s.rstrip() + "\n\n" + M + "\n" + text, encoding="utf-8"); print("[ok]  ", name)
