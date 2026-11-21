"""Tests of merging detections across video frames (FR-12)."""
import pytest

from sar_vision.detection import Detection, SimpleTracker


def det(cx, cy, conf=0.5, frame=0, size=20):
    return Detection(cx - size / 2, cy - size / 2, cx + size / 2, cy + size / 2, conf, frame)


def test_same_person_on_consecutive_frames_is_one_track():
    tr = SimpleTracker()
    a = tr.update([det(100, 100, 0.4, frame=0)])
    b = tr.update([det(110, 104, 0.9, frame=25)])     # moved a little
    c = tr.update([det(118, 110, 0.6, frame=50)])
    assert a == b == c
    [track] = tr.summary()
    assert track.hits == 3
    assert track.best.confidence == 0.9 and track.best.frame == 25   # best view is kept


def test_far_away_detection_starts_new_track():
    tr = SimpleTracker()
    first = tr.update([det(100, 100)])
    second = tr.update([det(900, 600)])
    assert first != second
    assert len(tr.summary()) == 2


def test_two_people_keep_their_own_tracks():
    tr = SimpleTracker()
    ids1 = tr.update([det(100, 100), det(300, 100)])
    ids2 = tr.update([det(305, 102), det(104, 98)])    # order swapped on the next frame
    assert ids2 == [ids1[1], ids1[0]]


def test_track_closes_after_gap():
    tr = SimpleTracker(max_gap=1)
    first = tr.update([det(100, 100)])
    tr.update([])
    tr.update([])                                       # 2 empty frames > max_gap
    again = tr.update([det(100, 100)])
    assert first != again


def test_min_hits_removes_one_frame_flicker():
    tr = SimpleTracker()
    tr.update([det(100, 100), det(500, 500)])
    tr.update([det(102, 101)])
    assert len(tr.summary(min_hits=1)) == 2
    assert len(tr.summary(min_hits=2)) == 1


def test_bad_parameters():
    with pytest.raises(ValueError):
        SimpleTracker(max_distance=0)
    with pytest.raises(ValueError):
        SimpleTracker(max_gap=0)
