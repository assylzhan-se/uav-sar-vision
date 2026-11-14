"""Tests of the CV module (SAR-15).

Fast tests check the data format and helpers without a neural network.
Tests marked "model" run the real YOLO model; they are skipped if ultralytics is not installed.
Run all:        pytest tests/test_detection.py -v
Only fast ones: pytest tests/test_detection.py -v -m "not model"
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pytest

from sar_vision.detection import Detection, PersonDetector, draw_detections, load_image

CONTRACT_KEYS = {"frame", "bbox", "confidence"}
WEIGHTS = os.environ.get("SAR_WEIGHTS", "yolov8s.pt")


# ---------- fast tests: data format --------------------------------------------------------
def test_detection_to_dict_matches_contract():
    d = Detection(10, 20, 30, 60, confidence=0.876543, frame=3)
    out = d.to_dict()
    assert set(out) == CONTRACT_KEYS
    assert out["bbox"] == [10.0, 20.0, 30.0, 60.0]
    assert out["confidence"] == 0.877
    assert out["frame"] == 3


def test_detection_center():
    assert Detection(10, 20, 30, 60, confidence=0.5).center == (20.0, 40.0)


@pytest.mark.parametrize("conf", [-0.1, 1.5])
def test_detection_rejects_bad_confidence(conf):
    with pytest.raises(ValueError):
        Detection(0, 0, 10, 10, confidence=conf)


def test_detection_rejects_inverted_box():
    with pytest.raises(ValueError):
        Detection(50, 0, 10, 10, confidence=0.5)


def test_detector_rejects_bad_parameters():
    with pytest.raises(ValueError):
        PersonDetector(conf=1.5)
    with pytest.raises(ValueError):
        PersonDetector(overlap=1.0)


def test_load_image_errors(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_image(tmp_path / "missing.jpg")
    with pytest.raises(ValueError):
        load_image(np.zeros((10, 10), dtype=np.uint8))  # grey image, not colour


def test_draw_detections_draws_and_keeps_original():
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    out = draw_detections(img, [Detection(10, 10, 50, 50, confidence=0.9)])
    assert out.shape == img.shape
    assert out.sum() > 0          # boxes were drawn on the copy
    assert img.sum() == 0         # the original is not changed


# ---------- model tests: real YOLO ---------------------------------------------------------
@pytest.fixture(scope="module")
def sample() -> Path:
    """A photo with four people that ships with the ultralytics package."""
    ultralytics = pytest.importorskip("ultralytics", reason="ultralytics is not installed")
    return Path(ultralytics.__file__).parent / "assets" / "bus.jpg"


@pytest.mark.model
def test_full_frame_detects_people_on_sample(sample):
    dets = PersonDetector(weights=WEIGHTS).detect(sample)
    assert len(dets) >= 3                       # four people stand by the bus
    assert all(set(d.to_dict()) == CONTRACT_KEYS for d in dets)
    assert all(0 < d.confidence <= 1 for d in dets)


@pytest.mark.model
def test_tiling_finds_small_people_that_full_frame_misses(sample):
    """Synthetic aerial-like image: four small copies of the sample on a large green field.

    This reproduces the main problem of the project: people are only ~60 px tall in a
    4000 x 3000 frame. Without tiling YOLO shrinks the frame to 640 px and loses them.
    """
    import cv2
    sample = cv2.imread(str(sample))
    field = np.full((3000, 4000, 3), (60, 110, 80), dtype=np.uint8)
    for x, y, s in [(300, 400, 0.22), (2600, 500, 0.2), (1500, 1800, 0.24), (3200, 2200, 0.21)]:
        small = cv2.resize(sample, None, fx=s, fy=s)
        field[y:y + small.shape[0], x:x + small.shape[1]] = small

    full = PersonDetector(weights=WEIGHTS, tiling=False).detect(field)
    tiled = PersonDetector(weights=WEIGHTS, tiling=True).detect(field)
    assert len(tiled) >= 8
    assert len(tiled) > len(full)
