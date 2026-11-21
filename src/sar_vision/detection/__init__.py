"""CV module: person detection in UAV images and video (owner: Shalmanov Assylzhan)."""
from .detector import DEFAULT_MODE, MODES, PersonDetector, draw_detections, load_image
from .schema import Detection
from .tracking import SimpleTracker, Track
from .video import VideoFinding, iter_frames, process_video

__all__ = ["DEFAULT_MODE", "MODES", "Detection", "PersonDetector", "SimpleTracker", "Track",
           "VideoFinding", "draw_detections", "iter_frames", "load_image", "process_video"]
