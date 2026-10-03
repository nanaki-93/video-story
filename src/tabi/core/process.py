"""Bounded subprocess execution for trusted local tools; never invoke a shell."""

import subprocess
import tempfile
import time
from collections.abc import Callable
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from pathlib import Path


class ToolError(RuntimeError):
    pass


class OperationCancelled(ToolError):
    pass


@dataclass
class ExecutionScope:
    cancelled: Callable[[], bool]
    on_process: Callable[[subprocess.Popen], None] | None = None
    last_check: float = field(default=0, init=False)

    def check(self, *, force=False):
        now = time.monotonic()
        if force or now - self.last_check >= 0.1:
            self.last_check = now
            if self.cancelled():
                raise OperationCancelled("the owned job was cancelled")


_scope: ContextVar[ExecutionScope | None] = ContextVar("tabi_execution_scope", default=None)


@contextmanager
def execution_scope(scope: ExecutionScope):
    token = _scope.set(scope)
    try:
        checkpoint(force=True)
        yield scope
    finally:
        _scope.reset(token)


def checkpoint(*, force=False):
    if scope := _scope.get():
        scope.check(force=force)


def _stop_owned(process):
    # Only a retained, unreaped Popen child is signalled. No persisted PID lookup,
    # process-name matching, process-group broadcast, or adoption after restart.
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def run_tool(
    args: list[str],
    *,
    timeout: float = 15,
    max_bytes: int = 2 * 1024 * 1024,
    capture_stderr: bool = False,
) -> bytes:
    """Keep tool output off the Python heap until its size has been checked.

    Cancellation is scoped to the calling job and checked during tool execution.
    Output is disk-backed and bounded; every error reaps only this call's child.
    """
    with tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as errors:
        checkpoint(force=True)
        try:
            process = subprocess.Popen(
                args,
                stdin=subprocess.DEVNULL,
                stdout=output,
                stderr=errors,
                close_fds=True,
            )
        except OSError as error:
            raise ToolError(f"{Path(args[0]).name}: {error}") from error
        try:
            if (scope := _scope.get()) and scope.on_process:
                scope.on_process(process)
            deadline = time.monotonic() + timeout
            while process.poll() is None:
                checkpoint()
                if output.tell() > max_bytes or errors.tell() > max(max_bytes, 8 * 1024 * 1024):
                    raise ToolError(f"{Path(args[0]).name}: output exceeds its byte limit")
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise ToolError(f"{Path(args[0]).name}: timed out after {timeout} seconds")
                try:
                    process.wait(timeout=min(0.1, remaining))
                except subprocess.TimeoutExpired:
                    pass
            checkpoint(force=True)
        except BaseException:
            _stop_owned(process)
            raise
        if process.returncode:
            errors.seek(max(0, errors.tell() - 4096))
            message = errors.read().decode("utf-8", errors="replace").strip()
            raise ToolError(f"{Path(args[0]).name} exited {process.returncode}: {message}")
        if output.tell() + (errors.tell() if capture_stderr else 0) > max_bytes:
            raise ToolError(f"{Path(args[0]).name}: output exceeds {max_bytes} bytes")
        output.seek(0)
        errors.seek(0)
        return output.read() + (errors.read() if capture_stderr else b"")
