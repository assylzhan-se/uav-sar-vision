"""Tests of video processing with a synthetic video and a simple colour detector (no model)."""
import cv2
import numpy as np
import pytest

from sar_vision.detection import Detection, iter_frames, process_video


class RedBlobDetector:
    """Finds red squares: stands in for YOLO so the test checks the video logic only."""

    def detect(self, image, frame=0):
        mask = cv2.inRange(image, (0, 0, 200), (60, 60, 255))
        n, _, stats, _ = cv2.connectedComponentsWithStats(mask)
        return [Detection(x, y, x + w, y + h, 0.5 + 0.004 * (frame % 100), frame)
                for x, y, w, h, area in stats[1:] if area > 20]


@pytest.fixture()
def video(tmp_path):
    """4 s at 10 fps: one red square moving slowly to the right."""
    path = tmp_path / "flight.avi"
    out = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), 10, (320, 240))
    for i in range(40):
        img = np.full((240, 320, 3), 90, np.uint8)
        x = 40 + i * 2
        cv2.rectangle(img, (x, 100), (x + 16, 116), (0, 0, 255), -1)
        out.write(img)
    out.release()
    return path


def test_iter_frames_samples_every_second(video):
    frames = list(iter_frames(video, every_s=1.0))
    assert [n for n, _, _ in frames] == [0, 10, 20, 30]
    assert [round(t) for _, t, _ in frames] == [0, 1, 2, 3]
    assert frames[0][2].shape == (240, 320, 3)


def test_iter_frames_errors(tmp_path):
    with pytest.raises(FileNotFoundError):
        list(iter_frames(tmp_path / "missing.mp4"))
    with pytest.raises(ValueError):
        list(iter_frames(tmp_path / "missing.mp4", every_s=0))


def test_process_video_merges_one_person(video):
    findings, stats = process_video(video, RedBlobDetector(), every_s=0.5)
    assert stats["frames_processed"] == 8
    assert stats["raw_detections"] == 8          # the square is found on every sampled frame
    assert len(findings) == 1                    # ...but it is one person
    f = findings[0]
    assert f.hits == 8
    assert f.frame_image.shape == (240, 320, 3)
    assert f.detection.frame == 35               # the most confident view (highest frame here)
    assert f.time_s == pytest.approx(3.5)
