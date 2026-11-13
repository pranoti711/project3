"""
patch_lit_review_v2.py - second verification pass (13 Nov 2026): full-text checks of Gizamba 2026 and the CDPH California assessment,
verification of Kidd 2019 and Shover 2020, Gezer abstract details, and a preprint/web search for competing work.
Run from the project3 folder:  python tools/patch_lit_review_v2.py
Edits 25_topic_literature_review.md, 24_novelty_search_log.md and 10_results_writeup.md. A file is changed only if all its anchors match.
"""
import re
import sys
from pathlib import Path

root = Path.cwd()
docs = root / "00_docs"
if not (docs / "25_topic_literature_review.md").exists():
    sys.exit("Run patch_lit_review.py first, from the project3 folder.")


def pat(s):
    return r"\s+".join(re.escape(t) for t in s.split())


def patch(path, edits, marker, line_edits=(), appendix=None):
    text = path.read_text(encoding="utf-8")
    if marker in text:
        print(f"SKIPPED {path.name}: already patched")
        return
    for i, (old, new) in enumerate(edits, 1):
        hits = list(re.finditer(pat(old), text))
        if len(hits) != 1:
            print(f"SKIPPED {path.name}: edit {i} matched {len(hits)} times ({old[:50]}...). File unchanged.")
            return
        m = hits[0]
        text = text[:m.start()] + new + text[m.end():]
    for rx, new in line_edits:
        ms = list(re.finditer(rx, text, flags=re.M))
        if len(ms) != 1:
            print(f"SKIPPED {path.name}: line pattern matched {len(ms)} times ({rx[:50]}). File unchanged.")
            return
        text = text[:ms[0].start()] + new + text[ms[0].end():]
    if appendix:
        text = text.rstrip() + "\n" + appendix
    path.write_text(text, encoding="utf-8", newline="\r\n")
    print(f"Patched {path.name}")


