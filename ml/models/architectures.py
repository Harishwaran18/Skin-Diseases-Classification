"""Model architecture definitions (scaffold).

A real implementation would define an EfficientNet/ResNet transfer-learning
model here. Left as a TODO — no model is trained and no accuracy is claimed.
"""
from __future__ import annotations


def build_model(num_classes: int = 7):  # pragma: no cover - scaffold
    """TODO: build and return a torchvision model for transfer learning.

    Example (NOT run here):
        import torchvision.models as M
        model = M.efficientnet_b0(weights=M.EfficientNet_B0_Weights.DEFAULT)
        model.classifier[1] = torch.nn.Linear(model.classifier[1].in_features, num_classes)
        return model
    """
    raise NotImplementedError(
        "Model architecture is a scaffold. No trained model is available."
    )
