"""Image quality check using OpenCV/Pillow (spec Section 12).

Checks: resolution, blur (Laplacian variance), brightness extremes.
Returns a 0-1 quality score and a boolean pass.
"""
from __future__ import annotations

import io

import cv2
import numpy as np
from PIL import Image


MIN_DIM = 128
BLUR_THRESHOLD = 80.0
BRIGHT_MIN = 40
BRIGHT_MAX = 220


def check_quality(file_bytes: bytes) -> dict:
    """Return {score, ok, width, height, reasons}.

    score in [0,1]; ok False when below threshold → AI is skipped.
    """
    try:
        pil = Image.open(io.BytesIO(file_bytes))
        pil.load()
    except Exception as exc:  # noqa: BLE001
        return {
            "score": 0.0,
            "ok": False,
            "width": None,
            "height": None,
            "reasons": [f"unreadable image: {exc}"],
        }
    width, height = pil.size
    reasons: list[str] = []
    if min(width, height) < MIN_DIM:
        reasons.append(f"resolution too low (min {MIN_DIM}px)")
    arr = np.array(pil.convert("L"))
    blur = float(cv2.Laplacian(arr, cv2.CV_64F).var())
    if blur < BLUR_THRESHOLD:
        reasons.append("image appears blurry")
    mean_brightness = float(arr.mean())
    if mean_brightness < BRIGHT_MIN:
        reasons.append("image too dark")
    elif mean_brightness > BRIGHT_MAX:
        reasons.append("image too bright")

    # Compose a 0-1 score from sub-metrics.
    res_score = min(1.0, min(width, height) / 512.0)
    blur_score = min(1.0, blur / 300.0)
    if mean_brightness < BRIGHT_MIN or mean_brightness > BRIGHT_MAX:
        bright_score = 0.2
    else:
        bright_score = 1.0
    score = round(0.3 * res_score + 0.4 * blur_score + 0.3 * bright_score, 3)
    ok = len(reasons) == 0 and score >= 0.4
    return {
        "score": score,
        "ok": ok,
        "width": width,
        "height": height,
        "reasons": reasons,
    }
