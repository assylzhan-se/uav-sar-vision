"""Bridge between the backend and the CV module.

"yolo": uses sar_vision.detection (the CV module).
"mock": returns two fixed detections; lets the backend and frontend work without a model.
"auto": "yolo" if the CV module and ultralytics are installed, otherwise "mock".
"""
from __future__ import annotations

from typing import Protocol

import numpy as np

from . import settings


class Detector(Protocol):
    name: str

    def detect(self, img: np.ndarray) -> list[dict]:
        """Return detections as dicts with keys frame, bbox, confidence."""


class MockDetector:
    name = "mock"

    def detect(self, img: np.ndarray) -> list[dict]:
        h, w = img.shape[:2]
        return [
            {"frame": 0, "bbox": [0.30 * w, 0.40 * h, 0.33 * w, 0.48 * h], "confidence": 0.91},
            {"frame": 0, "bbox": [0.62 * w, 0.55 * h, 0.65 * w, 0.62 * h], "confidence": 0.47},
        ]


class YoloDetector:
    name = "yolo"

    def __init__(self) -> None:
        from sar_vision.detection import PersonDetector
        self._det = PersonDetector(weights=settings.WEIGHTS, conf=settings.CONF,
                                   tiling=settings.TILING)

    def detect(self, img: np.ndarray) -> list[dict]:
        return [d.to_dict() for d in self._det.detect(img)]


def make_detector(kind: str | None = None) -> Detector:
    kind = kind or settings.DETECTOR
    if kind == "mock":
        return MockDetector()
    if kind == "yolo":
        return YoloDetector()
    try:  # auto: the CV module or ultralytics may not be installed yet
        import ultralytics  # noqa: F401
        return YoloDetector()
    except ImportError:
        return MockDetector()
