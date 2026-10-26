# Ergebnisse, 15 Minuten

Jede Zeile ist ein gelungener Fold aus `results.csv`. Zeilen ohne Metrik sind nicht enthalten.

Bei AutoGluon, Gender, Fold 3 steht die Wiederholung vom 26. Oktober 2026. Der frühere kurze Lauf ist nicht enthalten.

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

Constraint: `15m-12c`. Modus: docker.

Versionen:

- AutoGluon 1.6.3, Parameter `{'presets': 'good_quality', 'save_bag_folds': True}`
- H2OAutoML 3.46.0.12
- FLAML 2.7.0

Zeitraum der Folds: 2026-10-08T17:22:32 bis 2026-10-26T12:25:15.

## Mittelwerte der Testmetrik

| Aufgabe | Metrik | AutoGluon | FLAML | H2OAutoML |
| --- | --- | ---: | ---: | ---: |
| Age | RMSE | 11.06248 | 11.12258 | 11.27052 |
| Gender | AUC | 0.9287604 | 0.8613494 | 0.8119424 |
| Mortality | AUC | 0.9484058 | 0.918074 | 0.8527962 |
| Length of Stay | RMSE | 7.533596 | 8.02834 | 8.415262 |

## Age

Metrik: RMSE.

| Framework | Fold | RMSE | Trainingsdauer (s) | Vorhersagedauer (s) | Gesamtdauer (s) | Modelle | Ensembles |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| AutoGluon | 0 | 11.0278 | 900.8 | 1.2 | 923.0 | 30 | 12 |
| AutoGluon | 1 | 11.014 | 895.5 | 1.2 | 913.8 | 28 | 12 |
| AutoGluon | 2 | 11.0044 | 912.9 | 1.6 | 936.0 | 32 | 13 |
| AutoGluon | 3 | 11.0246 | 903.7 | 1.2 | 926.0 | 30 | 12 |
| AutoGluon | 4 | 11.2416 | 909.4 | 1.4 | 932.3 | 32 | 13 |
| AutoGluon | Mittelwert | 11.06248 | 904.46 | 1.32 | 926.22 | 30.4 | 12.4 |
| FLAML | 0 | 11.1373 | 936.8 | 0.5 | 943.5 | 13 |  |
| FLAML | 1 | 10.9765 | 1053.0 | 5.0 | 1060.3 | 14 |  |
| FLAML | 2 | 11.2101 | 1042.0 | 0.6 | 1044.9 | 17 |  |
| FLAML | 3 | 11.1305 | 1051.1 | 2.5 | 1055.9 | 16 |  |
| FLAML | 4 | 11.1585 | 927.7 | 0.5 | 930.6 | 14 |  |
| FLAML | Mittelwert | 11.12258 | 1002.12 | 1.82 | 1007.04 | 14.8 |  |
| H2OAutoML | 0 | 11.3142 | 901.8 | 2.1 | 913.9 | 185 |  |
| H2OAutoML | 1 | 11.212 | 901.7 | 2.3 | 912.8 | 192 |  |
| H2OAutoML | 2 | 11.3141 | 902.0 | 2.1 | 913.0 | 174 |  |
| H2OAutoML | 3 | 11.1966 | 902.4 | 1.9 | 913.1 | 173 |  |
| H2OAutoML | 4 | 11.3157 | 902.4 | 2.3 | 913.4 | 184 |  |
| H2OAutoML | Mittelwert | 11.27052 | 902.06 | 2.14 | 913.24 | 181.6 |  |

## Gender

Metrik: AUC.

| Framework | Fold | AUC | Trainingsdauer (s) | Vorhersagedauer (s) | Gesamtdauer (s) | Modelle | Ensembles |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| AutoGluon | 0 | 0.928648 | 918.9 | 1.5 | 942.0 | 42 | 14 |
| AutoGluon | 1 | 0.926143 | 921.3 | 1.6 | 940.6 | 42 | 15 |
| AutoGluon | 2 | 0.931737 | 917.2 | 1.0 | 934.6 | 34 | 11 |
| AutoGluon | 3 | 0.92887 | 916.5 | 1.9 | 940.9 | 42 | 15 |
| AutoGluon | 4 | 0.928404 | 930.1 | 1.5 | 953.4 | 42 | 15 |
| AutoGluon | Mittelwert | 0.9287604 | 920.8 | 1.5 | 942.3 | 40.4 | 14 |
| FLAML | 0 | 0.858594 | 916.5 | 0.4 | 919.8 | 17 |  |
| FLAML | 1 | 0.865153 | 1058.6 | 3.8 | 1068.7 | 15 |  |
| FLAML | 2 | 0.857967 | 912.2 | 0.4 | 915.3 | 12 |  |
| FLAML | 3 | 0.861381 | 949.8 | 1.0 | 954.2 | 15 |  |
| FLAML | 4 | 0.863652 | 951.0 | 0.8 | 954.9 | 13 |  |
| FLAML | Mittelwert | 0.8613494 | 957.62 | 1.28 | 962.58 | 14.4 |  |
| H2OAutoML | 0 | 0.808899 | 901.6 | 0.7 | 911.4 | 216 |  |
| H2OAutoML | 1 | 0.816324 | 902.7 | 0.6 | 911.9 | 200 |  |
| H2OAutoML | 2 | 0.80818 | 902.0 | 0.5 | 911.6 | 203 |  |
| H2OAutoML | 3 | 0.808008 | 905.4 | 2.3 | 915.9 | 191 |  |
| H2OAutoML | 4 | 0.818301 | 904.5 | 2.3 | 915.3 | 189 |  |
| H2OAutoML | Mittelwert | 0.8119424 | 903.24 | 1.28 | 913.22 | 199.8 |  |

