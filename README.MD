# Experimente

Dieses Verzeichnis enthält den für die Arbeit angepassten Fork von
[AutoML Benchmark](https://github.com/openml/automlbenchmark). Die Experimente
können lokal oder in Docker ausgeführt werden.

## Ausführung

Die folgenden Schritte werden aus diesem Verzeichnis ausgeführt.

1. Virtuelles Environment erstellen:

   ```text
   uv venv --seed
   ```

2. Virtuelles Environment aktivieren:

   ```text
   Linux/macOS: source .venv/bin/activate
   Windows:     .venv\Scripts\Activate.ps1
   ```

3. Abhängigkeiten installieren und Experimente ausführen:

   ```text
   uv pip install -r requirements.txt
   ```

   Die vorbereitete Datenbank wird relativ zum Workspace-Root unter
   `exp/char_data.db` abgelegt. Das Skript `exp_create_csvs.py` greift von
   dort auf die Datenbank zu und erzeugt die Trainings- und Testdateien unter
   `exp/csvs`:

   ```text
   python exp_create_csvs.py
   ```

   Das Skript fragt die gewünschte Zielgröße ab und erzeugt dafür fünf
   stratifizierte beziehungsweise zufällige 80/20-Splits. Anschließend wird
   das Training gestartet:

   ```text
   python exp_run.py
   ```

   Das interaktive Skript fragt Framework, Zeitlimit, Zielgröße, Fold,
   Ausführungsmodus und Setup-Verhalten ab. Mit `all` können mehrere
   Frameworks, Zeitlimits, Zielgrößen oder Folds nacheinander ausgeführt
   werden. Bei der Setup-Option `force` wird das Docker-Image neu gebaut;
   mit `auto` wird ein vorhandenes Image verwendet, sofern es verfügbar ist.

   Für eine lokale Ausführung wird als Modus `local` gewählt. Für die
   Docker-Ausführung wird `docker` gewählt; dafür muss ein Docker-Daemon
   laufen. Die Ergebnisse werden im Ordner `exp/results` abgelegt.
