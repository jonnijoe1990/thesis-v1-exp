from run import run

frameworks = ["flaml", "H2OAutoML"]

for framework in frameworks:
    run([
        framework,
        "test",
        "30m",
        "-t", "kc2",
        "-m", "local",
        "-s", "force"
    ])