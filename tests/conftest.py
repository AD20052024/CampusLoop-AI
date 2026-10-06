import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    """FastAPI TestClient fixture."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def valid_prediction_payload():
    """Representative valid operational payload for Tuesday lunch."""
    return {
        "day_number": 1,
        "month": 10,
        "meal": "Lunch",
        "expected_attendance": 260,
        "event_type": "Normal",
        "holiday": 0,
        "exam_period": 0,
        "weather_condition": "Clear",
    }
