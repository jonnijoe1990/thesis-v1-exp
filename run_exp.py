from pathlib import Path
from typing import Literal
from questionary import Choice, select
from run import run

frameworks = ["AutoGluon", "flaml", "H2OAutoML"]
Framework = Literal["AutoGluon", "flaml", "H2OAutoML"]
def select_framework() -> Framework:
    choices = [Choice(title=framework, value=framework) for framework in frameworks]
    selected = select(
        message="Framework wählen:",
        choices=choices,
        instruction="Pfeiltasten, Enter bestätigt"
    ).ask()
    return selected

constraints = ["5m-test", "5m-12c", "30m-12c"]
Constraint = Literal["5m-test", "5m-12c", "30m-12c"]
def select_constraint() -> Constraint:
    choices = [Choice(title=constraint, value=constraint) for constraint in constraints]
    selected = select(
        message="Constraint wählen:",
        choices=choices,
        instruction="Pfeiltasten, Enter bestätigt"
    ).ask()
    return selected

tasks = ["age", "gender", "mortality"]
Task = Literal["age", "gender", "mortality"]
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

#def select_fold() -> int:
#    selected = select(
#        message="Folds wählen:",
#        choices=[Choice(title=str(i), value=i) for i in range(5)],
#        instruction="Pfeiltasten, Enter bestätigt"
#    ).ask()
#    return selected

def main():
    framework = select_framework()
    if (framework is None):
        print("No framework selected. Training all frameworks.")

    constraint = select_constraint()
    if (constraint is None):
        print("No constraint selected. Using all constraints.")

    task = select_task()
    if (task is None):
        print("No task selected. Using all tasks.")

    mode = select_mode()
    if (mode is None):
        return

    s_arg = select_s_arg()
    if (s_arg is None):
        return

    def run_experiment(f: Framework, c: Constraint, t: Task = task):
        run([
            f,
            "sap-24g",
            c,
            "-i", str(Path(__file__).parent / "csvs"),
            "-t", t,
            "-m", mode,
            "-s", s_arg
        ])

    for f in frameworks:
        for t in tasks:
            for c in constraints:
                if framework == None or framework == f:
                    if task == None or task == t:
                        if (constraint == None and c != "5m-test") or constraint == c:
                            run_experiment(f, c, t)

if __name__ == "__main__":
    main()