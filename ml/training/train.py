"""Training entry point (STUB).

A real implementation would:
- load a labelled, ethically-sourced dermatology dataset,
- apply augmentation + train/val/test splits,
- fine-tune a transfer-learning model,
- evaluate with calibrated probabilities + per-class metrics,
- export a checkpoint for the torch backend.

This is explicitly out of scope for the prototype. No accuracy is claimed
and no model is produced here.
"""
from __future__ import annotations


def main() -> None:  # pragma: no cover - stub
    raise NotImplementedError(
        "Training is out of scope for this prototype. The integration path "
        "exists (ml/inference/torch_backend.py) but no trained model is "
        "available. Use AI_BACKEND=demo."
    )


if __name__ == "__main__":
    main()
