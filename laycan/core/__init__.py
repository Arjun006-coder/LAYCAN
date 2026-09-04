"""LAYCAN deterministic core.

Every number in a LAYCAN recommendation originates in this package. The agent
layer may read these values and describe them in English; it may not produce
them. See ``laycan.core.guards.assert_no_numerals``.
"""

from .provenance import (
    Provenance,
    ProvenanceError,
    Quantity,
    Source,
    Status,
    derived_q,
    dumps,
    is_unknown,
    observed_q,
    simulated_q,
    worst_status,
)
from .guards import (
    LookAheadError,
    NumeralLeakError,
    assert_no_numerals,
    assert_point_in_time,
    assert_window_causal,
    find_numerals,
    numerals_report,
)
from .reference import (
    CargoType,
    MissingDatumError,
    Port,
    ReferenceData,
    VesselClass,
    load_cargo_types,
    load_ports,
    load_vessel_classes,
)
from .config import (
    DEFAULT,
    BunkerPrices,
    CharterTerms,
    Config,
    DespatchBasis,
    Flags,
    HedgeConfig,
    LaytimeTerms,
    SafetyPolicy,
    StoppingConfig,
)

__all__ = [
    "Provenance", "ProvenanceError", "Quantity", "Source", "Status",
    "derived_q", "dumps", "is_unknown", "observed_q", "simulated_q", "worst_status",
    "LookAheadError", "NumeralLeakError", "assert_no_numerals",
    "assert_point_in_time", "assert_window_causal", "find_numerals", "numerals_report",
    "CargoType", "MissingDatumError", "Port", "ReferenceData", "VesselClass",
    "load_cargo_types", "load_ports", "load_vessel_classes",
    "DEFAULT", "BunkerPrices", "CharterTerms", "Config", "DespatchBasis",
    "Flags", "HedgeConfig", "LaytimeTerms", "SafetyPolicy", "StoppingConfig",
]
