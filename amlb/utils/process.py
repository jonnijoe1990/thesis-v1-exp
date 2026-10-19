from __future__ import annotations

import ctypes
import gc
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from functools import partial, wraps
import inspect
import io
import logging
import multiprocessing as mp
import os
import platform
import queue
import re
import select
import shutil
import signal
import stat
import subprocess
import sys
import threading
from typing import Dict, List, Union, Tuple, cast

import psutil

from .core import Namespace, as_list, flatten, fn_name
from .os import dir_of, to_mb, path_from_split, split_path
from .time import Timeout, Timer

log = logging.getLogger(__name__)

__no_export = set(dir())  # all variables defined above this are not exported


@contextmanager
def file_lock(path, timeout=-1):
    """
    :param path: the path of the file to lock.
        A matching lock file is automatically generated and associated to the file that we want to manipulate.
    :param timeout: timeout in seconds to wait for the lock to be acquired. Disabled by default.
    :raise: Timeout if the lock could not be acquired after timeout.
    """
    import filelock

    splits = split_path(path)
    splits.basename = f".{splits.basename}"  # keep the lock file as a hidden file as it's not deleted by filelock on release
    splits.extension = f"{splits.extension}.lock"
    lock_path = path_from_split(splits, real_path=False)
    with filelock.FileLock(lock_path, timeout=timeout):
        yield


class StaleProcessError(subprocess.TimeoutExpired):
    pass


def run_subprocess(
    *popenargs,
    input=None,
    capture_output=False,
    timeout=None,
    check=False,
    communicate_fn=None,
    **kwargs,
):
    """
    a clone of :function:`subprocess.run` which allows custom handling of communication
    :param popenargs:
    :param input:
    :param capture_output:
    :param timeout:
    :param check:
    :param communicate_fn:
    :param kwargs:
    :return:
    """
    if input is not None:
        if "stdin" in kwargs:
            raise ValueError("stdin and input arguments may not both be used.")
        kwargs["stdin"] = subprocess.PIPE

    if capture_output:
        if kwargs.get("stdout") is not None or kwargs.get("stderr") is not None:
            raise ValueError(
                "stdout and stderr arguments may not be used with capture_output."
            )
        kwargs["stdout"] = subprocess.PIPE
        kwargs["stderr"] = subprocess.PIPE

    def communicate(process, input=None, timeout=None):
        return (
            communicate_fn(process, input=input, timeout=timeout)
            if communicate_fn
            else process.communicate(input=input, timeout=timeout)
        )

    with subprocess.Popen(*popenargs, **kwargs) as process:
        try:
            stdout, stderr = communicate(process, input, timeout=timeout)
        except subprocess.TimeoutExpired as e:
            process.kill()
            if sys.platform == "win32":
                e.stdout, e.stderr = communicate(process)
            else:
                process.wait()
            raise subprocess.TimeoutExpired(
                process.args, timeout, output=stdout, stderr=stderr
            )
        except:  # also handles kb interrupts
            process.kill()
            raise

        # Communication is aborted if either
        #  - the process has completed, or
        #  - the process does not produce any output in the specified timeout
        # `communicate` can't distinguish those cases. If the process has a
        # return code then it stopped already, otherwise we stop it now.
        retcode = process.poll()
        if retcode is None:
            process.kill()
            process.wait()
            raise StaleProcessError(
                process.args, float("nan"), output=stdout, stderr=stderr
            )

        if check and retcode:
            raise subprocess.CalledProcessError(
                retcode, process.args, output=stdout, stderr=stderr
            )
    return subprocess.CompletedProcess(process.args, retcode, stdout, stderr)


def as_cmd_args(*args, **kwargs):
    return list(
        filter(
            None,
            []
            + ([] if args is None else list(args))
            + flatten(kwargs.items(), flatten_tuple=True)
            if kwargs is not None
            else [],
        )
    )


