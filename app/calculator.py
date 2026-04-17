"""Pure calculation functions for the Event Horizon probability toolkit.

All functions are pure (no side effects, no HTTP concerns). The module
implements:
1. Poisson annualized frequency — given an observed probability of at least
   one event in a time window, derive the annualized frequency.
2. Survival analysis — half-life, mean time between events, and survival
   probabilities at various horizons.
"""

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class CalculationSteps:
    """Intermediate and final results of the Poisson calculation pipeline."""

    lambda_value: float
    window_hours: float
    scaling_factor: float
    annualized_frequency: float


@dataclass(frozen=True)
class SurvivalSteps:
    """Results of the survival / half-life analysis."""

    lambda_per_hour: float
    half_life_hours: float
    half_life_days: float
    mean_time_between_events_hours: float
    mean_time_between_events_days: float
    survival_1d: float   # P(no event in 1 day)
    survival_7d: float   # P(no event in 7 days)
    survival_30d: float  # P(no event in 30 days)
    survival_365d: float # P(no event in 365 days)


def compute_lambda(probability_pct: float) -> float:
    """Derive λ from the observed probability using the inverse Poisson CDF.

    Given P(at least 1 event) = 1 − e^(−λ), solving for λ gives:
        λ = −ln(1 − probability / 100)

    Args:
        probability_pct: Observed probability as a percentage in (0, 100).

    Returns:
        The expected number of events (λ) in the observation window.
    """
    return -math.log(1 - probability_pct / 100)


def compute_window_hours(days: int, hours: int) -> float:
    """Convert a window duration of days and hours into total hours.

    Args:
        days: Number of whole days (≥ 0).
        hours: Number of additional hours (0–23).

    Returns:
        Total window duration in hours.
    """
    return (days * 24) + hours


def compute_scaling_factor(window_hours: float, hours_in_year: float = 8766.0) -> float:
    """Compute the ratio to scale from the observation window to one year.

    Args:
        window_hours: Duration of the observation window in hours (must be > 0).
        hours_in_year: Number of hours in a year. Defaults to 8766.0
            (average accounting for leap years).

    Returns:
        The scaling factor (hours_in_year / window_hours).
    """
    return hours_in_year / window_hours


def compute_annualized_frequency(lambda_val: float, scaling_factor: float) -> float:
    """Scale λ from the observation window to an annual frequency.

    Args:
        lambda_val: Expected number of events in the observation window.
        scaling_factor: Ratio of one year to the observation window.

    Returns:
        Annualized frequency rounded to two decimal places.
    """
    return round(lambda_val * scaling_factor, 2)


def calculate_poisson(probability_pct: float, days: int, hours: int) -> CalculationSteps:
    """Run the full Poisson calculation pipeline.

    Computes all intermediate steps and returns them together with the
    final annualized frequency.

    Args:
        probability_pct: Observed probability as a percentage in (0, 100).
        days: Days component of the observation window (≥ 0).
        hours: Hours component of the observation window (0–23).

    Returns:
        A CalculationSteps object containing lambda_value, window_hours,
        scaling_factor, and annualized_frequency.
    """
    lambda_val = compute_lambda(probability_pct)
    window_hours = compute_window_hours(days, hours)
    scaling_factor = compute_scaling_factor(window_hours)
    annualized_freq = compute_annualized_frequency(lambda_val, scaling_factor)
    return CalculationSteps(
        lambda_value=lambda_val,
        window_hours=window_hours,
        scaling_factor=scaling_factor,
        annualized_frequency=annualized_freq,
    )


def compute_survival_probability(lambda_per_hour: float, hours: float) -> float:
    """P(no event in the given time) = e^(−λ_per_hour × hours)."""
    return math.exp(-lambda_per_hour * hours)


def calculate_survival(lambda_value: float, window_hours: float) -> SurvivalSteps:
    """Run the survival / half-life analysis.

    Args:
        lambda_value: Expected events in the observation window (from Poisson).
        window_hours: Duration of the observation window in hours.

    Returns:
        A SurvivalSteps object with half-life, MTBE, and survival probabilities.
    """
    lambda_per_hour = lambda_value / window_hours

    # Half-life: time at which P(at least 1 event) = 50%
    # P(survive t) = e^(-λh * t) = 0.5  =>  t = ln(2) / λh
    half_life_hours = math.log(2) / lambda_per_hour
    half_life_days = half_life_hours / 24

    # Mean time between events = 1 / λ_per_hour
    mtbe_hours = 1.0 / lambda_per_hour
    mtbe_days = mtbe_hours / 24

    return SurvivalSteps(
        lambda_per_hour=lambda_per_hour,
        half_life_hours=round(half_life_hours, 2),
        half_life_days=round(half_life_days, 2),
        mean_time_between_events_hours=round(mtbe_hours, 2),
        mean_time_between_events_days=round(mtbe_days, 2),
        survival_1d=round(compute_survival_probability(lambda_per_hour, 24) * 100, 2),
        survival_7d=round(compute_survival_probability(lambda_per_hour, 168) * 100, 2),
        survival_30d=round(compute_survival_probability(lambda_per_hour, 720) * 100, 2),
        survival_365d=round(compute_survival_probability(lambda_per_hour, 8766) * 100, 2),
    )
