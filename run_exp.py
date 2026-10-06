from typing import Literal
from questionary import Choice, select
from run import run

frameworks = ["AutoGluon", "flaml", "H2OAutoML"]
tasks = ["gender", "mortality"]
Framework = Literal["AutoGluon", "flaml", "H2OAutoML"]
Task = Literal["gender", "mortality"]

def select_framework() -> Framework:
    choices = [Choice(title=framework, value=framework) for framework in frameworks]
    selected = select(
        message="Framework wählen:",
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

def main():
    framework = select_framework()
    if (framework is None):
        return

    task = select_task()
    if (task is None):
        return
    
    run([
        framework,
        "sap",
        "30m",
        "-t", task,
        "-m", "local",
        "-s", "force"
    ])

if __name__ == "__main__":
    main()