def live_output_windows(process: subprocess.Popen, **_) -> Tuple[str, str]:
    """Custom output forwarder, because select.select is not Windows compatible."""
    outputs = dict(
        out=dict(
            stream=process.stdout,
            queue=queue.Queue(),
            lines=[],
        ),
        err=dict(
            stream=process.stderr,
            queue=queue.Queue(),
            lines=[],
        ),
    )  # type: ignore  # no reasonable type annotation, should refactor

    def forward_output(stream, queue_):
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(errors="ignore")
        for line in stream:
            queue_.put(line)

    for output in outputs.values():
        t = threading.Thread(
            target=forward_output, args=(output["stream"], output["queue"])
        )
        t.daemon = True
        t.start()

    while process.poll() is None:
        for output in outputs.values():
            while True:
                try:
                    line = cast(queue.Queue, output["queue"]).get(timeout=0.5)
                    cast(list[str], output["lines"]).append(line)
                    print(line.rstrip())
                except queue.Empty:
                    break
    stdout = "".join(cast(list[str], outputs["out"]["lines"]))
    stderr = "".join(cast(list[str], outputs["err"]["lines"]))
    return stdout, stderr


def live_output_unix(
    process, input=None, timeout=None, activity_timeout=None, mode="line", **_
):
    if mode is True:
        mode = "line"

    if input is not None:
        try:
            with process.stdin as stream:
                stream.write(input)
        except BrokenPipeError:
            pass
        except:
            raise

    def read_pipe(pipe, timeout):
        pipes = as_list(pipe)
        # wait until a pipe is ready for reading, non-Windows only.
        ready, *_ = select.select(pipes, [], [], timeout)
        # if a pipe is not ready it could be timeout or it could be end of process
        # so at this point we do not know. Only after the communicate function is over do we know.
        # i.e., if the process is still running it does not have a retcode.
        reads = [""] * len(pipes)
        # print update for each pipe that is ready for reading
        for i, p in enumerate(pipes):
            if p in ready:
                line = p.readline()
                if mode == "line":
                    print(re.sub(r"\n$", "", line, count=1))
                elif mode == "block":
                    print(line, end="")
                reads[i] = line
        return reads if len(pipes) > 1 else reads[0]

    process_output = list(
        iter(
            lambda: read_pipe(
                [
                    process.stdout if process.stdout else 1,
                    process.stderr if process.stderr else 2,
                ],
                activity_timeout,
            ),
            ["", ""],
        )
    )
    if not process_output:
        log.warning(
            "No framework process output detected, "
            "this might indicate a problem with the logging configuration."
        )
        return "", ""

    output, error = zip(*process_output)
    print()  # ensure that the log buffer is flushed at the end
    return "".join(output), "".join(error)


def monitor_proc(process, monitor_params={}, **_):
    pid = process.pid
    ProcessMemoryMonitoring(pid=pid, **monitor_params).__enter__()


def run_cmd(cmd, *args, **kwargs):
    params = Namespace(
        input_str=None,
        capture_output=True,
        capture_error=True,
        bufsize=-1,
        text=True,
        live_output=False,  # one of (True, 'line', 'block', False)
        output_level=logging.DEBUG,
        error_level=logging.ERROR,
        shell=True,
        executable=None,
        env=None,
        preexec_fn=None,
        timeout=None,
        activity_timeout=None,
        log_level=logging.INFO,
        monitor=None,
    )
    for k, v in params:
        kk = "_" + k + "_"
        if kk in kwargs:
            params[k] = kwargs[kk]
            del kwargs[kk]
    cmd_args = as_cmd_args(*args, **kwargs)
    full_cmd = flatten([cmd]) + cmd_args
    str_cmd = " ".join(full_cmd)
    log.log(params.log_level, "Running cmd `%s`", str_cmd)
    log.debug("Running cmd `%s` with input: %s", str_cmd, params.input_str)

    hooks = []
    if params.monitor is True:
        hooks.append(monitor_proc)
    elif isinstance(params.monitor, dict):
        hooks.append(partial(monitor_proc, monitor_params=params.monitor))

    if params.live_output and params.capture_output:
        if platform.system() == "Windows":
            live_output = partial(
                live_output_windows, activity_timeout=params.activity_timeout
            )
        else:
            live_output = partial(
                live_output_unix,
                mode=params.live_output,
                activity_timeout=params.activity_timeout,
            )
        hooks.append(live_output)

    if hooks:

        def communicate(*args, **kwargs):
            res = None
            for (
                h
            ) in hooks:  # last hook should behave like a proper communicate function
                res = h(*args, **kwargs)
            return res
    else:
        communicate = None

    try:
        completed = run_subprocess(
            str_cmd if params.shell else full_cmd,
            input=params.input_str,
            timeout=params.timeout,
            check=True,
            communicate_fn=communicate,
            # stdin=subprocess.PIPE if params.input_str is not None else None,
            stdout=subprocess.PIPE if params.capture_output else None,
            stderr=subprocess.PIPE if params.capture_error else None,
            shell=params.shell,
            bufsize=params.bufsize,
            universal_newlines=params.text,
            executable=params.executable,
            env=params.env,
            preexec_fn=params.preexec_fn,
        )
        if completed.stdout:
            log.log(params.output_level, completed.stdout)
        if completed.stderr:
            log.log(params.error_level, completed.stderr)
        return completed.stdout, completed.stderr
    except subprocess.CalledProcessError as e:
        if e.stdout:
            log.log(params.output_level, e.stdout)
        if e.stderr:
            log.log(params.error_level, e.stderr)
        raise e


