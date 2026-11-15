"""
patch_verified_papers.py - updates the write-up, discussion draft, literature review, search log and checklist after the full-text and abstract
checks of 14 Nov 2026 (Gezer 2024, Abara 2019, Cohen 2003, Sumetsky 2019, Gonsalves 2021).
Run from the project3 folder:  python tools/patch_verified_papers.py
Each file is changed only if all its anchors match exactly once; otherwise it is skipped and the others still run.
"""
import re
import sys
from pathlib import Path

docs = Path.cwd() / "00_docs"
if not docs.exists():
    sys.exit("Run from the project3 folder.")

def pat(s):
    return r"\s+".join(re.escape(t) for t in s.split())

def patch(name, edits, marker, line_edits=(), appendix=None):
    path = docs / name
    if not path.exists():
        print(f"SKIPPED {name}: file not found")
        return
    text = path.read_text(encoding="utf-8")
    if marker in text:
        print(f"SKIPPED {name}: already patched")
        return
    for i, (old, new) in enumerate(edits, 1):
        hits = list(re.finditer(pat(old), text))
        if len(hits) != 1:
            print(f"SKIPPED {name}: edit {i} matched {len(hits)} times ({old[:50]}...). File unchanged.")
            return
        m = hits[0]
        text = text[:m.start()] + new + text[m.end():]
    for rx, new in line_edits:
        ms = list(re.finditer(rx, text, flags=re.M))
        if len(ms) != 1:
            print(f"SKIPPED {name}: line pattern matched {len(ms)} times ({rx[:45]}). File unchanged.")
            return
        text = text[:ms[0].start()] + new + text[ms[0].end():]
    if appendix:
        text = text.rstrip() + "\n" + appendix
    path.write_text(text, encoding="utf-8", newline="\r\n")
    print(f"Patched {name}")

# ------------------------------------------------------------ write-up
patch("10_results_writeup.md", [
 ("Gizamba et al. 2026; the CDPH California assessment",
  "Gizamba et al. 2026; the CDPH California assessment; Gezer et al. 2024; Abara et al. 2019"),
 ("Van Handel et al. 2016, Gezer et al. 2024, Sumetsky et al. 2019,",
  "Van Handel et al. 2016, Sumetsky et al. 2019 (abstract only),"),
 ("Not yet checked in full: Cohen et al. 2003 and Abara et al. 2019 (abstract level),",
  "Not yet checked in full: Cohen et al. 2003 (abstract level),"),
 ("the Abara association was positive but weakened over 2010-2015 and the authors noted possible confounding by men who have sex with men "
  "(abstract level); the Cohen description is also abstract level.",
  "in the Abara study of male gonorrhoea rates in US counties, opioid prescribing (a proxy for misuse) was positively associated with "
  "gonorrhoea (coefficient 0.068, 95% CI 0.031 to 0.105, cases per 100,000 males per prescription per 100 persons), the association weakened "
  "over 2010-2015, and the authors noted possible confounding by men who have sex with men (full text read; the Cohen description is from the abstract)."),
 ("although the authors state they were not making short-term predictions (Gonsalves et al., 2021)",
  "and the authors propose that such complications could serve as input to a sentinel system to trigger early intervention (Gonsalves et al., 2021; "
  "the rate ratio is from a search snippet and is not yet checked in the full text)"),
 ("and design (the mortality measure is all-cause, there is no incremental comparison against a population-adjusted baseline, and there are no "
  "placebo or held-out-disease controls).",
  "and design (the mortality measure is all-cause and each association was estimated one predictor at a time, adjusting for time and a population "
  "offset; community-level covariates were compared with a history-only model as a block and gave only a mild accuracy gain, so the contribution of "
  "mortality itself was not isolated; and there are no placebo or held-out-disease controls)."),
], marker="community-level covariates were compared with a history-only model")

# ------------------------------------------------------------ discussion draft
patch("27_discussion_draft.md", [
 ("None tested whether mortality adds predictive value beyond a population-adjusted baseline.",
  "Gezer et al. compared community-level covariates as a block with a history-only model and found only a mild accuracy gain, which is compatible with "
  "our result, but none isolated the added predictive value of mortality for infection events against a population-adjusted baseline."),
], marker="found only a mild accuracy gain, which is compatible")

