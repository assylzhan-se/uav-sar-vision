# Backend (FastAPI + SQLite)

Owner: Kurmantayev Ali. Format of all requests and responses: [docs/api-contract.md](../docs/api-contract.md).

## What it does

1. `POST /api/detect` receives a UAV image and optional telemetry (lat, lon, altitude, heading).
2. Calls the detector (CV module, or a mock while the model is not available).
3. Converts the centre of every box to GPS with `src/sar_vision/geolocation.py`.
4. Saves the image record and detections to SQLite (`data/operations.sqlite`, not in git).
5. `GET /api/detections` returns the list, `PATCH /api/detections/{id}` sets confirmed / rejected.

## Run (from the repository root)

```bash
pip install -r backend/requirements.txt
SAR_DETECTOR=mock uvicorn app.main:app --app-dir backend --reload     # without a model
SAR_DETECTOR=yolo uvicorn app.main:app --app-dir backend --reload     # with the CV module
```

On Windows PowerShell: `$env:SAR_DETECTOR="mock"; uvicorn app.main:app --app-dir backend --reload`

Open http://localhost:8000/docs → `POST /api/detect` → *Try it out* → choose an image,
enter `lat=43.2389`, `lon=76.8897`, `altitude_m=50` → *Execute*.

| Variable | Default | Meaning |
|---|---|---|
| `SAR_DETECTOR` | `auto` | `mock`, `yolo` or `auto` (yolo if installed) |
| `SAR_WEIGHTS` | `yolov8s.pt` | model weights |
| `SAR_TILING` | `0` | `1` = SAHI tiling |
| `SAR_DB_PATH` | `data/operations.sqlite` | database file |

## Tests

```bash
pytest backend/tests -v
```

12 tests: health check, contract fields, coordinates with and without telemetry,
bad files and bad telemetry, list and filter, operator confirm / reject, errors 404 and 422.
Tests use a temporary database and the mock detector, so they do not need the model.
