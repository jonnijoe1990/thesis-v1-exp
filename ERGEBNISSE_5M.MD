# Ergebnisse, 5 Minuten

Jede Zeile ist ein gelungener Fold aus `results.csv`. Zeilen ohne Metrik sind nicht enthalten.

In jedem gelungenen Fold stehen diese Zahlen:

| Zahl | Spalte |
| --- | --- |
| Testmetrik | AUC bei Gender und Mortality, RMSE bei Age und Length of Stay |
| Trainingsdauer | `training_duration`, in Sekunden |
| Vorhersagedauer | `predict_duration`, in Sekunden |
| Gesamtdauer | `duration`, in Sekunden |
| Anzahl der Modelle | `models_count` |

Die Ensemblezahl `models_ensemble_count` gibt es nur bei AutoGluon. Bei FLAML und H2OAutoML bleibt das Feld leer.

Der RMSE ist der positive Wert. AutoML-Benchmark speichert dieselbe Größe in `result` als `neg_rmse`.

Constraint: `5m-12c`. Modus: docker.

Versionen:

- AutoGluon 1.6.3, Parameter `{'presets': 'medium_quality'}`
- H2OAutoML 3.46.0.12
- FLAML 2.7.0

Zeitraum der Folds: 2026-10-08T07:43:03 bis 2026-10-16T14:04:00.

## Mittelwerte der Testmetrik

| Aufgabe | Metrik | AutoGluon | FLAML | H2OAutoML |
| --- | --- | ---: | ---: | ---: |
| Age | RMSE | 11.12382 | 11.23006 | 11.32356 |
| Gender | AUC | 0.927543 | 0.8587166 | 0.8071238 |
| Mortality | AUC | 0.945291 | 0.9161352 | 0.846899 |
| Length of Stay | RMSE | 7.929838 | 8.052826 | 8.133448 |

## Age

Metrik: RMSE.

| Framework | Fold | RMSE | Trainingsdauer (s) | Vorhersagedauer (s) | Gesamtdauer (s) | Modelle | Ensembles |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| AutoGluon | 0 | 11.066 | 306.0 | 0.7 | 315.0 | 6 | 5 |
| AutoGluon | 1 | 11.0749 | 301.0 | 0.6 | 304.8 | 7 | 5 |
| AutoGluon | 2 | 11.0671 | 298.3 | 0.6 | 302.0 | 6 | 5 |
| AutoGluon | 3 | 11.1496 | 300.0 | 0.7 | 304.8 | 7 | 6 |
| AutoGluon | 4 | 11.2615 | 300.9 | 0.8 | 305.5 | 6 | 6 |
| AutoGluon | Mittelwert | 11.12382 | 301.24 | 0.68 | 306.42 | 6.4 | 5.4 |
| FLAML | 0 | 11.3033 | 306.3 | 0.2 | 309.6 | 10 |  |
| FLAML | 1 | 11.0678 | 313.0 | 0.3 | 315.7 | 12 |  |
| FLAML | 2 | 11.3074 | 345.2 | 0.4 | 347.9 | 14 |  |
| FLAML | 3 | 11.1751 | 314.0 | 0.2 | 316.6 | 12 |  |
| FLAML | 4 | 11.2967 | 308.1 | 0.2 | 310.6 | 10 |  |
| FLAML | Mittelwert | 11.23006 | 317.32 | 0.26 | 320.08 | 11.6 |  |
| H2OAutoML | 0 | 11.3817 | 302.0 | 0.4 | 312.2 | 59 |  |
| H2OAutoML | 1 | 11.2532 | 302.7 | 0.4 | 311.7 | 58 |  |
| H2OAutoML | 2 | 11.331 | 302.5 | 0.4 | 312.1 | 63 |  |
| H2OAutoML | 3 | 11.2822 | 302.8 | 0.6 | 312.3 | 53 |  |
| H2OAutoML | 4 | 11.3697 | 303.0 | 0.6 | 312.4 | 58 |  |
| H2OAutoML | Mittelwert | 11.32356 | 302.6 | 0.48 | 312.14 | 58.2 |  |

## Gender

Metrik: AUC.

| Framework | Fold | AUC | Trainingsdauer (s) | Vorhersagedauer (s) | Gesamtdauer (s) | Modelle | Ensembles |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| AutoGluon | 0 | 0.927114 | 285.9 | 0.2 | 293.1 | 12 | 3 |
| AutoGluon | 1 | 0.925049 | 300.4 | 0.1 | 303.4 | 11 | 2 |
| AutoGluon | 2 | 0.931251 | 301.2 | 0.3 | 304.9 | 11 | 3 |
| AutoGluon | 3 | 0.927413 | 301.0 | 0.1 | 303.9 | 11 | 2 |
| AutoGluon | 4 | 0.926888 | 274.9 | 0.1 | 277.8 | 12 | 2 |
| AutoGluon | Mittelwert | 0.927543 | 292.68 | 0.16 | 296.62 | 11.4 | 2.4 |
| FLAML | 0 | 0.858594 | 316.5 | 0.4 | 319.8 | 17 |  |
| FLAML | 1 | 0.856512 | 434.1 | 4.1 | 444.8 | 13 |  |
| FLAML | 2 | 0.853444 | 383.4 | 1.6 | 389.0 | 12 |  |
| FLAML | 3 | 0.861381 | 350.0 | 1.1 | 354.7 | 15 |  |
| FLAML | 4 | 0.863652 | 348.2 | 0.8 | 352.3 | 13 |  |
| FLAML | Mittelwert | 0.8587166 | 366.44 | 1.6 | 372.12 | 14 |  |
| H2OAutoML | 0 | 0.80717 | 302.3 | 0.7 | 312.5 | 60 |  |
| H2OAutoML | 1 | 0.812301 | 302.8 | 0.5 | 312.5 | 65 |  |
| H2OAutoML | 2 | 0.798507 | 303.0 | 0.7 | 312.7 | 60 |  |
| H2OAutoML | 3 | 0.80561 | 303.2 | 0.5 | 312.2 | 65 |  |
| H2OAutoML | 4 | 0.812031 | 302.4 | 0.4 | 311.6 | 64 |  |
| H2OAutoML | Mittelwert | 0.8071238 | 302.74 | 0.56 | 312.3 | 62.8 |  |

