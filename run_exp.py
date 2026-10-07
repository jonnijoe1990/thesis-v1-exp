from pathlib import Path
from typing import Literal
from questionary import Choice, select
from run import run

s_args = ["force", "auto", "only"]
frameworks = ["AutoGluon", "flaml", "H2OAutoML", "all"]
constraints = ["5m-test", "30m-8c", "30m-12c", "15m-8c", "15m-12c"]
modes = ["docker", "local"]
tasks = ["age", "gender", "mortality"]
Framework = Literal["AutoGluon", "flaml", "H2OAutoML", "all"]
Task = Literal["age", "gender", "mortality"]
Constraint = Literal["5m-test", "30m-8c", "30m-12c", "15m-8c", "15m-12c"]
Mode = Literal["docker", "local"]
SArg = Literal["force", "auto", "only"]

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

def select_s_arg() -> SArg:
    choices = [Choice(title=s_arg, value=s_arg) for s_arg in s_args]
    selected = select(
        message="-s arg?",
        choices=choices,
        instruction="Pfeiltasten, Enter bestätigt"
    ).ask()
    return selected

def select_mode() -> Mode:
    choices = [Choice(title=mode, value=mode) for mode in modes]
    selected = select(
        message="Mode wählen:",
        choices=choices,
        instruction="Pfeiltasten, Enter bestätigt"
    ).ask()
    return selected

def select_fold() -> int:
    selected = select(
        message="Folds wählen:",
        choices=[Choice(title=str(i), value=i) for i in range(5)],
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

    mode = select_mode()
    if (mode is None):
        return

    s_arg = select_s_arg()
    if (s_arg is None):
        return

    #fold = select_fold()
    #if (fold is None):
    #    return

    def run_experiment(f: Framework):
        run([
            f,
            "sap-24g",
            constraint,
            "-i", str(Path(__file__).parent / "csvs"),
            "-t", task,
            "-m", mode,
            "-s", s_arg
            #"-f", fold
        ])

    if framework != "all":
        run_experiment(framework)
    else:
        for f in frameworks:
            if f != "all":
                run_experiment(f)

if __name__ == "__main__":
    main()