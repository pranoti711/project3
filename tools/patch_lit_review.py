"""
patch_lit_review.py - adds the topic-level literature review and the matching small corrections (13 Nov 2026).
Run from the project3 folder:  python tools/patch_lit_review.py
Writes:  00_docs/25_topic_literature_review.md (new)
Edits:   00_docs/10_results_writeup.md, 00_docs/24_novelty_search_log.md, 00_docs/20_tripod_probast.md
Each file is edited only if all its anchors match exactly once; otherwise that file is skipped and the others still run.
"""
import re
import sys
from pathlib import Path

root = Path.cwd()
docs = root / "00_docs"
if not docs.exists():
    sys.exit("Run from the project3 folder.")

def pat(s):
    return r"\s+".join(re.escape(t) for t in s.split())

def edit_file(path, edits, marker, appendix=None):
    if not path.exists():
        print(f"SKIPPED {path.name}: file not found")
        return
    text = path.read_text(encoding="utf-8")
    if marker in text:
        print(f"SKIPPED {path.name}: already patched")
        return
    for i, (old, new) in enumerate(edits, 1):
        hits = list(re.finditer(pat(old), text))
        if len(hits) != 1:
            print(f"SKIPPED {path.name}: edit {i} matched {len(hits)} times ({old[:55]}...). File unchanged.")
            return
        m = hits[0]
        text = text[:m.start()] + new + text[m.end():]
    if appendix:
        text = text.rstrip() + "\n" + appendix
    path.write_text(text, encoding="utf-8", newline="\r\n")
    print(f"Patched {path.name} ({len(edits)} edits{' + appendix' if appendix else ''})")

