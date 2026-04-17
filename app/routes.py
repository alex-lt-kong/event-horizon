"""API route handlers for the Poisson Calculator.

Defines the POST /api/calculate endpoint, wires up authentication,
and provides a custom exception handler to transform Pydantic
validation errors into structured ErrorResponse format.
"""

from datetime import timezone

from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.auth import verify_token
from app.calculator import calculate_poisson, calculate_survival
from app.models import (
    CalculationRequest,
    CalculationResponse,
    CalculationSteps,
    ErrorDetail,
    ErrorResponse,
    SurvivalSteps,
    TimestampRange,
)

router = APIRouter()


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Transform FastAPI/Pydantic validation errors into structured ErrorResponse.

    Maps each Pydantic error to an ErrorDetail with a dot-joined field path
    and a human-readable message.
    """
    errors: list[ErrorDetail] = []
    for err in exc.errors():
        loc = err.get("loc", ())
        # Skip the leading "body" segment that FastAPI adds
        field_parts = [str(part) for part in loc if part != "body"]
        field = ".".join(field_parts) if field_parts else "unknown"
        message = err.get("msg", "Validation error")
        errors.append(ErrorDetail(field=field, message=message))

    response = ErrorResponse(errors=errors)
    return JSONResponse(status_code=422, content=response.model_dump())


@router.post("/api/calculate", response_model=CalculationResponse)
async def calculate(
    request: CalculationRequest,
    token: str = Depends(verify_token),
) -> CalculationResponse:
    """Validate inputs, run Poisson calculation, and return all steps.

    - Converts timestamps to UTC
    - Computes window duration from the time range
    - Runs the calculation pipeline
    - Returns structured CalculationResponse with UTC time range and steps
    """
    # Convert timestamps to UTC
    start_utc = request.time_range.start.astimezone(timezone.utc)
    end_utc = request.time_range.end.astimezone(timezone.utc)

    # Compute window duration from time range
    diff_seconds = (end_utc - start_utc).total_seconds()
    total_hours = diff_seconds / 3600
    days = int(total_hours // 24)
    hours = int(total_hours % 24)

    # Run the Poisson calculation
    result = calculate_poisson(
        probability_pct=request.probability,
        days=days,
        hours=hours,
    )

    # Build the response — convert dataclass CalculationSteps to Pydantic model
    steps = CalculationSteps(
        lambda_value=result.lambda_value,
        window_hours=result.window_hours,
        scaling_factor=result.scaling_factor,
        annualized_frequency=result.annualized_frequency,
    )

    # Run survival analysis
    surv = calculate_survival(result.lambda_value, result.window_hours)
    survival = SurvivalSteps(
        lambda_per_hour=surv.lambda_per_hour,
        half_life_hours=surv.half_life_hours,
        half_life_days=surv.half_life_days,
        mean_time_between_events_hours=surv.mean_time_between_events_hours,
        mean_time_between_events_days=surv.mean_time_between_events_days,
        survival_1d=surv.survival_1d,
        survival_7d=surv.survival_7d,
        survival_30d=surv.survival_30d,
        survival_365d=surv.survival_365d,
    )

    return CalculationResponse(
        mode="poisson",
        time_range_utc=TimestampRange(start=start_utc, end=end_utc),
        steps=steps,
        survival=survival,
    )
