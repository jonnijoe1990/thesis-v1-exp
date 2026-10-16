# AutoML-Benchmark: Nutzung und Anpassungen

Vergleichsbasis für diesen Text ist der letzte Commit von `openml/automlbenchmark` auf `master` gegen den letzten Commit dieses Forks.

| | Commit | Datum | Nachricht |
| --- | --- | --- | --- |
| Upstream | `dfe8d218` | 19. April 2025 | `[pre-commit.ci] pre-commit autoupdate (#707)` |
| Fork | `ccb1064` | 16. Oktober 2026 | `Update exp_run.py` |

`dfe8d218` ist gleichzeitig der Merge-Base. Der Fork liegt 185 Commits darüber. Netto sind 408 Dateien geändert, mit etwa 1 200 eingefügten und 48 600 gelöschten Zeilen. Der Text beschreibt diesen Endstand, nicht jeden zwischenzeitlich wieder zurückgenommenen Versuch. Ein Zwischenstand wird nur dann genannt, wenn er den heutigen Code erklärt.

`exp_test.py` und `exp_misc.py` sind lokale Testskripte und werden hier nicht weiter beschrieben.

---

## 1. Wie das Werkzeug benutzt wird

Ein Lauf besteht aus drei Namen und ein paar Optionen:

```text
python run.py <framework> <benchmark> <constraint> [optionen]
```

Beispiel aus `exp_run.py`, das dieselben Argumente ohne Kommandozeile an `run()` übergibt:

```python
args = [
    f,                 # Framework, z. B. "AutoGluon"
    "sap-24g",         # Benchmark-Datei resources/benchmarks/sap-24g.yaml
    c,                 # Constraint, z. B. "15m-12c"
    "-i", str(Path(__file__).parent / "csvs"),
    "-m", mode,        # "local" oder "docker"
    "-s", s_arg,       # "auto", "skip", "force" oder "only"
]
if task != "all":
    args += ["-t", t]          # nur eine Zielgröße
if fold != "all":
    args += ["-f", str(fold)]  # nur ein Fold
run(args)
```

Die drei Namen werden in YAML-Dateien aufgelöst. `run.py` lädt zuerst `resources/config.yaml`, danach eine optionale Nutzer-Config, und legt die Kommandozeilenwerte darüber. Danach entsteht entweder ein lokaler `Benchmark` oder ein `DockerBenchmark`.

Wichtige Optionen:

- `-m local|docker`: wo der Lauf stattfindet. AWS und Singularity gibt es in diesem Fork nicht mehr.
- `-t`: ein oder mehrere Task-Namen aus der Benchmark-Datei. Ohne `-t` laufen alle Tasks.
- `-f`: einzelne Folds. Ohne `-f` laufen so viele Folds, wie der Constraint angibt.
- `-i`: Verzeichnis der Datendateien. `{input}` in den Benchmark-Dateien wird durch dieses Verzeichnis ersetzt.
- `-s`: `auto` installiert ein Framework nur, wenn die in `frameworks.yaml` genannte Version noch nicht im Marker `frameworks/<name>/.setup/installed` steht. `force` installiert immer. `only` installiert und startet keinen Lauf. `skip` überspringt die Installation. Im Docker-Modus baut oder sucht `-s` das Image. Der Container selbst startet danach immer mit `-s skip`.
- `-Xschlüssel=wert`: überschreibt einen Eintrag der Config, zum Beispiel `-Xseed=1`.

Im Docker-Modus werden die CSVs nicht ins Image kopiert. Der Host-Ordner aus `-i` wird nach `/input` gemountet, die Ergebnisse nach `/output`:

```python
cmd = (
    "docker run --name {name} {options} {run_as} "
    "-v '{input}':/input -v '{output}':/output -v '{custom}':/custom "
    "--rm {image} {params} -i /input -o /output -u /custom -s skip -Xrun_mode=docker {extra_params}"
)
```

Das Image enthält den Repository-Stand vom Bauzeitpunkt. Eine Änderung an `frameworks/AutoGluon/exec.py` gilt im Container erst nach einem Neubau mit `-s force`.

### 1.1 `resources/frameworks.yaml`

Die Datei benennt die AutoML-Systeme, die der erste Parameter auswählen kann. Ein Eintrag braucht mindestens einen Namen. Üblich sind dazu Version, Beschreibung, Projekt-URL und Parameter, die das Framework beim Training bekommt.

Im Fork sind drei Einträge übrig. AutoGluon bekommt das Preset fest mit:

```yaml
AutoGluon:
  version: stable
  project: https://auto.gluon.ai
  params:
    presets: medium_quality

flaml:
  version: stable

H2OAutoML:
  version: stable
```

`version: stable` ist kein Pin auf eine Zahl. Das Setup-Skript des Frameworks löst `stable` zur Installationszeit auf die dann aktuelle stabile Veröffentlichung auf. Das Docker-Image heißt daraus `automlbenchmark/<name>:stable`, also `automlbenchmark/autogluon:stable`, `automlbenchmark/flaml:stable` und `automlbenchmark/h2oautoml:stable`.

