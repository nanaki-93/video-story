"""Observe local media capabilities without claiming a listed encoder works."""

import hashlib
import os
import platform
import re
import shutil
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from .config import Settings
from .models.base import content_hash
from .models.diagnostics import CapabilityReport, MachineInfo, StorageInfo, ToolInfo
from .models.production import ValidationIssue
from .process import ToolError, run_tool

REQUIRED_FILTERS = {
    "alphamerge",
    "overlay",
    "crop",
    "format",
    "scale",
    "fps",
    "setpts",
    "setparams",
    "trim",
    "atrim",
    "aresample",
    "aformat",
    "apad",
    "loudnorm",
}
REQUIRED_ENCODERS = {"libx264", "aac"}
MIN_FREE_BYTES = 256 * 1024 * 1024


def file_hash(path: Path) -> str:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def issue(code: str, location: str, message: str, fix: str) -> ValidationIssue:
    return ValidationIssue(
        severity="error",
        code=code,
        location=[location],
        message=message,
        suggested_fix=fix,
    )


def machine_info() -> MachineInfo:
    system = platform.system()
    cpu, memory = platform.processor() or "unknown", None
    if system == "Darwin":
        try:
            cpu = run_tool(["/usr/sbin/sysctl", "-n", "machdep.cpu.brand_string"]).decode().strip()
            memory = int(run_tool(["/usr/sbin/sysctl", "-n", "hw.memsize"]))
        except (ToolError, ValueError):
            pass
    else:
        try:
            memory = os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")
        except (ValueError, OSError, AttributeError):
            pass
    return MachineInfo(
        os=system,
        os_version=platform.mac_ver()[0] if system == "Darwin" else platform.release(),
        architecture=platform.machine(),
        cpu=cpu,
        memory_bytes=memory,
        python_version=platform.python_version(),
        python_executable=sys.executable,
        is_target_m5_pro=system == "Darwin"
        and platform.machine() == "arm64"
        and cpu == "Apple M5 Pro",
    )


def probe_tool(name: str, requested: str) -> tuple[ToolInfo, list[ValidationIssue]]:
    found = shutil.which(requested)
    fix = (
        f"Install FFmpeg with ffprobe (macOS: brew install ffmpeg), or set TABI_{name.upper()} "
        f"/ tools.{name} to an executable from the same installation."
    )
    if not found:
        return ToolInfo(requested=requested), [
            issue("tool_missing", name, f"Executable not found: {requested}", fix)
        ]
    path = Path(found).resolve()
    try:
        output = run_tool([str(path), "-version"]).decode("utf-8", errors="replace").strip()
        match = re.match(rf"^{name} version (\S+)", output)
        if not match:
            raise ToolError(f"{path} did not identify itself as {name}")
        return ToolInfo(
            requested=requested,
            path=str(path),
            version=match[1],
            version_output=output,
            sha256=file_hash(path),
        ), []
    except (ToolError, OSError) as error:
        return ToolInfo(requested=requested, path=str(path)), [
            issue("tool_probe_failed", name, str(error), fix)
        ]


def parse_listing(output: str, kind: str) -> list[str]:
    # FFmpeg 9 has two filter flags; older versions have three. Skip
    # their legend rows (which use '=' in place of an identifier).
    pattern = (
        r"^\s*[TSC.]{2,3}\s+([a-zA-Z0-9_]+)\s"
        if kind == "filters"
        else r"^\s*[VAS.][A-Z.]{5}\s+([a-zA-Z0-9_]+)\s"
    )
    return sorted(set(re.findall(pattern, output, flags=re.M)))


