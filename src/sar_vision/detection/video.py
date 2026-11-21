"""Video processing: sample frames, detect people, merge repeated detections into tracks."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Protocol

import numpy as np

from .schema import Detection
from .tracking import SimpleTracker


class _Detector(Protocol):
    def detect(self, image: np.ndarray, frame: int = 0) -> list[Detection]: ...


@dataclass
class VideoFinding:
    """One person in a video: the best detection of a track and the frame it was taken from."""
    track_id: int
    detection: Detection      # best (most confident) detection; .frame = frame number
    time_s: float             # time of that frame in the video
    hits: int                 # on how many sampled frames the person was seen
    frame_image: np.ndarray   # the frame itself (BGR), to show the operator


def iter_frames(path: str | Path, every_s: float = 1.0,
                max_frames: int | None = None) -> Iterator[tuple[int, float, np.ndarray]]:
    """Yield (frame_number, time_s, image) every `every_s` seconds of the video."""
    import cv2
    if every_s <= 0:
        raise ValueError("every_s must be positive")
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise FileNotFoundError(f"cannot open video: {path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    step = max(1, round(fps * every_s))
    n = taken = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if n % step == 0:
                yield n, n / fps, frame
                taken += 1
                if max_frames is not None and taken >= max_frames:
                    break
            n += 1
    finally:
        cap.release()


def process_video(path: str | Path, detector: _Detector, every_s: float = 1.0,
                  min_hits: int = 1, max_frames: int | None = 600,
                  tracker: SimpleTracker | None = None) -> tuple[list[VideoFinding], dict]:
    """Run the detector on sampled frames and return one finding per tracked person.

    Returns (findings, stats); stats has frames_processed, raw_detections, duration_s.
    """
    tracker = tracker or SimpleTracker()
    best_frames: dict[int, tuple[float, np.ndarray]] = {}
    frames = raw = 0
    last_t = 0.0
    for n, t, img in iter_frames(path, every_s, max_frames):
        frames += 1
        last_t = t
        dets = detector.detect(img, frame=n)
        raw += len(dets)
        for tid, d in zip(tracker.update(dets), dets):
            best = next(tr.best for tr in tracker.tracks if tr.track_id == tid)
            if best is d:   # this frame holds the best view of the person so far
                best_frames[tid] = (t, img)
    findings = []
    for tr in tracker.summary(min_hits):
        t, img = best_frames[tr.track_id]
        findings.append(VideoFinding(tr.track_id, tr.best, t, tr.hits, img))
    stats = {"frames_processed": frames, "raw_detections": raw,
             "people": len(findings), "duration_s": round(last_t, 2)}
    return findings, stats