`params` landen beim Framework. Bei AutoGluon wird `presets` an `TabularPredictor.fit` gegeben. Upstream definiert zusätzlich eigene Einträge `AutoGluon_bestquality`, `AutoGluon_hq` und `AutoGluon_gq` über `extends`. Die sind hier entfernt. Es bleibt ein Eintrag. Sein Preset wird zwischen den Versuchen gewechselt, passend zur Trainingszeit:

| Versuch | Preset |
| --- | --- |
| 5 Minuten | `medium_quality` |
| 15 Minuten | `good_quality` |
| 30 Minuten | `high_quality_v150` |

`medium_quality` trainiert ohne Bagging und ohne anschließendes `refit_full`. `good_quality` und `high_quality_v150` tun beides. Die YAML-Datei zeigt immer nur den zuletzt eingetragenen Wert. Zum Zeitpunkt dieses Texts ist das `medium_quality`.

Der Modulpfad ist standardmäßig `frameworks.<Name>`. Dort liegen `__init__.py` (Aufruf aus dem Benchmark-Prozess), `exec.py` (Training in der eigenen virtuellen Umgebung) und `setup.sh`.

### 1.2 `resources/constraints.yaml`

Ein Constraint begrenzt einen Lauf, unabhängig davon, welcher Datensatz trainiert wird. Die Felder, die wir setzen, sind:

- `folds`: wie viele der vorbereiteten Splits ausgeführt werden. `1` bedeutet nur Fold 0, auch wenn die Benchmark-Datei fünf Dateien nennt.
- `cores`: Prozessorkerne für den Task. `-1` heißt alle sichtbaren Kerne.
- `max_runtime_seconds`: Trainingszeit, die an das Framework weitergegeben wird.

Die Datei ersetzt die Upstream-Staffel `1h4c`, `1h8c`, `4h8c`, `8h8c` und die AWS-Varianten mit `ec2_volume_type: gp3`. Stattdessen gibt es kurze Zeiten und die Kernzahlen dieser Maschine. `test` mit 10 Minuten und 4 Kernen ist der ursprüngliche Smoke-Test und bleibt erhalten.

Auszug der tatsächlich benutzten Gruppe:

```yaml
5m-12c:
  folds: 5
  cores: 12
  max_runtime_seconds: 300

15m-12c:
  folds: 5
  cores: 12
  max_runtime_seconds: 900

30m-12c:
  folds: 5
  cores: 12
  max_runtime_seconds: 1800

60m-12c:
  folds: 5
  cores: 12
  max_runtime_seconds: 3600
```

Dieselbe Staffel existiert noch einmal mit `cores: 8` und mit `cores: -1`, jeweils auch als Ein-Fold-Variante (`5m-12c-1f`, `5m-8c-1f`, `5m-1f`). `exp_run.py` bietet nur die 12-Kern-Varianten von 5, 15, 30 und 60 Minuten an.

`min_vol_size_mb` und `ec2_volume_type` setzt keiner unserer Constraints. Die Plattenprüfung entfällt damit, weil der Config-Default `min_vol_size_mb: -1` die Prüfung überspringt.

### 1.3 Benchmarks

Ein Benchmark ist eine YAML-Datei unter `resources/benchmarks/`. Der zweite Parameter ist der Dateiname ohne `.yaml`, ein Pfad zu einer eigenen Datei, oder weiterhin eine OpenML-Referenz `openml/s/<id>` bzw. `openml/t/<id>`. Der OpenML-Code ist in diesem Fork noch vorhanden. Die großen Upstream-Suiten `small`, `medium`, `large`, `validation` und `timeseries` sind gelöscht, weil die Arbeit sie nicht ausführt.

Jede Aufgabe in der Datei hat einen eindeutigen Namen, eine Beschreibung der Dateien, den Namen der Zielspalte, den Aufgabentyp und die Metrik. Unsere vier Aufgaben stehen in `sap.yaml`. Die Varianten `sap-8g.yaml`, `sap-16g.yaml` und `sap-24g.yaml` enthalten dieselben Aufgaben und setzen über einen Eintrag `__defaults__` nur das Speicherlimit:

```yaml
- name: __defaults__
  max_mem_size_mb: 24000
```

`sap.yaml` setzt kein Speicherlimit. Dann gilt der Config-Default `-1`, also der frei verfügbare Speicher abzüglich `os_mem_size_mb` (2048 MB). `exp_run.py` verwendet `sap-24g`. Das Limit wird vor dem Lauf gegen den sichtbaren Speicher geprüft. Es wird nicht als `--memory` an Docker und nicht als Trainingslimit an AutoGluon weitergegeben. Liegt es über dem verfügbaren Speicher und ist `on_unfulfilled_constraint` auf `fail` gestellt, bricht der Lauf ab.

Eine Aufgabe sieht so aus:

```yaml
- name: gender
  dataset:
    train:
      - '{input}/gender_train_0.csv'
      - '{input}/gender_train_1.csv'
      - '{input}/gender_train_2.csv'
      - '{input}/gender_train_3.csv'
      - '{input}/gender_train_4.csv'
    test:
      - '{input}/gender_test_0.csv'
      - '{input}/gender_test_1.csv'
      - '{input}/gender_test_2.csv'
      - '{input}/gender_test_3.csv'
      - '{input}/gender_test_4.csv'
    target: label
    type: binary
  metric:
    - auc
```

