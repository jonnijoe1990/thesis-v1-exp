import argparse
from amlb.defaults import default_dirs
from amlb.utils import str2bool

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument(
    "framework",
    type=str,
    help="The framework to evaluate as defined by default in resources/frameworks.yaml."
    "\nTo use a labelled framework (i.e. a framework defined in resources/frameworks-{label}.yaml),"
    "\nuse the syntax {framework}:{label}.",
)
parser.add_argument(
    "benchmark",
    type=str,
    nargs="?",
    default="test",
    help="The benchmark type to run as defined by default in resources/benchmarks/{benchmark}.yaml,"
    "\na path to a benchmark description file, or an openml suite or task."
    "\nOpenML references should be formatted as 'openml/s/X' and 'openml/t/Y',"
    "\nfor studies and tasks respectively. Use 'test.openml/s/X' for the "
    "\nOpenML test server."
    "\n(default: '%(default)s')",
)
parser.add_argument(
    "constraint",
    type=str,
    nargs="?",
    default="test",
    help="The constraint definition to use as defined by default in resources/constraints.yaml."
    "\n(default: '%(default)s')",
)
parser.add_argument(
    "-m",
    "--mode",
    choices=["local", "docker"],
    default="local",
    help="The mode that specifies how/where the benchmark tasks will be running."
    "\n(default: '%(default)s')",
)
parser.add_argument(
    "-t",
    "--task",
    metavar="task_id",
    nargs="*",
    default=None,
    help="The specific task name (as defined in the benchmark file) to run."
    "\nWhen an OpenML reference is used as benchmark, the dataset name should be used instead."
    "\nIf not provided, then all tasks from the benchmark will be run.",
)
parser.add_argument(
    "-f",
    "--fold",
    metavar="fold_num",
    type=int,
    nargs="*",
    default=None,
    help="If task is provided, the specific fold(s) to run."
    "\nIf fold is not provided, then all folds from the task definition will be run.",
)
parser.add_argument(
    "-i",
    "--indir",
    metavar="input_dir",
    default=None,
    help="Folder from where the datasets are loaded by default."
    f"\n(default: '{default_dirs.input_dir}')",
)
parser.add_argument(
    "-o",
    "--outdir",
    metavar="output_dir",
    default=None,
    help="Folder where all the outputs should be written."
    f"(default: '{default_dirs.output_dir}')",
)
parser.add_argument(
    "-u",
    "--userdir",
    metavar="user_dir",
    default=None,
    help="Folder where all the customizations are stored."
    f"(default: '{default_dirs.user_dir}')",
)
parser.add_argument(
    "--jobhistory",
    metavar="job_history",
    default=None,
    help="File where prior job run results are stored. Only used when --resume is specified."
    "(default: 'None')",
)
parser.add_argument(
    "-p",
    "--parallel",
    metavar="parallel_jobs",
    type=int,
    default=1,
    help="The number of jobs (i.e. tasks or folds) that can run in parallel."
    "\nA hard limit is defined by property `job_scheduler.max_parallel_jobs`"
    "\n in `resources/config.yaml`."
    "\nOverride this limit in your custom `config.yaml` file if needed."
    "\nSupported only in docker mode."
    "\n(default: %(default)s)",
)
parser.add_argument(
    "-s",
    "--setup",
    choices=["auto", "skip", "force", "only"],
    default="auto",
    help="Framework/platform setup mode. Available values are:"
    "\n• auto: setup is executed only if strictly necessary."
    "\n• skip: setup is skipped."
    "\n• force: setup is always executed before the benchmark."
    "\n• only: only setup is executed (no benchmark)."
    "\n(default: '%(default)s')",
)
parser.add_argument(
    "-k",
    "--keep-scores",
    type=str2bool,
    metavar="true|false",
    nargs="?",
    const=True,
    default=True,
    help="Set to true (default) to save/add scores in output directory.",
)
parser.add_argument(
    "-e",
    "--exit-on-error",
    action="store_true",
    dest="exit_on_error",
    help="If set, terminates on the first task that does not complete with a model.",
)
parser.add_argument(
    "--logging",
    type=str,
    default="console:info,app:debug,root:info",
    help="Set the log levels for the 3 available loggers:"
    "\n• console"
    "\n• app: for the log file including only logs from amlb (.log extension)."
    "\n• root: for the log file including logs from libraries (.full.log extension)."
    "\nAccepted values for each logger are: notset, debug, info, warning, error, fatal, critical."
    "\nExamples:"
    "\n  --logging=info (applies the same level to all loggers)"
    "\n  --logging=root:debug (keeps defaults for non-specified loggers)"
    "\n  --logging=console:warning,app:info"
    "\n(default: '%(default)s')",
)
parser.add_argument(
    "--openml-test-server",
    type=str2bool,
    metavar="true|false",
    nargs="?",
    const=True,
    default=False,
    help=argparse.SUPPRESS,
)  # "Set to true to connect to the OpenML test server instead."
parser.add_argument(
    "--openml-run-tag",
    type=str,
    default=None,
    help="Tag that will be saved in metadata and OpenML runs created during upload, must match '([a-zA-Z0-9_\-\.])+'.",
)

parser.add_argument(
    "--profiling", nargs="?", const=True, default=False, help=argparse.SUPPRESS
)
parser.add_argument(
    "--resume", nargs="?", const=True, default=False, help=argparse.SUPPRESS
)
parser.add_argument("--session", type=str, default=None, help=argparse.SUPPRESS)
parser.add_argument(
    "-X", "--extra", default=[], action="append", help=argparse.SUPPRESS
)