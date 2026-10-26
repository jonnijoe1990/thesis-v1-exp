# Ergebnisse, 30 Minuten

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

Constraint: `30m-12c`. Modus: docker.

Versionen:

- AutoGluon 1.6.3, Parameter `{'presets': 'high_quality_v150', 'save_bag_folds': True}`
- H2OAutoML 3.46.0.12
- FLAML 2.7.0

Zeitraum der Folds: 2026-10-13T09:51:34 bis 2026-10-25T19:43:11.

## Mittelwerte der Testmetrik

| Aufgabe | Metrik | AutoGluon | FLAML | H2OAutoML |
| --- | --- | ---: | ---: | ---: |
| Age | RMSE | 11.1105 | 11.10792 | 11.13428 |
| Gender | AUC | 0.9290014 | 0.8635876 | 0.8219038 |
| Mortality | AUC | 0.948991 | 0.9176698 | 0.8624702 |
| Length of Stay | RMSE | 7.451706 | 7.856388 | 7.880542 |

## Age

Metrik: RMSE.

| Framework | Fold | RMSE | Trainingsdauer (s) | Vorhersagedauer (s) | Gesamtdauer (s) | Modelle | Ensembles |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| AutoGluon | 0 | 11.0273 | 1937.5 | 1.2 | 1957.6 | 10 | 4 |
| AutoGluon | 1 | 11.0248 | 1942.7 | 1.2 | 1962.8 | 10 | 4 |
| AutoGluon | 2 | 11.1149 | 1829.6 | 0.8 | 1848.6 | 8 | 4 |
| AutoGluon | 3 | 11.0813 | 1941.6 | 1.3 | 1962.1 | 10 | 4 |
| AutoGluon | 4 | 11.3042 | 1850.6 | 1.0 | 1869.8 | 8 | 4 |
| AutoGluon | Mittelwert | 11.1105 | 1900.4 | 1.1 | 1920.18 | 9.2 | 4 |
| FLAML | 0 | 11.1373 | 1823.9 | 0.5 | 1830.6 | 13 |  |
| FLAML | 1 | 10.9765 | 1952.7 | 5.0 | 1960.0 | 14 |  |
| FLAML | 2 | 11.164 | 1874.1 | 1.7 | 1878.1 | 15 |  |
| FLAML | 3 | 11.1305 | 1951.8 | 2.5 | 1956.6 | 16 |  |
| FLAML | 4 | 11.1313 | 1955.5 | 5.0 | 1962.9 | 14 |  |
| FLAML | Mittelwert | 11.10792 | 1911.6 | 2.94 | 1917.64 | 14.4 |  |
| H2OAutoML | 0 | 11.1662 | 1801.3 | 0.9 | 1811.3 | 74 |  |
| H2OAutoML | 1 | 11.0056 | 1801.2 | 0.8 | 1810.7 | 71 |  |
| H2OAutoML | 2 | 11.1788 | 1801.1 | 1.0 | 1810.9 | 66 |  |
| H2OAutoML | 3 | 11.1266 | 1801.2 | 1.0 | 1810.8 | 62 |  |
| H2OAutoML | 4 | 11.1942 | 1802.2 | 1.1 | 1811.9 | 70 |  |
| H2OAutoML | Mittelwert | 11.13428 | 1801.4 | 0.96 | 1811.12 | 68.6 |  |

## Gender

Metrik: AUC.

| Framework | Fold | AUC | Trainingsdauer (s) | Vorhersagedauer (s) | Gesamtdauer (s) | Modelle | Ensembles |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| AutoGluon | 0 | 0.929125 | 1881.0 | 0.6 | 1899.9 | 12 | 3 |
| AutoGluon | 1 | 0.926882 | 1835.1 | 0.6 | 1854.3 | 10 | 3 |
| AutoGluon | 2 | 0.931662 | 1840.5 | 0.6 | 1859.4 | 8 | 3 |
| AutoGluon | 3 | 0.928929 | 1832.4 | 0.6 | 1851.6 | 12 | 3 |
| AutoGluon | 4 | 0.928409 | 1899.4 | 0.6 | 1918.7 | 14 | 3 |
| AutoGluon | Mittelwert | 0.9290014 | 1857.68 | 0.6 | 1876.78 | 11.2 | 3 |
| FLAML | 0 | 0.865408 | 1809.8 | 0.3 | 1816.8 | 19 |  |
| FLAML | 1 | 0.868397 | 1881.2 | 1.7 | 1886.9 | 15 |  |
| FLAML | 2 | 0.857725 | 1815.0 | 0.6 | 1818.6 | 14 |  |
| FLAML | 3 | 0.858882 | 1808.6 | 0.3 | 1811.5 | 16 |  |
| FLAML | 4 | 0.867526 | 1859.9 | 1.4 | 1865.1 | 15 |  |
| FLAML | Mittelwert | 0.8635876 | 1834.9 | 0.86 | 1839.78 | 15.8 |  |
| H2OAutoML | 0 | 0.828982 | 1802.1 | 1.4 | 1817.4 | 79 |  |
| H2OAutoML | 1 | 0.830692 | 1801.8 | 1.2 | 1811.2 | 75 |  |
| H2OAutoML | 2 | 0.810897 | 1802.2 | 1.0 | 1812.2 | 73 |  |
| H2OAutoML | 3 | 0.81399 | 1802.5 | 1.3 | 1812.8 | 79 |  |
| H2OAutoML | 4 | 0.824958 | 1802.5 | 1.1 | 1811.9 | 81 |  |
| H2OAutoML | Mittelwert | 0.8219038 | 1802.22 | 1.2 | 1813.1 | 77.4 |  |