Dieselbe Form haben `mortality` (binär, AUC), `age` (Regression, RMSE) und `length_of_stay` (Regression, RMSE). Fold `i` ist das Paar an Position `i` in den beiden Listen. Die Zahl der Listeneinträge und `folds` im Constraint müssen zusammenpassen: fünf Dateien und `folds: 5` ergeben die Folds 0 bis 4.

`{input}` wird durch das Verzeichnis aus `-i` ersetzt. Im Container ist das `/input`.

Die Metrik in der Aufgabe ist die, die das Framework optimiert und die in `results.csv` als Hauptwert steht. Weitere Metriken kann die Config pro Aufgabentyp nachrechnen. Für binäre Aufgaben sind das in `config.yaml` zusätzlich Log-Loss, Accuracy und Balanced Accuracy. Für Regression zusätzlich R² und MAE.

### 1.4 `resources/config.yaml`

Die Config ist die Schicht unter Framework, Benchmark und Constraint. Sie sagt dem Programm, wo Definitionen liegen, welche Defaults gelten, wenn ein Constraint ein Feld auslässt, und wie Docker und die Ergebnisdatei sich verhalten.

Für diese Arbeit relevante Stellen:

- `frameworks.definition_file` zeigt auf `resources/frameworks.yaml`. `tags` ist auf `stable` und `latest` gekürzt. Die Jahresstände `2020Q2`, `2021Q3` und `2023Q2` und ihre YAML-Dateien sind weg.
- `benchmarks.definition_dir` ist `resources/benchmarks`. `constraints_file` ist `resources/constraints.yaml`.
- `benchmarks.defaults` füllt fehlende Constraint-Felder. `folds` bleibt 10, `cores` und `max_mem_size_mb` bleiben `-1`. Die Trainingszeit setzen die Constraints selbst.
- `on_unfulfilled_constraint: fail`. Reichen Kerne oder Speicher nicht, stoppt der Lauf. Upstream steht auf `auto`: im lokalen Modus nur eine Warnung, in anderen Modi ein Abbruch bei Kern- oder Speicherproblemen.
- `versions.python: 3.11`. Diese Version benutzt Docker für den Benchmark-Prozess und für die virtuellen Umgebungen der Frameworks. Der lokale Treiber steht in `pyproject.toml` noch auf Python 3.10. Die beiden Stände werden angeglichen, entweder der Treiber auf 3.11 oder die Container auf 3.10.
- `docker.run_extra_options` ist weiterhin nur `--shm-size=2048M`. Zusätzliche Flags für CPU-Satz, Speicher und Thread-Umgebungsvariablen waren zwischendurch eingetragen und sind mit Commit `74d25dd` wieder entfernt.
- `openml.apikey` und der OpenML-Loader sind noch da. Die SAP-Dateien benutzen sie nicht.

`project_repository`, `container.force_branch`, `container.ignore_labels` und der gesamte Block `aws` und `singularity` sind entfernt.

### 1.5 Erwartetes Datenformat

Das Werkzeug liest pro Split eine Trainingsdatei und eine Testdatei. Unterstützt sind CSV und ARFF, dazu Parquet als abgeleitetes Format. Eine Zeitreihe wäre eine einzelne CSV im Long Format. Die benutzen wir nicht.

Für einen Ordner oder ein Archiv gilt die Namensregel aus `amlb/datasets/file.py`:

```text
{name}_train.csv und {name}_test.csv
{name}_train_0.csv, {name}_test_0.csv, {name}_train_1.csv, {name}_test_1.csv, ...
```

Die Folds beginnen bei 0. Train und Test eines Folds müssen beide existieren. Unsere Benchmark-Dateien zählen die Pfade stattdessen explizit auf. Dann entscheidet die Listenposition, nicht der Dateiname. Die Dateien folgen der Namensregel trotzdem: `gender_train_0.csv` bis `gender_test_4.csv`, analog für `mortality`, `age` und `length_of_stay`.

Eine CSV braucht eine Kopfzeile. Dieselbe Spalte ist in Train und Test die Zielspalte. Bei uns heißt sie `label` und steht in der Benchmark-Datei unter `dataset.target`. Fehlt diese Angabe, sucht das Werkzeug eine Spalte `target` oder `class` und nimmt sonst die letzte Spalte. Weitere Spalten sind Merkmale. Eine eigene Label-Datei oder eine Indexspalte erwartet das Werkzeug nicht. `read_csv` liest die Kopfzeile als Spaltennamen und die folgenden Zeilen als Beobachtungen.

`exp_create_csvs.py` erzeugt genau diese Dateien aus `char_data.db`. Es legt fünf Folds an, jeweils 80 Prozent Training und 20 Prozent Test. Der `random_state` des Splits ist der Fold-Index und hat nichts mit dem AMLB-Seed `-Xseed` zu tun. Klassifikation wird stratifiziert, Regression nicht. DuckDB schreibt die CSV mit Kopfzeile. Die Zielspalte und die Merkmale stammen aus demselben Join über die Patienten-`id`, die `id` bleibt als Spalte in der Datei:

```python
train_ids, test_ids = train_test_split(
    labels[["id"]],
    test_size=0.2,
    random_state=i,
    stratify=labels["label"] if label.problem_type == "classification" else None
)
# ...
COPY (
    SELECT fm.*
    FROM {split_table_name} AS included
    JOIN {feature_matrix_table_name} AS fm
        ON included.id = fm.id
) TO '{csv_pfad}' (FORMAT CSV, HEADER)
```

