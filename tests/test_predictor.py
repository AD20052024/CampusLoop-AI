import pytest
from app.ml.predictor import (
    get_model,
    predict_waste,
    is_model_loaded,
    ModelNotFoundError,
)
from app.config import settings


def test_model_is_available():
    assert is_model_loaded() is True


def test_lazy_loading_singleton():
    model1 = get_model()
    model2 = get_model()
    # Confirms caching singleton behavior
    assert model1 is model2


def test_predict_waste_returns_valid_float(valid_prediction_payload):
    result = predict_waste(valid_prediction_payload)
    assert isinstance(result, float)
    assert result >= 0.0


def test_missing_model_raises_custom_exception(monkeypatch):
    nonexistent_path = settings.base_dir / "data" / "processed" / "nonexistent_model.pkl"
    monkeypatch.setattr(settings, "model_path", nonexistent_path)

    with pytest.raises(ModelNotFoundError):
        get_model(force_reload=True)

