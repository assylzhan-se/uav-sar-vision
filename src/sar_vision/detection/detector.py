"""Person detector: YOLO (pretrained on COCO, baseline B1) with optional SAHI tiling.

Fine-tuning on VisDrone -> HERIDAL/SARD comes later; only the weights file will change.
"""
from __future__ import annotations

from pathlib import Path
from typing import Union

import numpy as np

from .schema import Detection

PERSON_CLASS_ID = 0  # "person" in COCO
ImageInput = Union[str, Path, np.ndarray]


class PersonDetector:
    """Finds people in an image.

    tiling=False: the whole frame is resized to the model input (fast, misses small people).
    tiling=True:  the frame is cut into overlapping tiles with SAHI (slower, finds small people).
    """

    def __init__(self, weights: str = "yolov8s.pt", conf: float = 0.25, tiling: bool = False,
                 tile: int = 640, overlap: float = 0.2, device: str | None = None) -> None:
        if not 0.0 < conf < 1.0:
            raise ValueError("conf must be between 0 and 1")
        if not 0.0 <= overlap < 1.0:
            raise ValueError("overlap must be in [0, 1)")
        self.weights = weights
        self.conf = conf
        self.tiling = tiling
        self.tile = tile
        self.overlap = overlap
        self.device = device
        self._yolo = None
        self._sahi = None

    # -- public -------------------------------------------------------------------------------
    def detect(self, image: ImageInput, frame: int = 0) -> list[Detection]:
        img = load_image(image)
        if self.tiling:
            return self._detect_tiled(img, frame)
        return self._detect_full(img, frame)

    # -- internals ----------------------------------------------------------------------------
    def _detect_full(self, img: np.ndarray, frame: int) -> list[Detection]:
        if self._yolo is None:
            from ultralytics import YOLO
            self._yolo = YOLO(self.weights)
        res = self._yolo(img, conf=self.conf, classes=[PERSON_CLASS_ID], device=self.device,
                         verbose=False)[0]
        return [Detection(*map(float, xyxy), confidence=float(c), frame=frame)
                for xyxy, c in zip(res.boxes.xyxy.tolist(), res.boxes.conf.tolist())]

    def _detect_tiled(self, img: np.ndarray, frame: int) -> list[Detection]:
        from sahi.predict import get_sliced_prediction
        if self._sahi is None:
            from sahi import AutoDetectionModel
            self._sahi = AutoDetectionModel.from_pretrained(
                model_type="ultralytics", model_path=self.weights,
                confidence_threshold=self.conf, device=self.device or "cpu")
        rgb = img[:, :, ::-1].copy()  # SAHI expects RGB, OpenCV gives BGR
        result = get_sliced_prediction(
            rgb, self._sahi, slice_height=self.tile, slice_width=self.tile,
            overlap_height_ratio=self.overlap, overlap_width_ratio=self.overlap, verbose=0)
        dets = []
        for p in result.object_prediction_list:
            if p.category.id != PERSON_CLASS_ID:
                continue
            b = p.bbox
            dets.append(Detection(float(b.minx), float(b.miny), float(b.maxx), float(b.maxy),
                                  confidence=float(p.score.value), frame=frame))
        return dets


def load_image(image: ImageInput) -> np.ndarray:
    """Read an image as a BGR array (OpenCV format)."""
    if isinstance(image, np.ndarray):
        if image.ndim != 3 or image.shape[2] != 3:
            raise ValueError("expected a colour image with shape (H, W, 3)")
        return image
    import cv2
    img = cv2.imread(str(image))
    if img is None:
        raise FileNotFoundError(f"cannot read image: {image}")
    return img


def draw_detections(img: np.ndarray, detections: list[Detection]) -> np.ndarray:
    """Return a copy of the image with red boxes and confidence labels."""
    import cv2
    out = img.copy()
    for d in detections:
        x1, y1, x2, y2 = map(int, d.bbox)
        cv2.rectangle(out, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(out, f"person {d.confidence:.2f}", (x1, max(12, y1 - 6)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    return out
