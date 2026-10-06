from fastapi import status


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert "text/html" in response.headers["content-type"]
    assert "Before the next service" in response.text


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert "model_loaded" in data


def test_predict_endpoint_valid_payload(client, valid_prediction_payload):
    response = client.post("/api/predict", json=valid_prediction_payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Core predictions and risk
    assert "predicted_waste" in data
    assert data["predicted_waste"] >= 0.0
    assert data["risk_level"] in ["Low", "Medium", "High"]

    # Structured risk object
    assert "risk" in data
    assert data["risk"]["risk_level"] == data["risk_level"]
    assert "priority" in data["risk"]
    assert "reason" in data["risk"]

    # Structured intervention
    assert "recommended_action" in data
    assert "intervention" in data
    assert "action_type" in data["intervention"]
    assert "requires_human_approval" in data["intervention"]

    # UN SDG 12 Impact metrics
    assert "impact" in data
    impact = data["impact"]
    assert impact["estimated_waste_prevented"] >= 0.0
    assert impact["co2e_prevented_kg"] >= 0.0
    assert impact["water_saved_liters"] >= 0.0
    assert impact["meals_salvaged"] >= 0.0
    assert impact["financial_savings_estimated"] >= 0.0

    # Model tracking
    assert "model_version" in data


def test_predict_validation_invalid_month(client, valid_prediction_payload):
    payload = valid_prediction_payload.copy()
    payload["month"] = 13  # Invalid month
    response = client.post("/api/predict", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_predict_validation_invalid_day_number(client, valid_prediction_payload):
    payload = valid_prediction_payload.copy()
    payload["day_number"] = 7  # Must be 0-6
    response = client.post("/api/predict", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_predict_validation_negative_attendance(client, valid_prediction_payload):
    payload = valid_prediction_payload.copy()
    payload["expected_attendance"] = -20  # Cannot be negative
    response = client.post("/api/predict", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_predict_validation_invalid_meal_enum(client, valid_prediction_payload):
    payload = valid_prediction_payload.copy()
    payload["meal"] = "MidnightSnack"  # Not a valid MealType enum
    response = client.post("/api/predict", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_predict_validation_invalid_holiday_flag(client, valid_prediction_payload):
    payload = valid_prediction_payload.copy()
    payload["holiday"] = 2  # Must be 0 or 1
    response = client.post("/api/predict", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
