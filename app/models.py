"""Pydantic request and response models for the Poisson Calculator API.

Defines all data structures for API communication, including input
validation with field-level and cross-field rules.
"""

from datetime import datetime, timezone

from pydantic import BaseModel, Field, field_validator, model_validator


class TimestampRange(BaseModel):
    """A pair of timezone-aware timestamps defining an observation period."""

    start: datetime = Field(..., description="Start of observation period (ISO 8601 with timezone)", examples=["2026-01-01T00:00:00+00:00"])
    end: datetime = Field(..., description="End of observation period (ISO 8601 with timezone)", examples=["2026-06-01T23:59:59-05:00"])

    @model_validator(mode="after")
    def start_must_precede_end(self) -> "TimestampRange":
        """Validate that start is strictly before end after UTC conversion."""
        start_utc = self.start.astimezone(timezone.utc)
        end_utc = self.end.astimezone(timezone.utc)
        if start_utc >= end_utc:
            raise ValueError("Start must be before End")
        return self


class WindowDuration(BaseModel):
    """Duration of the observation window expressed in days and hours."""

    days: int = Field(..., ge=0, description="Number of whole days (>= 0)")
    hours: int = Field(..., ge=0, le=23, description="Hours component (0-23)")

    @model_validator(mode="after")
    def total_must_be_positive(self) -> "WindowDuration":
        """Validate that the total window duration is greater than zero."""
        if self.days * 24 + self.hours == 0:
            raise ValueError("Window duration must be greater than zero")
        return self


class CalculationRequest(BaseModel):
    """Incoming request body for the /api/calculate endpoint."""

    time_range: TimestampRange = Field(..., description="Observation time range")
    probability: float = Field(..., gt=0, lt=100, description="Observed probability as a percentage, strictly between 0 and 100", examples=[30.0])

    @field_validator("probability")
    @classmethod
    def probability_must_be_in_range(cls, v: float) -> float:
        """Validate that probability is strictly between 0 and 100."""
        if v <= 0 or v >= 100:
            raise ValueError("Probability must be between 0 and 100 exclusive")
        return v


class CalculationSteps(BaseModel):
    """Intermediate and final results of the Poisson calculation pipeline."""

    lambda_value: float
    window_hours: float
    scaling_factor: float
    annualized_frequency: float


class SurvivalSteps(BaseModel):
    """Results of the survival / half-life analysis."""

    lambda_per_hour: float
    half_life_hours: float
    half_life_days: float
    mean_time_between_events_hours: float
    mean_time_between_events_days: float
    survival_1d: float
    survival_7d: float
    survival_30d: float
    survival_365d: float


class CalculationResponse(BaseModel):
    """Successful response from the /api/calculate endpoint."""

    mode: str
    time_range_utc: TimestampRange
    steps: CalculationSteps
    survival: SurvivalSteps


class ErrorDetail(BaseModel):
    """A single field-level validation error."""

    field: str
    message: str


class ErrorResponse(BaseModel):
    """Structured error response containing all validation failures."""

    errors: list[ErrorDetail]
