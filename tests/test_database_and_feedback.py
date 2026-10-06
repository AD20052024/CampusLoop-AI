from fastapi import status
from app.database.session import init_db


def test_database_initialization():
    # Calling init_db should execute without error
    init_db()


def test_full_closed_loop_api_workflow(client, valid_prediction_payload):
    # Step 1: PREDICT — Submit operational payload
    pred_res = client.post("/api/predict", json=valid_prediction_payload)
    assert pred_res.status_code == status.HTTP_200_OK
    pred_data = pred_res.json()

    prediction_id = pred_data.get("prediction_id")
    assert prediction_id is not None
    assert len(prediction_id) == 36  # UUID length

    intervention_id = pred_data["intervention"]["id"]
    assert intervention_id is not None

    # Step 2: INTERVENE — Human manager approves intervention
    approval_res = client.post(
        f"/api/predictions/{prediction_id}/interventions/{intervention_id}",
        json={"status": "APPROVED", "approved_by": "Chef Marcus (Dining Manager)"},
    )
    assert approval_res.status_code == status.HTTP_200_OK
    approval_data = approval_res.json()
    assert approval_data["new_status"] == "APPROVED"
    assert approval_data["approved_by"] == "Chef Marcus (Dining Manager)"

    # Step 3: MEASURE & LEARN — Record post-meal actual outcome
    outcome_payload = {
        "actual_attendance": 245,
        "actual_preparation": 88.0,
        "actual_consumption": 76.5,
        "actual_waste": 4.5,
    }
    outcome_res = client.post(
        f"/api/predictions/{prediction_id}/outcomes",
        json=outcome_payload,
    )
    assert outcome_res.status_code == status.HTTP_201_CREATED
    outcome_data = outcome_res.json()
    assert outcome_data["prediction_id"] == prediction_id
    assert outcome_data["actual_waste"] == 4.5
    assert "prediction_error" in outcome_data
    assert "absolute_error" in outcome_data
    assert "percent_error" in outcome_data

    # Step 4: VERIFY — Detail view captures all 3 stages
    detail_res = client.get(f"/api/predictions/{prediction_id}")
    assert detail_res.status_code == status.HTTP_200_OK
    detail_data = detail_res.json()
    assert detail_data["status"] == "OUTCOME_RECORDED"
    assert len(detail_data["interventions"]) >= 1
    assert detail_data["outcome"]["actual_waste"] == 4.5

    # Step 5: FEEDBACK ANALYTICS — Aggregated system trends
    feedback_res = client.get("/api/feedback/analytics")
    assert feedback_res.status_code == status.HTTP_200_OK
    feedback_data = feedback_res.json()
    assert feedback_data["total_predictions"] >= 1
    assert feedback_data["total_outcomes_recorded"] >= 1
    assert "cumulative_impact" in feedback_data
