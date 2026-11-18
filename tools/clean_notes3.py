import re, pathlib

files = [r"00_docs\10_results_writeup.md", r"00_docs\27_discussion_draft.md", r"00_docs\26_abstract_draft.md"]

p = pathlib.Path(r"06_paper\manuscript_draft.md")
t = p.read_text(encoding="utf-8")
R = [
 (r"why a first pass looked positive", "why an initial analysis appeared positive"),
 (r"the confounded first pass", "the confounded initial specification"),
 (r"Choices fixed in 19_advanced_evaluation_plan\.md.*?they are not new tests\.",
  "The choices for these additional analyses were fixed in a written evaluation plan before they were run; the code, results and figures are in the repository. All use the stage 1 out-of-fold predictions and the same 81 test events, so they describe how informative the null is rather than adding new tests."),
 (r"20_tripod_probast\.md maps.*?checks the leakage rules in code\.",
  "We mapped the study to reporting-guideline topics and completed a risk-of-bias self-assessment, rating the outcome and analysis domains as high concern. An automated test in the code checks the leakage rules."),
 (r"Script 27 \(27_proper.*?not part of 19_advanced_evaluation_plan\.md, so it is post-hoc\.",
  "Proper scoring rules and influence analysis. These used the same stage 1 out-of-fold predictions and 81 events, with 1,000 county-cluster bootstrap draws. They were added after the first set of advanced analyses and were not part of the evaluation plan, so they are post-hoc."),
 (r"The B intercept of -0\.524 in 21_supplementary_results\.md", "The B intercept of -0.524 in the supplementary results"),
 (r"Outputs: .*?hiv-ext\)\.", "Outputs are in the repository (tag hiv-ext)."),
 (r"Changes after seeing results are all logged in .*?\(retrospective record\)\.",
  "All changes made after the results were seen are documented in a deviations log and a retrospective pre-registration record in the repository."),
 (r" File names mentioned in the text \(for example 13_stage2_plan\.md\) refer to documents in this repository\.", ""),
 (r"California.s steepest rise in drug-related mortality came after 2019, mostly after the scored test years\.",
  "California\u2019s drug-overdose mortality rose most steeply between 2019 and 2021 (in the 39 counties with complete data, from about 15.6 to 27.7 deaths per 100,000; CDC WONDER, own calculation), mostly after the scored test years."),
]
for f in files:
    p = pathlib.Path(f)
    t = p.read_text(encoding="utf-8-sig")
    print("==", f)
    for pat, new in R:
        t, n = re.subn(pat, lambda m: new, t, flags=re.S)
        if n: print(n, "x", pat[:55])
    p.write_text(t, encoding="utf-8")
for pat, new in R:
    t, n = re.subn(pat, lambda m: new, t, flags=re.S)
    print(n, "x", pat[:55])
p.write_text(t, encoding="utf-8")
