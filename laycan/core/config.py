"""Configuration — commercial conventions as parameters, never as constants.

Everything in here is negotiated per fixture in real life. Laytime terms, the
despatch basis, address and brokerage commission, under-keel clearance policy:
none of these is a universal standard, and hardcoding one is how a tool starts
producing answers that a chartering manager knows are wrong.

The defaults below are documented and conservative. Each carries a note saying
what it actually depends on, so that when SAIL says "our COAs are SHEX and
despatch is nil", it is a config change and not a code change.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field, replace
from enum import Enum
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]


class LaytimeTerms(str, Enum):
    """Which days count against laytime.

    SHINC counts Sundays and holidays; SHEX excludes them. SHEX EIU ("even if
    used") excludes them even when the port works. The difference on a
    seven-day discharge is easily a day of demurrage, so it is never assumed.
    """

    SHINC = "SHINC"          # Sundays and Holidays INCluded
    SHEX = "SHEX"            # Sundays and Holidays EXcepted
    SHEX_EIU = "SHEX_EIU"    # excepted even if used


class DespatchBasis(str, Enum):
    """What the owner pays back for finishing early.

    Half demurrage is common in dry bulk but not universal. Nil despatch is
    frequent in coal COAs. "Working time saved" pays only on days the port would
    have worked, and is materially less than "all time saved".
    """

    NIL = "nil"
    HALF_DEMURRAGE = "half_demurrage"
    ALL_TIME_SAVED = "all_time_saved"
    WORKING_TIME_SAVED = "working_time_saved"


@dataclass(frozen=True, slots=True)
class CharterTerms:
    """The commercial envelope for one fixture."""

    laytime_terms: LaytimeTerms = LaytimeTerms.SHINC
    despatch_basis: DespatchBasis = DespatchBasis.HALF_DEMURRAGE
    demurrage_usd_per_day: float = 25_000.0
    laytime_hours_total: float | None = None      # None => derive from handling rate
    once_on_demurrage: bool = True
    """Once on demurrage, always on demurrage.

    Standard in dry bulk: after laytime expires, excepted periods stop being
    excepted and demurrage runs continuously including Sundays, holidays and
    weather stoppages. Switching this off changes the arithmetic materially and
    should only be done if the charterparty genuinely says so.
    """

    address_commission: float = 0.0325
    """Address commission, deducted from gross freight. Typically 2.5%-3.75%."""

    brokerage_commission: float = 0.0125
    """Brokerage, also deducted from gross freight. Typically 1.25%."""

    def commission_total(self) -> float:
        return self.address_commission + self.brokerage_commission

    def despatch_rate(self) -> float:
        if self.despatch_basis is DespatchBasis.NIL:
            return 0.0
        if self.despatch_basis is DespatchBasis.HALF_DEMURRAGE:
            return self.demurrage_usd_per_day * 0.5
        return self.demurrage_usd_per_day


@dataclass(frozen=True, slots=True)
class SafetyPolicy:
    """Under-keel clearance and the margins we will not trade away.

    UKC is a safety policy, not an optimisation variable. Squat grows with speed
    in shallow water and the seabed is not perfectly surveyed, so the clearance
    stays. If a recommendation only works by shaving UKC, it is not a
    recommendation, it is a grounding.
    """

    ukc_m: float = 0.60
    ukc_fraction_of_draft: float = 0.0
    """Some ports specify UKC as a fraction of draft rather than absolute.

    Hay Point mandates a minimum 1.5 m. When a port specifies its own, that
    figure wins over this default — see ``effective_ukc``.
    """

    min_ukc_floor_m: float = 0.30
    tidal_assumption: str = "mean_high_water_neaps"
    """Which tide we are allowed to assume.

    Conservative on purpose: assuming spring highs makes a shallow port look
    navigable on paper for a ship that will wait days for the right tide.
    """

    def effective_ukc(self, draft_m: float, port_ukc_m: float | None = None) -> float:
        if port_ukc_m is not None:
            return max(port_ukc_m, self.min_ukc_floor_m)
        frac = draft_m * self.ukc_fraction_of_draft
        return max(self.ukc_m, frac, self.min_ukc_floor_m)


@dataclass(frozen=True, slots=True)
class BunkerPrices:
    """Fuel, in USD per metric tonne. Sourced from EIA proxies; badge accordingly."""

    vlsfo_usd_per_mt: float = 600.0
    mgo_usd_per_mt: float = 850.0
    eca_applies: bool = False


@dataclass(frozen=True, slots=True)
class StoppingConfig:
    """Optimal stopping / reservation rate parameters."""

    n_paths: int = 20_000
    basis: str = "quadratic"           # regression basis for Longstaff-Schwartz
    seed: int = 20260904
    risk_aversion_lambda: float = 0.0
    """Zero means minimise expected cost.

    Raise it and the policy fixes earlier, buying certainty at a small expected
    premium — which is often what a plant with no coal actually wants.
    """

    late_penalty_usd_per_day: float = 0.0
    """Cost of missing the laycan window. Plant-specific; ask before assuming."""


@dataclass(frozen=True, slots=True)
class HedgeConfig:
    """FFA hedging policy."""

    max_hedge_ratio: float = 1.0
    min_hedge_ratio: float = 0.0
    lot_size_days: int = 30
    """FFA lots are quoted in days of a time-charter index, not tonnes."""

    report_residual_basis: bool = True
    """Non-negotiable. A hedge on a liquid index against a specific route leaves
    basis risk, and not reporting it overstates protection."""


@dataclass(frozen=True, slots=True)
class Flags:
    """Behaviour switches. These are the demo, not conveniences."""

    llm_enabled: bool = True
    demo_mode: bool = False
    demo_snapshot: Path = REPO_ROOT / "data" / "snapshots" / "demo-v1"
    llm_cache_enabled: bool = True
    llm_cache_dir: Path = REPO_ROOT / ".cache" / "llm"
    enforce_no_numerals: bool = True
    enforce_point_in_time: bool = True

    def __post_init__(self) -> None:
        if not self.enforce_no_numerals:
            # Loud, because someone will try this to make a test pass.
            import warnings

            warnings.warn(
                "ENFORCE_NO_NUMERALS is off. LLM output can now contain fabricated "
                "figures. This is the single most dangerous configuration in LAYCAN.",
                RuntimeWarning,
                stacklevel=2,
            )


@dataclass(frozen=True, slots=True)
class Config:
    """Top-level configuration, assembled from the environment with safe defaults."""

    terms: CharterTerms = field(default_factory=CharterTerms)
    safety: SafetyPolicy = field(default_factory=SafetyPolicy)
    bunkers: BunkerPrices = field(default_factory=BunkerPrices)
    stopping: StoppingConfig = field(default_factory=StoppingConfig)
    hedge: HedgeConfig = field(default_factory=HedgeConfig)
    flags: Flags = field(default_factory=Flags)

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    gemini_temperature: float = 0.1
    data_dir: Path = REPO_ROOT / "data"
    git_sha: str = "unknown"

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> "Config":
        e = env if env is not None else dict(os.environ)

        def b(key: str, default: bool) -> bool:
            raw = e.get(key)
            if raw is None or raw == "":
                return default
            return raw.strip().lower() in {"1", "true", "yes", "on"}

        def f(key: str, default: float) -> float:
            try:
                return float(e[key])
            except (KeyError, ValueError):
                return default

        flags = Flags(
            llm_enabled=b("LLM_ENABLED", True),
            demo_mode=b("DEMO_MODE", False),
            demo_snapshot=Path(e.get("DEMO_SNAPSHOT") or REPO_ROOT / "data" / "snapshots" / "demo-v1"),
            llm_cache_enabled=b("LLM_CACHE_ENABLED", True),
            llm_cache_dir=Path(e.get("LLM_CACHE_DIR") or REPO_ROOT / ".cache" / "llm"),
            enforce_no_numerals=b("ENFORCE_NO_NUMERALS", True),
            enforce_point_in_time=b("ENFORCE_POINT_IN_TIME", True),
        )
        return cls(
            flags=flags,
            gemini_api_key=e.get("GEMINI_API_KEY", ""),
            gemini_model=e.get("GEMINI_MODEL", "gemini-2.0-flash"),
            gemini_temperature=f("GEMINI_TEMPERATURE", 0.1),
            bunkers=BunkerPrices(
                vlsfo_usd_per_mt=f("VLSFO_USD_PER_MT", 600.0),
                mgo_usd_per_mt=f("MGO_USD_PER_MT", 850.0),
            ),
            git_sha=e.get("GIT_SHA", "unknown"),
        )

    def with_(self, **kw: Any) -> "Config":
        return replace(self, **kw)


DEFAULT = Config()
