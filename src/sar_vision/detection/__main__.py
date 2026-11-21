"""Command line demo of the CV module.

    python -m sar_vision.detection --image frame.jpg                      # balanced mode
    python -m sar_vision.detection --image frame.jpg --mode accurate      # SAHI tiles
    python -m sar_vision.detection --image frame.jpg --compare            # all three modes
    python -m sar_vision.detection --video flight.mp4 --every 1           # video, 1 frame/s

Writes images with boxes and JSON files in the format of docs/api-contract.md to --out.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import cv2

from .detector import DEFAULT_MODE, MODES, PersonDetector, draw_detections, load_image
from .video import process_video


def run_image(a) -> None:
    img = load_image(a.image)
    print(f"Image: {a.image}  size: {img.shape[1]}x{img.shape[0]}")
    for mode in (list(MODES) if a.compare else [a.mode]):
        det = PersonDetector.from_mode(mode, weights=a.weights, conf=a.conf)
        det.detect(img)                     # warm-up: the first call loads the model
        t0 = time.perf_counter()
        dets = det.detect(img)
        ms = (time.perf_counter() - t0) * 1000
        cv2.imwrite(str(a.out / f"{a.image.stem}_{mode}.jpg"), draw_detections(img, dets))
        (a.out / f"{a.image.stem}_{mode}.json").write_text(
            json.dumps([d.to_dict() for d in dets], indent=2), encoding="utf-8")
        print(f"  {mode:9s}: {len(dets):3d} people  {ms:7.0f} ms")


def run_video(a) -> None:
    det = PersonDetector.from_mode(a.mode, weights=a.weights, conf=a.conf)
    t0 = time.perf_counter()
    findings, stats = process_video(a.video, det, every_s=a.every, min_hits=a.min_hits)
    print(f"Video: {a.video}  {stats}  {time.perf_counter() - t0:.1f} s")
    for f in findings:
        name = a.out / f"{a.video.stem}_person{f.track_id}_t{f.time_s:.0f}s.jpg"
        cv2.imwrite(str(name), draw_detections(f.frame_image, [f.detection]))
        print(f"  person #{f.track_id}: t={f.time_s:6.1f} s  seen on {f.hits} frames  "
              f"confidence {f.detection.confidence:.2f}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Detect people in a UAV image or video")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--image", type=Path)
    src.add_argument("--video", type=Path)
    ap.add_argument("--mode", choices=list(MODES), default=DEFAULT_MODE)
    ap.add_argument("--compare", action="store_true", help="image: run all three modes")
    ap.add_argument("--every", type=float, default=1.0, help="video: seconds between frames")
    ap.add_argument("--min-hits", type=int, default=1, help="video: drop people seen fewer times")
    ap.add_argument("--weights", default="yolov8s.pt")
    ap.add_argument("--conf", type=float, default=0.25)
    ap.add_argument("--out", type=Path, default=Path("output"))
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    run_video(a) if a.video else run_image(a)
    print(f"Results saved to {a.out}/")


if __name__ == "__main__":
    main()