Die vier Zielgrößen und die Spalten, die dabei aus der Feature-Matrix fallen, stehen in `exp_labels.py`:

| Aufgabe | Typ | Label | Ausgeschlossene Spalten |
| --- | --- | --- | --- |
| `gender` | Klassifikation | `c_gender`, ohne den Wert `Divers` | `base__c_gender` |
| `mortality` | Klassifikation | `c_datetimeofdeath IS NOT NULL` | `base__c_entlassungsart` |
| `age` | Regression | `c_age` | `base__c_age`, `base__c_birthdate` |
| `length_of_stay` | Regression | Tage zwischen Aufnahme und Entlassung | `base__aufenthaltsdauer_tage` und die Stunden-Spalten der Bewegungen |

Die ausgeschlossenen Spalten sind die Zielgröße selbst oder eine direkte Abbildung davon. Sonst läge die Antwort schon in den Merkmalen.

AutoGluon bekommt nicht die CSV, sondern eine Parquet-Datei daneben. `frameworks/AutoGluon/__init__.py` verlangt sie ausdrücklich:

```python
data = dict(
    train=dict(path=dataset.train.data_path("parquet")),
    test=dict(path=dataset.test.data_path("parquet")),
    target=dict(name=dataset.target.name, classes=dataset.target.values),
    problem_type=dataset.type.name,
)
```

`data_path("parquet")` schreibt die Sidecar nur, wenn sie noch fehlt. String- und Objektspalten sowie das Klassifikationsziel werden dabei zu pandas-Kategorien. H2O und FLAML lesen die CSV. H2O bekommt den CSV-Pfad, FLAML die schon geladenen Merkmale und Labels.

---

## 2. Änderungen gegenüber dem Upstream

### 2.1 Projekt abgespeckt

Was der Versuch nicht ausführt, ist entfernt, statt es auf die neueren Abhängigkeiten anzupassen.

Gelöschte Frameworks, jeweils mit Modul, Setup und Eintrag in `frameworks.yaml`:

`autosklearn`, `AutoWEKA`, `constantpredictor`, `DecisionTree`, `FEDOT`, `GAMA`, `hyperoptsklearn`, `lightautoml`, `mljarsupervised`, `MLNet`, `MLPlan`, `mlr3automl`, `NaiveAutoML`, `oboe`, `RandomForest`, `ranger`, `SapientML`, `TPOT`, `TunedRandomForest`.

Übrig sind `AutoGluon`, `flaml` und `H2OAutoML`.

Ebenfalls entfernt, weil der Versuch sie nicht braucht:

- die Dokumentation unter `docs/`, die Website und `mkdocs.yml`
- die Unit-Tests unter `tests/` und `pytest.ini`
- die Ergebnisberichte unter `reports/`, `amlb_report/` und `requirements-report.txt`
- die Beispiele unter `examples/`
- die GitHub-Workflows unter `.github/`
- die Hilfsskripte `runall.py`, `runstable.sh`, `upload_results.py`, `concat_csv.py`, `recover_results.py` und `scripts/`
- die historischen Framework-Definitionen `frameworks_2020Q2.yaml`, `frameworks_2021Q3.yaml`, `frameworks_2023Q2.yaml`, `frameworks_latest.yaml` und `frameworks_stable.yaml`
- die Benchmark-Suiten `small.yaml`, `medium.yaml`, `large.yaml`, `validation.yaml`, `timeseries.yaml` und `example.yaml`
- AWS (`amlb/runners/aws.py`, `aws_monitor.ipynb`, der `aws`-Block in der Config) und Singularity (`amlb/runners/singularity.py`, `Singularityfile`-Ignore, `singularity_commands` in `frameworks/H2OAutoML/__init__.py`)
- `TaskConstraint.ec2_volume_type` und die automatische Wahl von `ec2_instance_type` in `amlb/resources.py`

`amlb/__init__.py` exportiert danach nur noch den lokalen Benchmark und Docker:

```python
from .runners import DockerBenchmark

__all__ = [
    "Resources",
    "Benchmark",
    "DockerBenchmark",
    "SetupMode",
    "TaskResult",
    "__version__",
]
```

`parse.py` akzeptiert bei `-m` nur `local` und `docker`.

### 2.2 Python 3.10 im Treiber, Python 3.11 in den Images

Upstream setzt `versions.python: 3.9`. AutoGluon 1.6 (die `stable`-Auflösung zum Zeitpunkt der Läufe, veröffentlicht als 1.6.3) verlangt Python `>=3.10` und `<3.14`. FLAML 2.7.0 verlangt ebenfalls Python `>=3.10`. Damit ist 3.9 keine lauffähige Basis mehr für die beiden Frameworks, die der Versuch neben H2O benutzt.

Der Treiber pinnt die Minor-Version in `pyproject.toml`, damit `uv venv --seed` die Umgebung mit Python 3.10 anlegt:

```toml
[project]
name = "exp"
version = "0.1.0"
requires-python = ">=3.10, <3.11"
```

In der Datei stehen keine Abhängigkeiten. Installiert wird weiterhin mit pip aus `requirements.in` und `requirements.txt`. Ruff steht in derselben Datei noch auf `target-version = "py39"`. Das betrifft nur den Linter.

