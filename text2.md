 Select-String -Path 06_paper\manuscript_draft.md -Pattern '`|\b\d\d[a-z]?_[a-z_]+\.(md|py|R|csv)|\bsection \d|\bSection \d|commit|\btag\b|frozen|paste-ready|FILL|TODO|stage1|bbc9ebe|hash' | ForEach-Object { "{0}: {1}" -f $_.LineNumber, $_.Line.Trim().Substring(0, [Math]::Min(150, $_.Line.Trim().Length)) }
62: (`upcross_local_0.80`). Evaluation: leave-future-out over 2017-2020 (81 events in 3,712 county-disease-year
86: `review_travel` group (Malaria) had 4 scored events and was left out of the placebo tests.
142: Pre-specified in `13_stage2_plan.md` (stage 1 frozen at commit bbc9ebe). Same test years and events as stage 1, so
166: Pre-specified in `17_stage3_plan.md` (committed as ee54e5f before the run). Same test years and 81 events, so
195: Choices fixed in `19_advanced_evaluation_plan.md` before running. Scripts 19-26 (the second layer, script 27, is section 12); numbers in `20_advanced_
196: `21_supplementary_results.md`; figures in `05_results/figures_report/`. All use the stage 1 out-of-fold predictions and the
216: `figures_report/map_*.png`. The average correlation between diseases' county-year trend slopes is only 0.05 (range -0.07 to
218: - **Reporting.** `20_tripod_probast.md` maps the project to reporting-guideline topics and gives a risk-of-bias self-assessment
219: (outcome and analysis domains rated high concern); `04_scripts/test_leakage.py` checks the leakage rules in code.
223: Script 27 (`27_proper_scoring_and_influence.py`, numbers in `23_proper_scoring_results.md`, tables `adv2_*.csv`). Same
225: and not part of `19_advanced_evaluation_plan.md`, so it is post-hoc. AUC only looks at ranking; proper scoring rules also
240: `21_supplementary_results.md` comes from a fit with a free slopeand is not comparable to the fixed-slope intercept here.
248: Taken together with section 11, the proper-scoring and calibration checks agree with the AUC result: no evidence that
275: (git commit a1b6688, tag hiv-ext).
335: - Changes after seeing results are all logged in `07_deviations_log.md` and `04_prereg.md` (retrospective record).
349: - Bootstrap shares reported in section 12 are frequentist approximations to a region-of-practical-equivalence statement, not posteriorprobabilities.
351: - County mortality counts are suppressed by CDC WONDER when fewer than 10 deaths occur (rates from fewer than 20 deaths are flagged unreliable), and s
363: Code, processed data, logs and the pre-registration are at https://github.com/pranoti711/project3 (tag final-draft-v12).
PS E:\iit tirupati\PROJECT\project3> 