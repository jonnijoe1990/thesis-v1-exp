from run import run

run([
    "AutoGluon",
    "test",
    "30m",
    "-t", "kc2",
    "-m", "docker",
    "-s", "force"
])