Die Images und die virtuellen Umgebungen der Frameworks lesen `versions.python` aus `config.yaml`. Der Weg dort war 3.9, dann 3.10 (`5304757`), dann 3.12 (`1800052`), dann 3.11 (`5b05ce6`). Der Endstand ist:

```yaml
versions:
  python: 3.11
```

Ein lokaler Lauf startet mit dem 3.10-Interpreter des Treibers. Der legt die Framework-Umgebungen mit der Version aus der Config an, also mit 3.11. Dieser Unterschied ist vorläufig. Entweder wird `requires-python` auf 3.11 angehoben oder `versions.python` auf 3.10 gesenkt, damit Treiber und Container dieselbe Minor-Version benutzen. Der gemeinsame Framework-Lock `frameworks/shared/requirements.txt` ist mit Python 3.11 erzeugt (`pyarrow==18.1.0`, `psutil==5.8.0`). Der Kopf von `requirements.txt` im Projektroot nennt noch `uv pip compile --python 3.9`, obwohl die Pins darunter bereits NumPy 2 und pandas 2.2 sind. Die Datei wurde nach dem Sprachversionswechsel nicht neu kompiliert.

### 2.3 Abhängigkeiten des Treibers

`requirements.in` hebt die Bibliotheken an, die mit den neueren Frameworks und mit NumPy 2 zusammenpassen, und ergänzt die zwei Pakete für den CSV-Export und die Auswahlmenüs:

```text
minio>=7.2.3,<7.2.19
numpy>=2.0.2,<2.1
pandas>=2.2.2,<2.3
openml==0.15.1
scikit-learn>=1.5,<1.6
scipy>=1.13.1,<1.14
pyarrow>=16,<19

duckdb>=1.4.5
questionary>=2.1.1
```

Upstream hatte `numpy>=1.24,<2.0`, `pandas>=1.5,<2.0`, `openml==0.13.1`, `scikit-learn>=1.0,<2.0` und `pyarrow>=11.0`. Die aufgelösten Stände im Lock sind unter anderem `numpy==2.0.2`, `pandas==2.2.3`, `pyarrow==18.1.0`, `scikit-learn==1.5.2`, `scipy==1.13.1`, `openml==0.15.1`, `duckdb==1.4.5` und `questionary==2.1.1`.

`minio` ist auf `>=7.2.3,<7.2.19` begrenzt, weil OpenML 0.15.1 `ProgressType` aus diesem MinIO-Stand importiert und 7.2.19 dabei ausschließt. OpenML selbst wird von den SAP-Läufen nicht aufgerufen. Der Import bleibt, weil `run.py` `openml` weiterhin lädt, sobald ein Lauf startet.

DuckDB liest `char_data.db` und schreibt die CSVs. Questionary stellt die Auswahl in `exp_run.py` und `exp_create_csvs.py` dar. Die kleine Klasse in `exp_db.py` öffnet die Verbindung:

```python
class DB:
    def __init__(self, path: str):
        self.con = duckdb.connect(path)

    def __enter__(self):
        return self.con

    def __exit__(self, exc_type, exc_value, traceback):
        self.con.close()
```

### 2.4 Umbenannte NumPy-, pandas- und scikit-learn-Funktionen

Der Versionswechsel in Abschnitt 2.3 entfernt Aufrufe, die der Upstream-Code noch benutzt. Die betroffenen Stellen sind umbenannt. Das Verhalten bleibt dasselbe. Ohne die Umbenennung startet der Lauf mit den neuen Pins nicht, oder er scheitert nach dem Training beim Schreiben der Ergebnisse.

NumPy 2 hat den Alias `np.NaN` entfernt. In `amlb/datautils.py` steht an seiner Stelle `np.nan`. Das betrifft die Wiederherstellung fehlender Werte in `Encoder.transform` und den Default von `missing_values` in `impute_array`, `impute_dataframe` und `_impute_pd`:

```python
# upstream
res[mask] = np.NaN if self.encoded_type is float else None

def impute_array(..., missing_values: Any = np.NaN, ...):
def impute_dataframe(..., missing_values: Any = np.NaN, ...):
def _impute_pd(..., missing_values: Any = np.NaN, ...):

# fork
res[mask] = np.nan if self.encoded_type is float else None

def impute_array(..., missing_values: Any = np.nan, ...):
def impute_dataframe(..., missing_values: Any = np.nan, ...):
def _impute_pd(..., missing_values: Any = np.nan, ...):
```

pandas 2 hat `DataFrame.append` entfernt. Beide Stellen, die eine neue Ergebniszeile an die Score-Datei hängen, stehen in `amlb/results.py`. `Scoreboard.save_df` hängt an, wenn das CSV-Format sich geändert hat. `Scoreboard.append` baut das Scoreboard für den nächsten Schreibvorgang. Beide rufen jetzt `pd.concat` auf:

```python
# upstream
df = read_csv(path).append(data_frame)
scores = self.as_data_frame().append(to_append)

# fork
df = pd.concat([read_csv(path), data_frame])
scores = pd.concat([self.as_data_frame(), to_append])
```

Ohne diese Änderung ist die Bewertung schon berechnet, die Zeile lässt sich aber nicht mehr an `results.csv` anfügen.

