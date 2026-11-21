"""Person detector: YOLO (pretrained on COCO, baseline B1) with optional SAHI tiling.

Three ready-made modes (measured on 40 VisDrone val images, see docs/results-baseline.md):

    fast      whole frame at 640 px      recall 0.22   ~0.2 s/img on CPU
    balanced  whole frame at 1280 px     recall 0.42   ~0.6 s/img on CPU
    accurate  SAHI tiles of 416 px       recall 0.51   ~2.7 s/img on CPU

Fine-tuning on VisDrone -> HERIDAL/SARD comes later; only the weights file will change.
"""
from __future__ import annotations

from pathlib import Path
from typing import Union

import numpy as np

from .schema import Detection

PERSON_CLASS_ID = 0  # "person" in COCO
ImageInput = Union[str, Path, np.ndarray]

MODES: dict[str, dict] = {
    "fast": {"tiling": False, "imgsz": 640},
    "balanced": {"tiling": False, "imgsz": 1280},
    "accurate": {"tiling": True, "tile": 416, "imgsz": 640},
}
DEFAULT_MODE = "balanced"


class PersonDetector:
    """Finds people in an image.

    tiling=False: the whole frame is resized to `imgsz` (fast, misses small people).
    tiling=True:  the frame is cut into overlapping tiles with SAHI (slower, finds small people).
    """

    def __init__(self, weights: str = "yolov8s.pt", conf: float = 0.25, tiling: bool = False,
                 tile: int = 640, overlap: float = 0.2, imgsz: int = 640,
                 device: str | None = None) -> None:
        if not 0.0 < conf < 1.0:
            raise ValueError("conf must be between 0 and 1")
        if not 0.0 <= overlap < 1.0:
            raise ValueError("overlap must be in [0, 1)")
        if tile < 64 or imgsz < 64:
            raise ValueError("tile and imgsz must be at least 64 px")
        self.weights = weights
        self.conf = conf
        self.tiling = tiling
        self.tile = tile
        self.overlap = overlap
        self.imgsz = imgsz
        self.device = device
        self._yolo = None
        self._sahi = None

    @classmethod
    def from_mode(cls, mode: str = DEFAULT_MODE, **kwargs) -> "PersonDetector":
        """Create a detector from a named mode: fast, balanced or accurate."""
        if mode not in MODES:
            raise ValueError(f"unknown mode {mode!r}, expected one of {list(MODES)}")
        return cls(**{**MODES[mode], **kwargs})

    # -- public -------------------------------------------------------------------------------
    def detect(self, image: ImageInput, frame: int = 0) -> list[Detection]:
        img = load_image(image)
        if self.tiling:
            return self._detect_tiled(img, frame)
        return self._detect_full(img, frame)

    # -- internals ----------------------------------------------------------------------------
    def _load_yolo(self):
        if self._yolo is None:
            from ultralytics import YOLO
            self._yolo = YOLO(self.weights)
        return self._yolo

    def _detect_full(self, img: np.ndarray, frame: int) -> list[Detection]:
        res = self._load_yolo()(img, conf=self.conf, imgsz=self.imgsz, classes=[PERSON_CLASS_ID],
                                device=self.device, verbose=False)[0]
        return [Detection(*map(float, xyxy), confidence=float(c), frame=frame)
                for xyxy, c in zip(res.boxes.xyxy.tolist(), res.boxes.conf.tolist())]

    def _detect_tiled(self, img: np.ndarray, frame: int) -> list[Detection]:
        from sahi.predict import get_sliced_prediction
        if self._sahi is None:
            from sahi import AutoDetectionModel
            self._sahi = AutoDetectionModel.from_pretrained(
                model_type="ultralytics", model_path=self.weights,
                confidence_threshold=self.conf, device=self.device or "cpu",
                image_size=self.imgsz)
        rgb = img[:, :, ::-1].copy()  # SAHI expects RGB, OpenCV gives BGR
        result = get_sliced_prediction(
            rgb, self._sahi, slice_height=self.tile, slice_width=self.tile,
            overlap_height_ratio=self.overlap, overlap_width_ratio=self.overlap, verbose=0)
        dets = []
        for p in result.object_prediction_list:
            if p.category.id != PERSON_CLASS_ID:
                continue
            b = p.bbox
            if b.maxx <= b.minx or b.maxy <= b.miny:
                continue
            dets.append(Detection(float(b.minx), float(b.miny), float(b.maxx), float(b.maxy),
                                  confidence=min(1.0, float(p.score.value)), frame=frame))
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
