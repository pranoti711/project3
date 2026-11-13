Abstract (about 250 words)

Background. Overdose, suicide and homicide mortality are often assumed to signal rising infectious disease in the same communities, but it is unknown whether county mortality improves out-of-sample forecasts of infectious disease increases.

Methods. We used 2001–2023 data for 16 notifiable diseases in California’s 58 counties. The outcome was an up-transition: the posterior probability of a rising local trend crossing 0.80, after removing the statewide yearly change. A baseline (own history plus county population) was compared with models adding lagged within-county mortality deviations, air quality and drought, or both. Validation was leave-future-out over 2017–2020 (81 events in 3,712 county-disease-year rows), using within-year-and-disease AUC with county-cluster bootstrap intervals. Stage 1 was pre-specified; placebo, held-out-disease, spatial-block, equivalence, power, gradient-boosting, decision-curve and proper-scoring analyses were exploratory or post hoc.

Results. Mortality did not improve discrimination (ΔAUC +0.001, 95% CI −0.028 to +0.034); context features gave +0.003 (−0.005 to +0.013) and the combined model +0.003 (−0.028 to +0.037). No disease group survived placebo testing with Holm correction, and results did not transfer to held-out diseases. The 90% interval for mortality lay within ±0.03 AUC, and the minimum detectable gain was 0.045. Log-loss and Brier differences were indistinguishable from zero. An initial apparent gain (ΔAUC +0.025) was explained by county population, which marks detectability in small counties.

Conclusions. County mortality showed no detectable added predictive value. With 81 events, gains below about 0.045 AUC cannot be excluded. Baselines should include population, and placebo tests must be able to separate the hypothesis from county size.

Journals usually want 250–300 words, so cut the Methods sentence on exploratory analyses first if you need space.

What my quick prior-art check found
No study in the snippets forecasts infectious disease transitions from county mortality. The closest work forecasts overdose deaths themselves, such as the Lancet Public Health 2021 county model. That is related work for your discussion, not a challenge to the claim.
Drewes et al. (IJERPH, published December 2020, volume 18 issue 1) studied opioid death rates against gonorrhea, chlamydia and HIV in Northeast counties. Its outcome is county STI rates in a regression, not out-of-sample prediction of transitions.
A discrepancy in section 8. The write-up says Drewes found an association “for gonorrhea in urban counties”, but a peer-reviewer comment in the snippets says it was significant “only for rural counties in 2016–2017”. Check the full paper and fix the sentence. Also confirm the year in references.bib (2020 online, 2021 volume).