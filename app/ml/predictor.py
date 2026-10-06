from pathlib import Path
from typing import Any, Dict, Optional

import joblib
import pandas as pd
from app.config import settings

class ModelNotFoundError(FileNotFoundError):
    """Raised when the configured prediction model artifact is unavailable."""


_model: Optional[Any] = None
_loaded_model_path: Optional[Path] = None


def get_model(force_reload: bool = False) -> Any:
    """Load and cache the trained model from the configured artifact path."""
    global _model, _loaded_model_path

    model_path = settings.model_path
    if _model is not None and _loaded_model_path == model_path and not force_reload:
        return _model

    if not model_path.is_file():
        raise ModelNotFoundError(f"Prediction model not found: {model_path}")

    try:
        loaded_model = joblib.load(model_path)
    except Exception as exc:
        raise RuntimeError(f"Could not load prediction model: {model_path}") from exc

    _model = loaded_model
    _loaded_model_path = model_path
    return _model


def is_model_loaded() -> bool:
    """Return whether the configured model artifact can be loaded."""
    try:
        get_model()
    except (ModelNotFoundError, RuntimeError):
        return False
    return True


def predict_waste(data: Dict[str, Any]) -> float:
    model = get_model()
    df = pd.DataFrame([data])
    prediction = model.predict(df)[0]
    return round(max(prediction, 0), 2)