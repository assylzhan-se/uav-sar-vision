"""Make a short demo "flight" video from one still aerial image (owner: Shalmanov Assylzhan).

The camera window slides across the image, like a drone flying over the scene. This is a
SYNTHETIC video for the demo of the video mode (FR-12); say so when you show it.

    python scripts/make_demo_video.py --image path/to/visdrone.jpg --out demo_flight.mp4
"""
import argparse

import cv2


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--out", default="demo_flight.mp4")
    ap.add_argument("--seconds", type=float, default=8)
    ap.add_argument("--fps", type=int, default=15)
    a = ap.parse_args()
    img = cv2.imread(a.image)
    if img is None:
        raise SystemExit(f"cannot read {a.image}")
    h, w = img.shape[:2]
    win_w, win_h = int(w * 0.6), int(h * 0.6)
    n = int(a.seconds * a.fps)
    out = cv2.VideoWriter(a.out, cv2.VideoWriter_fourcc(*"mp4v"), a.fps, (win_w, win_h))
    for i in range(n):
        t = i / max(n - 1, 1)
        x, y = int((w - win_w) * t), int((h - win_h) * (0.5 + 0.5 * (t - 0.5)))
        out.write(img[y:y + win_h, x:x + win_w])
    out.release()
    print(f"saved {a.out}: {n} frames, {win_w}x{win_h}, {a.seconds} s")


if __name__ == "__main__":
    main()
