"""API tests (SAR-16). Run from the repository root:  pytest backend/tests -v"""
import cv2
import numpy as np
import pytest

from sar_vision.geolocation import haversine_m

CONTRACT_KEYS = {"id", "image_id", "frame", "bbox", "confidence", "lat", "lon", "status"}
UAV = {"lat": "43.2389", "lon": "76.8897", "altitude_m": "50", "yaw_deg": "0"}


def jpg(width=1920, height=1080) -> bytes:
    img = np.full((height, width, 3), 120, dtype=np.uint8)
    return cv2.imencode(".jpg", img)[1].tobytes()


def upload(client, data=None, content=None):
    return client.post("/api/detect", data=data or {},
                       files={"file": ("frame.jpg", content if content is not None else jpg(),
                                       "image/jpeg")})


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "detector": "mock"}


def test_detect_without_telemetry_has_no_coordinates(client):
    r = upload(client)
    assert r.status_code == 200
    body = r.json()
    assert (body["width"], body["height"]) == (1920, 1080)
    assert len(body["detections"]) == 2
    for d in body["detections"]:
        assert set(d) == CONTRACT_KEYS
        assert d["status"] == "new"
        assert d["lat"] is None and d["lon"] is None


def test_detect_with_telemetry_gives_coordinates_near_uav(client):
    body = upload(client, data=UAV).json()
    for d in body["detections"]:
        assert d["lat"] is not None and d["lon"] is not None
        dist = haversine_m(43.2389, 76.8897, d["lat"], d["lon"])
        assert 0 < dist < 100   # at 50 m altitude the whole frame covers less than 100 m


def test_partial_telemetry_is_ignored(client):
    body = upload(client, data={"lat": "43.2", "lon": "76.8"}).json()   # no altitude
    assert all(d["lat"] is None for d in body["detections"])


@pytest.mark.parametrize("content", [b"", b"this is not an image"])
def test_detect_rejects_bad_file(client, content):
    assert upload(client, content=content).status_code == 400


@pytest.mark.parametrize("field,value", [("altitude_m", "-5"), ("lat", "95"), ("yaw_deg", "360")])
def test_detect_rejects_bad_telemetry(client, field, value):
    data = dict(UAV, **{field: value})
    assert upload(client, data=data).status_code == 422


def test_list_and_filter_detections(client):
    upload(client)
    upload(client)
    all_dets = client.get("/api/detections").json()
    assert len(all_dets) == 4
    assert [d["id"] for d in all_dets] == sorted(d["id"] for d in all_dets)
    assert len(client.get("/api/detections", params={"status": "new"}).json()) == 4
    assert client.get("/api/detections", params={"status": "confirmed"}).json() == []
    assert client.get("/api/detections", params={"status": "maybe"}).status_code == 422


def test_operator_confirms_and_rejects(client):
    first, second = upload(client).json()["detections"]
    r = client.patch(f"/api/detections/{first['id']}", json={"status": "confirmed"})
    assert r.status_code == 200 and r.json()["status"] == "confirmed"
    client.patch(f"/api/detections/{second['id']}", json={"status": "rejected"})
    confirmed = client.get("/api/detections", params={"status": "confirmed"}).json()
    assert [d["id"] for d in confirmed] == [first["id"]]


def test_update_errors(client):
    det = upload(client).json()["detections"][0]
    assert client.patch(f"/api/detections/{det['id']}", json={"status": "maybe"}).status_code == 422
    assert client.patch("/api/detections/9999", json={"status": "confirmed"}).status_code == 404
