"""Versioned SHA-256 counter timing; no interpreter-dependent random/hash state."""

import hashlib

from ..models import Episode
from ..models.base import canonical_bytes, content_hash
from ..models.episode import ActionRequest
from ..models.production import Fingerprint
from .curves import TimelineError

ALGORITHM = {
    "name": "tabi-sha256-counter",
    "version": "1",
    "encoding": "canonical-json({domain,version,seed,id,counter}) UTF-8; big-endian SHA-256",
    "range": "reject integers >= 2**256 - (2**256 % width); then modulo width",
    "placement": "start + inclusive gap, then previous end + inclusive gap; whole actions only",
}


def prng_fingerprint() -> Fingerprint:
    return Fingerprint(
        name=ALGORITHM["name"], version=ALGORITHM["version"], sha256=content_hash(ALGORITHM)
    )


class CounterRandom:
    def __init__(self, seed: int, identity: str):
        self.seed, self.identity, self.counter = seed, identity, 0

    def below(self, width: int) -> int:
        if type(width) is not int or not 0 < width <= 2**256:
            raise TimelineError("random width must be an integer in 1..2**256")
        limit = 2**256 - (2**256 % width)
        while True:
            payload = canonical_bytes(
                {
                    "domain": ALGORITHM["name"],
                    "version": ALGORITHM["version"],
                    "seed": self.seed,
                    "id": self.identity,
                    "counter": self.counter,
                }
            )
            self.counter += 1
            number = int.from_bytes(hashlib.sha256(payload).digest(), "big")
            if number < limit:
                return number % width


def expand_random_actions(episode: Episode) -> list[ActionRequest]:
    episode = Episode.model_validate(episode)
    result = list(episode.actions)
    for timing in sorted(episode.random_actions, key=lambda timing: timing.id):
        random = CounterRandom(episode.seed, timing.id)
        frame, index = timing.start_frame, 0
        while True:
            frame += timing.minimum_gap_frames + random.below(
                timing.maximum_gap_frames - timing.minimum_gap_frames + 1
            )
            if frame + timing.duration_frames > timing.end_frame:
                break
            identity = hashlib.sha256(
                canonical_bytes({"timing": timing.id, "index": index})
            ).hexdigest()[:24]
            result.append(
                ActionRequest(
                    id=f"random.{identity}",
                    scene_id=timing.scene_id,
                    pack=timing.pack,
                    action_id=timing.action_id,
                    version=timing.version,
                    channel=timing.channel,
                    repeat=timing.repeat,
                    start_frame=frame,
                    end_frame=frame + timing.duration_frames,
                )
            )
            frame += timing.duration_frames
            index += 1
            if len(result) > 100000:
                raise TimelineError(
                    "expanded schedule exceeds 100,000 actions; narrow timing ranges"
                )
    result.sort(key=lambda action: (action.start_frame, action.scene_id, action.channel, action.id))
    # Use the shared structural checks to reject generated collisions, never silently drop them.
    Episode.model_validate({**episode.model_dump(), "actions": result, "random_actions": []})
    return result
