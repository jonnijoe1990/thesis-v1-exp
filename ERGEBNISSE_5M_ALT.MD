# Ergebnisse, 5 Minuten, alte AutoGluon-Auswertung

Diese Tabelle steht getrennt von den korrigierten 5-Minuten-Ergebnissen. Sie enthält die AutoGluon-Läufe, in denen die Auswertung die Vorhersagen falsch zugeordnet hat.

In jedem gelungenen Fold stehen diese Zahlen:

| Zahl | Spalte |
| --- | --- |
| Testmetrik | AUC bei Gender und Mortality, RMSE bei Age |
| Trainingsdauer | `training_duration`, in Sekunden |
| Vorhersagedauer | `predict_duration`, in Sekunden |
| Gesamtdauer | `duration`, in Sekunden |
| Anzahl der Modelle | `models_count` |

Die Ensemblezahl steht in `models_ensemble_count`.

Der RMSE ist der positive Wert. AutoML-Benchmark speichert dieselbe Größe in `result` als `neg_rmse`.

Constraint: `5m-12c`. Modus: docker.

Versionen:

- AutoGluon 1.6.3, Parameter `{'presets': 'medium_quality'}`

Zeitraum der Folds: 2026-10-08T15:51:05 bis 2026-10-08T17:03:26.

Length of Stay wurde in diesem Lauf nicht gemessen.

## Mittelwerte der Testmetrik

| Aufgabe | Metrik | AutoGluon |
| --- | --- | ---: |
| Age | RMSE | 20.7520 |
| Gender | AUC | 0.5086108 |
| Mortality | AUC | 0.5200884 |
| Length of Stay | RMSE | nicht gemessen |

## Age

Metrik: RMSE.

| Framework | Fold | RMSE | Trainingsdauer (s) | Vorhersagedauer (s) | Gesamtdauer (s) | Modelle | Ensembles |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| AutoGluon | 0 | 20.7828 | 309.6 | 0.6 | 320.6 | 6 | 5 |
| AutoGluon | 1 | 20.8001 | 303.0 | 0.6 | 309.3 | 6 | 5 |
| AutoGluon | 2 | 20.8738 | 303.2 | 0.6 | 308.4 | 6 | 5 |
| AutoGluon | 3 | 20.5929 | 300.5 | 0.8 | 307.0 | 7 | 7 |
| AutoGluon | 4 | 20.7104 | 300.3 | 0.9 | 306.5 | 7 | 6 |
| AutoGluon | Mittelwert | 20.7520 | 303.32 | 0.7 | 310.36 | 6.4 | 5.6 |

## Gender

Metrik: AUC.

| Framework | Fold | AUC | Trainingsdauer (s) | Vorhersagedauer (s) | Gesamtdauer (s) | Modelle | Ensembles |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| AutoGluon | 0 | 0.501135 | 273.4 | 0.3 | 278.6 | 12 | 3 |
| AutoGluon | 1 | 0.50818 | 300.6 | 0.1 | 305.1 | 11 | 2 |
| AutoGluon | 2 | 0.511122 | 301.2 | 0.3 | 307.4 | 11 | 3 |
| AutoGluon | 3 | 0.515645 | 300.3 | 0.1 | 304.8 | 11 | 2 |
| AutoGluon | 4 | 0.506972 | 265.6 | 0.1 | 270.0 | 12 | 2 |
| AutoGluon | Mittelwert | 0.5086108 | 288.22 | 0.18 | 293.18 | 11.4 | 2.4 |

## Mortality

Metrik: AUC.

| Framework | Fold | AUC | Trainingsdauer (s) | Vorhersagedauer (s) | Gesamtdauer (s) | Modelle | Ensembles |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| AutoGluon | 0 | 0.515067 | 219.8 | 0.2 | 224.7 | 12 | 3 |
| AutoGluon | 1 | 0.526126 | 300.2 | 0.1 | 304.8 | 12 | 3 |
| AutoGluon | 2 | 0.520961 | 265.2 | 0.3 | 270.4 | 12 | 4 |
| AutoGluon | 3 | 0.521579 | 301.1 | 0.3 | 306.3 | 11 | 4 |
| AutoGluon | 4 | 0.516709 | 166.6 | 0.4 | 171.5 | 12 | 4 |
| AutoGluon | Mittelwert | 0.5200884 | 250.58 | 0.26 | 255.54 | 11.8 | 3.6 |
