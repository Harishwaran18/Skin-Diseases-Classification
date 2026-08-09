"""Real-model (torch) backend scaffold — UNTRAINED.

This provides a clean integration path for a validated, trained model. It
is NOT trained and makes NO accuracy claims. Heavy dependencies (torch,
torchvision) are imported lazily inside methods so the app runs without
them. If no checkpoint is available, the factory falls back to the demo
backend with a notice.
"""
from __future__ import annotations

import io
import logging
from pathlib import Path

from ml.inference.classifier import PredictionResult

logger = logging.getLogger("skincare.ai.torch")

VERSION = "torch-scaffold-0.1.0-untrained"

CATEGORIES = [
    "eczema_like",
    "psoriasis_like",
    "acne_like",
    "rosacea_like",
    "fungal_like",
    "benign_nevus_like",
    "unremarkable",
]


class TorchClassifier:
    """Skeleton for a real EfficientNet/ResNet backend.

    Requires torch + torchvision (see requirements-ml.txt) and a trained
    checkpoint at AI_MODEL_PATH. Without a checkpoint it raises so the
    factory can fall back to the demo backend.
    """

    is_demo = False

    def __init__(self) -> None:
        self._model = None
        self._checkpoint: Path | None = None

    def load_model(self) -> None:
        from app.core.config import settings

        if not settings.ai_model_path:
            raise RuntimeError(
                "No AI_MODEL_PATH configured. The torch backend requires a "
                "trained checkpoint. Falling back to demo backend."
            )
        ckpt = Path(settings.ai_model_path)
        if not ckpt.exists():
            raise RuntimeError(
                f"Model checkpoint not found at {ckpt}. Falling back to demo."
            )
        self._checkpoint = ckpt
        try:
            import torch  # noqa: F401
            import torchvision  # noqa: F401
        except ImportError as exc:  # noqa: BLE001
            raise RuntimeError(
                "torch/torchvision not installed (see requirements-ml.txt). "
                "Falling back to demo backend."
            ) from exc
        # TODO: instantiate model, load state_dict, set eval().
        # Do NOT fabricate accuracy. Only load a real, validated checkpoint.
        raise RuntimeError(
            "Torch backend is a scaffold only — model loading is not "
            "implemented because no trained/validated model is available. "
            "Falling back to demo backend."
        )

    def preprocess(self, image_bytes: bytes) -> object:
        from PIL import Image

        pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        pil = pil.resize((224, 224))
        # TODO: apply training-time normalization transforms here.
        return pil

    def predict(self, image_bytes: bytes) -> PredictionResult:
        if self._model is None:
            self.load_model()
        # TODO: run self._model(tensor) -> logits -> softmax.
        # Until implemented, this remains unreachable (load_model raises).
        raise RuntimeError("Torch backend predict() not implemented.")
