"""Geolocation of detections: image pixel -> latitude/longitude.

Draft version: assumes a nadir camera (gimbal pitch -90 degrees) over flat terrain.
Tilted cameras and terrain elevation are not handled yet (see FR-13).
Not yet validated against real flight data (test T-4).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

METERS_PER_DEG_LAT = 111_320.0


@dataclass(frozen=True)
class Camera:
    sensor_width_mm: float   # sensor width
    focal_length_mm: float   # focal length
    image_width_px: int
    image_height_px: int


@dataclass(frozen=True)
class Telemetry:
    lat: float          # UAV latitude, degrees
    lon: float          # UAV longitude, degrees
    altitude_m: float   # height above ground, m (DJI reports height above take-off point)
    yaw_deg: float      # camera heading, 0 = north, clockwise


def ground_sample_distance(cam: Camera, altitude_m: float) -> float:
    """Ground sample distance in metres per pixel."""
    if altitude_m <= 0:
        raise ValueError("altitude_m must be positive")
    return (altitude_m * cam.sensor_width_mm) / (cam.focal_length_mm * cam.image_width_px)


def pixel_to_latlon(u: float, v: float, cam: Camera, tel: Telemetry) -> tuple[float, float]:
    """Convert pixel (u, v) to geographic coordinates.

    u is the column (to the right), v is the row (downwards); origin at the top-left corner.
    """
    gsd = ground_sample_distance(cam, tel.altitude_m)
    # offset from the image centre: x to the right, y forward (up in the image)
    dx = (u - cam.image_width_px / 2) * gsd
    dy = (cam.image_height_px / 2 - v) * gsd
    # rotate by heading -> east / north
    yaw = math.radians(tel.yaw_deg)
    d_east = dx * math.cos(yaw) + dy * math.sin(yaw)
    d_north = -dx * math.sin(yaw) + dy * math.cos(yaw)
    lat = tel.lat + d_north / METERS_PER_DEG_LAT
    lon = tel.lon + d_east / (METERS_PER_DEG_LAT * math.cos(math.radians(tel.lat)))
    return lat, lon


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two points in metres (used to measure geolocation error)."""
    r = 6_371_000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))
