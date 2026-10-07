from pathlib import Path
from typing import Literal
from questionary import Choice, select
from run import run

frameworks = ["AutoGluon", "flaml", "H2OAutoML", "all"]
Framework = Literal["AutoGluon", "flaml", "H2OAutoML", "all"]
def select_framework() -> Framework:
    choices = [Choice(title=framework, value=framework) for framework in frameworks]
    selected = select(
        message="Framework wählen:",
        choices=choices,
        instruction="Pfeiltasten, Enter bestätigt"
    ).ask()
    return selected

constraints = ["5m-12c", "30m-12c", "all"]
Constraint = Literal["5m-12c", "30m-12c", "all"]
def select_constraint() -> Constraint:
    choices = [Choice(title=constraint, value=constraint) for constraint in constraints]
    selected = select(
        message="Constraint wählen:",
        choices=choices,
        instruction="Pfeiltasten, Enter bestätigt"
    ).ask()
    return selected

tasks = ["age", "gender", "mortality", "all"]
Task = Literal["age", "gender", "mortality", "all"]
def select_task() -> Task:
    choices = [Choice(title=task, value=task) for task in tasks]
    selected = select(
        message="Zielgröße wählen:",
        choices=choices,
        instruction="Pfeiltasten, Enter bestätigt"
    ).ask()
    return selected

s_args = ["force", "auto", "only"]
SArg = Literal["force", "auto", "only"]
def select_s_arg() -> SArg:
    choices = [Choice(title=s_arg, value=s_arg) for s_arg in s_args]
    selected = select(
        message="-s arg?",
        choices=choices,
        instruction="Pfeiltasten, Enter bestätigt"
    ).ask()
    return selected

modes = ["docker", "local"]
Mode = Literal["docker", "local"]
def select_mode() -> Mode:
    choices = [Choice(title=mode, value=mode) for mode in modes]
    selected = select(
        message="Mode wählen:",
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

    mode = select_mode()
    if (mode is None):
        return

    s_arg = select_s_arg()
    if (s_arg is None):
        return

    def run_experiment(f: Framework, c: Constraint, t: Task):
        run([
            f,
            "sap-24g",
            c,
            "-i", str(Path(__file__).parent / "csvs"),
            "-t", t,
            "-m", mode,
            "-s", s_arg
        ])

    for c in constraints:
        if c != "all" and (constraint == "all" or constraint == c):
            for f in frameworks:
                if f != "all" and (framework == "all" or framework == f):
                    for t in tasks:
                        if t != "all" and (task == "all" or task == t):
                            run_experiment(f, c, t)

if __name__ == "__main__":
    main()