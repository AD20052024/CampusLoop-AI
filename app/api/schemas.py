from typing import Literal

from pydantic import BaseModel, Field


class PredictionInput(BaseModel):
    day_number: int = Field(ge=0, le=6)
    month: int = Field(ge=1, le=12)
    meal: Literal["Breakfast", "Lunch", "Dinner"]
    expected_attendance: int = Field(ge=1, le=10000)
    event_type: Literal["Normal", "Event", "Festival"]
    holiday: Literal[0, 1]
    exam_period: Literal[0, 1]
    weather_condition: Literal["Clear", "Cloudy", "Rainy"]


class InterventionUpdate(BaseModel):
    status: Literal["APPROVED", "REJECTED", "EXECUTED"]
    approved_by: str = Field(min_length=1, max_length=100)


class OutcomeInput(BaseModel):
    actual_attendance: int = Field(ge=0, le=10000)
    actual_preparation: float = Field(ge=0, allow_inf_nan=False)
    actual_consumption: float = Field(ge=0, allow_inf_nan=False)
    actual_waste: float = Field(ge=0, allow_inf_nan=False)