pandas 2.2 legt String-Spalten zusammen mit PyArrow 18 in einem Arrow-Array ab. `Series.values` liefert dann dieses Array und kein NumPy-Array. Die Serialisierung der Vorhersagen erwartet ein Array, das sich als JSON schreiben lässt. In `frameworks/H2OAutoML/exec.py` holt `extract_preds` Vorhersage, Wahrscheinlichkeiten und Wahrheit deshalb mit `Series.to_numpy()`:

```python
# upstream
predictions = y_pred.values
probabilities = preds.iloc[:, 1:].values
truth = y_truth.values

# fork
predictions = y_pred.to_numpy()
probabilities = preds.iloc[:, 1:].to_numpy()
truth = y_truth.to_numpy()
```

Der vollständige Zusammenhang mit dem H2O-Lauf steht in Abschnitt 2.9. Dieselbe Umstellung auf `to_numpy()` benutzt der AutoGluon-Adapter für die Klassenlabels aus `predict_from_proba` und für die zurückgegebene Wahrheit. Dort ist sie Teil des Hotfixes aus Abschnitt 2.10 und war im Upstream für die Vorhersage schon vorhanden. Neu gegenüber Upstream ist dort nur `truth`.

scikit-learn 1.4 hat das Argument `sparse` von `OneHotEncoder` entfernt. Es heißt seit 1.2 `sparse_output`. Der Merkmals-Encoder in `Encoder.__init__` ist angepasst:

```python
# upstream
OneHotEncoder(sparse=False, handle_unknown="ignore")

# fork
OneHotEncoder(sparse_output=False, handle_unknown="ignore")
```

### 2.5 PyArrow in den Framework-Umgebungen

`frameworks/shared/requirements.in` wird in jede Framework-Umgebung installiert, bevor die Pakete des Frameworks kommen. Upstream verlangt `pyarrow>=4.0`. Der alte Lock stand auf PyArrow 11, gebaut für NumPy 1. Unter NumPy 2 bricht der Import mit `AttributeError: _ARRAY_API not found` ab.

Der erste PyArrow-Stand mit NumPy-2-Wheels ist 17. Die Obergrenze bleibt unter 19, passend zum Treiber-Lock:

```text
# 17 is the first release built for NumPy 2. Stay below 19, matching the benchmark lock.
pyarrow>=17,<19
```

Aufgelöst ist `pyarrow==18.1.0`. AutoGluon installiert danach sein eigenes PyArrow (bei 1.6 die Reihe 23) und ersetzt diese Version in seiner eigenen Umgebung. FLAML und H2O behalten 18.

Mit pandas 2.2 und PyArrow 18 liegen String-Spalten in einem Arrow-Array. `Series.values` liefert dann dieses Array und kein NumPy-Array. Das ist der Grund für die H2O-Änderung in Abschnitt 2.9.

### 2.6 `pyproject.toml` nur für die Python-Version

Siehe Abschnitt 2.2. Die Datei existed upstream bereits für Ruff und Mypy. Der Block `[project]` ist neu und enthält nur Name, Version und `requires-python`. Ein `uv lock` oder eine Installation über das Projektfile gibt es nicht. Ein früherer Versuch, die Abhängigkeiten nach uv zu ziehen, ist zurückgenommen (`418ab37`, `f7641c4`).

### 2.7 `runbenchmark.py` wird `run.py`, der Parser liegt in `parse.py`

Upstream sammelt die Argumente und startet den Lauf in einer Datei, `runbenchmark.py`. Die Datei ist gelöscht. `parse.py` enthält nur den `ArgumentParser`. `run.py` importiert ihn und bietet `run(arguments)` an. Ohne Argumente liest `parse_args` die Kommandozeile. Mit einer Liste, wie `exp_run.py` sie baut, läuft derselbe Code außerhalb eines CLI-Aufrufs:

```python
def run(arguments: Optional[Iterable[str]] = None):
    args = parser.parse_args(arguments)
    # Config laden, Benchmark oder DockerBenchmark erzeugen, setup, run
    return exit_code

if __name__ == "__main__":
    sys.exit(run())
```

`README.MD` verweist noch auf `run_exp.py`. Die Datei heißt `exp_run.py`.

`exp_run.py` fragt Framework, Constraint, Zielgröße, Fold, Modus und Setup-Modus über Questionary ab und ruft `run` für jede Kombination auf. Die angebotenen Werte sind die drei Frameworks, die Constraints `5m-12c`, `15m-12c`, `30m-12c` und `60m-12c`, die vier Zielgrößen, die Folds 0 bis 4, die Modi `docker` und `local`, und die Setup-Modi `force`, `auto` und `only`. Der Benchmark ist fest `sap-24g`, das Input-Verzeichnis fest `csvs/`.

### 2.8 Eigene Benchmark-Dateien

`sap.yaml` und die drei Speicher-Varianten sind neu. Inhalt und der Unterschied nur im `__defaults__`-Speicherlimit stehen in Abschnitt 1.3. `test.yaml` ist bis auf das entfernte Feld `ec2_instance_type: m5.large` unverändert und enthält weiterhin die kleinen OpenML-Aufgaben des Upstream.

