"""Create a synthetic aerial-like test image with small people (for the tiling demo).

Four small copies of the ultralytics sample photo are placed on a 4000 x 3000 green field,
so people are only ~60 px tall, as in a real frame from 50-100 m altitude.
This is NOT real UAV data; use VisDrone/HERIDAL images for real evaluation.

    python scripts/make_synthetic_sample.py  ->  data/samples/synthetic_field.jpg
"""
from pathlib import Path

import cv2
import numpy as np
import ultralytics

out = Path("data/samples/synthetic_field.jpg")
out.parent.mkdir(parents=True, exist_ok=True)
sample = cv2.imread(str(Path(ultralytics.__file__).parent / "assets" / "bus.jpg"))
rng = np.random.default_rng(7)
field = np.full((3000, 4000, 3), (60, 110, 80), dtype=np.int16)
field = np.clip(field + rng.integers(-25, 25, field.shape), 0, 255).astype(np.uint8)
field = cv2.GaussianBlur(field, (5, 5), 0)
for x, y, s in [(300, 400, 0.22), (2600, 500, 0.2), (1500, 1800, 0.24), (3200, 2200, 0.21)]:
    small = cv2.resize(sample, None, fx=s, fy=s)
    field[y:y + small.shape[0], x:x + small.shape[1]] = small
cv2.imwrite(str(out), field, [cv2.IMWRITE_JPEG_QUALITY, 92])
print(f"Saved {out}")