# ---------------------------------------------------------------- 1. new literature review file
REVIEW = """# 25_topic_literature_review.md - topic-level literature review (13 Nov 2026)

Purpose: place the project (does county mortality add out-of-sample predictive value for next-year infectious-disease up-transitions?) in the
wider literature, beyond the closest prior studies in `24_novelty_search_log.md`. Method: structured PubMed screens (see the log) plus about 15
web searches on 12-13 Nov 2026. Verification level is given per source: FULL = full text read; ABSTRACT = abstract or full-text snippets;
TITLE = title or citation only. Verify every entry against the paper before citing it in a manuscript.

## 1. Substantive evidence: mortality and opioid indicators versus infection
- Cross-sectional vulnerability work treats overdose mortality as an indicator of infection risk. Van Handel et al. (2016) regressed county acute
  hepatitis C (a proxy for injection drug use) on 15 indicators; six were retained, including drug-overdose deaths (ABSTRACT). Rickles et al.
  (2018) used opioid-related mortality in Tennessee (ABSTRACT, Marks review table).
- Associations at area level are mixed. Sumetsky et al. (2019): previous-year opioid hospitalisations, rate ratios about 1.09 (HCV) and 1.10 (HIV)
  in Pennsylvania ZIP codes (ABSTRACT). Gezer et al. (2024): all-cause mortality per 1,000 residents associated with opioid-related and
  HCV-related hospitalisations, rate ratio 1.18 per SD (ABSTRACT). Drewes et al. (2021): after adjustment, opioid death rates were not
  associated with gonorrhoea, chlamydia or HIV except for gonorrhoea in urban counties (rate ratio 1.11, 95% CI 1.02 to 1.20); homicide rate
  also associated with urban gonorrhoea (FULL). Gonsalves et al. (2021): fatal overdoses about 8 months earlier associated with HIV counts in
  Lawrence and Lowell (rate ratio 1.03, 90% CrI 1.00 to 1.06); Gonsalves et al. (2023): no overdose association statewide (ABSTRACT).
- Abara et al. (opioid prescribing trends and gonorrhoea in US counties, 2010-2015): positive association that weakened over the period; the
  authors note possible confounding by men who have sex with men (ABSTRACT).
- Individual-level link: methamphetamine and injection drug use among people with primary and secondary syphilis (Kidd et al., MMWR 2019;
  TITLE). Individual links do not imply that county mortality predicts county infection counts.
Reading: the link is plausible and sometimes significant in association models, but no study reports a test of added predictive value.

## 2. Prediction and validation evidence
- Marks et al. (2021, Transl Res; FULL): 46 studies on detection, risk assessment and prediction of opioid-related epidemics (search to
  January 2021). Risk assessments such as Van Handel were fitted and scored on the same data without validation; geospatial methods were mainly
  explanatory; bloodborne-infection prediction used dynamic models.
- Gezer et al. (2024): fully adjusted negative binomial mixed models trained on 2016-2020 and checked on 2021 hospitalisations; accuracy is the
  median percent agreement between predicted and observed ZIP-code counts (about 80% opioid-related, 75% HCV-related). There is no ablation
  of mortality and no placebo design (ABSTRACT and snippets; Table 2 not read).
- Ma et al. (2026, Front Public Health 14:1888674; FULL): state-level forecasting of primary and secondary syphilis with gradient boosting,
  neural network, Bayesian and baseline models. Co-STI, HIV, poverty, unemployment and income covariates improved holdout error modestly
  (XGBoost WAPE 22.7% to 20.0%); mortality or overdose was not used. State counts, not county transitions.
Reading: the missing piece is an incremental, out-of-sample, placebo-controlled test at county level, which this project provides.

## 3. Outcome definition and detectability
- Richardson et al. (2004, Environ Health Perspect; ABSTRACT): classifying areas by the posterior probability that relative risk exceeds a
  threshold, with a 70-80% cut-off, is specific; the models are conservative, with low sensitivity when the true excess is under 2-fold or
  expected counts are not substantial (about 50 per area). This explains why small counties rarely register an up-transition and why population
  acts as a detectability marker.
- Abellan, Richardson and Best (2008, Environ Health Perspect 116:1111) extend decision rules to space-time disease mapping (TITLE; cited from
  memory, verify).

## 4. Exposure data quality
- CDC WONDER suppresses county counts of 1 to 9 deaths and flags counts under 20 as unreliable; suppression falls mostly on small, rural counties
  (ABSTRACT-level sources, including County Health Rankings documentation). In this panel 43% of drug-overdose and suicide rows and 66% of
  homicide rows were missing (write-up section 5).
- Fentanyl-related mortality rose steeply west of the Mississippi later than in the East (Drug Alcohol Depend 2020;216:108314; TITLE). Whether this
  limited exposure variation in California during 2017-2020 is a hypothesis, not a finding.

## 5. Evaluation and reporting methods
- A small change in AUC can hide decision value, and a very large association is needed to move AUC (Pencina et al., 2008; Cook, 2007); decision
  analysis answers whether a small AUC change is worthwhile (Baker et al., 2014); reclassification measures have known limits (Leening et al., 2014)
  (all ABSTRACT or TITLE). The project already reports decision curves, calibration and proper scores.
- Reporting and bias tools: TRIPOD+AI (Collins et al., BMJ 2024;385:e078378, 27 items, supersedes TRIPOD 2015), PROBAST+AI (BMJ 2025;388),
  TRIPOD-Cluster (Debray et al., 2023) for clustered data.
- Negative controls (Lipsitch et al., 2010, Epidemiology 21:383) and leave-future-out validation (Burkner et al., 2020, J Stat Comput Simul) are
  verified (ABSTRACT).

## 6. Implications for the paper
1. Novelty wording: to our knowledge, no study tests whether county mortality adds out-of-sample predictive value for infectious-disease
   up-transition events across multiple diseases, against a population-adjusted baseline, with placebo and held-out-disease controls. State the
   search dates and limits (`24_novelty_search_log.md`).
2. Framing: a stress test of the assumption behind overdose-indicator vulnerability assessments, not a claim that mortality and infection are unrelated.
3. Scope limits to state: no HCV or HIV among the 16 diseases; 81 events; stage 1 pre-specified and later layers post hoc; mortality suppressed in
   small counties.
4. Do not claim: that prior associations are explained by county size (a hypothesis); that the null covers bloodborne outbreaks; that the study is
   an operational early-warning system.

## 7. Still to verify
Gezer 2024 Table 2 and the accuracy formula; Gizamba 2026 predictor list; Sumetsky 2019, Gonsalves 2021 and 2023 full text; Kidd 2019; the
fentanyl-timing paper; Abellan 2008; Leening 2014 page numbers; Embase, Web of Science, Scopus and preprint searches.
"""
rev = docs / "25_topic_literature_review.md"
if rev.exists():
    print("SKIPPED 25_topic_literature_review.md: already exists")
else:
    rev.write_text(REVIEW, encoding="utf-8", newline="\r\n")
    print("Wrote 25_topic_literature_review.md")

