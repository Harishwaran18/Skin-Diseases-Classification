"""Preprocessing helpers shared by training/inference (scaffold)."""
from __future__ import annotations

import io

from PIL import Image

IMG_SIZE = 224


def load_image(image_bytes: bytes) -> Image.Image:
    return Image.open(io.BytesIO(image_bytes)).convert("RGB")


def resize_normalize(image: Image.Image):
    """Resize to IMG_SIZE and return a normalized numpy array in [0,1]."""
    import numpy as np

    img = image.resize((IMG_SIZE, IMG_SIZE))
    arr = np.asarray(img, dtype="float32") / 255.0
    return arr
