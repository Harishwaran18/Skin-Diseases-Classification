"""Demo/mock inference backend (clearly labelled).

Returns a deterministic, reproducible distribution derived from image bytes
so results are stable for the same image. No real model is loaded and no
accuracy is claimed. Used when AI_BACKEND=demo (default).
"""
from __future__ import annotations

import hashlib
import io

import numpy as np
from PIL import Image

from ml.inference.classifier import PredictionResult

CATEGORIES = [
    "eczema_like",
    "psoriasis_like",
    "acne_like",
    "rosacea_like",
    "fungal_like",
    "benign_nevus_like",
    "unremarkable",
]

VERSION = "demo-0.1.0"


def _seed_from_bytes(image_bytes: bytes) -> int:
    return int(hashlib.sha256(image_bytes).hexdigest()[:8], 16)


class DemoClassifier:
    """Clearly-labelled demo classifier. Not a diagnostic device."""

    is_demo = True

    def load_model(self) -> None:
        # Nothing to load.
        return None

    def preprocess(self, image_bytes: bytes) -> np.ndarray:
        try:
            pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            pil = pil.resize((224, 224))
            arr = np.asarray(pil, dtype=np.float32) / 255.0
            return arr
        except Exception:
            # Return zeros so predict can still produce a deterministic
            # (but low-confidence) result rather than crashing.
            return np.zeros((224, 224, 3), dtype=np.float32)

    def predict(self, image_bytes: bytes) -> PredictionResult:
        seed = _seed_from_bytes(image_bytes)
        rng = np.random.default_rng(seed)
        # Bias distribution by mean brightness for plausible variation.
        arr = self.preprocess(image_bytes)
        brightness = float(arr.mean()) if arr.size else 0.5
        logits = rng.standard_normal(len(CATEGORIES))
        logits = logits + (brightness - 0.5) * 1.5
        probs = _softmax(logits)
        idx = int(np.argmax(probs))
        # Add some randomness to confidence, kept modest (honest uncertainty).
        confidence = float(min(0.75, max(0.25, probs[idx] + rng.uniform(-0.05, 0.05))))
        severity_score = float(min(1.0, max(0.0, brightness * 0.6 + rng.uniform(-0.1, 0.1))))
        severity = _severity_label(severity_score)
        probabilities = {CATEGORIES[i]: round(float(probs[i]), 4) for i in range(len(CATEGORIES))}
        return PredictionResult(
            model_version=VERSION,
            is_demo=True,
            category=CATEGORIES[idx],
            confidence=round(confidence, 3),
            probabilities=probabilities,
            severity=severity,
            severity_score=round(severity_score, 3),
            attention_note=(
                "Demo attention note (synthetic): the model attended most to "
                "central image regions. This is a placeholder, not a real "
                "explanation."
            ),
            reliable=True,
        )


def _softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - np.max(x))
    return e / e.sum()


def _severity_label(score: float) -> str:
    if score < 0.33:
        return "mild"
    if score < 0.66:
        return "moderate"
    return "severe"
