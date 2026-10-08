"""
**container** module is build on top of **benchmark** module to provide logic to create and run container images (docker)
that are preconfigured with a given automl framework, and that can be used to run a benchmark anywhere.
The image embeds a version of the automlbenchmark app so that tasks are later run in local mode inside the container,
providing the same parameters and features allowing to import config and export results through mounted folders.
"""

from __future__ import annotations

from abc import abstractmethod
import logging
import re
from typing import cast

from ..benchmark import Benchmark, SetupMode
from ..frameworks.definitions import Framework
from ..job import Job
from ..resources import config as rconfig, get as rget


log = logging.getLogger(__name__)


class ContainerBenchmark(Benchmark):
    """ContainerBenchmark
    an extension of Benchmark to run benchmarks inside a container.
    """

    framework_install_required = False

    @classmethod
    def image_name(cls, framework_def: Framework) -> str:
        """Image name from the framework definition, without a branch or dev suffix."""
        di = framework_def.image
        author = di.author
        image = di.image if di.image else framework_def.name.lower()
        tag = di.tag if di.tag else framework_def.version.lower()
        # A version like #HASH would make the tag start with '.', which is invalid.
        tag = re.sub(r"([^\w.-])", ".", tag).lstrip(".")
        return f"{author}/{image}:{tag}"

    @abstractmethod
    def __init__(self, framework_name, benchmark_name, constraint_name):
        """

        :param framework_name:
        :param benchmark_name:
        :param constraint_name:
        """
        super().__init__(framework_name, benchmark_name, constraint_name)
        self._custom_image_name = rconfig().container.image
        self.minimize_instances = rconfig().container.minimize_instances
        self.container_name = None
        self.custom_commands = ""
        self.image = None

    def _container_image_name(self) -> str:
        return self.image_name(cast(Framework, self.framework_def))

    def _validate(self):
        max_parallel_jobs = rconfig().job_scheduler.max_parallel_jobs
        if self.parallel_jobs == 0 or self.parallel_jobs > max_parallel_jobs:
            log.warning(
                "Forcing parallelization to its upper limit: %s.", max_parallel_jobs
            )
            self.parallel_jobs = max_parallel_jobs

    def setup(self, mode, upload=False):
        if mode == SetupMode.skip:
            return

        if mode == SetupMode.auto:
            self.image = self._find_image()
            if self.image:
                return

        self._generate_script(self.custom_commands)
        self.image = self._build_image(cache=(mode != SetupMode.force))
        if upload:
            self._upload_image(self.image)

    def cleanup(self):
        pass

    def run(
        self, tasks: str | list[str] | None = None, folds: int | list[int] | None = None
    ):
        self._get_task_defs(tasks)  # validates tasks
        if self.parallel_jobs > 1 or not self.minimize_instances:
            return super().run(tasks, folds)
        else:
            job = self._make_container_job(tasks, folds)
            try:
                results = self._run_jobs([job])
                scoreboard = self._process_results(results)
                return self._results_summary(scoreboard)
            finally:
                self.cleanup()

    def _make_job(self, task_def, fold=int):
        return (
            self._make_container_job([task_def.name], [fold])
            if not self._skip_job(task_def, fold)
            else None
        )

    def _make_container_job(self, task_names=None, folds=None):
        task_names = [] if task_names is None else task_names
        folds = [] if folds is None else [str(f) for f in folds]

        def _run():
            self._start_container(
                "{framework} {benchmark} {constraint} {task_param} {folds_param} -Xseed={seed}".format(
                    framework=self._forward_params["framework_name"],
                    benchmark=self._forward_params["benchmark_name"],
                    constraint=self._forward_params["constraint_name"],
                    task_param=""
                    if len(task_names) == 0
                    else " ".join(["-t"] + task_names),
                    folds_param="" if len(folds) == 0 else " ".join(["-f"] + folds),
                    seed=rget().seed(int(folds[0]))
                    if len(folds) == 1
                    else rconfig().seed,
                )
            )

        job = Job(
            rconfig().token_separator.join(
                [
                    self.container_name,
                    self.benchmark_name,
                    self.constraint_name,
                    ",".join(task_names) if len(task_names) > 0 else "all_tasks",
                    ",".join(folds) if len(folds) > 0 else "all_folds",
                    self.framework_name,
                ]
            ),
            raise_on_failure=rconfig().job_scheduler.exit_on_job_failure,
        )
        job._run = _run
        return job

    def _start_container(self, script_params=""):
        """Implementes the container run method"""
        raise NotImplementedError

    def _find_image(self):
        image = self._custom_image_name or self._container_image_name()
        if image and self._image_exists(image):
            return image
        return None

    def _image_exists(self, image):
        """Implements a method to see if the container image is available"""
        raise NotImplementedError

    def _build_image(self, cache=True):
        image = self._custom_image_name or self._container_image_name()
        self._run_container_build_command(image, cache)
        return image

    def _run_container_build_command(self, image, cache):
        """Implements a method to build a container image"""
        raise NotImplementedError

    def _upload_image(self, image):
        """Implements a method to upload images to hub"""
        raise NotImplementedError

    def _generate_script(self, custom_commands):
        """Implements a method to create the recipe for a container script"""
        raise NotImplementedError
