"""Demo: detect people in a UAV image with a pretrained YOLO model (baseline B1).

Usage:
    pip install -r requirements.txt
    python -m sar_vision.detect_demo --image path/to/frame.jpg --tiling

Without --tiling the whole frame is processed at once; with --tiling the image is sliced
with SAHI, which helps with small people.
"""
from __future__ import annotations

import argparse
from pathlib import Path

PERSON_CLASS_ID = 0  # "person" class in COCO


def run(image: Path, weights: str, conf: float, tiling: bool, out: Path) -> int:
    import cv2

    img = cv2.imread(str(image))
    if img is None:
        raise FileNotFoundError(image)

    boxes: list[tuple[int, int, int, int, float]] = []
    if tiling:
        from sahi import AutoDetectionModel
        from sahi.predict import get_sliced_prediction

        model = AutoDetectionModel.from_pretrained(
            model_type="ultralytics", model_path=weights, confidence_threshold=conf)
        result = get_sliced_prediction(str(image), model, slice_height=640, slice_width=640,
                                       overlap_height_ratio=0.2, overlap_width_ratio=0.2)
        for p in result.object_prediction_list:
            if p.category.id == PERSON_CLASS_ID:
                b = p.bbox
                boxes.append((int(b.minx), int(b.miny), int(b.maxx), int(b.maxy), p.score.value))
    else:
        from ultralytics import YOLO

        res = YOLO(weights)(img, conf=conf, classes=[PERSON_CLASS_ID], verbose=False)[0]
        for xyxy, c in zip(res.boxes.xyxy.tolist(), res.boxes.conf.tolist()):
            boxes.append((*map(int, xyxy), c))

    for x1, y1, x2, y2, c in boxes:
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(img, f"person {c:.2f}", (x1, max(0, y1 - 6)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    cv2.imwrite(str(out), img)
    print(f"People detected: {len(boxes)}. Output: {out}")
    return len(boxes)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--image", type=Path, required=True)
    ap.add_argument("--weights", default="yolov8s.pt")
    ap.add_argument("--conf", type=float, default=0.25)
    ap.add_argument("--tiling", action="store_true")
    ap.add_argument("--out", type=Path, default=Path("detections.jpg"))
    a = ap.parse_args()
    run(a.image, a.weights, a.conf, a.tiling, a.out)


if __name__ == "__main__":
    main()
