"""Bounded subprocess execution for trusted local tools; never invoke a shell."""

import subprocess
import tempfile
from pathlib import Path


class ToolError(RuntimeError):
    pass


def run_tool(
    args: list[str],
    *,
    timeout: float = 15,
    max_bytes: int = 2 * 1024 * 1024,
    capture_stderr: bool = False,
) -> bytes:
    """Keep tool output off the Python heap until its size has been checked.

    subprocess.run kills and waits for its own child on timeout. This does not
    implement the persistent job/cancellation service planned in T20.
    """
    with tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as errors:
        try:
            result = subprocess.run(
                args,
                stdin=subprocess.DEVNULL,
                stdout=output,
                stderr=errors,
                timeout=timeout,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise ToolError(f"{Path(args[0]).name}: {error}") from error
        if result.returncode:
            errors.seek(max(0, errors.tell() - 4096))
            message = errors.read().decode("utf-8", errors="replace").strip()
            raise ToolError(f"{Path(args[0]).name} exited {result.returncode}: {message}")
        if output.tell() + (errors.tell() if capture_stderr else 0) > max_bytes:
            raise ToolError(f"{Path(args[0]).name}: output exceeds {max_bytes} bytes")
        output.seek(0)
        errors.seek(0)
        return output.read() + (errors.read() if capture_stderr else b"")
