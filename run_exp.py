from pathlib import Path
from typing import Literal
from questionary import Choice, select
from run import run

frameworks = ["AutoGluon", "Autogluon-sbf-high-v150", "flaml", "H2OAutoML"]
tasks = ["gender", "mortality"]
Framework = Literal["AutoGluon", "Autogluon-sbf-high-v150", "flaml", "H2OAutoML"]
Task = Literal["gender", "mortality"]

def select_framework() -> Framework:
    choices = [Choice(title=framework, value=framework) for framework in frameworks]
    selected = select(
        message="Framework wählen:",
        choices=choices,
        instruction="Pfeiltasten, Enter bestätigt"
    ).ask()
    return selected

def select_constraint() -> str:
    choices = [
        Choice(title="5m-test", value="5m-test"),
        Choice(title="30m", value="30m")
    ]
    selected = select(
        message="Constraint wählen:",
        choices=choices,
        instruction="Pfeiltasten, Enter bestätigt"
    ).ask()
    return selected

def select_task() -> Task:
    choices = [Choice(title=task, value=task) for task in tasks]
    selected = select(
        message="Zielgröße wählen:",
        choices=choices,
        instruction="Pfeiltasten, Enter bestätigt"
    ).ask()
    return selected

def select_s_arg() -> str:
    choices = [Choice(title="Ja", value="force"), Choice(title="Nein", value="auto")]
    selected = select(
        message="Docker container neu bauen?",
        choices=choices,
        instruction="Pfeiltasten, Enter bestätigt"
    ).ask()
    return selected

def main():
    framework = select_framework()
    if (framework is None):
        return

    constraint = select_constraint()
    if (constraint is None):
        return

    task = select_task()
    if (task is None):
        return
    
    force = select_s_arg()
    if (force is None):
        return

    run([
        framework,
        "sap",
        constraint,
        "-i", str(Path(__file__).parent / "csvs"),
        "-t", task,
        "-m", "docker",
        "-s", force
    ])

if __name__ == "__main__":
    main()