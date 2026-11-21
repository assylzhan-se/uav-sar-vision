"""Merging repeated detections of the same person across video frames (FR-12).

In a video the same person appears on many frames. Without merging the operator would get
dozens of identical findings. The tracker links a detection to an existing track when its
centre is close to the track's last centre (relative to the box size) and keeps the best
(most confident) detection of every track.

Limitation: the drone's own motion is not compensated yet (planned: telemetry-based
compensation, see literature review 2, paper 8). Sample frames often enough (about 1 s).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from .schema import Detection


@dataclass
class Track:
    track_id: int
    best: Detection
    last: Detection
    last_frame: int
    hits: int = 1
    frames: list[int] = field(default_factory=list)


def _centre_distance(a: Detection, b: Detection) -> float:
    (ax, ay), (bx, by) = a.center, b.center
    return math.hypot(ax - bx, ay - by)


def _size(d: Detection) -> float:
    return math.hypot(d.x2 - d.x1, d.y2 - d.y1)


class SimpleTracker:
    """Greedy nearest-centre tracker.

    max_distance: how far (in box diagonals) the centre may move between sampled frames.
    max_gap:      after how many sampled frames without a match a track is closed.
    """

    def __init__(self, max_distance: float = 2.0, max_gap: int = 3) -> None:
        if max_distance <= 0 or max_gap < 1:
            raise ValueError("max_distance must be > 0 and max_gap >= 1")
        self.max_distance = max_distance
        self.max_gap = max_gap
        self.tracks: list[Track] = []
        self._step = 0
        self._next_id = 1

    def update(self, detections: list[Detection]) -> list[int]:
        """Add the detections of the next sampled frame. Returns the track id of each."""
        self._step += 1
        active = [t for t in self.tracks if self._step - t.last_frame <= self.max_gap]
        pairs = []
        for i, d in enumerate(detections):
            for t in active:
                dist = _centre_distance(d, t.last) / max(_size(d), _size(t.last), 1.0)
                if dist <= self.max_distance:
                    pairs.append((dist, i, t))
        pairs.sort(key=lambda p: p[0])
        ids: list[int | None] = [None] * len(detections)
        used_tracks: set[int] = set()
        for _, i, t in pairs:
            if ids[i] is not None or t.track_id in used_tracks:
                continue
            d = detections[i]
            ids[i] = t.track_id
            used_tracks.add(t.track_id)
            t.last, t.last_frame, t.hits = d, self._step, t.hits + 1
            t.frames.append(d.frame)
            if d.confidence > t.best.confidence:
                t.best = d
        for i, d in enumerate(detections):
            if ids[i] is None:
                t = Track(self._next_id, best=d, last=d, last_frame=self._step, frames=[d.frame])
                self.tracks.append(t)
                ids[i] = t.track_id
                self._next_id += 1
        return [int(i) for i in ids]

    def summary(self, min_hits: int = 1) -> list[Track]:
        """Tracks seen at least `min_hits` times; min_hits=2 removes one-frame flickers."""
        return [t for t in self.tracks if t.hits >= min_hits]
