# Data gate results

Mortality source: mortality_ca_wide_wonder.csv

Counties: 58. Thresholds: {'min_overlap_years': 10, 'min_counties_per_year': 20, 'min_usable_counties': 20, 'max_missing': 0.3, 'max_zero': 0.7, 'min_diseases_per_group': 3, 'windows': {'full_2001_2023': (2001, 2023), 'overlap_2019_2023': (2019, 2023)}}

## Gate 1 - overlap of usable county mortality (need >= 10 years; registered value 10)
| mortality_series      | years_in_file   |   usable_overlap_years | pass_gate1   |
|:----------------------|:----------------|-----------------------:|:-------------|
| all_cause (benchmark) | 1999-2024       |                     23 | True         |
| drug_od               | 1999-2024       |                     23 | True         |
| homicide              | 1999-2024       |                     23 | True         |
| suicide               | 1999-2024       |                     23 | True         |

## Gates 2-4 - full_2001_2023: 16 of 56 diseases pass

## Gates 2-4 - overlap_2019_2023: 18 of 56 diseases pass

Full per-disease table: 05_results/tables/data_gate_disease_screen.csv

## Gate 5 - disease groups (proxy: diseases passing gates 2-4 in full window; source: disease_groups_draft.csv)
| group         |   diseases |   passing_2_3_4 | pass_gate5_proxy   |
|:--------------|-----------:|----------------:|:-------------------|
| ambiguous     |          2 |               1 | False              |
| comparison    |         11 |               8 | True               |
| drug_linked   |          1 |               0 | False              |
| environment   |         15 |               4 | True               |
| review_sti    |          2 |               2 | False              |
| review_travel |          7 |               1 | False              |
| unassigned    |         18 |               0 | False              |

Gate 5 is a proxy. The real test is transition events per group, available after step 4 (transitions).