## Mortality

Metrik: AUC.

| Framework | Fold | AUC | Trainingsdauer (s) | Vorhersagedauer (s) | Gesamtdauer (s) | Modelle | Ensembles |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| AutoGluon | 0 | 0.951557 | 925.1 | 1.3 | 947.7 | 42 | 13 |
| AutoGluon | 1 | 0.947061 | 920.5 | 1.3 | 939.5 | 42 | 14 |
| AutoGluon | 2 | 0.947826 | 906.8 | 1.2 | 924.0 | 40 | 13 |
| AutoGluon | 3 | 0.946644 | 910.4 | 0.7 | 927.1 | 34 | 9 |
| AutoGluon | 4 | 0.948941 | 918.2 | 1.2 | 937.0 | 42 | 14 |
| AutoGluon | Mittelwert | 0.9484058 | 916.2 | 1.14 | 935.06 | 40 | 12.6 |
| FLAML | 0 | 0.921255 | 1029.9 | 4.1 | 1044.5 | 12 |  |
| FLAML | 1 | 0.918207 | 910.2 | 0.3 | 913.2 | 13 |  |
| FLAML | 2 | 0.916674 | 925.2 | 0.6 | 928.8 | 11 |  |
| FLAML | 3 | 0.920424 | 943.5 | 0.9 | 947.8 | 12 |  |
| FLAML | 4 | 0.91381 | 941.8 | 0.7 | 949.5 | 14 |  |
| FLAML | Mittelwert | 0.918074 | 950.12 | 1.32 | 956.76 | 12.4 |  |
| H2OAutoML | 0 | 0.854413 | 904.2 | 0.4 | 913.7 | 188 |  |
| H2OAutoML | 1 | 0.849823 | 902.9 | 2.3 | 913.5 | 165 |  |
| H2OAutoML | 2 | 0.855532 | 902.2 | 0.5 | 911.3 | 216 |  |
| H2OAutoML | 3 | 0.854822 | 905.5 | 0.7 | 914.5 | 185 |  |
| H2OAutoML | 4 | 0.849391 | 902.3 | 0.4 | 910.7 | 204 |  |
| H2OAutoML | Mittelwert | 0.8527962 | 903.42 | 0.86 | 912.74 | 191.6 |  |

## Length of Stay

Metrik: RMSE.

| Framework | Fold | RMSE | Trainingsdauer (s) | Vorhersagedauer (s) | Gesamtdauer (s) | Modelle | Ensembles |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| AutoGluon | 0 | 7.35059 | 904.9 | 0.8 | 926.4 | 32 | 9 |
| AutoGluon | 1 | 7.09641 | 912.3 | 1.0 | 934.9 | 34 | 12 |
| AutoGluon | 2 | 7.28276 | 913.0 | 1.0 | 935.2 | 34 | 11 |
| AutoGluon | 3 | 8.59517 | 933.0 | 0.5 | 951.9 | 16 | 5 |
| AutoGluon | 4 | 7.34305 | 917.8 | 1.0 | 939.7 | 34 | 10 |
| AutoGluon | Mittelwert | 7.533596 | 916.2 | 0.86 | 937.62 | 30 | 9.4 |
| FLAML | 0 | 7.60155 | 983.6 | 1.1 | 990.4 | 16 |  |
| FLAML | 1 | 7.35299 | 962.4 | 0.3 | 965.0 | 12 |  |
| FLAML | 2 | 7.86183 | 905.9 | 0.2 | 911.8 | 14 |  |
| FLAML | 3 | 9.30955 | 903.9 | 0.2 | 909.8 | 15 |  |
| FLAML | 4 | 8.01578 | 910.7 | 0.2 | 916.5 | 15 |  |
| FLAML | Mittelwert | 8.02834 | 933.3 | 0.4 | 938.7 | 14.4 |  |
| H2OAutoML | 0 | 8.22917 | 902.2 | 0.2 | 916.5 | 180 |  |
| H2OAutoML | 1 | 7.80726 | 902.1 | 0.4 | 911.8 | 189 |  |
| H2OAutoML | 2 | 8.31155 | 902.8 | 0.2 | 911.6 | 178 |  |
| H2OAutoML | 3 | 9.47465 | 901.6 | 0.7 | 911.3 | 164 |  |
| H2OAutoML | 4 | 8.25368 | 902.6 | 0.4 | 911.9 | 163 |  |
| H2OAutoML | Mittelwert | 8.415262 | 902.26 | 0.38 | 912.62 | 174.8 |  |
