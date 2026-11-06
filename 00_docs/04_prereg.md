# 04_prereg.md - Registration record

> **Retrospective record, written 2026-11-03 after results were seen.** It documents what the plan specified
> and what changed. It is a transparency record, not a prospective preregistration, and should be described
> that way in any paper. Part B is a genuine prospective registration: freeze it (date, commit hash) before
> loading any drug-linked county data.

## Part A - Record of the design

### A1. Hypotheses
- H1 (primary): adding county mortality (model B) improves out-of-sample AUC over own-history (model A) for
  next-year disease up-transitions.
- H2: any gain is larger for drug-linked diseases than for comparison diseases.
- H3: any gain holds in held-out diseases, held-out groups and held-out counties.

### A2. Specified in the plan (before modelling)
| Item | Value |
|---|---|
| Unit / years | county x disease x year, California, 2001-2023 |
| Outcome | up-crossing of Pr(rising) at 0.80 (0.70 / 0.90 sensitivity) |
| Models | A history; B + mortality; C + context; D all |
| Mortality primary source | CDC final counts (pooled), NCHS model-based as sensitivity only |
| Validation | leave-future-out, spatial-block CV, leave-one-disease-out, leave-one-group-out |
| Early warning | matched false-alarm rate |
| Nulls | surrogate-disease null; simulation before real cross-domain results |
| Gates | >= 10 overlapping usable mortality years; >= 20 usable counties; max missing 0.3; max zero 0.7; >= 3 diseases per group |
| Groups | drug-linked, ambiguous, environment-linked, comparison (frozen before modelling; review groups added by draft rules) |

### A3. Changes made after seeing results (post-hoc, all logged in `07_deviations_log.md`)
| Change | Reason | Effect on conclusions |
|---|---|---|
| Headline AUC became within year x disease (pooled kept) | pooled AUC < 0.5 from year-level miscalibration | removed spurious run-1 signals |
| Year effect RW2 -> iid | RW2 extrapolates wildly into the hidden year | calibration fixed |
| Added local outcome `upcross_local_0.80` | statewide trend dominated the outcome | both outcomes reported |
| Gate-1 deviation (5 years) withdrawn | gate shows 23 years | none |
| Holm correction across groups added | multiplicity | placebo support disappeared |
| Test years reduced to 2017-2020 | no local events in 2021-2022 | lower power (81 scored events) |
| Population added to the baseline model A; mortality changed from levels to lagged within-county deviations; missing-value flags removed | the first positive result was explained by county size (see `07_deviations_log.md`) | removed the apparent mortality gain |
| Placebo N1 changed from county-swap to within-county year shuffle | county-swap cannot tell mortality from a fixed county trait | stricter null |
| `physicians_per_100k` dropped from context set | about 96% missing | none |
| `review_travel` group not included in placebo tests | 4 scored events | Holm over 4 groups |

### A4. Decision rules (as applied)
- Mortality "adds value" only if the B - A bootstrap interval excludes 0 **and** the gain beats both placebo
  nulls after Holm correction **and** transfers to held-out diseases or groups.
- None of these conditions was met in the corrected run (pooled B - A = +0.001, 95% CI -0.028 to +0.034;
  no group supported after Holm; held-out transfer and spatial-block CV show no consistent gain).
- H1, H2 and H3 are therefore not supported. The result is a null result with low power (81 events).

## Part B - Prospective registration for the drug-linked analysis (freeze before data load)

How to use: fill the **FILL** cells, save, then compute the file hash with the command at the end and
write it in the last row. Do not change this section after that. (This project is not a git repository, so the
SHA-256 hash of the frozen group file stands in for a commit hash.)

| Item | Fixed value |
|---|---|
| Data source and version for county drug-linked series | **FILL**: name of the county-level hepatitis B/C (or other injection-related) source, its URL, download date and version. None is currently available; the AtlasPlus export is state-level only. The file goes in `02_data/raw/downloads/` and is converted with `04_scripts/01d_make_drug_linked_csv.py`. |
| Diseases entering the drug-linked group | Hepatitis C (acute) and hepatitis B (acute), the names the grouping rule in `03_disease_groups.py` recognises as drug-linked. Injection drug use is the established transmission route for hepatitis C. **FILL**: one citation per disease (for example a CDC or WHO page) before freezing. |
| Group frozen in `disease_groups_frozen.csv` on | **FILL**: date. Hash recorded in the last row. |
| Primary outcome | `upcross_local_0.80` (fixed) |
| Primary statistic | within year x disease AUC, B - A, drug-linked group; B uses the four lagged within-county mortality deviations; A includes `pop_log` |
| Primary contrast | drug-linked gain minus comparison-group gain, county-cluster bootstrap (500 reps) |
| Test years | rolling origin, all years with >= 1 event; a test year is dropped if the drug-linked group has fewer than 10 events in it |
| Multiplicity | Holm across groups; `drug_od_dev` pre-specified as the primary mortality series |
| Placebos | N1 within-county year shuffle and N2 outcome shuffle, >= 1000 permutations each; surrogate-disease rank test |
| Success criterion | contrast CI excludes 0, beats both placebos, Holm p < 0.05 |
| Stopping rule | if the drug-linked group has fewer than 30 events over all test years, report as underpowered and do not analyse further |
| SHA-256 of `disease_groups_frozen.csv` | **FILL** (compute with the command below) |

The two numeric rules (10 events per tested year, 30 events in total) are my suggested values; change them
before freezing if you prefer other limits.

Command to compute the hash (PowerShell, from the project3 folder):

```powershell
Get-FileHash 02_data/processed/disease_groups_frozen.csv -Algorithm SHA256
```