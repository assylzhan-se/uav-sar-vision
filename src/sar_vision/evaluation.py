"""Detection quality evaluation: recall, precision and AP@0.5 for the "person" class.

Labels can be in VisDrone format (x,y,w,h,score,category,...; people = categories 1 and 2)
or YOLO format (class cx cy w h, normalised; people = class 0).

    python -m sar_vision.evaluation --images data/VisDrone2019-DET-val/images \
        --labels data/VisDrone2019-DET-val/annotations --format visdrone \
        --modes fast,balanced,accurate --limit 40
"""
from __future__ import annotations

import argparse
import random
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

VISDRONE_PEOPLE = {"1", "2"}   # pedestrian, people
IMAGE_EXT = (".jpg", ".jpeg", ".png")


def load_visdrone(path: Path) -> np.ndarray:
    boxes = []
    for line in Path(path).read_text().splitlines():
        p = line.strip().rstrip(",").split(",")
        if len(p) >= 6 and p[5] in VISDRONE_PEOPLE:
            x, y, w, h = map(float, p[:4])
            if w > 0 and h > 0:
                boxes.append([x, y, x + w, y + h])
    return np.array(boxes, dtype=float).reshape(-1, 4)


def load_yolo(path: Path, width: int, height: int, person_class: int = 0) -> np.ndarray:
    boxes = []
    for line in Path(path).read_text().splitlines():
        p = line.split()
        if len(p) >= 5 and int(float(p[0])) == person_class:
            cx, cy, w, h = (float(v) for v in p[1:5])
            boxes.append([(cx - w / 2) * width, (cy - h / 2) * height,
                          (cx + w / 2) * width, (cy + h / 2) * height])
    return np.array(boxes, dtype=float).reshape(-1, 4)


def iou_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    if len(a) == 0 or len(b) == 0:
        return np.zeros((len(a), len(b)))
    x1 = np.maximum(a[:, None, 0], b[None, :, 0])
    y1 = np.maximum(a[:, None, 1], b[None, :, 1])
    x2 = np.minimum(a[:, None, 2], b[None, :, 2])
    y2 = np.minimum(a[:, None, 3], b[None, :, 3])
    inter = np.clip(x2 - x1, 0, None) * np.clip(y2 - y1, 0, None)
    area_a = (a[:, 2] - a[:, 0]) * (a[:, 3] - a[:, 1])
    area_b = (b[:, 2] - b[:, 0]) * (b[:, 3] - b[:, 1])
    return inter / (area_a[:, None] + area_b[None, :] - inter + 1e-9)


def match(pred: np.ndarray, scores: np.ndarray, gt: np.ndarray,
          iou_thr: float = 0.5) -> list[tuple[float, bool]]:
    """Greedy matching, most confident first. Returns (score, is_true_positive) per prediction."""
    order = np.argsort(-scores)
    ious = iou_matrix(pred[order], gt)
    used = np.zeros(len(gt), dtype=bool)
    out = []
    for k, i in enumerate(order):
        ok = False
        if len(gt):
            cand = np.where(~used, ious[k], -1.0)
            j = int(np.argmax(cand))
            if cand[j] >= iou_thr:
                used[j] = True
                ok = True
        out.append((float(scores[i]), ok))
    return out


@dataclass
class Metrics:
    images: int
    persons: int
    tp: int
    fp: int
    fn: int
    ap50: float
    ms_per_image: float

    @property
    def recall(self) -> float:
        return self.tp / self.persons if self.persons else 0.0

    @property
    def precision(self) -> float:
        return self.tp / (self.tp + self.fp) if self.tp + self.fp else 0.0


def average_precision(results: list[tuple[float, bool]], n_gt: int) -> float:
    """101-point interpolated AP (COCO style) for one class."""
    if n_gt == 0 or not results:
        return 0.0
    results = sorted(results, key=lambda r: -r[0])
    tp = np.cumsum([r[1] for r in results])
    fp = np.cumsum([not r[1] for r in results])
    recall = tp / n_gt
    precision = tp / np.maximum(tp + fp, 1)
    ap = 0.0
    for t in np.linspace(0, 1, 101):
        p = precision[recall >= t]
        ap += (p.max() if len(p) else 0.0) / 101
    return float(ap)


def evaluate(detector, pairs: list[tuple[Path, np.ndarray]], iou_thr: float = 0.5) -> Metrics:
    """pairs: (image path, ground-truth boxes). detector: anything with .detect(image)."""
    import cv2
    all_results: list[tuple[float, bool]] = []
    n_gt = tp = fp = 0
    seconds = 0.0
    for img_path, gt in pairs:
        img = cv2.imread(str(img_path))
        t0 = time.perf_counter()
        dets = detector.detect(img)
        seconds += time.perf_counter() - t0
        pred = np.array([d.bbox for d in dets], dtype=float).reshape(-1, 4)
        scores = np.array([d.confidence for d in dets], dtype=float)
        res = match(pred, scores, gt, iou_thr)
        all_results += res
        hits = sum(ok for _, ok in res)
        tp += hits
        fp += len(res) - hits
        n_gt += len(gt)
    return Metrics(len(pairs), n_gt, tp, fp, n_gt - tp, average_precision(all_results, n_gt),
                   1000 * seconds / max(len(pairs), 1))


def collect_pairs(images: Path, labels: Path, fmt: str, limit: int | None,
                  seed: int = 0) -> list[tuple[Path, np.ndarray]]:
    import cv2
    files = sorted(p for p in Path(images).iterdir() if p.suffix.lower() in IMAGE_EXT)
    random.Random(seed).shuffle(files)
    pairs = []
    for img in files:
        lab = Path(labels) / (img.stem + ".txt")
        if not lab.exists():
            continue
        if fmt == "visdrone":
            gt = load_visdrone(lab)
        else:
            h, w = cv2.imread(str(img)).shape[:2]
            gt = load_yolo(lab, w, h)
        if len(gt):
            pairs.append((img, gt))
        if limit and len(pairs) >= limit:
            break
    return pairs


def main() -> None:
    from .detection import MODES, PersonDetector
    ap = argparse.ArgumentParser(description="Evaluate person detection (recall, precision, AP50)")
    ap.add_argument("--images", type=Path, required=True)
    ap.add_argument("--labels", type=Path, required=True)
    ap.add_argument("--format", choices=["visdrone", "yolo"], default="visdrone")
    ap.add_argument("--modes", default="fast,balanced,accurate")
    ap.add_argument("--weights", default="yolov8s.pt")
    ap.add_argument("--conf", type=float, default=0.15)
    ap.add_argument("--limit", type=int, default=40, help="number of images (0 = all)")
    a = ap.parse_args()
    pairs = collect_pairs(a.images, a.labels, a.format, a.limit or None)
    print(f"{len(pairs)} images, {sum(len(g) for _, g in pairs)} people, IoU 0.5, conf {a.conf}\n")
    print("| Mode | Recall | Precision | AP50 | ms / image |")
    print("|---|---|---|---|---|")
    for mode in a.modes.split(","):
        if mode not in MODES:
            raise SystemExit(f"unknown mode {mode}")
        m = evaluate(PersonDetector.from_mode(mode, weights=a.weights, conf=a.conf), pairs)
        print(f"| {mode} | {m.recall:.3f} | {m.precision:.3f} | {m.ap50:.3f} | {m.ms_per_image:.0f} |",
              flush=True)


if __name__ == "__main__":
    main()
