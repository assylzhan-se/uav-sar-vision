"""Command line demo of the CV module.

    python -m sar_vision.detection --image data/samples/frame.jpg            # whole frame
    python -m sar_vision.detection --image data/samples/frame.jpg --tiling   # SAHI tiles
    python -m sar_vision.detection --image data/samples/frame.jpg --compare  # both, side by side

Writes an image with boxes and a JSON file in the format of docs/api-contract.md.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from .detector import PersonDetector, draw_detections, load_image


def run_once(img, weights: str, conf: float, tiling: bool, tile: int):
    det = PersonDetector(weights=weights, conf=conf, tiling=tiling, tile=tile)
    det.detect(img)  # warm-up: the first call loads the model
    t0 = time.perf_counter()
    dets = det.detect(img)
    return dets, time.perf_counter() - t0


def main() -> None:
    ap = argparse.ArgumentParser(description="Detect people in a UAV image")
    ap.add_argument("--image", type=Path, required=True)
    ap.add_argument("--weights", default="yolov8s.pt")
    ap.add_argument("--conf", type=float, default=0.25)
    ap.add_argument("--tile", type=int, default=640)
    ap.add_argument("--tiling", action="store_true", help="use SAHI tiling")
    ap.add_argument("--compare", action="store_true", help="run without and with tiling")
    ap.add_argument("--out", type=Path, default=Path("output"))
    a = ap.parse_args()

    import cv2
    img = load_image(a.image)
    a.out.mkdir(parents=True, exist_ok=True)
    modes = [False, True] if a.compare else [a.tiling]
    print(f"Image: {a.image}  size: {img.shape[1]}x{img.shape[0]}")
    for tiling in modes:
        name = "tiled" if tiling else "full"
        dets, sec = run_once(img, a.weights, a.conf, tiling, a.tile)
        cv2.imwrite(str(a.out / f"{a.image.stem}_{name}.jpg"), draw_detections(img, dets))
        (a.out / f"{a.image.stem}_{name}.json").write_text(
            json.dumps([d.to_dict() for d in dets], indent=2), encoding="utf-8")
        print(f"  {name:5s}: {len(dets):3d} people  {sec * 1000:7.0f} ms")
    print(f"Results saved to {a.out}/")


if __name__ == "__main__":
    main()
