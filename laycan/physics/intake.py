"""Draft-limited intake — the arithmetic that makes shipping people trust us.

A ship sinks deeper the more you load into it. Every port has a depth limit. So
a port's depth limit is really a cargo limit, and the universal instinct —
bigger ship, lower cost per tonne, always better — is frequently wrong.

The chain, in order:

  1. permissible draft at the berth, minus under-keel clearance -> d_max
  2. if the water is brackish, the ship floats deeper: apply FWA/DWA
  3. deadweight sacrificed = TPC x 100 x (summer_draft - d_max)
  4. cargo intake = DWT - constants - bunkers, capped by hold volume
  5. take the *lower* of the weight limit and the volume limit

Worked example, real numbers. A Capesize at 180,000 DWT draws about 18.0 m
summer. Haldia permits about 8.5 m. Subtract clearance and the ship would have
to shed roughly nine metres of draft — which is not a reduced cargo, it is a
physical impossibility, because the vessel's own lightship draft exceeds the
limit. So Haldia is not a "load less" port for a Cape; it is a no.

Newcastle is the subtler and more interesting case: sailing draft around 16.1 m
against a Cape's 18.0 m means the ship *cannot leave the load port full*
regardless of how deep the discharge port is. Load-end limits bite first and
teams forget them.

Every figure here is DERIVED from OBSERVED port and vessel data. Nothing in this
module is allowed to depend on a modelled input — ``require_defensible``
enforces that, because a feasibility promise built on a simulated draft is how
you ground a ship.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ..core.config import SafetyPolicy
from ..core.provenance import Provenance, Quantity, Status
from ..core.reference import CargoType, MissingDatumError, Port, VesselClass

SEAWATER_DENSITY = 1025.0  # kg/m3, the load-line reference


# ---------------------------------------------------------------------------
# fresh / dock water allowance
# ---------------------------------------------------------------------------

def fresh_water_allowance_mm(displacement_t: float, tpc: float) -> float:
    """FWA = displacement / (4 x TPC), in millimetres.

    The standard load-line result: how much deeper a ship floats in fresh water
    (1000 kg/m3) than in salt (1025). Derived from the requirement that
    displaced mass is conserved as density changes.
    """
    if tpc <= 0:
        raise ValueError("TPC must be positive")
    return displacement_t / (4.0 * tpc)


def dock_water_allowance_mm(fwa_mm: float, dock_density_kg_m3: float) -> float:
    """DWA = FWA x (1025 - rho_dock) / 25.

    Interpolates between salt and fresh. At Haldia's roughly 1010 kg/m3 this is
    about 60% of the full FWA — a real and non-trivial extra immersion that is
    routinely forgotten. Ignore it and your arrival draft is optimistic by
    several centimetres of loaded cargo, in the one place with the least
    clearance to spare.
    """
    if dock_density_kg_m3 >= SEAWATER_DENSITY:
        return 0.0
    return fwa_mm * (SEAWATER_DENSITY - dock_density_kg_m3) / 25.0


# ---------------------------------------------------------------------------
# results
# ---------------------------------------------------------------------------

Verdict = Literal["feasible", "infeasible", "requires_lightering", "data_missing"]


@dataclass(frozen=True, slots=True)
class IntakeResult:
    """How much cargo a class can actually load for a given port pair."""

    verdict: Verdict
    vessel: VesselClass
    load_port: Port
    discharge_port: Port
    cargo: CargoType

    intake_t: Quantity | None
    binding_constraint: str
    d_max_m: Quantity | None
    draft_deficit_m: Quantity | None
    dwt_sacrificed_t: Quantity | None
    volume_limit_t: Quantity | None
    weight_limit_t: Quantity | None
    dwa_mm: Quantity | None
    utilisation: float | None
    reasons: tuple[str, ...] = ()

    @property
    def feasible(self) -> bool:
        return self.verdict in ("feasible", "requires_lightering")

    @property
    def status(self) -> Status:
        return self.intake_t.status if self.intake_t else Status.DERIVED

    def explain(self) -> str:
        lines = [
            f"{self.vessel.name} : {self.load_port.name} -> {self.discharge_port.name} "
            f"({self.cargo.name})",
            f"  verdict           {self.verdict}",
        ]
        if self.d_max_m:
            lines.append(f"  max sailing draft {self.d_max_m.fmt(2)}")
        if self.dwa_mm and self.dwa_mm.value > 0:
            lines.append(f"  dock water allow. {self.dwa_mm.fmt(0)} (brackish correction)")
        if self.draft_deficit_m and self.draft_deficit_m.value > 0:
            lines.append(f"  draft deficit     {self.draft_deficit_m.fmt(2)} vs summer marks")
        if self.dwt_sacrificed_t and self.dwt_sacrificed_t.value > 0:
            lines.append(f"  deadweight lost   {self.dwt_sacrificed_t.fmt(0)}")
        if self.weight_limit_t:
            lines.append(f"  weight limit      {self.weight_limit_t.fmt(0)}")
        if self.volume_limit_t:
            lines.append(f"  volume limit      {self.volume_limit_t.fmt(0)}")
        if self.intake_t:
            lines.append(f"  INTAKE            {self.intake_t.badged(0)}  [{self.binding_constraint}]")
        if self.utilisation is not None:
            lines.append(f"  hold utilisation  {self.utilisation:.1%}")
        for r in self.reasons:
            lines.append(f"  - {r}")
        return "\n".join(lines)


def _infeasible(
    vessel: VesselClass,
    load_port: Port,
    discharge_port: Port,
    cargo: CargoType,
    reasons: list[str],
    verdict: Verdict = "infeasible",
) -> IntakeResult:
    return IntakeResult(
        verdict=verdict,
        vessel=vessel,
        load_port=load_port,
        discharge_port=discharge_port,
        cargo=cargo,
        intake_t=None,
        binding_constraint="none",
        d_max_m=None,
        draft_deficit_m=None,
        dwt_sacrificed_t=None,
        volume_limit_t=None,
        weight_limit_t=None,
        dwa_mm=None,
        utilisation=None,
        reasons=tuple(reasons),
    )


# ---------------------------------------------------------------------------
# the calculation
# ---------------------------------------------------------------------------

def max_sailing_draft(
    port: Port,
    vessel: VesselClass,
    safety: SafetyPolicy,
    *,
    port_ukc_m: float | None = None,
) -> tuple[Quantity, Quantity]:
    """Permissible draft minus under-keel clearance, with brackish correction.

    Returns (d_max, dwa_mm). UKC is a safety policy and is never traded away to
    make a recommendation work.
    """
    permissible = port.q("max_draft_m", "m")
    permissible.prov.require_defensible(f"{port.name} permissible draft")

    ukc = safety.effective_ukc(vessel.summer_draft_m, port_ukc_m)
    d_max_val = permissible.value - ukc

    dwa_mm_val = 0.0
    if port.is_brackish and port.water_density is not None:
        # Displacement at summer marks approximates DWT plus lightship; using
        # DWT alone understates FWA slightly, which is the conservative
        # direction for a feasibility answer.
        tpc_q = vessel.estimated_tpc()
        fwa = fresh_water_allowance_mm(vessel.dwt_typical, tpc_q.value)
        dwa_mm_val = dock_water_allowance_mm(fwa, port.water_density)
        # The ship floats deeper in brackish water, so the draft it may show on
        # arrival is reduced by the allowance.
        d_max_val -= dwa_mm_val / 1000.0

    d_max = Quantity(
        d_max_val,
        "m",
        Provenance.derived(
            f"d_max = permissible_draft - UKC({ukc:.2f} m)"
            + (" - DWA" if dwa_mm_val else ""),
            permissible.prov,
            code_ref="physics.intake.max_sailing_draft",
        ),
        f"{port.port_id}.d_max",
    )
    dwa = Quantity(
        dwa_mm_val,
        "mm",
        Provenance.derived("DWA = FWA x (1025 - rho_dock)/25", permissible.prov),
        f"{port.port_id}.dwa",
    )
    return d_max, dwa


def compute_intake(
    vessel: VesselClass,
    load_port: Port,
    discharge_port: Port,
    cargo: CargoType,
    *,
    safety: SafetyPolicy | None = None,
    bunkers_on_board_t: float = 0.0,
    conservative_stowage: bool = True,
) -> IntakeResult:
    """How many tonnes this class can actually carry on this route.

    The binding draft is the *shallower* of the two ends, because the ship must
    both leave the load port and enter the discharge port. Teams that check only
    the discharge port miss Newcastle, where a Capesize cannot sail full at all.
    """
    safety = safety or SafetyPolicy()
    reasons: list[str] = []

    # --- dimensional gates: LOA and beam are absolute, no cargo reduction helps
    for port, role in ((load_port, "load"), (discharge_port, "discharge")):
        if port.max_loa_m is not None and vessel.loa_m > port.max_loa_m:
            reasons.append(
                f"LOA {vessel.loa_m:.0f} m exceeds {port.name} limit "
                f"{port.max_loa_m:.0f} m ({role} port) — no cargo reduction resolves this"
            )
        if port.max_beam_m is not None and vessel.beam_m > port.max_beam_m:
            reasons.append(
                f"beam {vessel.beam_m:.0f} m exceeds {port.name} limit "
                f"{port.max_beam_m:.0f} m ({role} port)"
            )
        if port.max_dwt is not None and vessel.dwt_min > port.max_dwt:
            reasons.append(
                f"class minimum {vessel.dwt_min:,.0f} DWT exceeds {port.name} "
                f"maximum {port.max_dwt:,.0f} DWT"
            )
    if reasons:
        return _infeasible(vessel, load_port, discharge_port, cargo, reasons)

    # --- draft at both ends
    try:
        d_load, dwa_load = max_sailing_draft(load_port, vessel, safety)
        d_disch, dwa_disch = max_sailing_draft(discharge_port, vessel, safety)
    except MissingDatumError as e:
        return _infeasible(
            vessel, load_port, discharge_port, cargo, [str(e)], verdict="data_missing"
        )

    binding_port = load_port if d_load.value <= d_disch.value else discharge_port
    d_max = d_load if d_load.value <= d_disch.value else d_disch
    dwa = dwa_load if binding_port is load_port else dwa_disch
    reasons.append(f"binding draft is {binding_port.name} at {d_max.fmt(2)}")

    deficit_val = vessel.summer_draft_m - d_max.value
    draft_deficit = Quantity(
        max(0.0, deficit_val),
        "m",
        Provenance.derived("summer_draft - d_max", d_max.prov),
        "draft_deficit",
    )

    tpc_q = vessel.estimated_tpc()

    if deficit_val <= 0:
        dwt_sacrificed = Quantity(
            0.0, "t", Provenance.derived("no draft restriction binds", d_max.prov), "dwt_sacrificed"
        )
        weight_avail = vessel.dwt_typical
    else:
        # DWT sacrificed = TPC x 100 x deficit_in_metres.
        # TPC is tonnes per *centimetre*, hence the factor of 100.
        sacrificed = tpc_q.value * 100.0 * deficit_val
        dwt_sacrificed = Quantity(
            sacrificed,
            "t",
            Provenance.derived(
                "dwt_sacrificed = TPC x 100 x (summer_draft - d_max)",
                tpc_q.prov,
                d_max.prov,
                code_ref="physics.intake.compute_intake",
            ),
            "dwt_sacrificed",
        )
        weight_avail = vessel.dwt_typical - sacrificed

        if weight_avail <= vessel.constants_mt + bunkers_on_board_t:
            reasons.append(
                f"draft limit at {binding_port.name} removes {sacrificed:,.0f} t of "
                f"{vessel.dwt_typical:,.0f} t deadweight — nothing left for cargo after "
                f"constants and bunkers. Physically cannot trade this pair."
            )
            return _infeasible(vessel, load_port, discharge_port, cargo, reasons)

    # --- weight limit: deadweight less the things that are not cargo
    weight_limit_val = weight_avail - vessel.constants_mt - bunkers_on_board_t
    weight_limit = Quantity(
        weight_limit_val,
        "t",
        Provenance.derived(
            "weight_limit = DWT - dwt_sacrificed - constants - bunkers",
            dwt_sacrificed.prov,
            vessel.prov("constants_mt"),
        ),
        "weight_limit",
    )

    # --- volume limit: the hold fills before the marks do, for light cargo
    volume_limit: Quantity | None = None
    if vessel.grain_capacity_m3 is not None:
        sf = cargo.sf(conservative=conservative_stowage)
        volume_limit = Quantity(
            vessel.grain_capacity_m3 / sf.value,
            "t",
            Provenance.derived(
                "volume_limit = grain_capacity_m3 / stowage_factor",
                vessel.prov("grain_capacity_m3"),
                sf.prov,
            ),
            "volume_limit",
        )
    else:
        reasons.append(
            "grain capacity unknown for this class, so the volume limit cannot be "
            "checked; intake is the weight limit only. For coal at a stowage factor "
            "near 1.2 m3/t this is usually weight-limited anyway, but verify against "
            "EU MRV before relying on it for a light cargo."
        )

    # --- INTAKE = min(weight, volume)
    if volume_limit is not None and volume_limit.value < weight_limit.value:
        intake = Quantity(
            volume_limit.value,
            "t",
            Provenance.derived("INTAKE = min(weight_limit, volume_limit)", volume_limit.prov),
            "intake",
        )
        binding = "volume (hold cubic capacity)"
    else:
        intake = Quantity(
            weight_limit.value,
            "t",
            Provenance.derived("INTAKE = min(weight_limit, volume_limit)", weight_limit.prov),
            "intake",
        )
        binding = "draft" if deficit_val > 0 else "deadweight"

    utilisation = intake.value / vessel.dwt_typical if vessel.dwt_typical else None

    verdict: Verdict = "feasible"
    if deficit_val > 0 and utilisation is not None and utilisation < 0.75:
        if discharge_port.lightering_available or binding_port.lightering_available:
            verdict = "requires_lightering"
            reasons.append(
                f"only {utilisation:.0%} of deadweight usable — compare against "
                f"lightering, or against a smaller class that simply fits"
            )
        else:
            reasons.append(
                f"only {utilisation:.0%} of deadweight usable and no lightering at "
                f"{discharge_port.name}; a smaller class is very likely cheaper per tonne"
            )

    return IntakeResult(
        verdict=verdict,
        vessel=vessel,
        load_port=load_port,
        discharge_port=discharge_port,
        cargo=cargo,
        intake_t=intake,
        binding_constraint=binding,
        d_max_m=d_max,
        draft_deficit_m=draft_deficit,
        dwt_sacrificed_t=dwt_sacrificed,
        volume_limit_t=volume_limit,
        weight_limit_t=weight_limit,
        dwa_mm=dwa,
        utilisation=utilisation,
        reasons=tuple(reasons),
    )
