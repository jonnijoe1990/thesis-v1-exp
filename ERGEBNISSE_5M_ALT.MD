# Alte AutoGluon-Ergebnisse, 5 Minuten

Diese Tabellen stammen aus `results_5m_old`. Es sind die AutoGluon-Läufe vor der Korrektur der Auswertung. Übernommen sind nur Zeilen mit einem Zahlenwert aus `results.csv`. Logs, Fehlermeldungen, Vorhersagedateien und Leaderboards sind nicht enthalten.

In den drei vorhandenen Aufgaben liegt je ein vollständiger Lauf mit den Folds 0 bis 4. Fehlerzeilen gibt es in diesen Dateien nicht. Length of Stay wurde in `results_5m_old` nicht gemessen.

Gemeinsame Angaben aller Läufe:

| | |
| --- | --- |
| Framework | AutoGluon 1.6.3 |
| Preset | `medium_quality` |
| Constraint | `5m-12c` |
| Modus | docker |
| Datum | 8. Oktober 2026 |

Der Mittelwert ist das arithmetische Mittel der fünf Folds. Bei Age ist die Metrik der positive RMSE. AutoML-Benchmark speichert daneben `neg_rmse` als negativen Ergebniswert.

## Überblick

| Aufgabe | Metrik | Mittelwert |
| --- | --- | --- |
| Age | RMSE | 20.7520 |
| Gender | AUC | 0.508611 |
| Mortality | AUC | 0.520088 |
| Length of Stay | | nicht gemessen |

## Age

Metrik: RMSE. Quelle: `results_5m_old/autogluon_mq_age/results.csv`.

| Fold | RMSE | Trainingsdauer (s) | Vorhersagedauer (s) | Gesamtdauer (s) | Modelle | Ensembles | UTC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 20.7828 | 309.6 | 0.6 | 320.6 | 6 | 5 | 2026-10-08T15:51:05 |
| 1 | 20.8001 | 303.0 | 0.6 | 309.3 | 6 | 5 | 2026-10-08T15:56:14 |
| 2 | 20.8738 | 303.2 | 0.6 | 308.4 | 6 | 5 | 2026-10-08T16:01:22 |
| 3 | 20.5929 | 300.5 | 0.8 | 307.0 | 7 | 7 | 2026-10-08T16:06:29 |
| 4 | 20.7104 | 300.3 | 0.9 | 306.5 | 7 | 6 | 2026-10-08T16:11:36 |
| Mittelwert | 20.7520 | 303.32 | 0.70 | 310.36 | 6.4 | 5.6 | |

## Gender

Metrik: AUC. Quelle: `results_5m_old/autogluon_mq_gender/results.csv`.

| Fold | AUC | Trainingsdauer (s) | Vorhersagedauer (s) | Gesamtdauer (s) | Modelle | Ensembles | UTC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0.501135 | 273.4 | 0.3 | 278.6 | 12 | 3 | 2026-10-08T16:19:24 |
| 1 | 0.50818 | 300.6 | 0.1 | 305.1 | 11 | 2 | 2026-10-08T16:24:29 |
| 2 | 0.511122 | 301.2 | 0.3 | 307.4 | 11 | 3 | 2026-10-08T16:29:37 |
| 3 | 0.515645 | 300.3 | 0.1 | 304.8 | 11 | 2 | 2026-10-08T16:34:42 |
| 4 | 0.506972 | 265.6 | 0.1 | 270.0 | 12 | 2 | 2026-10-08T16:39:12 |
| Mittelwert | 0.508611 | 288.22 | 0.18 | 293.18 | 11.4 | 2.4 | |

## Mortality

Metrik: AUC. Quelle: `results_5m_old/autogluon_mq_mortality/results.csv`.

| Fold | AUC | Trainingsdauer (s) | Vorhersagedauer (s) | Gesamtdauer (s) | Modelle | Ensembles | UTC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0.515067 | 219.8 | 0.2 | 224.7 | 12 | 3 | 2026-10-08T16:45:53 |
| 1 | 0.526126 | 300.2 | 0.1 | 304.8 | 12 | 3 | 2026-10-08T16:50:58 |
| 2 | 0.520961 | 265.2 | 0.3 | 270.4 | 12 | 4 | 2026-10-08T16:55:28 |
| 3 | 0.521579 | 301.1 | 0.3 | 306.3 | 11 | 4 | 2026-10-08T17:00:34 |
| 4 | 0.516709 | 166.6 | 0.4 | 171.5 | 12 | 4 | 2026-10-08T17:03:26 |
| Mittelwert | 0.520088 | 250.58 | 0.26 | 255.54 | 11.8 | 3.6 | |

## Length of Stay

In `results_5m_old` gibt es keinen Ordner und keine Ergebnisdatei für Length of Stay.