# ---------------------------------------------------------------- 2. write-up
edit_file(
    docs / "10_results_writeup.md",
    [
     ("so the result does not address bloodborne outbreaks.",
      "so the result does not address bloodborne outbreaks.\n"
      "- County mortality counts are suppressed by CDC WONDER when fewer than 10 deaths occur (rates from fewer than 20 deaths are flagged "
      "unreliable), and suppression falls mostly on small, rural counties. Missing mortality therefore tracks county size (section 5) and "
      "weakens the exposure where events are hardest to detect. Whether limited year-to-year variation in California mortality during 2017-2020 "
      "also reduced the signal is a hypothesis, not a finding."),
     ("Model A is well calibrated (slope 1.03, intercept 0.01) but barely beats predicting the average rate (Brier skill 0.005).",
      "Model A is well calibrated (slope 1.03, intercept 0.01) but barely beats predicting the average rate (Brier skill 0.005). Because a "
      "small change in AUC can hide decision value (Pencina et al., 2008; Baker et al., 2014), net benefit was assessed directly."),
     ("and is conservative for small counts (Richardson et al., 2004).",
      "and is conservative for small counts (Richardson et al., 2004); its sensitivity is low when the true excess is under 2-fold or expected "
      "counts are small, which is consistent with the county-size pattern seen here."),
     ("these two are not yet verified.",
      "the Abara association was positive but weakened over 2010-2015 and the authors noted possible confounding by men who have sex with men "
      "(abstract level); Cohen is not verified."),
     ("Patton et al. 2025, and the methods references",
      "Patton et al. 2025; Lipsitch 2010, Burkner 2020 and Richardson 2004 were checked on 2026-11-13; the wider review is in "
      "`25_topic_literature_review.md`"),
    ],
    marker="Abara association was positive but weakened",
)

# ---------------------------------------------------------------- 3. search log
LOG_ADD = """
## Additional sources checked 2026-11-13 (see 25_topic_literature_review.md)
| Source | Level | Note |
|---|---|---|
| Abara et al., opioid prescribing trends and gonorrhoea, US counties 2010-2015 | Abstract | Positive but weakening association; possible confounding by MSM |
| Ma et al., Front Public Health 2026;14:1888674 | Full text | State-level syphilis forecasting; co-STI and socioeconomic covariates helped modestly; no mortality |
| Richardson et al., Environ Health Perspect 2004 | Abstract | Posterior-probability rule specific but low sensitivity under 2-fold excess |
| Lipsitch et al., Epidemiology 2010; Burkner et al., J Stat Comput Simul 2020 | Abstract | Methods references verified |
| Pencina 2008; Cook 2007; Baker 2014; Leening 2014 | Abstract or title | Small AUC change vs decision value; NRI limits |
| TRIPOD+AI (BMJ 2024); PROBAST+AI (BMJ 2025); TRIPOD-Cluster (2023) | Abstract or title | Reporting and risk-of-bias tools |
| CDC WONDER suppression rule (1-9 deaths; under 20 unreliable) | Documentation | Suppression concentrated in small rural counties |
| Kidd et al., MMWR 2019; fentanyl-timing paper, Drug Alcohol Depend 2020;216:108314 | Title only | Verify before citing |
"""
edit_file(docs / "24_novelty_search_log.md", [], marker="Additional sources checked 2026-11-13", appendix=LOG_ADD)

# ---------------------------------------------------------------- 4. TRIPOD / PROBAST map
edit_file(
    docs / "20_tripod_probast.md",
    [
     ("TRIPOD+AI (Collins et al., BMJ 2024) and PROBAST (Wolff et al., Annals of Internal Medicine 2019) are the reference guidelines;",
      "TRIPOD+AI (Collins et al., BMJ 2024) and PROBAST (Wolff et al., Annals of Internal Medicine 2019) are the reference guidelines; "
      "PROBAST+AI (BMJ 2025) and TRIPOD-Cluster (Debray et al., 2023, for county-clustered data) are newer companions to check;"),
     ("| `21_advanced_results.md` | Done (stage 1 predictions) |",
      "| `20_advanced_results.md`, `23_proper_scoring_results.md` | Done (stage 1 predictions) |"),
     ("| `21_advanced_results.md` s.1-2 |",
      "| `20_advanced_results.md`, `23_proper_scoring_results.md` |"),
     ("| `21_advanced_results.md` s.4 |",
      "| `21_supplementary_results.md` |"),
     ("| Funding, conflicts, patient involvement | - | Not applicable / to write |",
      "| Literature search and novelty claim | `24_novelty_search_log.md`, `25_topic_literature_review.md` | Done; only PubMed searched systematically |\n"
      "| Funding, conflicts, patient involvement | - | Not applicable / to write |"),
    ],
    marker="PROBAST+AI (BMJ 2025)",
)
print("Done.")