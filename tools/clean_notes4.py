import re, pathlib, sys
APPLY = "--apply" in sys.argv
files = [r"00_docs\10_results_writeup.md", r"00_docs\27_discussion_draft.md"]
S = r"\s+"
R = [
 (r"why a first pass looked positive", "why an initial analysis appeared positive"),
 (r"the confounded first pass", "the confounded initial specification"),
 (r"Choices fixed in 19_advanced_evaluation_plan\.md.*?they are not new tests\.",
  "The choices for these additional analyses were fixed in a written evaluation plan before they were run; the code, results and figures are in the repository. All use the stage 1 out-of-fold predictions and the same 81 test events, so they describe how informative the null is rather than adding new tests."),
 (r"20_tripod_probast\.md maps.*?checks the leakage rules in code\.",
  "We mapped the study to reporting-guideline topics and completed a risk-of-bias self-assessment, rating the outcome and analysis domains as high concern. An automated test in the code checks the leakage rules."),
 (r"Script 27 \(27_proper.*?not part of 19_advanced_evaluation_plan\.md, so it is post-hoc\.",
  "Proper scoring rules and influence analysis. These used the same stage 1 out-of-fold predictions and 81 events, with 1,000 county-cluster bootstrap draws. They were added after the first set of advanced analyses and were not part of the evaluation plan, so they are post-hoc."),
 (r"in" + S + r"21_supplementary_results\.md", "in the supplementary results"),
 (r"Outputs:" + S + r"05_results/tables/\*__hiv17\*" + S + r"\(repository" + S + r"tag" + S + r"hiv-ext\)\.",
  "Outputs are in the repository (tag hiv-ext)."),
 (r"Changes" + S + r"after" + S + r"seeing" + S + r"results" + S + r"are" + S + r"all" + S + r"logged" + S + r"in" + S + r"`?07_deviations_log\.md`?" + S + r"and" + S + r"`?04_prereg\.md`?" + S + r"\(retrospective" + S + r"record\)\.",
  "All changes made after the results were seen are documented in a deviations log and a retrospective pre-registration record in the repository."),
 (r"California.s" + S + r"steepest" + S + r"rise" + S + r"in" + S + r"drug-related" + S + r"mortality" + S + r"came" + S + r"after" + S + r"2019,"+ S + r"mostly" + S + r"after" + S + r"the" + S + r"scored" + S + r"test" + S + r"years\.",
  "California\u2019s drug-overdose mortality rose most steeply between 2019 and 2021 (in the 39 counties with complete data, from about 15.6 to 27.7 deaths per 100,000; CDC WONDER, own calculation), mostly after the scored test years."),
]
for f in files:
    p = pathlib.Path(f); t = p.read_text(encoding="utf-8-sig"); print("==", f)
    for pat, new in R:
        ms = list(re.finditer(pat, t, flags=re.S))
        if ms: print(f"  {len(ms)} x {pat[:45]}  (longest match {max(len(m.group()) for m in ms)} chars)")
        t = re.sub(pat, lambda m: new, t, flags=re.S)
    if APPLY: p.write_text(t, encoding="utf-8")
print("APPLIED" if APPLY else "dry run only")
