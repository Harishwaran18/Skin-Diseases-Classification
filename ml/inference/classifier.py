"""SkinImageClassifier interface + factory (spec Sections 13, 15).

The interface decouples the API layer from the inference backend. Swapping
the demo backend for a real trained model requires only changing the
AI_BACKEND config switch — no API changes.
"""
from __future__ import annotations

import abc
from dataclasses import dataclass, field


@dataclass
class PredictionResult:
    model_version: str
    is_demo: bool
    category: str | None = None
    confidence: float = 0.0
    probabilities: dict[str, float] = field(default_factory=dict)
    severity: str | None = None
    severity_score: float | None = None
    attention_note: str | None = None
    reliable: bool = True


class SkinImageClassifier(abc.ABC):
    """Abstract classifier interface."""

    @abc.abstractmethod
    def load_model(self) -> None: ...

    @abc.abstractmethod
    def preprocess(self, image_bytes: bytes) -> object: ...

    @abc.abstractmethod
    def predict(self, image_bytes: bytes) -> PredictionResult: ...

    def get_confidence(self, result: PredictionResult) -> float:
        return result.confidence

    def get_class_probabilities(self, result: PredictionResult) -> dict[str, float]:
        return result.probabilities


def get_classifier() -> SkinImageClassifier:
    """Factory: select backend by AI_BACKEND env (demo | torch)."""
    from app.core.config import settings

    backend = settings.ai_backend.lower()
    if backend == "torch":
        from ml.inference.torch_backend import TorchClassifier

        return TorchClassifier()
    # default + fallback
    from ml.inference.demo_backend import DemoClassifier

    return DemoClassifier()