def run_script(script_path, *args, **kwargs):
    mod = os.stat(script_path).st_mode
    os.chmod(script_path, mod | stat.S_IEXEC)
    return run_cmd(script_path, *args, **kwargs)


def call_script_in_same_dir(caller_file, script_file, *args, **kwargs):
    here = dir_of(caller_file)
    script_path = os.path.join(here, script_file)
    return run_script(script_path, *args, **kwargs)


def is_main_thread(tid=None):
    return get_thread(tid) == threading.main_thread()


def get_thread(tid=None):
    return (
        threading.current_thread()
        if tid is None
        else threading.main_thread()
        if tid == 0
        else next(filter(lambda t: t.ident == tid, threading.enumerate()), None)
    )


def get_process(pid=None):
    pid = os.getpid() if pid is None else os.getppid() if pid == 0 else pid
    return psutil.Process(pid) if psutil.pid_exists(pid) else None


def _alive(proc):
    try:
        return proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE
    except psutil.Error:
        return False


def _reap_zombies():
    """Reap children the killed parent did not wait for. Zombies hold no RAM."""
    if os.name == "nt":
        return
    while True:
        try:
            pid, _status = os.waitpid(-1, os.WNOHANG)
        except ChildProcessError:
            return
        if pid == 0:
            return


def _terminate_processes(procs, timeout=None, on_terminate=None):
    """Stop ``procs``, leaves first, then wait until each one has exited.

    Signalling a Ray parent and its workers in one shot makes the workers
    zombies and SIGKILLs ``raylet`` before it can unlink ``/dev/shm``.
    """

    def on_proc_terminated(proc):
        log.info("Process %s terminated with exit code %s", proc, proc.returncode)
        if on_terminate is not None:
            on_terminate(proc)

    pending = []
    seen = set()
    for proc in procs:
        if proc is None or proc.pid in seen:
            continue
        seen.add(proc.pid)
        pending.append(proc)

    stopped = 0
    while pending:
        roots = {proc.pid for proc in pending}
        leaves = []
        for proc in pending:
            try:
                child_pids = {child.pid for child in proc.children(recursive=False)}
            except psutil.Error:
                child_pids = set()
            if not child_pids & roots:
                leaves.append(proc)
        if not leaves:
            leaves = list(pending)

        for proc in leaves:
            if not _alive(proc):
                continue
            log.warning("Terminating process %s.", proc)
            try:
                proc.terminate()
            except psutil.NoSuchProcess:
                pass
        _gone, alive = psutil.wait_procs(
            leaves, timeout=timeout, callback=on_proc_terminated
        )
        for proc in alive:
            if not _alive(proc):
                continue
            log.warning("Killing process %s.", proc)
            try:
                proc.kill()
            except psutil.NoSuchProcess:
                pass
        psutil.wait_procs(alive, timeout=5)
        _reap_zombies()

        leaf_ids = {proc.pid for proc in leaves}
        still_pending = []
        for proc in pending:
            if proc.pid not in leaf_ids:
                still_pending.append(proc)
                continue
            if not _alive(proc):
                stopped += 1
        pending = still_pending
    return stopped


def kill_proc_tree(pid=None, include_parent=True, timeout=None, on_terminate=None):
    parent = get_process(pid)
    if parent is None:
        return 0
    procs = parent.children(recursive=True)
    if include_parent:
        procs.append(parent)
    stopped = _terminate_processes(procs, timeout=timeout, on_terminate=on_terminate)
    _reap_zombies()
    return stopped


def _running_in_container():
    return os.path.exists("/.dockerenv") or os.path.exists("/run/.containerenv")


