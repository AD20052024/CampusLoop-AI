import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from app.database.session import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class PredictionRecord(Base):
    """Stores operational input features and ML output predictions."""
    __tablename__ = "predictions"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Operational features
    day_number = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    meal = Column(String(20), nullable=False, index=True)
    expected_attendance = Column(Integer, nullable=False)
    event_type = Column(String(50), default="Normal")
    holiday = Column(Integer, default=0)
    exam_period = Column(Integer, default=0)
    weather_condition = Column(String(50), default="Clear")

    # Outputs
    predicted_waste = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False, index=True)
    model_version = Column(String(20), default="0.1.0")
    status = Column(String(30), default="PREDICTED", index=True)

    # Relationships
    interventions = relationship(
        "InterventionRecord",
        back_populates="prediction",
        cascade="all, delete-orphan",
    )
    outcome = relationship(
        "OutcomeRecord",
        back_populates="prediction",
        uselist=False,
        cascade="all, delete-orphan",
    )


class InterventionRecord(Base):
    """Tracks recommended and human-approved dining interventions."""
    __tablename__ = "interventions"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    prediction_id = Column(String(36), ForeignKey("predictions.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    action_type = Column(String(50), nullable=False)
    priority = Column(String(20), default="Standard")
    recommendation = Column(Text, nullable=False)
    requires_human_approval = Column(Boolean, default=True)

    # Operational status: RECOMMENDED, APPROVED, REJECTED, EXECUTED
    status = Column(String(30), default="RECOMMENDED", index=True)
    approved_by = Column(String(100), nullable=True)
    executed_at = Column(DateTime, nullable=True)

    prediction = relationship("PredictionRecord", back_populates="interventions")


class OutcomeRecord(Base):
    """Captures post-service actual dining metrics to close the feedback loop."""
    __tablename__ = "outcomes"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    prediction_id = Column(String(36), ForeignKey("predictions.id"), nullable=False, unique=True, index=True)
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    actual_attendance = Column(Integer, nullable=False)
    actual_preparation = Column(Float, nullable=False)
    actual_consumption = Column(Float, nullable=False)
    actual_surplus = Column(Float, nullable=False)
    actual_waste = Column(Float, nullable=False)

    # Evaluation & Feedback Analytics
    prediction_error = Column(Float, nullable=False)      # predicted - actual
    absolute_error = Column(Float, nullable=False)        # |predicted - actual|
    percent_error = Column(Float, nullable=True)          # Absolute percentage error (MAPE)
    waste_reduction_achieved = Column(Float, default=0.0) # Estimated waste avoided (kg)

    prediction = relationship("PredictionRecord", back_populates="outcome")


class ModelVersionRecord(Base):
    """Tracks model versions, deployment dates, and benchmark performance."""
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_version = Column(String(30), nullable=False, unique=True)
    algorithm = Column(String(100), default="RandomForestRegressor")
    mae = Column(Float, nullable=False)
    rmse = Column(Float, nullable=False)
    r2 = Column(Float, nullable=False)
    features = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