# ---------------------------------------------------------------- 25 review
REVIEW_ADD = """
## 8. Second verification pass (13 Nov 2026)
- Gizamba et al. (2026, BMC Public Health 26:2297; FULL): cross-sectional study of 245 Los Angeles County ZIP code tabulation areas, first-time
  RNA-positive hepatitis C among ages 18-39, January 2020 to December 2023; 31 predictors covering socioeconomic conditions, healthcare access and
  opioid-related morbidity (hospitalisations and emergency visits for 2022, new HIV diagnoses). Overdose mortality was not a predictor. Validation was
  random 5-fold nested cross-validation (RMSE 11, pseudo R-squared 0.34); agreement between predicted and observed risk categories was modest
  (accuracy 34.6%, kappa 0.18); calibration was not assessed. The authors say the map supports prioritisation and hypothesis generation, not
  fine-scale allocation. It is not a temporal holdout and does not test mortality.
- California Department of Public Health vulnerability assessment (2017 data; FULL): all 58 counties; separate models for fatal opioid overdose and for
  HIV or HCV vulnerability. The HIV or HCV model retained race and ethnicity, heroin emergency visits (ages 15-29), estimated HCV prevalence (age 40+),
  felony drug arrests and households without a vehicle; overdose mortality was not in that model. The report states that its findings are not
  predictive. Twelve counties were high risk for HIV or HCV and 11 for fatal overdose, concentrated in northern California and small counties. This is the
  closest California precedent and shares the project's 58 counties.
- CDC jurisdictional assessments (CDC web pages and Shrestha et al., Prev Med 2023;170:107490; ABSTRACT): core indicators used by states include drug
  overdose mortality, prescriptions, arrests and acute HCV; these are ranking tools, not forecasts.
- Kidd et al. (MMWR 2019;68:144; ABSTRACT and CDC summary): among women with primary and secondary syphilis, methamphetamine use rose from 6.2% to 16.6%
  during 2013-2017, injection drug use from 4.0% to 10.5% and heroin use from 2.1% to 5.8%; among men who have sex with men methamphetamine use fell from
  9.2% to 8.0%. Stimulants matter for syphilis, so a mortality series dominated by opioids may be a weak proxy. A California report notes that
  amphetamine-related overdose deaths rose 198% in 2012-2018.
- Shover et al. (Drug Alcohol Depend 2020;216:108314; ABSTRACT and partial full text): in 2018 states east of the Mississippi had 88% of synthetic opioid
  deaths; available 2020 data showed a 63% rise in fentanyl mortality over 2019. A 2025 JAMA Netw Open report (abstract level) found that states such as
  California had rapidly rising drug mortality after 2019 relative to pre-2020 trends. The steepest California rise therefore falls mostly after the scored
  test years (a hypothesis, not a finding).
- Gezer et al. (2024; ABSTRACT, Table 2 not accessible): 41,691 opioid-related and 26,860 HCV-related hospitalisations in South Carolina, 2016-2021; per
  standard deviation, relative risks 1.24 (uninsured, poverty), 1.18 (mortality, 95% CI 1.12 to 1.25) and 1.17 (social vulnerability), and 0.79 (income);
  trained on 2016-2020, median accuracy for 2021 was 80.4% (IQR 66.8 to 91.1) for opioid-related and 75.2% (61.2 to 87.7) for HCV-related
  hospitalisations. Whether the mortality estimate is mutually adjusted, and the exact accuracy formula, remain unconfirmed (the paper cites the "Table 2
  fallacy" literature, which hints at a multivariable model).
- Others (ABSTRACT or title level): Yedinak et al., Int J Drug Policy 2021;96:103395 (statewide neighbourhood machine-learning vulnerability scores using overdose
  deaths as a proxy outcome); an Oklahoma county vulnerability index using drug-related mortality as an indicator (PubMed 38722958, 2024; findings not
  retrieved); a July 2026 medRxiv preprint on surveillance-adjusted syphilis risk across US counties (cross-sectional Bayesian spatial model, no
  mortality predictor); Gizamba et al. 2025 systematic synthesis of area-level hepatitis C determinants (BMC Public Health 25:687; not read).
- Search coverage: Embase, Web of Science and Scopus could not be accessed with the tools used; PubMed was screened systematically and medRxiv and arXiv were
  covered only through web searches. No study testing incremental out-of-sample value of mortality for infection transitions was found.
"""
patch(
    docs / "25_topic_literature_review.md",
    [
     ("(Kidd et al., MMWR 2019; TITLE)", "(Kidd et al., MMWR 2019; ABSTRACT, details in section 8)"),
     ("(Drug Alcohol Depend 2020;216:108314; TITLE)", "(Shover et al., Drug Alcohol Depend 2020;216:108314; ABSTRACT, details in section 8)"),
     ("Gezer 2024 Table 2 and the accuracy formula; Gizamba 2026 predictor list; Sumetsky 2019, Gonsalves 2021 and 2023 full text; Kidd 2019; the "
      "fentanyl-timing paper; Abellan 2008; Leening 2014 page numbers; Embase, Web of Science, Scopus and preprint searches.",
      "Gezer 2024 Table 2 and the accuracy formula (PMC blocked automated access); Sumetsky 2019, Gonsalves 2021 and 2023 full text; Gizamba 2025 "
      "systematic synthesis; the Oklahoma county study; Abellan 2008; Leening 2014 page numbers; Embase, Web of Science and Scopus (not accessible)."),
    ],
    marker="Second verification pass (13 Nov 2026)",
    appendix=REVIEW_ADD,
)