## Mortality

Metrik: AUC.

| Framework | Fold | AUC | Trainingsdauer (s) | Vorhersagedauer (s) | Gesamtdauer (s) | Modelle | Ensembles |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| AutoGluon | 0 | 0.952057 | 1920.7 | 0.6 | 1940.0 | 20 | 3 |
| AutoGluon | 1 | 0.947105 | 1927.3 | 0.7 | 1943.3 | 20 | 4 |
| AutoGluon | 2 | 0.948465 | 1906.7 | 0.7 | 1926.8 | 20 | 4 |
| AutoGluon | 3 | 0.947366 | 1924.4 | 0.5 | 1943.7 | 20 | 3 |
| AutoGluon | 4 | 0.949962 | 1937.8 | 0.5 | 1957.0 | 20 | 3 |
| AutoGluon | Mittelwert | 0.948991 | 1923.38 | 0.6 | 1942.16 | 20 | 3.4 |
| FLAML | 0 | 0.921627 | 1878.5 | 1.1 | 1887.1 | 12 |  |
| FLAML | 1 | 0.918207 | 1809.5 | 0.3 | 1812.4 | 13 |  |
| FLAML | 2 | 0.914281 | 1820.9 | 0.6 | 1824.5 | 12 |  |
| FLAML | 3 | 0.920424 | 1841.4 | 0.9 | 1845.7 | 12 |  |
| FLAML | 4 | 0.91381 | 1846.9 | 0.7 | 1850.8 | 14 |  |
| FLAML | Mittelwert | 0.9176698 | 1839.44 | 0.72 | 1844.1 | 12.6 |  |
| H2OAutoML | 0 | 0.86639 | 1801.9 | 1.1 | 1811.2 | 78 |  |
| H2OAutoML | 1 | 0.866522 | 1801.9 | 0.9 | 1811.8 | 70 |  |
| H2OAutoML | 2 | 0.860905 | 1801.7 | 1.3 | 1811.4 | 71 |  |
| H2OAutoML | 3 | 0.861997 | 1801.3 | 1.1 | 1810.6 | 71 |  |
| H2OAutoML | 4 | 0.856537 | 1802.4 | 0.4 | 1811.1 | 76 |  |
| H2OAutoML | Mittelwert | 0.8624702 | 1801.84 | 0.96 | 1811.22 | 73.2 |  |

## Length of Stay

Metrik: RMSE.

| Framework | Fold | RMSE | Trainingsdauer (s) | Vorhersagedauer (s) | Gesamtdauer (s) | Modelle | Ensembles |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| AutoGluon | 0 | 7.09346 | 1952.9 | 1.2 | 1972.6 | 10 | 4 |
| AutoGluon | 1 | 7.04389 | 1948.1 | 1.2 | 1967.9 | 10 | 4 |
| AutoGluon | 2 | 7.22119 | 1957.8 | 1.2 | 1977.5 | 12 | 4 |
| AutoGluon | 3 | 8.62658 | 1985.5 | 0.7 | 2003.7 | 6 | 3 |
| AutoGluon | 4 | 7.27341 | 1951.5 | 1.2 | 1971.2 | 12 | 4 |
| AutoGluon | Mittelwert | 7.451706 | 1959.16 | 1.1 | 1978.58 | 10 | 3.8 |
| FLAML | 0 | 7.37825 | 1858.7 | 0.3 | 1864.7 | 19 |  |
| FLAML | 1 | 7.22633 | 1855.6 | 0.3 | 1858.2 | 20 |  |
| FLAML | 2 | 7.47822 | 1887.5 | 2.9 | 1892.6 | 16 |  |
| FLAML | 3 | 9.45164 | 1808.2 | 0.3 | 1810.6 | 16 |  |
| FLAML | 4 | 7.7475 | 1879.7 | 3.3 | 1885.2 | 22 |  |
| FLAML | Mittelwert | 7.856388 | 1857.94 | 1.42 | 1862.26 | 18.6 |  |
| H2OAutoML | 0 | 7.53519 | 1801.8 | 0.4 | 1811.9 | 64 |  |
| H2OAutoML | 1 | 7.39776 | 1802.0 | 0.4 | 1811.6 | 61 |  |
| H2OAutoML | 2 | 7.6493 | 1801.9 | 0.4 | 1811.2 | 51 |  |
| H2OAutoML | 3 | 9.02789 | 1801.0 | 0.4 | 1810.6 | 53 |  |
| H2OAutoML | 4 | 7.79257 | 1801.2 | 0.6 | 1811.0 | 55 |  |
| H2OAutoML | Mittelwert | 7.880542 | 1801.58 | 0.44 | 1811.26 | 56.8 |  |
