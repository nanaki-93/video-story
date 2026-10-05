"""Check P01 evidence integrity, without granting artistic or legal approval."""

import argparse
import hashlib
import json
import struct
import subprocess
from pathlib import Path
from typing import Literal

from PIL import Image
from pydantic import BaseModel, ConfigDict, Field

REQUIRED_GATES = {
    "likeness",
    "frills_and_anatomy",
    "breathing_and_head_turn",
    "walking",
    "train_and_cafe_reuse",
    "different_garment",
    "cup_contact",
    "deep_breath",
    "light_and_dark_motion",
    "restart_reuse",
    "production_rehearsal",
    "automation",
    "commercial_rights",
    "user_visual_review",
}


class StrictRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Artifact(StrictRecord):
    path: str
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    kind: Literal["file", "image", "video", "glb"]
    role: str
    width: int | None = Field(default=None, gt=0)
    height: int | None = Field(default=None, gt=0)
    frames: int | None = Field(default=None, gt=0)
    fps: str | None = None
    master_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")


class Gate(StrictRecord):
    status: Literal["passed", "failed", "not_run", "pending"]
    evidence: str


class LicenseReview(StrictRecord):
    component: str
    revision: str
    disposition: Literal["used_reviewed", "excluded", "pending", "attempted_not_used"]
    license: str
    urls: list[str]
    obligations_and_limits: str


class Report(StrictRecord):
    schema_version: Literal["1.0"]
    task_id: Literal["P01"]
    review_date: str
    decision: Literal["no_go", "pending", "go"]
    decision_scope: str
    production_ready: bool
    user_visual_approval: Literal["pending", "approved", "rejected"]
    summary: str
    master_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    artifacts: list[Artifact]
    gates: dict[str, Gate]
    licenses: list[LicenseReview]
    environment: dict[str, str]
    measurements: dict[str, str | int | float | bool | None]
    operations: list[str]
    unresolved: list[str]
    generation_prompt: str


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def verify(report: Report, root: Path, ffprobe: str = "ffprobe") -> int:
    root = root.resolve()
    if set(report.gates) != REQUIRED_GATES:
        raise ValueError("The report must account for every P01 acceptance gate")
    if report.production_ready != (report.decision == "go"):
        raise ValueError("Production readiness contradicts the recorded decision")
    if report.decision == "no_go" and not any(
        gate.status == "failed" for gate in report.gates.values()
    ):
        raise ValueError("A no-go decision must record the failed gate")
    if report.decision == "go":
        if report.user_visual_approval != "approved" or any(
            gate.status != "passed" for gate in report.gates.values()
        ):
            raise ValueError("Unperformed or unapproved gates cannot support a go decision")
        videos = [a for a in report.artifacts if a.kind == "video" and a.master_sha256]
        if len(videos) < 2:
            raise ValueError("A go decision needs multiple outputs reusing the master")
    paths = set()
    masters = []
    for artifact in report.artifacts:
        relative = Path(artifact.path)
        path = (root / relative).resolve()
        if relative.is_absolute() or ".." in relative.parts or not path.is_relative_to(root):
            raise ValueError(f"Evidence path escapes the project: {artifact.path}")
        if path in paths:
            raise ValueError(f"Duplicate evidence path: {artifact.path}")
        paths.add(path)
        if not path.is_file() or digest(path) != artifact.sha256:
            raise ValueError(f"Missing or changed evidence: {artifact.path}")
        if artifact.role == "master":
            masters.append(artifact.sha256)
        if artifact.master_sha256 and artifact.master_sha256 != report.master_sha256:
            raise ValueError(f"Master identity changed: {artifact.path}")
        if artifact.kind == "image":
            with Image.open(path) as image:
                image.load()
                if image.size != (artifact.width, artifact.height):
                    raise ValueError(f"Image dimensions changed: {artifact.path}")
        elif artifact.kind == "glb":
            with path.open("rb") as stream:
                header = stream.read(12)
            if len(header) != 12 or struct.unpack("<4sII", header) != (
                b"glTF",
                2,
                path.stat().st_size,
            ):
                raise ValueError(f"Invalid GLB header: {artifact.path}")
        elif artifact.kind == "video":
            result = subprocess.run(
                [
                    ffprobe,
                    "-v",
                    "error",
                    "-select_streams",
                    "v:0",
                    "-count_frames",
                    "-show_entries",
                    "stream=width,height,nb_read_frames,r_frame_rate",
                    "-of",
                    "json",
                    str(path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            stream = json.loads(result.stdout)["streams"][0]
            measured = (
                stream["width"],
                stream["height"],
                int(stream["nb_read_frames"]),
                stream["r_frame_rate"],
            )
            if measured != (artifact.width, artifact.height, artifact.frames, artifact.fps):
                raise ValueError(f"Video metadata changed: {artifact.path}")
    if masters != [report.master_sha256]:
        raise ValueError("Exactly one recorded master must match the candidate identity")
    return len(paths)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--ffprobe", default="ffprobe")
    parser.add_argument("--require-go", action="store_true")
    args = parser.parse_args()
    report = Report.model_validate_json(args.report.read_text())
    count = verify(report, args.root, args.ffprobe)
    print(f"Evidence integrity verified: {count} files. Decision: {report.decision}.")
    print("This check does not grant visual, commercial-rights or publication approval.")
    if not report.production_ready:
        print("P01 production feasibility has NOT passed.")
    return 2 if args.require_go and report.decision != "go" else 0


if __name__ == "__main__":
    raise SystemExit(main())
