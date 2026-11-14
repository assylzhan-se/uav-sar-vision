"""Backend settings, read from environment variables (no secrets are stored in git)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Make the shared package src/sar_vision importable (geolocation, detection).
_src = str(REPO_ROOT / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

DB_PATH = Path(os.environ.get("SAR_DB_PATH", REPO_ROOT / "data" / "operations.sqlite"))
DETECTOR = os.environ.get("SAR_DETECTOR", "auto")      # auto | yolo | mock
WEIGHTS = os.environ.get("SAR_WEIGHTS", "yolov8s.pt")
TILING = os.environ.get("SAR_TILING", "0") == "1"
CONF = float(os.environ.get("SAR_CONF", "0.25"))
CORS_ORIGINS = os.environ.get("SAR_CORS", "http://localhost:5173").split(",")

# Camera of the reference UAV (config/config.example.yaml). Image size is taken from the upload.
SENSOR_WIDTH_MM = float(os.environ.get("SAR_SENSOR_WIDTH_MM", "17.3"))
FOCAL_LENGTH_MM = float(os.environ.get("SAR_FOCAL_LENGTH_MM", "12.29"))