def _is_ray_process(proc):
    try:
        name = proc.info.get("name") if getattr(proc, "info", None) else None
        cmdline = proc.info.get("cmdline") if getattr(proc, "info", None) else None
        if name is None:
            name = proc.name()
        if cmdline is None:
            cmdline = proc.cmdline()
    except (psutil.Error, OSError):
        return False
    blob = " ".join([name or "", *(cmdline or [])])
    markers = (
        "gcs_server",
        "raylet",
        "plasma_store",
        "ray::",
        "ray-dashboard",
        "default_worker.py",
        "ray.dashboard",
        "ray._private.workers",
        "ray/_private/workers",
    )
    return any(marker in blob for marker in markers)


def _ray_processes():
    me = os.getpid()
    found = []
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        if proc.pid == me:
            continue
        if _is_ray_process(proc):
            found.append(proc)
    return found


def _path_size(path):
    if os.path.isfile(path) or os.path.islink(path):
        try:
            return os.path.getsize(path)
        except OSError:
            return 0
    total = 0
    for dirpath, _dirnames, filenames in os.walk(path):
        for name in filenames:
            try:
                total += os.path.getsize(os.path.join(dirpath, name))
            except OSError:
                pass
    return total


def _remove_path(path):
    try:
        if os.path.isdir(path) and not os.path.islink(path):
            shutil.rmtree(path, ignore_errors=True)
        else:
            os.remove(path)
    except OSError:
        pass


def _release_ray_ipc():
    """Unlink Ray shared memory. It survives ``kill -9`` of ``raylet``."""
    freed = 0
    shm = "/dev/shm"
    if os.path.isdir(shm):
        for name in os.listdir(shm):
            lower = name.lower()
            if "ray" not in lower and "plasma" not in lower:
                continue
            path = os.path.join(shm, name)
            freed += _path_size(path)
            _remove_path(path)
    ray_tmp = "/tmp/ray"
    if os.path.isdir(ray_tmp):
        freed += _path_size(ray_tmp)
        shutil.rmtree(ray_tmp, ignore_errors=True)
    return freed


def reap_ray_runtime():
    """Stop Ray processes and files left after a fold.

    Inside a container the tmpfs is private, so a full sweep cannot hit a
    Ray cluster outside this run. Local mode only stops our own children,
    via ``kill_proc_tree``, and relies on ``ray.shutdown()``.
    """
    if not _running_in_container():
        return 0
    victims = _ray_processes()
    stopped = _terminate_processes(victims, timeout=5) if victims else 0
    freed = _release_ray_ipc()
    if stopped or freed:
        log.info(
            "Ray cleanup: stopped %d process(es), freed %.0f MB of shared memory.",
            stopped,
            to_mb(freed),
        )
    remaining = [proc.pid for proc in _ray_processes() if _alive(proc)]
    if remaining:
        log.warning("Ray processes still alive after cleanup: %s", remaining)
    return stopped


def release_os_memory():
    """Return freed heap pages to the OS.

    The benchmark process lives for every fold. After it drops a dataset,
    glibc keeps the arena mapped, so the next fold's memory check sees a
    smaller ``MemAvailable`` than the first fold.
    """
    gc.collect()
    if sys.platform == "win32":
        return
    try:
        libc = ctypes.CDLL("libc.so.6")
    except OSError:
        return
    trim = getattr(libc, "malloc_trim", None)
    if trim is None:
        return
    trim.argtypes = [ctypes.c_size_t]
    trim.restype = ctypes.c_int
    trim(0)


def cleanup_between_folds():
    before = system_memory_mb()
    stopped = reap_ray_runtime()
    release_os_memory()
    after = system_memory_mb()
    log.info(
        "Fold cleanup: stopped %d leftover process(es). "
        "Available memory %.0f MB -> %.0f MB (total %.0f MB).",
        stopped,
        before.available,
        after.available,
        after.total,
    )


def call_in_subprocess(target, *args, **kwargs):
    def call_target(q, *args, **kwargs):
        try:
            result = target(*args, **kwargs)
            q.put_nowait(result)
        except BaseException as e:
            log.exception(e)
            q.put_nowait(e)

    q = mp.Queue(maxsize=1)
    p = mp.Process(target=call_target, args=(q, *args), kwargs=kwargs)
    try:
        p.start()
        p.join()
        result = q.get_nowait()
        if isinstance(result, BaseException):
            raise result
        else:
            return result
    except queue.Empty:
        raise Exception("Subprocess running {} died abruptly.".format(target.__name__))
    except BaseException:
        try:
            kill_proc_tree(p.pid)
        except Exception:
            pass
        raise