`.gitignore` ignoriert `*.db` und `csvs/`, damit die Datenbank und die erzeugten Splits nicht ins Repository wandern. Das Verzeichnis der virtuellen Umgebung heißt dort `.venv/` statt `venv/`. `.dockerignore` ignoriert `*.db` statt `*.sif`. Die Singularity-Images gibt es nicht mehr. Die Datenbank soll nicht in den Image-Kontext.

### 2.9 H2O: Vorhersagen serialisierbar machen

Nach dem Training zieht `extract_preds` Vorhersage, Wahrscheinlichkeiten und Wahrheit aus der H2O-Tabelle in pandas. Upstream übergibt `Series.values`. Unter pandas 2.2 mit PyArrow-Strings ist das für die Label-Spalte ein `ArrowStringArray`. Die Serialisierung in `frameworks/shared/callee.py` kann dieses Array nicht als JSON schreiben. Der Lauf ist dann nach einem erfolgreichen `predict` fehlgeschlagen, die Metrik fehlt.

`.to_numpy()` liefert für Labels, Wahrscheinlichkeiten und Wahrheit ein echtes ndarray. Die vorhergesagten Klassen bleiben dieselben, weil die Werte schon vorher mit `use_pandas=False` aus H2O kamen und nur die pandas-Hülle gewechselt hat:

```python
# pandas 3 keeps strings in a PyArrow array. Series.values then returns
# that array, which the benchmark cannot serialize. to_numpy() gives a
# real ndarray for the labels, the probabilities, and the truth column.
predictions = y_pred.to_numpy()
probabilities = preds.iloc[:, 1:].to_numpy()
prob_labels = h2o_labels = h2o_preds[0][1:]
if all([re.fullmatch(r"p(-?\d)+", p) for p in prob_labels]):
    prob_labels = None
truth = y_truth.to_numpy()
```

Der Kommentar spricht von pandas 3. Der Fehlschlag tritt schon mit pandas 2.2 auf, sobald PyArrow 18 die String-Spalten trägt. pandas 3 macht dasselbe Verhalten zum Default.

H2O typisiert Trainings- und Test-CSV getrennt. Eine seltene numerische Spalte, die im Test nur fehlt, wird dort nicht kategorisch, und die Vorhersage bricht ab. Das ist im Framework-Code nicht geändert. Solche Spalten fallen vor dem Export aus der Feature-Matrix, nicht in `exec.py`.

### 2.10 AutoGluon: Zufällige Scores

Die Scores von AutoGluon für Geschlecht, Sterblichkeit und Alter lagen auf dem Niveau einer Zufallsvorhersage, obwohl das Training intern hohe Validierungsmetriken gezeigt hat. Mehr Trainingszeit hat daran nichts geändert.

Ursache ist die Zuordnung von Vorhersage und Label, nicht das Modell.

Seit 2021 übergibt der tabellarische AutoGluon-Adapter keine Wahrheit an den Elternprozess. `frameworks/shared/caller.py` nimmt dann die Labels aus der Test-CSV, in der Reihenfolge, in der der Benchmark diese CSV geladen hat:

```python
truth=(
    as_vec(res.truth)
    if res.truth is not None
    else dataset.test.y_enc
    if res.target_is_encoded
    else dataset.test.y
),
```

Trainiert und vorhergesagt hat AutoGluon aber auf der Parquet-Sidecar aus Abschnitt 1.5. Eine veraltete Sidecar, etwa `gender_test_0.parquet` neben einer neu geschriebenen CSV, behält die alte Zeilenreihenfolge. Die Vorhersagen sind dann gegen die aktuellen CSV-Labels verrutscht. Die Länge bleibt gleich, es gibt also keinen Fehler. AUC landet bei etwa 0,5, das Regressions-RMSE beim Wert unkorrelierter Vorhersagen.

FLAML und H2O geben die Wahrheit aus derselben Tabelle zurück, auf der sie vorhersagen. Deshalb betrifft der Fehler nur den tabellarischen AutoGluon-Adapter.

Commit `50ff572` hat zwei Dinge gleichzeitig geändert. Der Adapter hat die CSV-Pfade statt `data_path("parquet")` übergeben, und `exec.py` hat die Labels aus genau dieser Testtabelle zurückgegeben. Die Zufallsscores waren damit ausgeschlossen, auch wenn die Parquet-Datei daneben veraltet blieb.

Die rohe CSV hat einen anderen Fehler erzeugt. pandas liest die Zahlen als float64, einschließlich Werte, die nicht in float32 passen. ExtraTrees im AutoGluon-Training bricht dann mit `ValueError` ab, bevor eine Vorhersage existiert. Die typisierte Parquet-Datei vermeidet das, weil der Benchmark String-Spalten vorher zu Kategorien macht und die Zahlen so schreibt, wie die CSV-Leseroutine sie festgelegt hat.

Commit `3f27754` setzt den Pfad deshalb auf Parquet zurück. Die Rückgabe der Wahrheit aus derselben Testtabelle bleibt. Das ist der verbleibende Unterschied zu Upstream in `exec.py`:

```python
test_data = TabularDataset(test_path)
# ...
y_test = test_data[label].to_numpy()
with Timer() as predict:
    predictions, probabilities = infer(test_data)
# ...
return result(
    output_file=config.output_predictions_file,
    predictions=predictions,
    truth=y_test,
    probabilities=probabilities,
    probabilities_labels=prob_labels,
    target_is_encoded=False,
    # ...
)
```

