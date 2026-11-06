# Simulation summary (A1, stand-in logistic test)

58 counties, 5 mortality years, 100 replicates per cell, alpha=0.05. Shared yearly shocks sd=1.0.

False-positive rate with year effects and NO true link (average over cells): 0.047 (nominal 0.05).

False-positive rate WITHOUT year effects and no true link:
|   diseases | test                          |   rejection_rate |
|-----------:|:------------------------------|-----------------:|
|          3 | no year effects, no true link |             0.15 |
|          8 | no year effects, no true link |             0.33 |

Power (rejection rate) when a link is planted. Columns: effect on log-odds, then number of lags tested.
|             |   (0.5, 1) |   (0.5, 2) |   (0.5, 3) |   (1.0, 1) |   (1.0, 2) |   (1.0, 3) |
|:------------|-----------:|-----------:|-----------:|-----------:|-----------:|-----------:|
| (1, 3, 0.1) |       0.48 |       0.31 |       0.24 |       0.95 |       0.84 |       0.64 |
| (1, 3, 0.2) |       0.7  |       0.47 |       0.29 |       0.98 |       0.93 |       0.83 |
| (1, 8, 0.1) |       0.85 |       0.56 |       0.53 |       1    |       1    |       0.95 |
| (1, 8, 0.2) |       0.93 |       0.74 |       0.68 |       1    |       1    |       0.95 |
| (2, 3, 0.1) |       0.04 |       0.32 |       0.26 |       0.04 |       0.92 |       0.76 |
| (2, 3, 0.2) |       0.03 |       0.43 |       0.38 |       0.07 |       0.96 |       0.84 |
| (2, 8, 0.1) |       0.04 |       0.67 |       0.55 |       0.07 |       0.99 |       0.94 |
| (2, 8, 0.2) |       0.01 |       0.75 |       0.72 |       0.06 |       0.99 |       1    |

Reading: target years usable by number of lags tested = {1: 5, 2: 4, 3: 3}. Power is for this stand-in test only.