def process_memory_mb(pid=None, extended=False):
    proc = pid if isinstance(pid, psutil.Process) else get_process(pid)
    try:
        mem = proc.memory_full_info() if extended else proc.memory_info()
        res = Namespace(
            resident=to_mb(mem.rss),
            virtual=to_mb(mem.vms),
        )
        if hasattr(mem, "uss"):
            res.unique = to_mb(mem.uss)
        if hasattr(mem, "shared"):
            res.shared = to_mb(mem.shared)
        if hasattr(mem, "swap"):
            res.swap = to_mb(mem.swap)
        if hasattr(mem, "data"):
            res.data = to_mb(mem.data)
        return res
    except Exception as e:
        return Namespace(error=str(e))


def system_cores():
    return psutil.cpu_count()


def system_memory_mb():
    vm = psutil.virtual_memory()
    return Namespace(
        total=to_mb(vm.total), available=to_mb(vm.available), used_percentage=vm.percent
    )


def system_volume_mb(root="/"):
    du = psutil.disk_usage(root)
    return Namespace(
        total=to_mb(du.total),
        free=to_mb(du.free),
        used=to_mb(du.used),
        used_percentage=du.percent,
    )


@contextmanager
def signal_handler(sig, handler):
    """
    :param sig: a signal as defined in https://docs.python.org/3.7/library/signal.html#module-contents
    :param handler: a handler function executed when the given signal is raised in the current thread.
    """
    prev_handler = None
    try:
        prev_handler = signal.signal(sig, handler)
        yield
    finally:
        # restore previous signal handler
        signal.signal(sig, prev_handler or signal.SIG_DFL)


def raise_in_thread(thread_id, exc):
    """
    :param thread_id: the thread in which the exception will be raised.
    :param exc: the exception to raise in the thread: it can be an exception class or an instance.
    """
    import ctypes

    tid = ctypes.c_long(thread_id)
    exc_class = (
        exc
        if inspect.isclass(exc)
        else type(
            exc.__class__.__name__,
            (exc.__class__,),
            dict(__init__=lambda s: super(s.__class__, s).__init__(str(exc))),
        )
    )
    exc_class = ctypes.py_object(exc_class)
    ret = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, exc_class)
    if ret == 0:
        raise ValueError(f"Nonexistent thread {thread_id}")
    elif ret > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError(f"Failed raising exception in thread {thread_id}")


