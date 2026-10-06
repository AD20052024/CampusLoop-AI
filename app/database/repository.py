from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database.models import (
    InterventionRecord,
    OutcomeRecord,
    PredictionRecord,
)
from app.services.impact import (
    CO2E_PER_KG_FOOD,
    ESTIMATED_COST_PER_KG,
    KG_PER_MEAL_PORTION,
    WATER_LITERS_PER_KG_FOOD,
)


def save_prediction(
    db: Session,
    input_data: Dict[str, Any],
    predicted_waste: float,
    risk_level: str,
    model_version: str,
) -> PredictionRecord:
    """Persist an operational prediction record to the database."""
    record = PredictionRecord(
        day_number=input_data.get("day_number", 0),
        month=input_data.get("month", 1),
        meal=str(input_data.get("meal", "Lunch")),
        expected_attendance=input_data.get("expected_attendance", 0),
        event_type=str(input_data.get("event_type", "Normal")),
        holiday=input_data.get("holiday", 0),
        exam_period=input_data.get("exam_period", 0),
        weather_condition=str(input_data.get("weather_condition", "Clear")),
        predicted_waste=round(float(predicted_waste), 2),
        risk_level=risk_level,
        model_version=model_version,
        status="PREDICTED",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def save_intervention(
    db: Session,
    prediction_id: str,
    action_type: str,
    priority: str,
    recommendation: str,
    requires_human_approval: bool = True,
) -> InterventionRecord:
    """Persist an intervention recommendation linked to a specific prediction."""
    record = InterventionRecord(
        prediction_id=prediction_id,
        action_type=action_type,
        priority=priority,
        recommendation=recommendation,
        requires_human_approval=requires_human_approval,
        status="RECOMMENDED",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def update_intervention_status(
    db: Session,
    intervention_id: str,
    status: str,
    approved_by: Optional[str] = None,
) -> Optional[InterventionRecord]:
    """Update human approval status or execution of an intervention."""
    record = db.query(InterventionRecord).filter(InterventionRecord.id == intervention_id).first()
    if not record:
        return None

    record.status = status
    if approved_by:
        record.approved_by = approved_by
    if status == "EXECUTED":
        record.executed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(record)
    return record


def record_outcome(
    db: Session,
    prediction_id: str,
    actual_attendance: int,
    actual_preparation: float,
    actual_consumption: float,
    actual_waste: float,
) -> OutcomeRecord:
    """
    Log post-service actual dining metrics, calculate prediction errors,
    and close the feedback loop for a prediction.
    """
    pred = db.query(PredictionRecord).filter(PredictionRecord.id == prediction_id).first()
    if not pred:
        raise ValueError(f"Prediction with ID '{prediction_id}' does not exist.")

    pred_waste = pred.predicted_waste
    surplus = max(round(actual_preparation - actual_consumption, 2), 0.0)
    actual_w = round(max(float(actual_waste), 0.0), 2)

    pred_error = round(pred_waste - actual_w, 2)
    abs_error = round(abs(pred_waste - actual_w), 2)
    pct_error = (
        round((abs_error / actual_w) * 100, 2) if actual_w > 0 else 0.0
    )

    # If predicted waste was higher than actual waste, the difference represents potential waste avoided
    reduction_achieved = max(round(pred_waste - actual_w, 2), 0.0)

    outcome = OutcomeRecord(
        prediction_id=prediction_id,
        actual_attendance=actual_attendance,
        actual_preparation=round(actual_preparation, 2),
        actual_consumption=round(actual_consumption, 2),
        actual_surplus=surplus,
        actual_waste=actual_w,
        prediction_error=pred_error,
        absolute_error=abs_error,
        percent_error=pct_error,
        waste_reduction_achieved=reduction_achieved,
    )
    pred.status = "OUTCOME_RECORDED"

    db.add(outcome)
    db.commit()
    db.refresh(outcome)
    return outcome


def get_prediction(db: Session, prediction_id: str) -> Optional[PredictionRecord]:
    """Retrieve a single prediction along with linked interventions and outcome."""
    return db.query(PredictionRecord).filter(PredictionRecord.id == prediction_id).first()


def list_predictions(
    db: Session,
    limit: int = 50,
    offset: int = 0,
) -> List[PredictionRecord]:
    """Retrieve recent predictions ordered by creation timestamp."""
    return (
        db.query(PredictionRecord)
        .order_by(PredictionRecord.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_feedback_analytics(db: Session) -> Dict[str, Any]:
    """Compute aggregated accuracy metrics, cumulative SDG impact, and feedback trends."""
    total_preds = db.query(func.count(PredictionRecord.id)).scalar() or 0
    total_outcomes = db.query(func.count(OutcomeRecord.id)).scalar() or 0

    avg_mae = (
        db.query(func.avg(OutcomeRecord.absolute_error)).scalar() or 0.0
    )
    avg_mape = (
        db.query(func.avg(OutcomeRecord.percent_error)).scalar() or 0.0
    )
    total_waste_prevented = (
        db.query(func.sum(OutcomeRecord.waste_reduction_achieved)).scalar() or 0.0
    )

    # Risk level distribution
    risk_counts = (
        db.query(PredictionRecord.risk_level, func.count(PredictionRecord.id))
        .group_by(PredictionRecord.risk_level)
        .all()
    )
    risk_dist = {r[0]: r[1] for r in risk_counts}

    # Time series of recent prediction vs actuals
    recent_outcomes = (
        db.query(
            OutcomeRecord.recorded_at,
            PredictionRecord.meal,
            PredictionRecord.predicted_waste,
            OutcomeRecord.actual_waste,
            OutcomeRecord.absolute_error,
        )
        .join(PredictionRecord, OutcomeRecord.prediction_id == PredictionRecord.id)
        .order_by(OutcomeRecord.recorded_at.desc())
        .limit(20)
        .all()
    )

    comparison_history = [
        {
            "recorded_at": r[0].isoformat() if r[0] else "",
            "meal": r[1],
            "predicted_waste": r[2],
            "actual_waste": r[3],
            "absolute_error": r[4],
        }
        for r in recent_outcomes
    ]

    return {
        "total_predictions": total_preds,
        "total_outcomes_recorded": total_outcomes,
        "mean_absolute_error_historical": round(float(avg_mae), 2),
        "mean_absolute_percentage_error": round(float(avg_mape), 2),
        "cumulative_impact": {
            "waste_prevented_kg": round(float(total_waste_prevented), 2),
            "co2e_prevented_kg": round(float(total_waste_prevented * CO2E_PER_KG_FOOD), 2),
            "water_saved_liters": round(float(total_waste_prevented * WATER_LITERS_PER_KG_FOOD), 2),
            "meals_salvaged": round(float(total_waste_prevented / KG_PER_MEAL_PORTION), 1) if KG_PER_MEAL_PORTION > 0 else 0.0,
            "financial_savings_usd": round(float(total_waste_prevented * ESTIMATED_COST_PER_KG), 2),
        },
        "risk_distribution": risk_dist,
        "prediction_vs_actual_history": comparison_history,
    }
