"""Local review evidence. Diagnostics never substitute for visual acceptance."""

import json
import statistics
from uuid import uuid4

from ..assets.probe import probe_media
from ..assets.service import digest_file
from ..models.base import Crop, FrameInterval, HashedFile, MediaPath
from ..process import run_tool
from .service import FlowError, updated
from .shots import remaining_frames, shot_by_id


def repeated_ranges(frames: list[bytes], *, minimum: int) -> list[dict]:
    ranges, start = [], 0
    for index in range(1, len(frames) + 1):
        if index < len(frames) and frames[index] == frames[start]:
            continue
        if index - start >= minimum:
            ranges.append({"start_frame": start, "end_frame": index})
        start = index
    return ranges


def difference(first: bytes, second: bytes) -> float:
    return statistics.fmean(abs(a - b) for a, b in zip(first, second, strict=True))


class FlowReview:
    def __init__(self, service, settings):
        self.service, self.settings = service, settings

    def prepare(
        self,
        episode_id,
        candidate_id,
        *,
        revision: int,
        window: Crop | None = None,
        trim: FrameInterval | None = None,
        media_sha256: str | None = None,
    ):
        episode = self.service.get(episode_id)
        if episode.revision != revision:
            raise FlowError("Video changed; reload its review.")
        candidate = self.service.candidate(episode, candidate_id)
        if trim is not None:
            self._validate_section(episode, candidate, trim, media_sha256)
            candidate = updated(candidate, trim=trim, review_packet=None)
        path = self.service.verify_file(candidate.media)
        probe = probe_media(
            [path], "video", fps=None, ffmpeg=self.settings.ffmpeg, ffprobe=self.settings.ffprobe
        )
        if (probe.fps, probe.canvas, probe.frame_count) != (
            candidate.fps,
            candidate.canvas,
            candidate.frame_count,
        ):
            raise FlowError("Clip time or canvas differs from its imported record.")
        parent = (
            self.service.candidate(episode, candidate.parent_id) if candidate.parent_id else None
        )
        if parent and (parent.canvas != candidate.canvas or parent.fps != candidate.fps):
            raise FlowError("Continuation canvas or frame rate changed; request a compatible clip.")
        if window and (
            window.x + window.width > candidate.canvas.width
            or window.y + window.height > candidate.canvas.height
        ):
            raise FlowError("Window region is outside the picture.")
        folder = f".cache/flow-review/{candidate.id}/{uuid4().hex}"
        with self.service.store._directory(tuple(folder.split("/")), create=True):
            pass
        root = self.service.store.root / folder
        first, end = candidate.trim.start_frame, candidate.trim.end_frame
        selected = candidate.media.model_dump(mode="json")
        if first != 0 or end != candidate.frame_count:
            selected_path = root / "selected.mp4"
            run_tool(
                [
                    self.settings.ffmpeg,
                    "-v",
                    "error",
                    "-xerror",
                    "-nostdin",
                    "-protocol_whitelist",
                    "file,pipe",
                    "-i",
                    str(path),
                    "-vf",
                    f"trim=start_frame={first}:end_frame={end},setpts=PTS-STARTPTS",
                    "-an",
                    "-c:v",
                    "libx264",
                    "-pix_fmt",
                    "yuv420p",
                    "-movflags",
                    "+faststart",
                    str(selected_path),
                ],
                timeout=300,
            )
            selected_probe = probe_media(
                [selected_path],
                "video",
                fps=None,
                ffmpeg=self.settings.ffmpeg,
                ffprobe=self.settings.ffprobe,
            )
            if (selected_probe.frame_count, selected_probe.fps, selected_probe.canvas) != (
                end - first,
                candidate.fps,
                candidate.canvas,
            ):
                raise FlowError("Selected preview does not match the requested section.")
            selected = self._record(selected_path, f"{folder}/selected.mp4")
        samples = sorted(
            {
                first,
                first + (end - first) // 4,
                first + (end - first) // 2,
                first + 3 * (end - first) // 4,
                end - 1,
            }
        )
        images = []
        for frame in samples:
            output = root / f"candidate-{frame}.png"
            self._image(path, frame, output)
            images.append(
                {
                    "role": "candidate",
                    "frame": frame,
                    "media": self._record(output, f"{folder}/{output.name}"),
                }
            )
        cut = first + remaining_frames(episode)
        if episode.recipe.shots and first < cut <= end:
            output = root / "planned-ending.png"
            self._image(path, cut - 1, output)
            images.append(
                {
                    "role": "planned ending",
                    "frame": cut - 1,
                    "media": self._record(output, f"{folder}/{output.name}"),
                }
            )
        attempt = next(a for a in episode.attempts if a.id == candidate.attempt_id)
        shot = shot_by_id(episode, attempt.shot_id)
        camera_cut = attempt.mode == "shot_start" and parent is not None
        seam = None
        seam_difference = None
        if parent:
            parent_path = self.service.verify_file(parent.media)
            output = root / "parent-ending.png"
            self._image(parent_path, parent.trim.end_frame - 1, output)
            images.insert(
                0,
                {
                    "role": "parent",
                    "frame": parent.trim.end_frame - 1,
                    "media": self._record(output, f"{folder}/{output.name}"),
                },
            )
            tail = max(parent.trim.start_frame, parent.trim.end_frame - 24)
            head = min(end, first + 24)
            graph = (
                f"[0:v]trim=start_frame={tail}:end_frame={parent.trim.end_frame},"
                "setpts=PTS-STARTPTS[a];"
                f"[1:v]trim=start_frame={first}:end_frame={head},setpts=PTS-STARTPTS[b];"
                "[a][b]concat=n=2:v=1:a=0[v]"
            )
            seam_path = root / "join.mp4"
            run_tool(
                [
                    self.settings.ffmpeg,
                    "-v",
                    "error",
                    "-xerror",
                    "-nostdin",
                    "-protocol_whitelist",
                    "file,pipe",
                    "-i",
                    str(parent_path),
                    "-protocol_whitelist",
                    "file,pipe",
                    "-i",
                    str(path),
                    "-filter_complex",
                    graph,
                    "-map",
                    "[v]",
                    "-an",
                    "-c:v",
                    "libx264",
                    "-pix_fmt",
                    "yuv420p",
                    "-movflags",
                    "+faststart",
                    str(seam_path),
                ],
                timeout=300,
            )
            seam = self._record(seam_path, f"{folder}/join.mp4")
            seam_difference = difference(
                self._frames(parent_path, parent.trim.end_frame - 1, parent.trim.end_frame)[0],
                self._frames(path, first, first + 1)[0],
            )
        frames = self._frames(path, first, min(end, first + 7200), window)
        repeats = repeated_ranges(
            frames, minimum=max(2, round(2 * candidate.fps.num / candidate.fps.den))
        )
        for interval in repeats:
            interval["start_frame"] += first
            interval["end_frame"] += first
        cuts = [
            {"start_frame": first + index - 1, "end_frame": first + index + 1}
            for index in range(1, len(frames))
            if difference(frames[index - 1], frames[index]) > 40
        ]
        packet = {
            "schema_version": "1.0",
            "episode_id": episode.id,
            "candidate_id": candidate.id,
            "candidate_sha256": candidate.media.sha256,
            "candidate_trim": candidate.trim.model_dump(mode="json"),
            "selected_video": selected,
            "parent_sha256": candidate.parent_sha256,
            "reference_hashes": [item.media.sha256 for item in episode.references],
            "images": images,
            "join_video": seam,
            "diagnostics": {
                "join_kind": "camera cut"
                if camera_cut
                else "continuation"
                if parent
                else "opening",
                "timestamp_schedule": "verified",
                "repeated_scaled_frames": repeats,
                "possible_cut_ranges": cuts,
                "seam_mean_difference": seam_difference,
                "window_motion": "needs visual review"
                if window
                else "unassessed: window region not selected",
                "scan_complete": len(frames) == end - first,
                "advisory_only": True,
            },
            "review_checklist": [
                "Original identity and attached gills",
                "Connected neck and two arms",
                "Cup, hands, book and bag",
                "Matched character/props, travel direction and lighting across the camera cut"
                if camera_cut
                else "Fixed camera and continuous exterior",
                "Clear cabin air and stable mouth; no spreading particles",
                "Requested action completion and actual ending state",
            ],
        }
        if shot is not None and shot.exterior:
            packet["review_checklist"].extend(
                [
                    "Planned window view: " + shot.exterior,
                    "Level horizon, correct window perspective and foreground occlusion; "
                    "consistent travel direction and parallax through the final frame",
                    "The district advances at this camera cut; the view stays consistent "
                    "within the shot"
                    if camera_cut
                    else "The assigned scenery keeps progressing without repeating or resetting",
                ]
            )
        packet_path = f"{folder}/packet.json"
        with self.service.store.writer_lock():
            self.service.store._atomic_write(
                packet_path, json.dumps(packet).encode(), overwrite=False
            )
        candidate = updated(candidate, review_packet=packet_path)
        return self.service.save(
            updated(
                episode,
                candidates=[
                    candidate if item.id == candidate.id else item for item in episode.candidates
                ],
            ),
            expected_revision=revision,
        )

    def read(self, candidate):
        if not candidate.review_packet:
            raise FlowError("Prepare the clip review first.")
        packet = json.loads(self.service.store._read_bytes(candidate.review_packet))
        if packet["candidate_sha256"] != candidate.media.sha256 or (
            "candidate_trim" in packet
            and packet["candidate_trim"] != candidate.trim.model_dump(mode="json")
            and candidate.review == "pending"
        ):
            raise FlowError("Review packet is stale.")
        return packet

    @staticmethod
    def _validate_section(episode, candidate, trim, media_sha256):
        if candidate.review != "pending" or candidate.media.sha256 != media_sha256:
            raise FlowError("Section is stale or this clip has already been reviewed.")
        parent = episode.accepted_ids[-1] if episode.accepted_ids else None
        if candidate.parent_id != parent:
            raise FlowError("This clip belongs to an old branch; reload the active clip.")
        if trim.end_frame > candidate.frame_count:
            raise FlowError("Section exceeds the decoded source frames.")
        attempt = next(a for a in episode.attempts if a.id == candidate.attempt_id)
        if attempt.mode == "extend" and trim.start_frame != candidate.trim.start_frame:
            raise FlowError("Keep the opening of a continuation to preserve its join.")
        if (
            trim.end_frame < candidate.frame_count
            and trim.end_frame - trim.start_frame < remaining_frames(episode)
        ):
            raise FlowError(
                "Keep the source ending while this shot still needs an extension. "
                "An early ending is available when the section completes the shot."
            )

    def _record(self, path, relative):
        digest, size = digest_file(path)
        return HashedFile(
            location=MediaPath(path=relative), sha256=digest, size_bytes=size
        ).model_dump(mode="json")

    def _image(self, path, frame, output):
        run_tool(
            [
                self.settings.ffmpeg,
                "-v",
                "error",
                "-xerror",
                "-nostdin",
                "-protocol_whitelist",
                "file,pipe",
                "-i",
                str(path),
                "-vf",
                f"select=eq(n\\,{frame})",
                "-frames:v",
                "1",
                str(output),
            ],
            timeout=300,
        )

    def _frames(self, path, start, end, crop=None):
        crop_filter = f",crop={crop.width}:{crop.height}:{crop.x}:{crop.y}" if crop else ""
        output = run_tool(
            [
                self.settings.ffmpeg,
                "-v",
                "error",
                "-xerror",
                "-nostdin",
                "-protocol_whitelist",
                "file,pipe",
                "-i",
                str(path),
                "-an",
                "-vf",
                f"trim=start_frame={start}:end_frame={end}{crop_filter},scale=64:36,format=gray",
                "-fps_mode",
                "passthrough",
                "-f",
                "rawvideo",
                "-",
            ],
            timeout=300,
            max_bytes=32 * 1024 * 1024,
        )
        size = 64 * 36
        if len(output) != (end - start) * size:
            raise FlowError("Review decode does not cover the requested frames.")
        return [output[index : index + size] for index in range(0, len(output), size)]