# ------------------------------------------------------------ literature review
REVIEW_ADD = """
## 9. Third verification pass (14 Nov 2026)
- Gezer et al. (2024; FULL text read): Table 2 estimates were fitted one predictor at a time, each adjusting for time and a ZIP-code population offset
  (the paper's partially adjusted models, with random intercepts and slopes for year); the mortality estimate (all-cause deaths per 1,000 residents,
  RR 1.21 opioid, 1.17 HCV, 1.18 combined) is therefore not mutually adjusted. Fully adjusted models (all covariates except doctors per 1,000, because of
  collinearity) were used only for prediction and also included lagged hospitalisation counts. Accuracy is the median percent agreement between predicted
  and observed 2021 counts (formula in appendix page 3). Fully adjusted models were compared with models using previous hospitalisations, time and random
  effects only, and with previous-year counts alone; covariate inclusion gave only a mild gain (for example 80.4% against 75.0% for opioid-related
  hospitalisations in the annual 2021 scenario). The authors call the gain modest and note limited room for improvement given the strong benchmark.
  Mortality was not isolated, the outcome was hospitalisation counts, and there was no placebo design.
- Abara et al. (Ann Epidemiol 2019;36:26-32; FULL): linear mixed models, 2010-2015, county opioid prescribing rate (proxy for misuse) and male gonorrhoea
  rate; coefficient 0.068 (95% CI 0.031 to 0.105); the association weakened over time (interaction -0.014, -0.023 to -0.006) except in counties where
  prescribing increased; limits include ecologic design, proxy exposure and possible confounding by men who have sex with men.
- Cohen et al. (Am J Public Health 2003;93:467; ABSTRACT): 107 US cities; boarded-up housing predicted gonorrhoea and premature mortality (including
  homicide and suicide) after adjustment; mortality was an outcome, not a predictor.
- Sumetsky et al. (JECH 2019;73:935; ABSTRACT confirmed): Bayesian hierarchical spatiotemporal Poisson regression with conditionally autoregressive effects,
  Pennsylvania ZIP codes 2004-2014; previous-year opioid-related hospitalisations RR 1.092 (1.078 to 1.106) for HCV and 1.098 (1.068 to 1.126) for HIV;
  the conclusion is that hospitalisations are connected to the comorbidities (association).
- Gonsalves et al. (OFID 2021;8:ofab128; ABSTRACT confirmed): distributed-lag Poisson regression in a Bayesian setting, Lawrence and Lowell, 2005-2018;
  current-month HIV counts were associated with fatal overdoses about 8 months earlier, endocarditis 10 months earlier and skin and soft tissue infections
  12 months earlier; the authors suggest these could feed a sentinel (early-warning) system. The rate ratio of 1.03 and any statement about short-term
  prediction came from search snippets and are not confirmed.
- Still unverified beyond abstract or snippet: Gonsalves 2023 (CID), Bauer 2023, Patton 2025, Rickles 2018, Van Handel 2016 full text.
"""
patch("25_topic_literature_review.md", [
 ("There is no ablation of mortality and no placebo design (ABSTRACT and snippets; Table 2 not read).",
  "Community-level covariates as a block were compared with a history-only model and gave only a mild accuracy gain; mortality was not isolated and there "
  "was no placebo design (FULL, see section 9)."),
 ("Gezer et al. (2024; ABSTRACT, Table 2 not accessible):", "Gezer et al. (2024; FULL, see section 9):"),
 ("Whether the mortality estimate is mutually adjusted, and the exact accuracy formula, remain unconfirmed (the paper cites the \"Table 2 fallacy\" "
  "literature, which hints at a multivariable model).",
  "Resolved on 14 Nov 2026 (section 9): the Table 2 estimates are one predictor at a time, so mortality is not mutually adjusted."),
 ("Gezer 2024 Table 2 and the accuracy formula (PMC blocked automated access);", "Gezer 2024 appendix page 3 (accuracy formula);"),
], marker="Third verification pass (14 Nov 2026)", appendix=REVIEW_ADD)

# ------------------------------------------------------------ search log
patch("24_novelty_search_log.md", [
 ("- Read Table 2 and the accuracy formula in Gezer 2024 in a browser; read Sumetsky 2019, Gonsalves 2021 and 2023 in full;",
  "- Read the Gezer 2024 appendix (page 3, accuracy formula); read Sumetsky 2019, Gonsalves 2021 and 2023 in full;"),
], marker="Gezer 2024 appendix (page 3", line_edits=[
 (r"^\| Gezer et al\., Lancet Public Health 2024 \| SC ZIP codes.*$",
  "| Gezer et al., Lancet Public Health 2024 | SC ZIP codes; train 2016-20, validate 2021; accuracy = median percent agreement of predicted vs observed counts (appendix p 3); Table 2 RRs one predictor at a time (time and population offset), mortality RR 1.18 (1.12-1.25) combined | Full text read 2026-11-14 | Closest study; covariate block vs history-only gave only a mild gain; mortality not isolated; one state, hospitalisation counts, no placebo design. |"),
 (r"^\| Gezer et al\., Lancet Public Health 2024 \| Abstract \|.*$",
  "| Gezer et al., Lancet Public Health 2024 | Full text | Table 2 and accuracy definition resolved; see the main table |"),
 (r"^\| Abara et al\., opioid prescribing trends and gonorrhoea, US counties 2010-2015 \|.*$",
  "| Abara et al., Ann Epidemiol 2019;36:26-32 | Full text | Opioid prescribing vs male gonorrhoea, counties 2010-2015; coefficient 0.068 (0.031-0.105); weakened over time; MSM confounding noted |"),
])

# ------------------------------------------------------------ checklist
patch("28_final_checklist.md", [
 ("1. Open Gezer 2024 on PMC in a browser: read the Table 2 footnote (is mortality mutually adjusted?) and the accuracy method; update 24 and 25.",
  "1. Gezer 2024: Table 2 and the accuracy definition were read on 14 Nov 2026 (see 25, section 9); only the appendix (page 3, accuracy formula) is unread."),
 ("2. Read in full: Sumetsky 2019, Gonsalves 2021 and 2023, Gizamba 2025 synthesis. Verify Cohen 2003, Abara 2019, Bauer 2023, Patton 2025.",
  "2. Read in full: Sumetsky 2019, Gonsalves 2021 and 2023, Gizamba 2025 synthesis. Verify Bauer 2023 and Patton 2025 (Abara 2019 and Cohen 2003 checked 14 Nov 2026)."),
], marker="Table 2 and the accuracy definition were read on 14 Nov 2026")
print("Done.")s