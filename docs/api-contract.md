# API contract (SAR-15)

This file is the agreement between the three modules: CV (detection), backend and frontend.
Any change to the format below must be agreed by the whole team and made in a separate pull request.

## 1. One detection

```json
{
  "id": 1,
  "image_id": 1,
  "frame": 0,
  "bbox": [412.0, 230.5, 448.0, 301.0],
  "confidence": 0.87,
  "lat": 43.238912,
  "lon": 76.889701,
  "status": "new"
}
```

| Field | Type | Meaning |
|---|---|---|
| `id` | integer | Unique id, assigned by the backend (database) |
| `image_id` | integer | Which uploaded image or video the detection belongs to |
| `frame` | integer | Frame number in a video; `0` for a single image |
| `bbox` | 4 numbers | Box in pixels of the original image: `[x1, y1, x2, y2]`, origin top-left |
| `confidence` | number 0..1 | Detector confidence |
| `lat`, `lon` | number or `null` | Estimated position (WGS-84). `null` if no telemetry was given |
| `status` | string | `new`, `confirmed` or `rejected` (set by the operator) |

The CV module returns detections **without** `id`, `image_id`, `lat`, `lon`, `status`;
the backend adds these fields.

## 2. Endpoints (backend)

Base URL during development: `http://localhost:8000`

| Method | Path | Request | Response |
|---|---|---|---|
| GET | `/api/health` | – | `{"status": "ok", "detector": "yolo" or "mock"}` |
| POST | `/api/detect` | `multipart/form-data`: `file` (jpg/png); optional `lat`, `lon`, `altitude_m`, `yaw_deg` | `{"image_id", "width", "height", "detections": [ ... ]}` |
| GET | `/api/detections` | optional `?status=new` | `[ ...detections ]` |
| PATCH | `/api/detections/{id}` | JSON `{"status": "confirmed"}` | the updated detection |

If any of `lat`, `lon`, `altitude_m` is missing, the backend stores `lat` and `lon` as `null`.

## 3. Geolocation assumptions

Coordinates are computed by `src/sar_vision/geolocation.py`: nadir camera, flat terrain,
camera parameters from `config/config.example.yaml`. Target accuracy: mean error ≤ 10 m at 50 m altitude (NFR).