class InterruptTimeout(Timeout):
    """
    A :class:`Timeout` implementation that can send a signal to the interrupted thread or process,
    or raise an exception in the thread (works only for thread interruption)
    if the passed signal is an exception class or instance.
    If sig is None, then it raises a TimeoutError internally that is not propagated outside the context manager.
    """

    def __init__(
        self,
        timeout_secs,
        message=None,
        log_level=logging.WARNING,
        interrupt="thread",
        sig=signal.SIGINT,
        id=None,
        interruptions: Union[Dict, List[Dict]] | None = None,
        wait_retry_secs=1,
        before_interrupt=None,
    ):
        def interruption():
            inter_iter = iter(self._interruptions)
            while not self._interrupt_event.is_set():
                inter = self._last_attempt = next(inter_iter, self._last_attempt)
                log.log(self._log_level, inter.message)
                if inter.before_interrupt is not None:
                    try:
                        inter.before_interrupt()
                    except Exception:
                        log.warning(
                            "Swallowing the error raised by `before_interrupt` hook: %s",
                            inter.before_interrupt,
                            exc_info=True,
                        )
                try:
                    if inter.interrupt == "thread":
                        if isinstance(inter.sig, (type(None), BaseException)):
                            exc = (
                                TimeoutError(inter.message)
                                if inter.sig is None
                                else inter.sig
                            )
                            raise_in_thread(inter.id, exc)
                        else:
                            # _thread.interrupt_main()
                            signal.pthread_kill(inter.id, inter.sig)
                    elif inter.interrupt == "process":
                        os.kill(inter.id, inter.sig)
                except Exception:
                    raise
                finally:
                    self._interrupt_event.wait(
                        inter.wait
                    )  # retry every second if interruption didn't work

        super().__init__(timeout_secs, on_timeout=interruption)
        self._timeout_secs = timeout_secs
        self._message = message
        self._log_level = log_level
        self._interrupt = interrupt
        self._sig = sig
        self._id = id
        self._wait_retry_secs = wait_retry_secs
        self._before_interrupt = before_interrupt
        self._interruptions = [
            self._make_interruption(i)
            for i in (
                interruptions
                if isinstance(interruptions, list)
                else [interruptions]
                if isinstance(interruptions, dict)
                else [dict()]
            )
        ]
        self._interrupt_event = threading.Event()
        self._last_attempt = None

    def _make_interruption(self, interruption: dict):
        interrupt = interruption.get("interrupt", self._interrupt)
        sig = interruption.get("sig", self._sig)
        id = interruption.get("id", self._id)
        message = interruption.get("message", self._message)
        wait = interruption.get("wait", self._wait_retry_secs)

        inter = Namespace()
        if interrupt not in ["thread", "process"]:
            raise ValueError(
                "`interrupt` value should be one of ['thread', 'process']."
            )
        inter.interrupt = interrupt
        inter.before_interrupt = self._before_interrupt
        tp = get_thread(id) if interrupt == "thread" else get_process(id)
        if tp is None:
            raise ValueError(f"no {interrupt} with id {id}")
        if message is None:
            sid = (
                f"ident={tp.ident}"
                if isinstance(tp, threading.Thread)
                else f"pid={tp.pid}"
            )
            inter.message = f"Interrupting {interrupt} {tp.name} [{sid}] after {self._timeout_secs}s timeout."
        else:
            inter.message = message
        inter.id = tp.ident if isinstance(tp, threading.Thread) else tp.pid
        inter.sig = (
            sig(inter.message)
            if inspect.isclass(sig) and BaseException in inspect.getmro(sig)
            else sig
        )
        inter.wait = wait
        return inter

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        self._interrupt_event.set()
        if not self._last_attempt:
            return False
        if self.timed_out:
            sig = self._last_attempt.sig
            if isinstance(sig, BaseException):
                raise sig
            elif sig is None:
                return True


class Monitoring:
    def __init__(
        self,
        name=None,
        interval_seconds=60,
        check_on_exit=False,
        thread_prefix="monitoring_",
    ):
        self._exec = None
        self._name = name or f"{get_process().name()} [{os.getpid()}]"
        self._interval = interval_seconds
        self._thread_prefix = thread_prefix
        self._interrupt = threading.Event()
        self._check_on_exit = check_on_exit

    def __enter__(self):
        if self._interval > 0:
            self._interrupt.clear()
            self._exec = ThreadPoolExecutor(
                max_workers=1, thread_name_prefix=self._thread_prefix
            )
            self._exec.submit(self._monitor)
        return self

    def __exit__(self, *args):
        if self._exec is not None:
            self._interrupt.set()
            self._exec.shutdown(wait=False)
            if self._check_on_exit:
                self._check_state()
            self._exec = None

    def _monitor(self):
        while not self._interrupt.is_set():
            try:
                self._check_state()
            except Exception as e:
                log.exception(e)
            finally:
                self._interrupt.wait(self._interval)

    def _check_state(self):
        pass


class CPUMonitoring(Monitoring):
    def __init__(
        self,
        name=None,
        interval_seconds=60,
        check_on_exit=False,
        use_interval=False,
        verbosity=0,
        log_level=logging.INFO,
    ):
        super().__init__(
            name=name,
            interval_seconds=0 if use_interval else interval_seconds,
            check_on_exit=check_on_exit,
            thread_prefix="cpu_monitoring_",
        )
        self._interval = interval_seconds if use_interval else None
        self._verbosity = verbosity
        self._log_level = log_level

    def _check_state(self):
        if self._verbosity == 0:
            percent = psutil.cpu_percent(interval=self._interval, percpu=False)
            log.log(
                self._log_level,
                "[MONITORING] [%s] CPU Utilization: %s%%",
                self._name,
                percent,
            )
        elif self._verbosity == 1:
            percent = psutil.cpu_percent(interval=self._interval, percpu=True)
            log.log(
                self._log_level,
                "[MONITORING] [%s] CPU Utilization: %s%%",
                self._name,
                percent,
            )
        elif self._verbosity == 2:
            percent = psutil.cpu_times_percent(interval=self._interval, percpu=False)
            log.log(
                self._log_level,
                "[MONITORING] [%s] CPU Utilization (in percent):\n%s",
                self._name,
                percent,
            )
        elif self._verbosity > 2:
            percent = psutil.cpu_times_percent(interval=self._interval, percpu=True)
            log.log(
                self._log_level,
                "[MONITORING] [%s] CPU Utilization (in percent):\n%s",
                self._name,
                percent,
            )


