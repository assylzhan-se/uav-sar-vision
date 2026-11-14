"""Pixel -> GPS for a detection, using the shared module src/sar_vision/geolocation.py."""
from __future__ import annotations

from . import settings
from sar_vision.geolocation import Camera, Telemetry, pixel_to_latlon


def detection_latlon(bbox: list[float], width: int, height: int,
                     tel: Telemetry | None) -> tuple[float | None, float | None]:
    """Coordinates of the box centre, or (None, None) when there is no telemetry."""
    if tel is None:
        return None, None
    cam = Camera(sensor_width_mm=settings.SENSOR_WIDTH_MM,
                 focal_length_mm=settings.FOCAL_LENGTH_MM,
                 image_width_px=width, image_height_px=height)
    u = (bbox[0] + bbox[2]) / 2
    v = (bbox[1] + bbox[3]) / 2
    lat, lon = pixel_to_latlon(u, v, cam, tel)
    return round(lat, 7), round(lon, 7)
