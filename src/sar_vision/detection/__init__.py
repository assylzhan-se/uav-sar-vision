"""CV module: person detection in UAV images (owner: Shalmanov Assylzhan)."""
from .detector import PersonDetector, draw_detections, load_image
from .schema import Detection

__all__ = ["Detection", "PersonDetector", "draw_detections", "load_image"]