class SysMemoryMonitoring(Monitoring):
    def __init__(
        self,
        name=None,
        interval_seconds=60,
        check_on_exit=False,
        verbosity=0,
        log_level=logging.INFO,
    ):
        super().__init__(
            name=name,
            interval_seconds=interval_seconds,
            check_on_exit=check_on_exit,
            thread_prefix="sys_memory_monitoring_",
        )
        self._verbosity = verbosity
        self._log_level = log_level

    def _check_state(self):
        if self._verbosity == 0:
            percent = system_memory_mb().used_percentage
            log.log(
                self._log_level,
                "[MONITORING] [%s] Memory Usage: %s%%",
                self._name,
                percent,
            )
        elif self._verbosity == 1:
            mem = system_memory_mb()
            log.log(
                self._log_level,
                "[MONITORING] [%s] Memory Usage (in MB): %s",
                self._name,
                mem,
            )
        elif self._verbosity > 1:
            mem = psutil.virtual_memory()
            log.log(
                self._log_level,
                "[MONITORING] [%s] Memory Usage (in Bytes): %s",
                self._name,
                mem,
            )


class ProcessMemoryMonitoring(Monitoring):
    def __init__(
        self,
        name=None,
        pid=None,
        interval_seconds=60,
        check_on_exit=False,
        verbosity=0,
        log_level=logging.INFO,
    ):
        proc = get_process(pid)
        super().__init__(
            name=name if name else f"{proc.name()} [{proc.pid}]",
            interval_seconds=interval_seconds,
            check_on_exit=check_on_exit,
            thread_prefix="proc_memory_monitoring_",
        )
        self._proc = proc
        self._verbosity = verbosity
        self._log_level = log_level

    def _check_state(self):
        with self._proc.oneshot():
            if not psutil.pid_exists(self._proc.pid):
                self.__exit__()
                return
            if self._verbosity == 0:
                mem = process_memory_mb(self._proc)
                log.log(
                    self._log_level,
                    "[MONITORING] [%s] Process Memory Usage (in MB): %s",
                    self._name,
                    mem,
                )
            else:
                mem = process_memory_mb(self._proc, extended=True)
                log.log(
                    self._log_level,
                    "[MONITORING] [%s] Process Memory Usage (in MB): %s",
                    self._name,
                    mem,
                )
            if "error" in mem:
                self.__exit__()


class VolumeMonitoring(Monitoring):
    def __init__(
        self,
        name=None,
        interval_seconds=60,
        check_on_exit=False,
        root="/",
        verbosity=0,
        log_level=logging.INFO,
    ):
        super().__init__(
            name=name,
            interval_seconds=interval_seconds,
            check_on_exit=check_on_exit,
            thread_prefix="volume_monitoring_",
        )
        self._root = root
        self._verbosity = verbosity
        self._log_level = log_level

    def _check_state(self):
        if self._verbosity == 0:
            percent = system_volume_mb(self._root).used_percentage
            log.log(
                self._log_level,
                "[MONITORING] [%s] Disk Usage: %s%%",
                self._name,
                percent,
            )
        elif self._verbosity == 1:
            du = system_volume_mb(self._root)
            log.log(
                self._log_level,
                "[MONITORING] [%s] Disk Usage (in MB): %s",
                self._name,
                du,
            )
        elif self._verbosity > 1:
            du = psutil.disk_usage(self._root)
            log.log(
                self._log_level,
                "[MONITORING] [%s] Disk Usage (in Bytes): %s",
                self._name,
                du,
            )


