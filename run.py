import logging
import os
import re
import shutil
import sys
from typing import Iterable, Optional

# prevent asap other modules from defining the root logger using basicConfig
import amlb.logger

import openml

import amlb
from amlb.utils import (
    Namespace as ns,
    config_load,
    datetime_iso,
    str_sanitize,
    zip_path,
    StaleProcessError,
    Namespace,
)
from amlb import log, AutoMLError
from amlb.defaults import default_dirs
from parse import parser
# group = parser.add_mutually_exclusive_group()
# group.add_argument('--keep-scores', dest='keep_scores', action='store_true',
#                    help="Set to true [default] to save/add scores in output directory")
# group.add_argument('--no-keep-scores', dest='keep_scores', action='store_false')
# parser.set_defaults(keep_scores=True)

# removing this command line argument for now: by default, we're using the user default region as defined in ~/aws/config
#  on top of this, user can now override the aws.region setting in his custom ~/.config/automlbenchmark/config.yaml settings.
# parser.add_argument('-r', '--region', metavar='aws_region', default=None,
#                     help="The region on which to run the benchmark when using AWS.")

def run(arguments: Optional[Iterable[str]] = None):
    args = parser.parse_args(arguments)
    script_name = os.path.splitext(os.path.basename(__file__))[0]
    extras = {
        t[0]: t[1] if len(t) > 1 else True for t in [x.split("=", 1) for x in args.extra]
    }

    now_str = datetime_iso(date_sep="", time_sep="")
    sid = (
        args.session
        if args.session is not None
        else "{}.{}".format(
            ".".join(
                [
                    str_sanitize(args.framework.split(":", 1)[0]),
                    str_sanitize(
                        args.benchmark
                        if re.fullmatch(r"(openml)/[st]/\d+", args.benchmark)
                        else os.path.splitext(os.path.basename(args.benchmark))[0]
                    ),
                    str_sanitize(args.constraint),
                    extras.get("run_mode", args.mode),
                ]
            ).lower(),
            now_str,
        )
    )
    log_dir = amlb.resources.output_dirs(
        args.outdir or default_dirs.output_dir, session=sid, subdirs="logs", create=True
    )["logs"]
    # now_str = datetime_iso(time=False, no_sep=True)
    if args.profiling:
        logging.TRACE = logging.INFO
    log_levels = ns(
        {
            logger: int(level) if level.isnumeric() else level.upper()
            for logger, level in [d.split(":") for d in args.logging.split(",")]
        }
        if ":" in args.logging
        else dict(
            console=args.logging.upper(),
            app=args.logging.upper(),
            root=args.logging.upper(),
        )
        if args.logging
        else {}
    ) | ns(console="INFO", app="DEBUG", root="INFO")  # adding defaults if needed
    amlb.logger.setup(
        log_file=os.path.join(
            log_dir, "{script}.{now}.log".format(script=script_name, now=now_str)
        ),
        root_file=os.path.join(
            log_dir, "{script}.{now}.full.log".format(script=script_name, now=now_str)
        ),
        root_level=log_levels.root,
        app_level=log_levels.app,
        console_level=log_levels.console,
        print_to_log=True,
    )

    log.info(
        "Running task `%s:%s` on `%s` framework in `%s` mode.",
        args.benchmark,
        args.task[0],
        args.framework,
        args.mode,
    )
    if args.openml_test_server:
        openml.config.start_using_configuration_for_example()
        log.info("Connecting to the OpenML test server.")

    log.debug("Script args: %s.", args)

    config_default = config_load(
        os.path.join(default_dirs.root_dir, "resources", "config.yaml")
    )
    config_default_dirs = default_dirs
    # allowing config override from user_dir: useful to define custom benchmarks and frameworks for example.
    config_user = config_load(
        extras.get(
            "config", os.path.join(args.userdir or default_dirs.user_dir, "config.yaml")
        )
    )
    # config listing properties set by command line
    config_args = ns.parse(
        {"results.global_save": args.keep_scores},
        input_dir=args.indir,
        output_dir=args.outdir,
        user_dir=args.userdir,
        script=os.path.basename(__file__),
        run_mode=args.mode,
        parallel_jobs=args.parallel,
        sid=sid,
        exit_on_error=args.exit_on_error,
        test_server=args.openml_test_server,
        tag=args.openml_run_tag,
        command=" ".join(sys.argv),
    ) + ns.parse(extras)
    if args.mode != "local":
        config_args + ns.parse({"monitoring.frequency_seconds": 0})
    config_args = ns({k: v for k, v in config_args if v is not None})
    log.debug("Config args: %s.", config_args)
    # merging all configuration files
    amlb_res = amlb.resources.from_configs(
        config_default, config_default_dirs, config_user, config_args
    )
    if args.resume:
        if args.jobhistory is not None:
            job_history = args.jobhistory
        else:
            job_history = os.path.join(
                amlb_res.config.output_dir, amlb.results.Scoreboard.results_file
            )
    else:
        job_history = None

    bench = None
    exit_code = 0
    try:
        bench_kwargs = dict(
            framework_name=args.framework,
            benchmark_name=args.benchmark,
            constraint_name=args.constraint,
        )
        if job_history is not None:
            bench_kwargs["job_history"] = job_history

        if args.mode == "local":
            bench_cls = amlb.Benchmark
        elif args.mode == "docker":
            bench_cls = amlb.DockerBenchmark
        elif args.mode == "singularity":
            bench_cls = amlb.SingularityBenchmark
        elif args.mode == "aws":
            bench_cls = amlb.AWSBenchmark
            # bench = amlb.AWSBenchmark(args.framework, args.benchmark, args.constraint, region=args.region)
        # elif args.mode == "aws-remote":
        #     bench = amlb.AWSRemoteBenchmark(args.framework, args.benchmark, args.constraint, region=args.region)
        else:
            raise ValueError(
                "`mode` must be one of 'aws', 'docker', 'singularity' or 'local'."
            )
        bench = bench_cls(**bench_kwargs)

        if args.setup == "only":
            log.warning(
                "Setting up %s environment only for %s, no benchmark will be run.",
                args.mode,
                args.framework,
            )

        if not args.keep_scores and args.mode != "local":
            log.warning(
                "`keep_scores` parameter is currently ignored in %s mode, scores are always saved in this mode.",
                args.mode,
            )

        try:
            bench.setup(amlb.SetupMode[args.setup])
        except StaleProcessError as e:
            setting = "setup.activity_timeout"
            timeout = Namespace.get(amlb_res.config, setting)
            log.error(
                f"Process '{e.cmd}' was aborted after producing no output for {timeout} seconds. "
                f"If the process is expected to take more time, please raise the '{setting}' limit."
            )
            exit_code = 1
        else:
            if args.setup != "only":
                res = bench.run(args.task, args.fold)
    except (ValueError, AutoMLError) as e:
        log.error("\nERROR:\n%s", e)
        if extras.get("verbose") is True:
            log.exception(e)
        exit_code = 1
    except Exception as e:
        log.exception(e)
        exit_code = 2
    finally:
        archives = amlb.resources.config().archive
        if archives and bench:
            out_dirs = bench.output_dirs
            for d in archives:
                if d in out_dirs:
                    zip_path(
                        out_dirs[d],
                        os.path.join(out_dirs.session, f"{d}.zip"),
                        arc_path_format="long",
                    )
                    shutil.rmtree(out_dirs[d], ignore_errors=True)
        if args.openml_test_server:
            openml.config.stop_using_configuration_for_example()

    return exit_code


if __name__ == "__main__":
    sys.exit(run())
