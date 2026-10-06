from pathlib import Path
from typing import Literal
from questionary import Choice, select
from run import run

frameworks = ["AutoGluon", "flaml", "H2OAutoML"]
constraints = ["5m-test", "30m"]
tasks = ["gender", "mortality", "age", "all"]
Framework = Literal["AutoGluon", "flaml", "H2OAutoML"]
Task = Literal["gender", "mortality", "age", "all"]
Constraint = Literal["5m-test", "30m"]

def select_framework() -> Framework:
    choices = [Choice(title=framework, value=framework) for framework in frameworks]
    selected = select(
        message="Framework wählen:",
        choices=choices,
        instruction="Pfeiltasten, Enter bestätigt"
    ).ask()
    return selected

def select_constraint() -> Constraint:
    choices = [Choice(title=constraint, value=constraint) for constraint in constraints]
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

    def run_experiment(task: Task):
        run([
            framework,
            "sap",
            constraint,
            "-i", str(Path(__file__).parent / "csvs"),
            "-t", task,
            "-m", "docker",
            "-s", force
        ])

    if task != "all":
        run_experiment(task)
    else:
        for t in tasks:
            if t != "all":
                run_experiment(t)

if __name__ == "__main__":
    main()