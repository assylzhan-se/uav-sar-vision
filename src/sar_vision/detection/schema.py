"""Detection data structure shared with the backend (see docs/api-contract.md)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Detection:
    """One person found in an image. Coordinates are pixels of the original image."""

    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
    frame: int = 0

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be in [0, 1], got {self.confidence}")
        if self.x2 <= self.x1 or self.y2 <= self.y1:
            raise ValueError(f"invalid box: {self.bbox}")

    @property
    def bbox(self) -> list[float]:
        return [self.x1, self.y1, self.x2, self.y2]

    @property
    def center(self) -> tuple[float, float]:
        """Centre of the box (u, v); this pixel is converted to GPS by the backend."""
        return (self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2

    def to_dict(self) -> dict:
        """Part of the contract produced by the CV module."""
        return {
            "frame": self.frame,
            "bbox": [round(v, 1) for v in self.bbox],
            "confidence": round(self.confidence, 3),
        }
