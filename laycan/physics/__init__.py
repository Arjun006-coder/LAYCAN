"""Physical feasibility and voyage economics.

This package is the credibility layer. Nothing here is a forecast: it is
arithmetic and geometry, unit-tested, right or wrong. If a Capesize cannot enter
Haldia that is a fact about the world, and it holds whatever any model says.
"""

from .intake import (
    IntakeResult,
    compute_intake,
    dock_water_allowance_mm,
    fresh_water_allowance_mm,
    max_sailing_draft,
)
from .voyage import (
    LaytimeResult,
    VoyageLegs,
    VoyageResult,
    build_legs,
    compute_voyage,
    consumption_at_speed,
    great_circle_nm,
    laytime_outcome,
    port_days_from_rate,
    route_distance_nm,
)
from .lightering import LighteringPlan, plan_lightering

__all__ = [
    "IntakeResult", "compute_intake", "dock_water_allowance_mm",
    "fresh_water_allowance_mm", "max_sailing_draft",
    "LaytimeResult", "VoyageLegs", "VoyageResult", "build_legs", "compute_voyage",
    "consumption_at_speed", "great_circle_nm", "laytime_outcome",
    "port_days_from_rate", "route_distance_nm",
    "LighteringPlan", "plan_lightering",
]
