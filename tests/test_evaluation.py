"""Tests of the evaluation metrics (recall, precision, AP50) on hand-made examples."""
import numpy as np
import pytest

from sar_vision.evaluation import (average_precision, evaluate, iou_matrix, load_visdrone,
                                   load_yolo, match)
from sar_vision.detection import Detection


def test_iou():
    a = np.array([[0, 0, 10, 10]], float)
    b = np.array([[0, 0, 10, 10], [5, 0, 15, 10], [20, 20, 30, 30]], float)
    assert iou_matrix(a, b).round(3).tolist() == [[1.0, 0.333, 0.0]]


def test_match_counts_each_person_once():
    gt = np.array([[0, 0, 10, 10]], float)
    pred = np.array([[0, 0, 10, 10], [1, 1, 10, 10]], float)   # two boxes on one person
    res = match(pred, np.array([0.9, 0.8]), gt)
    assert res == [(0.9, True), (0.8, False)]                  # the second is a false positive


def test_perfect_and_empty_ap():
    assert average_precision([(0.9, True), (0.8, True)], n_gt=2) == pytest.approx(1.0)
    assert average_precision([], n_gt=3) == 0.0
    assert average_precision([(0.9, True)], n_gt=2) < 0.6           # half the people missed


def test_load_visdrone_keeps_only_people(tmp_path):
    f = tmp_path / "a.txt"
    f.write_text("10,20,5,10,1,1,0,0\n30,40,6,12,1,2,0,0\n50,50,20,10,1,4,0,0\n")  # 4 = car
    assert load_visdrone(f).tolist() == [[10, 20, 15, 30], [30, 40, 36, 52]]


def test_load_yolo_converts_to_pixels(tmp_path):
    f = tmp_path / "a.txt"
    f.write_text("0 0.5 0.5 0.2 0.4\n2 0.1 0.1 0.1 0.1\n")
    assert load_yolo(f, 100, 50).tolist() == [[40, 15, 60, 35]]


def test_evaluate_with_fake_detector(tmp_path):
    import cv2
    img = tmp_path / "img.jpg"
    cv2.imwrite(str(img), np.zeros((100, 100, 3), np.uint8))
    gt = np.array([[10, 10, 30, 30], [60, 60, 80, 80]], float)

    class Fake:
        def detect(self, image):
            return [Detection(10, 10, 30, 30, 0.9), Detection(0, 50, 5, 60, 0.4)]

    m = evaluate(Fake(), [(img, gt)])
    assert (m.persons, m.tp, m.fp, m.fn) == (2, 1, 1, 1)
    assert m.recall == 0.5 and m.precision == 0.5
