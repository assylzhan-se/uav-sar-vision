"""SQLite storage for uploaded images and detections."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

SCHEMA = """
CREATE TABLE IF NOT EXISTS images (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    filename    TEXT    NOT NULL,
    width       INTEGER NOT NULL,
    height      INTEGER NOT NULL,
    uav_lat     REAL,
    uav_lon     REAL,
    altitude_m  REAL,
    yaw_deg     REAL,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS detections (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    image_id    INTEGER NOT NULL REFERENCES images(id) ON DELETE CASCADE,
    frame       INTEGER NOT NULL DEFAULT 0,
    x1 REAL NOT NULL, y1 REAL NOT NULL, x2 REAL NOT NULL, y2 REAL NOT NULL,
    confidence  REAL    NOT NULL CHECK (confidence BETWEEN 0 AND 1),
    lat         REAL,
    lon         REAL,
    status      TEXT    NOT NULL DEFAULT 'new'
                CHECK (status IN ('new', 'confirmed', 'rejected'))
);
CREATE INDEX IF NOT EXISTS idx_detections_status ON detections(status);
"""

STATUSES = ("new", "confirmed", "rejected")


def init_db(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with connect(path) as con:
        con.executescript(SCHEMA)


@contextmanager
def connect(path: Path) -> Iterator[sqlite3.Connection]:
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    try:
        yield con
        con.commit()
    finally:
        con.close()


def row_to_detection(row: sqlite3.Row) -> dict:
    """Database row -> detection in the format of docs/api-contract.md."""
    return {
        "id": row["id"],
        "image_id": row["image_id"],
        "frame": row["frame"],
        "bbox": [row["x1"], row["y1"], row["x2"], row["y2"]],
        "confidence": row["confidence"],
        "lat": row["lat"],
        "lon": row["lon"],
        "status": row["status"],
    }