`test_path` ist hier bereits der Parquet-Pfad, den `__init__.py` in den Kindprozess gibt. `caller.py` benutzt `res.truth`, sobald es nicht `None` ist, und fällt nicht mehr auf `dataset.test.y` zurück. Vorhersage und bewertetes Label stammen aus derselben Zeilenreihenfolge.

Eine neu geschriebene CSV braucht eine neu geschriebene Sidecar. `data_path("parquet")` überschreibt eine vorhandene Datei nicht. Liegt neben der aktuellen CSV noch die alte Parquet-Datei, trainiert AutoGluon weiter auf dem alten Stand, die Scores sind dann nur in sich stimmig.

### 2.11 AutoGluon: `high_quality_v150` und die Zeit für `refit_full`

`good_quality` und `high_quality` trainieren gebaggte Modelle und rufen danach `refit_full` auf. Das kann etwa 15 Prozent der Gesamtzeit kosten. Der Adapter kürzt `max_runtime_seconds` deshalb auf 90 Prozent, damit der Refit noch in das Job-Limit passt. Upstream prüft nur die beiden alten Namen.

AutoGluon 1.5 führt `high_quality_v150` ein. Auch dieses Preset setzt `refit_full: True`. Ohne den neuen Namen in der Menge würde ein Lauf mit diesem Preset die vollen 100 Prozent an `fit` geben, und der anschließende Refit liefe in den Abbruch des Jobs.

```python
if (
    preset_with_refit_full := (set(presets) & {"good_quality", "high_quality", "high_quality_v150"})
) and (time_limit is not None):
    preserve = 0.9
    time_limit = preserve * config.max_runtime_seconds
```

`medium_quality`, das Preset der 5-Minuten-Läufe, macht diesen Refit nicht. `good_quality` für 15 Minuten war schon upstream abgedeckt. `high_quality_v150` ist das Preset der 30-Minuten-Läufe und der Name, den die Menge neu enthält.

### 2.12 AutoGluon: CPU-Wheels für PyTorch

Die Linux-Wheels von PyTorch auf PyPI ziehen die CUDA-Bibliotheken `nvidia-*` mit. Die Läufe rechnen auf der CPU. `frameworks/AutoGluon/setup.sh` installiert AutoGluon deshalb mit `--torch-backend=cpu`, für `stable`, für eine numerische Version und für die Installation aus dem Quellbaum:

```bash
# CPU torch: the PyPI Linux wheel pulls in the nvidia-* CUDA libraries.
if [[ "$VERSION" == "stable" ]]; then
    $UV pip install --no-cache-dir -U --torch-backend=cpu "${PKG}"
    $UV pip install --no-cache-dir -U --torch-backend=cpu "${PKG}.tabular[${DEPENDENCIES}]"
```

### 2.13 Docker-Image ohne Branch-Suffix

Upstream hängt an den Image-Tag den Git-Branch oder das Label `dev`. Ein Image heißt dann zum Beispiel `automlbenchmark/autogluon:stable-master` oder `automlbenchmark/autogluon:stable-dev`. Vor dem Bau prüft der Code, ob der Arbeitsbaum sauber ist und zum Branch aus `project_repository` passt, und fragt sonst interaktiv nach.

Beides ist entfernt. `ContainerBenchmark.image_name` bildet den Tag nur noch aus der Framework-Version:

```python
def image_name(cls, framework_def: Framework) -> str:
    """Image name from the framework definition, without a branch or dev suffix."""
    di = framework_def.image
    author = di.author
    image = di.image if di.image else framework_def.name.lower()
    tag = di.tag if di.tag else framework_def.version.lower()
    tag = re.sub(r"([^\w.-])", ".", tag).lstrip(".")
    return f"{author}/{image}:{tag}"
```

`_find_image` und `_build_image` suchen nur noch diesen einen Namen oder ein explizit gesetztes Image. `force_branch`, `ignore_labels`, `project_repository` und `Resources.project_info` sind gelöscht. Vorhandene Images mit `-dev` oder `-master` werden nicht wiedererkannt. Der nächste Docker-Lauf baut unter dem neuen Namen.

Der Branch-Suffix hat denselben Framework-Stand je nach Checkout anders benannt und den Bau an eine Rückfrage gebunden. Für die wiederholten Läufe dieser Arbeit ist der Tag allein die Version aus `frameworks.yaml`.

### 2.14 Was im Endstand nicht mehr drin ist

Diese Versuche sind in der Historie sichtbar und im Diff gegen Upstream nicht mehr enthalten:

- Docker-Flags `--cpuset-cpus=0-11`, `--memory=24g` und die Thread-Variablen `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `MKL_NUM_THREADS`. Eingefügt in `6335405`, entfernt in `74d25dd`. Übrig ist `--shm-size=2048M`, wie upstream.
- Der AutoGluon-Pfad über die rohe CSV. Eingeführt in `50ff572`, zurückgenommen in `3f27754`. Übrig ist die Rückgabe von `truth` aus der Parquet-Testtabelle.
- Ein vollständiger Umzug der Installation auf uv. Zurückgenommen. Übrig ist der `[project]`-Block für `uv venv --seed`. AutoGluon benutzt `uv` weiterhin innerhalb seiner eigenen Umgebung. Das tut upstream auch.
