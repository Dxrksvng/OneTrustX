# Synthetic evaluation report

Simulated MVP Result — Not actual airport performance.

First 70% training; last 30% testing; 60-minute embargo; no random shuffle

| Model | Horizon | MAE | RMSE | P90 error | Precision | Recall | F1 | Interval coverage |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| persistence | 15 | 5.97 | 8.13 | 11.32 | 0.96 | 0.95 | 0.95 | 0.67 |
| moving_average | 15 | 8.81 | 11.41 | 17.14 | 0.93 | 0.93 | 0.93 | 0.52 |
| fluid | 15 | 2.20 | 5.07 | 3.96 | 0.99 | 0.99 | 0.99 | 0.94 |
| linear | 15 | 4.27 | 6.67 | 12.12 | 0.98 | 1.00 | 0.99 | 0.88 |
| random_forest | 15 | 1.75 | 4.32 | 3.58 | 0.99 | 1.00 | 0.99 | 0.97 |
| persistence | 30 | 11.70 | 14.96 | 22.70 | 0.91 | 0.91 | 0.91 | 0.42 |
| moving_average | 30 | 14.41 | 18.20 | 28.35 | 0.89 | 0.88 | 0.89 | 0.36 |
| fluid | 30 | 4.57 | 8.43 | 9.28 | 0.98 | 0.98 | 0.98 | 0.84 |
| linear | 30 | 5.91 | 8.75 | 15.69 | 0.95 | 0.99 | 0.97 | 0.77 |
| random_forest | 30 | 3.21 | 6.37 | 7.36 | 0.98 | 1.00 | 0.99 | 0.93 |
| persistence | 60 | 22.56 | 28.06 | 44.99 | 0.82 | 0.81 | 0.82 | 0.26 |
| moving_average | 60 | 25.17 | 31.11 | 50.36 | 0.80 | 0.79 | 0.80 | 0.23 |
| fluid | 60 | 10.34 | 16.08 | 24.34 | 0.96 | 0.95 | 0.96 | 0.60 |
| linear | 60 | 9.34 | 12.99 | 21.84 | 0.90 | 0.99 | 0.94 | 0.60 |
| random_forest | 60 | 6.13 | 9.79 | 16.35 | 0.96 | 0.98 | 0.97 | 0.80 |

No ML model promoted. Offline candidates must beat persistence and fluid across horizons and pass independent validation.

Confidence is a heuristic, not a calibrated probability. Coverage is empirical synthetic test coverage of ±(15% of estimate + 2 min). No airport accuracy claims. Lead times in JSON are onset-matched warning measurements; undetected onsets are reported separately.

Targets: MAE ≤5 min, recall ≥0.80, warning lead ≥15 min. Targets are MVP aspirations, not industry standards. See JSON for measured results; failing targets are not waived.