## Mortality

Metrik: AUC.

| Framework | Fold | AUC | Trainingsdauer (s) | Vorhersagedauer (s) | Gesamtdauer (s) | Modelle | Ensembles |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| AutoGluon | 0 | 0.948568 | 224.8 | 0.2 | 231.9 | 12 | 3 |
| AutoGluon | 1 | 0.944109 | 299.0 | 0.2 | 302.0 | 12 | 3 |
| AutoGluon | 2 | 0.945211 | 261.6 | 0.3 | 265.0 | 12 | 4 |
| AutoGluon | 3 | 0.943987 | 300.7 | 0.3 | 304.2 | 11 | 4 |
| AutoGluon | 4 | 0.94458 | 165.0 | 0.3 | 168.2 | 12 | 4 |
| AutoGluon | Mittelwert | 0.945291 | 250.22 | 0.26 | 254.26 | 11.8 | 3.6 |
| FLAML | 0 | 0.921496 | 325.3 | 0.6 | 329.1 | 11 |  |
| FLAML | 1 | 0.913741 | 349.7 | 0.5 | 353.1 | 10 |  |
| FLAML | 2 | 0.916674 | 325.6 | 0.6 | 329.2 | 11 |  |
| FLAML | 3 | 0.920424 | 340.8 | 1.0 | 345.2 | 12 |  |
| FLAML | 4 | 0.908341 | 406.7 | 1.0 | 411.4 | 14 |  |
| FLAML | Mittelwert | 0.9161352 | 349.62 | 0.74 | 353.6 | 11.6 |  |
| H2OAutoML | 0 | 0.851692 | 302.8 | 0.5 | 317.0 | 74 |  |
| H2OAutoML | 1 | 0.845355 | 302.8 | 0.4 | 313.6 | 66 |  |
| H2OAutoML | 2 | 0.846451 | 302.3 | 0.4 | 311.4 | 66 |  |
| H2OAutoML | 3 | 0.848049 | 302.1 | 0.4 | 311.6 | 76 |  |
| H2OAutoML | 4 | 0.842948 | 302.5 | 0.4 | 312.7 | 64 |  |
| H2OAutoML | Mittelwert | 0.846899 | 302.5 | 0.42 | 313.26 | 69.2 |  |

## Length of Stay

Metrik: RMSE.

| Framework | Fold | RMSE | Trainingsdauer (s) | Vorhersagedauer (s) | Gesamtdauer (s) | Modelle | Ensembles |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| AutoGluon | 0 | 7.33405 | 300.3 | 0.3 | 306.6 | 7 | 4 |
| AutoGluon | 1 | 7.05597 | 301.1 | 0.7 | 306.8 | 8 | 5 |
| AutoGluon | 2 | 8.82625 | 300.5 | 0.3 | 304.4 | 9 | 4 |
| AutoGluon | 3 | 8.98982 | 300.6 | 0.5 | 304.9 | 9 | 5 |
| AutoGluon | 4 | 7.4431 | 299.7 | 0.6 | 303.8 | 8 | 5 |
| AutoGluon | Mittelwert | 7.929838 | 300.44 | 0.48 | 305.3 | 8.2 | 4.6 |
| FLAML | 0 | 7.62174 | 315.6 | 0.4 | 321.7 | 13 |  |
| FLAML | 1 | 7.47774 | 333.0 | 0.4 | 335.5 | 17 |  |
| FLAML | 2 | 7.84493 | 308.6 | 0.2 | 311.0 | 12 |  |
| FLAML | 3 | 9.35705 | 321.0 | 0.3 | 323.5 | 12 |  |
| FLAML | 4 | 7.96267 | 310.7 | 0.2 | 313.1 | 13 |  |
| FLAML | Mittelwert | 8.052826 | 317.78 | 0.3 | 320.96 | 13.4 |  |
| H2OAutoML | 0 | 7.53835 | 302.6 | 0.2 | 317.1 | 56 |  |
| H2OAutoML | 1 | 7.64659 | 302.8 | 0.4 | 311.8 | 45 |  |
| H2OAutoML | 2 | 7.95503 | 302.3 | 0.4 | 311.8 | 41 |  |
| H2OAutoML | 3 | 9.35232 | 303.3 | 0.2 | 312.3 | 51 |  |
| H2OAutoML | 4 | 8.17495 | 302.9 | 0.6 | 312.6 | 54 |  |
| H2OAutoML | Mittelwert | 8.133448 | 302.78 | 0.36 | 313.12 | 49.4 |  |
