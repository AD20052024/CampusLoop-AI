from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.agents.campus_agent import get_campus_agent
from app.api.schemas import InterventionUpdate, OutcomeInput, PredictionInput
from app.config import settings
from app.database import repository
from app.database.session import get_db
from app.ml.predictor import predict_waste
from app.rag.knowledge_retriever import retrieve_policies
from app.rules.intervention import get_intervention, get_structured_intervention
from app.rules.waste_risk import calculate_risk
from app.services.impact import calculate_impact

router = APIRouter()


@router.post('/predict')
def predict(data: PredictionInput, db: Session = Depends(get_db)):
    input_data = data.model_dump()
    predicted_waste = predict_waste(input_data)
    risk = calculate_risk(predicted_waste)
    intervention = get_structured_intervention(risk['risk_level'])
    impact = calculate_impact(predicted_waste)
    prediction = repository.save_prediction(
        db=db,
        input_data=input_data,
        predicted_waste=predicted_waste,
        risk_level=risk['risk_level'],
        model_version=settings.app_version,
    )
    intervention_record = repository.save_intervention(
        db=db,
        prediction_id=prediction.id,
        action_type=intervention['action_type'],
        priority=intervention['priority'],
        recommendation=intervention['recommendation'],
        requires_human_approval=intervention['requires_human_approval'],
    )
    intervention.update({
        'id': intervention_record.id,
        'status': intervention_record.status,
    })

    return {
        'prediction_id': prediction.id,
        'predicted_waste': predicted_waste,
        'risk_level': risk['risk_level'],
        'risk': risk,
        'recommended_action': get_intervention(risk['risk_level']),
        'intervention': intervention,
        'impact': impact,
        'model_version': settings.app_version,
    }


@router.post('/predictions/{prediction_id}/interventions/{intervention_id}')
def update_intervention(
    prediction_id: str,
    intervention_id: str,
    update: InterventionUpdate,
    db: Session = Depends(get_db),
):
    prediction = repository.get_prediction(db, prediction_id)
    if prediction is None:
        raise HTTPException(status_code=404, detail='Prediction not found')
    if not any(item.id == intervention_id for item in prediction.interventions):
        raise HTTPException(status_code=404, detail='Intervention not found')

    intervention = repository.update_intervention_status(
        db,
        intervention_id=intervention_id,
        status=update.status,
        approved_by=update.approved_by,
    )
    return {
        'prediction_id': prediction_id,
        'intervention_id': intervention.id,
        'new_status': intervention.status,
        'approved_by': intervention.approved_by,
    }


@router.post('/predictions/{prediction_id}/outcomes', status_code=status.HTTP_201_CREATED)
def create_outcome(
    prediction_id: str,
    outcome: OutcomeInput,
    db: Session = Depends(get_db),
):
    prediction = repository.get_prediction(db, prediction_id)
    if prediction is None:
        raise HTTPException(status_code=404, detail='Prediction not found')
    if prediction.outcome is not None:
        raise HTTPException(status_code=409, detail='An outcome has already been recorded')

    record = repository.record_outcome(
        db,
        prediction_id=prediction_id,
        actual_attendance=outcome.actual_attendance,
        actual_preparation=outcome.actual_preparation,
        actual_consumption=outcome.actual_consumption,
        actual_waste=outcome.actual_waste,
    )
    return {
        'prediction_id': record.prediction_id,
        'actual_attendance': record.actual_attendance,
        'actual_preparation': record.actual_preparation,
        'actual_consumption': record.actual_consumption,
        'actual_surplus': record.actual_surplus,
        'actual_waste': record.actual_waste,
        'prediction_error': record.prediction_error,
        'absolute_error': record.absolute_error,
        'percent_error': record.percent_error,
        'waste_reduction_achieved': record.waste_reduction_achieved,
    }


@router.get('/predictions/{prediction_id}')
def prediction_detail(prediction_id: str, db: Session = Depends(get_db)):
    prediction = repository.get_prediction(db, prediction_id)
    if prediction is None:
        raise HTTPException(status_code=404, detail='Prediction not found')
    outcome = prediction.outcome
    return {
        'prediction_id': prediction.id,
        'created_at': prediction.created_at.isoformat() if prediction.created_at else None,
        'meal': prediction.meal,
        'expected_attendance': prediction.expected_attendance,
        'predicted_waste': prediction.predicted_waste,
        'risk_level': prediction.risk_level,
        'model_version': prediction.model_version,
        'status': prediction.status,
        'interventions': [
            {
                'id': item.id,
                'action_type': item.action_type,
                'priority': item.priority,
                'recommendation': item.recommendation,
                'requires_human_approval': item.requires_human_approval,
                'status': item.status,
                'approved_by': item.approved_by,
            }
            for item in prediction.interventions
        ],
        'outcome': ({
            'actual_attendance': outcome.actual_attendance,
            'actual_preparation': outcome.actual_preparation,
            'actual_consumption': outcome.actual_consumption,
            'actual_waste': outcome.actual_waste,
            'prediction_error': outcome.prediction_error,
            'absolute_error': outcome.absolute_error,
            'percent_error': outcome.percent_error,
            'waste_reduction_achieved': outcome.waste_reduction_achieved,
        } if outcome else None),
    }


@router.get('/predictions')
def predictions(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    records = repository.list_predictions(db, limit=limit, offset=offset)
    return {
        'items': [
            {
                'prediction_id': item.id,
                'created_at': item.created_at.isoformat() if item.created_at else None,
                'meal': item.meal,
                'expected_attendance': item.expected_attendance,
                'predicted_waste': item.predicted_waste,
                'risk_level': item.risk_level,
                'status': item.status,
                'outcome': ({
                    'actual_waste': item.outcome.actual_waste,
                    'prediction_error': item.outcome.prediction_error,
                    'waste_reduction_achieved': item.outcome.waste_reduction_achieved,
                } if item.outcome else None),
            }
            for item in records
        ],
        'limit': limit,
        'offset': offset,
    }


@router.get('/feedback/analytics')
def feedback_analytics(db: Session = Depends(get_db)):
    return repository.get_feedback_analytics(db)


@router.get('/rag/policies')
def rag_policies(
    query: str = Query(min_length=1, max_length=500),
    top_k: int = Query(default=3, ge=1, le=10),
):
    return {
        'query': query,
        'citations': retrieve_policies(query, top_k=top_k),
    }


@router.post('/agent/run')
def run_agent(data: PredictionInput, db: Session = Depends(get_db)):
    return get_campus_agent().run_workflow(data.model_dump(), db=db)