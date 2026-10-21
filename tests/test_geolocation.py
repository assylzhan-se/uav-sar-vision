import math

import pytest

from sar_vision.geolocation import (
    Camera, Telemetry, ground_sample_distance, haversine_m, pixel_to_latlon,
)

# Example camera parameters (approximately a 4/3-inch sensor); replace with the real UAV camera specs
CAM = Camera(sensor_width_mm=17.3, focal_length_mm=12.29, image_width_px=5280, image_height_px=3956)
TEL = Telemetry(lat=44.8521, lon=65.5024, altitude_m=50.0, yaw_deg=0.0)


def test_gsd_positive_and_reasonable():
    gsd = ground_sample_distance(CAM, 50.0)
    assert 0.005 < gsd < 0.05  # between 0.5 and 5 cm per pixel


def test_gsd_rejects_non_positive_altitude():
    with pytest.raises(ValueError):
        ground_sample_distance(CAM, 0)


def test_center_pixel_maps_to_drone_position():
    lat, lon = pixel_to_latlon(CAM.image_width_px / 2, CAM.image_height_px / 2, CAM, TEL)
    assert haversine_m(lat, lon, TEL.lat, TEL.lon) < 0.01


def test_top_of_frame_is_north_when_yaw_zero():
    lat, lon = pixel_to_latlon(CAM.image_width_px / 2, 0, CAM, TEL)
    assert lat > TEL.lat
    assert math.isclose(lon, TEL.lon, abs_tol=1e-9)


def test_yaw_90_top_of_frame_is_east():
    tel = Telemetry(TEL.lat, TEL.lon, TEL.altitude_m, yaw_deg=90.0)
    lat, lon = pixel_to_latlon(CAM.image_width_px / 2, 0, CAM, tel)
    assert lon > TEL.lon
    assert math.isclose(lat, TEL.lat, abs_tol=1e-7)


def test_offset_distance_matches_gsd():
    gsd = ground_sample_distance(CAM, TEL.altitude_m)
    lat, lon = pixel_to_latlon(CAM.image_width_px / 2 + 1000, CAM.image_height_px / 2, CAM, TEL)
    assert math.isclose(haversine_m(lat, lon, TEL.lat, TEL.lon), 1000 * gsd, rel_tol=0.01)
