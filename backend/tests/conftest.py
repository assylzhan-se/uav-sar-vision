"""Test setup: temporary database and the mock detector (no neural network needed)."""
import sys
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(BACKEND.parent / "src"))   # sar_vision, needed by test_api.py at import time


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("SAR_DETECTOR", "mock")
    from app import settings
    monkeypatch.setattr(settings, "DB_PATH", tmp_path / "test.sqlite")
    monkeypatch.setattr(settings, "DETECTOR", "mock")
    from fastapi.testclient import TestClient
    from app.main import app
    with TestClient(app) as c:
        yield c
