"""Lightering — the cost of not fitting.

When a ship draws more than the port permits, part of the cargo is discharged
into smaller vessels at a deepwater anchorage first. Sandheads serves Haldia and
Kolkata this way; the Vizag outer anchorage does the same job for restricted
inner-harbour berths.

It is never free, and the cost has three parts people routinely miss:

  1. the barge or lighter hire, per tonne moved
  2. the extra days the mother vessel spends at anchor — and she is still on
     hire, still burning port fuel, and if laytime has expired she is on
     demurrage the whole time
  3. the second discharge operation, because the lightered parcel has to be
     unloaded again at the berth

Point 2 dominates. A Capesize sitting at anchorage for four days at typical
demurrage costs more than the barge hire on a large parcel, which is why the
right comparison is almost never "lighter versus don't lighter" but "lighter
versus use the smaller ship that simply fits". The assignment optimiser makes
exactly that comparison.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..core.config import CharterTerms
from ..core.provenance import Provenance, Quantity, Source
from ..core.reference import Port, VesselClass


@dataclass(frozen=True, slots=True)
class LighteringPlan:
    tonnes_lightered: Quantity
    barge_cost_usd: Quantity
    extra_days: Quantity
    mother_vessel_cost_usd: Quantity
    second_handling_cost_usd: Quantity
    total_cost_usd: Quantity
    cost_per_tonne_of_cargo: Quantity
    anchorage: Port
    notes: tuple[str, ...] = ()

    def explain(self) -> str:
        lines = [
            f"lightering at {self.anchorage.name}",
            f"  tonnes moved      {self.tonnes_lightered.fmt(0)}",
            f"  barge hire        {self.barge_cost_usd.fmt(0)}",
            f"  extra days        {self.extra_days.fmt(1)}",
            f"  mother vessel     {self.mother_vessel_cost_usd.fmt(0)} (hire/demurrage + port fuel)",
            f"  second handling   {self.second_handling_cost_usd.fmt(0)}",
            f"  TOTAL             {self.total_cost_usd.badged(0)}",
            f"  per tonne cargo   {self.cost_per_tonne_of_cargo.badged(2)}",
        ]
        lines += [f"  - {n}" for n in self.notes]
        return "\n".join(lines)


def plan_lightering(
    vessel: VesselClass,
    total_cargo_t: float,
    max_intake_at_berth_t: float,
    anchorage: Port,
    *,
    terms: CharterTerms,
    barge_rate_usd_per_t: float | None = None,
    barge_capacity_t: float = 8_000.0,
    barge_cycle_days: float = 1.5,
    barges_available: int = 2,
    bunker_price_usd_per_mt: float = 600.0,
    second_handling_usd_per_t: float | None = None,
) -> LighteringPlan:
    """Cost of moving the excess parcel over the side at an anchorage.

    ``barge_rate_usd_per_t`` and ``second_handling_usd_per_t`` are commercial
    quotes, not physical constants. When not supplied they are badged SIMULATED
    and the memo shows it — a lightering recommendation carrying a modelled barge
    rate must not be presented as a firm number to a procurement officer.
    """
    notes: list[str] = []
    excess = max(0.0, total_cargo_t - max_intake_at_berth_t)

    if excess <= 0:
        zero = Provenance.derived("vessel fits at berth; no lightering required")
        z = Quantity(0.0, "USD", zero, "lightering_total")
        return LighteringPlan(
            tonnes_lightered=Quantity(0.0, "t", zero, "tonnes_lightered"),
            barge_cost_usd=z,
            extra_days=Quantity(0.0, "day", zero, "extra_days"),
            mother_vessel_cost_usd=z,
            second_handling_cost_usd=z,
            total_cost_usd=z,
            cost_per_tonne_of_cargo=Quantity(0.0, "USD/t", zero, "lightering_per_t"),
            anchorage=anchorage,
            notes=("no lightering required",),
        )

    if barge_rate_usd_per_t is None:
        barge_rate_usd_per_t = 6.50
        barge_prov = Provenance.simulated(
            "assumed barge/lighter rate pending a real quote",
            note="East Coast India transhipment; obtain a quote before relying on this",
        )
        notes.append(
            "barge rate is an assumption, not a quote — get a real figure from the "
            "transhipment operator before this number leaves the building"
        )
    else:
        barge_prov = Provenance.observed(
            Source(name="transhipment operator quote"), confidence="high"
        )

    tonnes = Quantity(
        excess,
        "t",
        Provenance.derived(
            f"excess = total_cargo({total_cargo_t:,.0f} t) - berth_intake({max_intake_at_berth_t:,.0f} t)"
        ),
        "tonnes_lightered",
    )

    barge_cost = Quantity(
        excess * barge_rate_usd_per_t,
        "USD",
        Provenance.derived(
            f"tonnes_lightered x barge_rate({barge_rate_usd_per_t:.2f} USD/t)",
            tonnes.prov,
            barge_prov,
        ),
        "barge_cost",
    )

    # Barge cycles run in parallel up to the number of barges available.
    import math

    trips = math.ceil(excess / barge_capacity_t)
    waves = math.ceil(trips / max(1, barges_available))
    extra = waves * barge_cycle_days
    extra_days = Quantity(
        extra,
        "day",
        Provenance.derived(
            f"ceil({trips} trips / {barges_available} barges) x {barge_cycle_days} d/cycle",
            tonnes.prov,
        ),
        "extra_days",
    )

    # The mother vessel is idle but not free: demurrage (once laytime has gone,
    # it runs continuously) plus port-mode fuel.
    daily_vessel = terms.demurrage_usd_per_day + vessel.consumption_port_mtpd * bunker_price_usd_per_mt
    mother = Quantity(
        extra * daily_vessel,
        "USD",
        Provenance.derived(
            f"extra_days x (demurrage {terms.demurrage_usd_per_day:,.0f} USD/day "
            f"+ port fuel {vessel.consumption_port_mtpd:.1f} mt/day "
            f"x {bunker_price_usd_per_mt:,.0f} USD/mt)",
            extra_days.prov,
        ),
        "mother_vessel_cost",
    )

    if second_handling_usd_per_t is None:
        second_handling_usd_per_t = 2.00
        sh_prov = Provenance.simulated("assumed second-handling cost per tonne")
        notes.append("second-handling cost is an assumption pending a terminal quote")
    else:
        sh_prov = Provenance.observed(Source(name="terminal handling quote"), confidence="high")

    second = Quantity(
        excess * second_handling_usd_per_t,
        "USD",
        Provenance.derived(
            f"tonnes_lightered x second_handling({second_handling_usd_per_t:.2f} USD/t)",
            tonnes.prov,
            sh_prov,
        ),
        "second_handling_cost",
    )

    total = Quantity(
        barge_cost.value + mother.value + second.value,
        "USD",
        Provenance.derived(
            "total = barge_hire + mother_vessel_idle + second_handling",
            barge_cost.prov,
            mother.prov,
            second.prov,
        ),
        "lightering_total",
    )

    per_t = Quantity(
        total.value / total_cargo_t if total_cargo_t else 0.0,
        "USD/t",
        Provenance.derived("total_lightering / total_cargo", total.prov),
        "lightering_per_t",
    )

    share = mother.value / total.value if total.value else 0.0
    if share > 0.4:
        notes.append(
            f"idle mother-vessel time is {share:.0%} of the lightering bill — "
            f"compare hard against a smaller class that berths directly"
        )

    return LighteringPlan(
        tonnes_lightered=tonnes,
        barge_cost_usd=barge_cost,
        extra_days=extra_days,
        mother_vessel_cost_usd=mother,
        second_handling_cost_usd=second,
        total_cost_usd=total,
        cost_per_tonne_of_cargo=per_t,
        anchorage=anchorage,
        notes=tuple(notes),
    )