def probe_storage(path: Path) -> tuple[StorageInfo, list[ValidationIssue]]:
    root = path.expanduser().resolve()
    free, writable, problems = None, False, []
    try:
        if not root.is_dir():
            raise OSError("output directory does not exist or is not a directory")
        free = shutil.disk_usage(root).free
        with tempfile.TemporaryFile(dir=root) as probe:
            probe.write(b"tabi writable storage probe")
            probe.flush()
            os.fsync(probe.fileno())
            probe.seek(0)
            if probe.read() != b"tabi writable storage probe":
                raise OSError("temporary write verification failed")
        writable = True
        if free < MIN_FREE_BYTES:
            problems.append(
                issue(
                    "storage_low",
                    "storage",
                    f"Only {free} bytes free; need {MIN_FREE_BYTES} for the spike.",
                    "Free space or select another --output-dir.",
                )
            )
    except OSError as error:
        problems.append(
            issue(
                "storage_unwritable",
                "storage",
                str(error),
                "Create a writable local directory and pass --output-dir PATH.",
            )
        )
    return StorageInfo(
        path=str(root), writable=writable, free_bytes=free, required_free_bytes=MIN_FREE_BYTES
    ), problems


def doctor(settings: Settings, output_dir: Path) -> CapabilityReport:
    machine = machine_info()
    ffmpeg, problems = probe_tool("ffmpeg", settings.ffmpeg)
    ffprobe, probe_problems = probe_tool("ffprobe", settings.ffprobe)
    problems.extend(probe_problems)
    filters, encoders, hardware = [], [], []
    if ffmpeg.version:
        try:
            filters = parse_listing(
                run_tool([ffmpeg.path, "-hide_banner", "-filters"]).decode(), "filters"
            )
            encoders = parse_listing(
                run_tool([ffmpeg.path, "-hide_banner", "-encoders"]).decode(), "encoders"
            )
            hardware = sorted(
                line.strip()
                for line in run_tool([ffmpeg.path, "-hide_banner", "-hwaccels"])
                .decode()
                .splitlines()
                if line.strip() and not line.endswith(":")
            )
            for kind, required, observed in [
                ("filters", REQUIRED_FILTERS, filters),
                ("encoders", REQUIRED_ENCODERS, encoders),
            ]:
                missing = required - set(observed)
                if missing:
                    problems.append(
                        issue(
                            "capability_missing",
                            kind,
                            f"Missing {kind}: {', '.join(sorted(missing))}",
                            "Use an FFmpeg build with these features; on macOS the Homebrew "
                            "ffmpeg formula provides the tested baseline.",
                        )
                    )
        except (ToolError, UnicodeError) as error:
            problems.append(
                issue(
                    "capability_probe_failed",
                    "ffmpeg",
                    str(error),
                    "Check the configured FFmpeg executable and its -filters/-encoders output.",
                )
            )
    if ffmpeg.version and ffprobe.version and ffmpeg.version != ffprobe.version:
        problems.append(
            issue(
                "tool_version_mismatch",
                "ffprobe",
                "FFmpeg and ffprobe versions differ.",
                "Configure both executables from the same installation.",
            )
        )
    if not (3, 11) <= sys.version_info[:2] < (3, 13):
        problems.append(
            issue(
                "python_unsupported",
                "python",
                "Supported Python versions are 3.11 and 3.12.",
                "Install the repository's pinned Python and run make setup.",
            )
        )
    storage, storage_problems = probe_storage(output_dir)
    problems.extend(storage_problems)
    fingerprint = content_hash(
        {
            "ffmpeg": ffmpeg.model_dump(),
            "ffprobe": ffprobe.model_dump(),
            "filters": filters,
            "encoders": encoders,
            "hardware_accelerators": hardware,
        }
    )
    return CapabilityReport(
        schema_version="1.0",
        observed_at=datetime.now(UTC),
        machine=machine,
        ffmpeg=ffmpeg,
        ffprobe=ffprobe,
        filters=filters,
        encoders=encoders,
        hardware_accelerators=hardware,
        required_filters=sorted(REQUIRED_FILTERS),
        required_encoders=sorted(REQUIRED_ENCODERS),
        storage=storage,
        fingerprint=fingerprint,
        ready=not problems,
        issues=problems,
    )
