"""SAR-Vision backend (owner: Kurmantayev Ali).

Run from the repository root:
    uvicorn app.main:app --app-dir backend --reload
Interactive API docs: http://localhost:8000/docs
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Literal, Optional

import cv2
import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import settings
from .db import STATUSES, connect, init_db, row_to_detection
from .detector import make_detector
from .geo import detection_latlon
from sar_vision.geolocation import Telemetry

MAX_UPLOAD_BYTES = 50 * 1024 * 1024


class StatusUpdate(BaseModel):
    status: Literal["new", "confirmed", "rejected"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(settings.DB_PATH)
    app.state.detector = make_detector()
    yield


app = FastAPI(title="SAR-Vision API", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS,
                   allow_methods=["*"], allow_headers=["*"])


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "detector": app.state.detector.name}


@app.post("/api/detect")
async def detect(
    file: UploadFile = File(...),
    lat: Optional[float] = Form(None, ge=-90, le=90),
    lon: Optional[float] = Form(None, ge=-180, le=180),
    altitude_m: Optional[float] = Form(None, gt=0, le=1000),
    yaw_deg: float = Form(0.0, ge=0, lt=360),
) -> dict:
    data = await file.read()
    if not data:
        raise HTTPException(400, "empty file")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "file is larger than 50 MB")
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(400, "file is not a JPG or PNG image")
    height, width = img.shape[:2]

    has_tel = lat is not None and lon is not None and altitude_m is not None
    tel = Telemetry(lat=lat, lon=lon, altitude_m=altitude_m, yaw_deg=yaw_deg) if has_tel else None
    found = app.state.detector.detect(img)

    with connect(settings.DB_PATH) as con:
        cur = con.execute(
            "INSERT INTO images (filename, width, height, uav_lat, uav_lon, altitude_m, yaw_deg)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (file.filename or "upload", width, height, lat, lon, altitude_m, yaw_deg))
        image_id = cur.lastrowid
        ids = []
        for d in found:
            dlat, dlon = detection_latlon(d["bbox"], width, height, tel)
            cur = con.execute(
                "INSERT INTO detections (image_id, frame, x1, y1, x2, y2, confidence, lat, lon)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (image_id, d["frame"], *d["bbox"], d["confidence"], dlat, dlon))
            ids.append(cur.lastrowid)
        rows = con.execute(
            f"SELECT * FROM detections WHERE id IN ({','.join('?' * len(ids))}) ORDER BY id",
            ids).fetchall() if ids else []

    return {"image_id": image_id, "width": width, "height": height,
            "detections": [row_to_detection(r) for r in rows]}


@app.get("/api/detections")
def list_detections(status: Optional[str] = Query(None)) -> list[dict]:
    if status is not None and status not in STATUSES:
        raise HTTPException(422, f"status must be one of {STATUSES}")
    with connect(settings.DB_PATH) as con:
        if status:
            rows = con.execute("SELECT * FROM detections WHERE status = ? ORDER BY id",
                               (status,)).fetchall()
        else:
            rows = con.execute("SELECT * FROM detections ORDER BY id").fetchall()
    return [row_to_detection(r) for r in rows]


@app.patch("/api/detections/{detection_id}")
def update_status(detection_id: int, body: StatusUpdate) -> dict:
    with connect(settings.DB_PATH) as con:
        cur = con.execute("UPDATE detections SET status = ? WHERE id = ?",
                          (body.status, detection_id))
        if cur.rowcount == 0:
            raise HTTPException(404, "detection not found")
        row = con.execute("SELECT * FROM detections WHERE id = ?", (detection_id,)).fetchone()
    return row_to_detection(row)
