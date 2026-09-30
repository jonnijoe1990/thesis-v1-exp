from run import run

constraints = ["30m"]
frameworks = ["AutoGluon", "flaml", "H2OAutoML"]
task = "gender"
folds = 1

for c in constraints:
    for fold_num in range(folds):
        for f in frameworks:
            run([
                f,
                "sap",
                c,
                "-t", task,
                "-m", "local",
                "-s", "force",
                "-f", fold_num
            ])