# ---------------------------------------------------------------- 24 log
LOG_ADD = """
## Second pass 2026-11-13: full-text and extra searches
| Source | Level | Note |
|---|---|---|
| Gizamba et al., BMC Public Health 2026;26:2297 | Full text | Cross-sectional; no overdose mortality predictor; random 5-fold CV; category accuracy 34.6%, kappa 0.18 |
| CDPH California fatal opioid overdose and HIV/HCV vulnerability assessment (2017 data) | Full text | 58 counties; not predictive by its own statement; overdose mortality not in the HIV/HCV model |
| Kidd et al., MMWR 2019;68:144 | Abstract and CDC summary | Meth, injection and heroin use rose among women and heterosexual men with syphilis |
| Shover et al., Drug Alcohol Depend 2020;216:108314 | Abstract and partial full text | Fentanyl reached western markets late; 63% rise 2019 to 2020 in available data |
| Gezer et al., Lancet Public Health 2024 | Abstract | Mortality RR 1.18 (1.12-1.25) per SD; Table 2 and accuracy formula still unseen |
| Yedinak 2021; Oklahoma county index 2024; medRxiv syphilis county mapping 2026 | Abstract | No competing incremental-prediction study |
Coverage: Embase, Web of Science and Scopus not accessible; medRxiv and arXiv reached only by web search.
"""
patch(
    docs / "24_novelty_search_log.md",
    [],
    marker="Second pass 2026-11-13",
    line_edits=[
      (r"^\| Gizamba et al\., BMC Public Health 2026 \|.*$",
       "| Gizamba et al., BMC Public Health 2026 | Cross-sectional, 245 LA County ZIP codes, Elastic Net and random forest, hepatitis C ages 18-39 | Full text read 2026-11-13 | No overdose mortality predictor (opioid hospitalisations, emergency visits and HIV were); random 5-fold CV; modest category agreement; not temporal. |"),
      (r"^\| Kidd et al\., MMWR 2019; fentanyl-timing paper.*$",
       "| Kidd et al., MMWR 2019; Shover et al., Drug Alcohol Depend 2020 | Verified 2026-11-13 | See the second-pass table below |"),
      (r"^- Read Table 2, Table 3 and the accuracy method in Gezer 2024.*$",
       "- Read Table 2 and the accuracy formula in Gezer 2024 in a browser; read Sumetsky 2019, Gonsalves 2021 and 2023 in full; Gizamba 2025 synthesis; Embase, Web of Science, Scopus."),
    ],
    appendix=LOG_ADD,
)

# ---------------------------------------------------------------- write-up
patch(
    docs / "10_results_writeup.md",
    [
     ("its predictor set has not been checked).",
      "its predictors included opioid-related hospitalisations and emergency visits and new HIV diagnoses but not overdose mortality, validation "
      "was random 5-fold cross-validation, and agreement between predicted and observed risk categories was modest). The California Department of "
      "Public Health assessment of all 58 counties (2017 data) used indicators such as heroin emergency visits, hepatitis C prevalence and drug "
      "arrests, did not include overdose mortality in its HIV or HCV model, and states that its results are not predictive."),
     ("rate ratio 1.18 per standard deviation for the combined outcome",
      "rate ratio 1.18, 95% CI 1.12 to 1.25, per standard deviation for the combined outcome, alongside poverty and uninsured rate"),
     ("Embase, Web of Science, Scopus and preprint servers are not yet searched;",
      "Embase, Web of Science and Scopus could not be accessed and medRxiv was reached only through web search;"),
     ("Full text read: Drewes et al. 2021; Marks et al. 2021 (Transl Res review).",
      "Full text read: Drewes et al. 2021; Marks et al. 2021 (Transl Res review); Gizamba et al. 2026; the CDPH California assessment; Kidd et al. 2019 and "
      "Shover et al. 2020 were checked at abstract and summary level."),
     ("also reduced the signal is a hypothesis, not a finding.",
      "also reduced the signal is a hypothesis, not a finding: fentanyl reached western illicit drug markets late (Shover et al., 2020) and California's "
      "steepest rise in drug-related mortality came after 2019 (an abstract-level report), mostly after the scored test years."),
    ],
    marker="alongside poverty and uninsured rate",
)
print("Done.")