class OSMonitoring(Monitoring):
    def __init__(
        self,
        name=None,
        interval_seconds=60,
        check_on_exit=False,
        statistics=("cpu", "proc_memory", "sys_memory", "volume"),
        verbosity=0,
        log_level=logging.INFO,
    ):
        super().__init__(
            name=name, interval_seconds=interval_seconds, check_on_exit=check_on_exit
        )
        self.monitors = []
        if "cpu" in statistics:
            self.monitors.append(
                CPUMonitoring(
                    name=name,
                    interval_seconds=interval_seconds,
                    verbosity=verbosity,
                    log_level=log_level,
                )
            )
        if "proc_memory" in statistics:
            self.monitors.append(
                ProcessMemoryMonitoring(
                    name=name,
                    interval_seconds=interval_seconds,
                    verbosity=verbosity,
                    log_level=log_level,
                )
            )
        if "sys_memory" in statistics:
            self.monitors.append(
                SysMemoryMonitoring(
                    name=name,
                    interval_seconds=interval_seconds,
                    verbosity=verbosity,
                    log_level=log_level,
                )
            )
        if "volume" in statistics:
            self.monitors.append(
                VolumeMonitoring(
                    name=name,
                    interval_seconds=interval_seconds,
                    verbosity=verbosity,
                    log_level=log_level,
                )
            )

    def _check_state(self):
        for monitor in self.monitors:
            monitor._check_state()


class MemoryProfiler:
    def __init__(self, process=psutil.Process(), enabled=True):
        self.ps = process if enabled else None
        self.before_mem = None
        self.after_mem = None

    def __enter__(self):
        if self.ps is not None:
            self.before_mem = self.ps.memory_full_info()
        return self

    def __exit__(self, *args):
        if self.ps is not None:
            self.after_mem = self.ps.memory_full_info()

    def usage(self, before=False):
        if self.ps is not None:
            mem = (
                self.before_mem
                if before
                else self.after_mem
                if self.after_mem is not None
                else self.ps.memory_full_info()
            )
            res = Namespace(
                resident=to_mb(mem.rss), virtual=to_mb(mem.vms), unique=to_mb(mem.uss)
            )
            if not before:
                res.resident_diff = to_mb(mem.rss - self.before_mem.rss)
                res.virtual_diff = to_mb(mem.vms - self.before_mem.vms)
                res.unique_diff = to_mb(mem.uss - self.before_mem.uss)
            return res


def obj_size(o):
    if o is None:
        return 0
    return (
        o.nbytes
        if hasattr(o, "nbytes")  # handling numpy obj size (nbytes property)
        else o.memory_usage(deep=True).sum()
        if hasattr(o, "memory_usage")  # handling pandas obj size
        else sys.getsizeof(o, -1)
    )


def profile(logger=log, log_level=None, duration=True, memory=True):
    def decorator(fn):
        @wraps(fn)
        def profiler(*args, **kwargs):
            nonlocal log_level
            log_level = log_level or (
                logging.TRACE if hasattr(logging, "TRACE") else logging.DEBUG
            )
            if not logger.isEnabledFor(log_level):
                return fn(*args, **kwargs)

            name = fn_name(fn)
            with MemoryProfiler(enabled=memory) as m:
                if memory:
                    mem = m.usage(before=True)
                    logger.log(
                        log_level,
                        "[PROFILING] `%s`\n"
                        "memory before; resident: %.2f MB, virtual: %.2f MB, unique: %.2f MB.\n"
                        "gc before; threshold: %s, gen_count: %s, perm_count: %s",
                        name,
                        mem.resident,
                        mem.virtual,
                        mem.unique,
                        gc.get_threshold(),
                        gc.get_count(),
                        gc.get_freeze_count(),
                    )
                with Timer(enabled=duration) as t:
                    ret = fn(*args, **kwargs)
            if duration:
                logger.log(
                    log_level, "[PROFILING] `%s` executed in %.3fs.", name, t.duration
                )
            if memory:
                ret_size = obj_size(ret)
                if ret_size > 0:
                    logger.log(
                        log_level,
                        "[PROFILING] `%s` returned object size: %.3f MB.",
                        name,
                        to_mb(ret_size),
                    )
                mem = m.usage()
                logger.log(
                    log_level,
                    "[PROFILING] `%s`\n"
                    "memory after; resident: %+.2f MB/%.2f MB, virtual: %+.2f MB/%.2f MB, unique: %+.2f MB/%.2f MB.\n"
                    "gc after; threshold: %s, gen_count: %s, perm_count: %s",
                    name,
                    mem.resident_diff,
                    mem.resident,
                    mem.virtual_diff,
                    mem.virtual,
                    mem.unique_diff,
                    mem.unique,
                    gc.get_threshold(),
                    gc.get_count(),
                    gc.get_freeze_count(),
                )
            return ret

        return profiler

    return decorator


__all__ = [s for s in dir() if not s.startswith("_") and s not in __no_export]
