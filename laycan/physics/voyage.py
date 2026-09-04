"""Voyage economics — what a fixture actually costs, and what the owner nets.

Two numbers matter and they are not the same:

  Delivered freight cost per tonne — what the charterer pays. This is what
  LAYCAN optimises, because we act for the buyer.

  TCE, time charter equivalent — what the owner earns per day. We compute it
  because it is the language the market quotes in, and because the reservation
  rate has to be comparable to an FFA level which is quoted as a daily rate.

The commission subtlety that trips teams up: address and brokerage commission
come off *gross* freight before anything else. So

    net_revenue = F x Q x (1 - c_addr - c_brok)
    TCE = (net_revenue - voyage_costs) / total_days

Deducting commission after voyage costs, or netting it against costs, overstates
owner earnings by roughly the commission rate and quietly breaks any comparison
against a quoted TCE.

Bunker consumption follows the admiralty cube law, FC(v) = FC_ref x (v/v_ref)^3.
Cubic, so slowing down is disproportionately effective: shed a knot from
fourteen and burn roughly a fifth less fuel per day. That is the whole basis of
slow-steaming as an idle-time strategy, and it is why "wait at anchorage" is
usually the worst of the four options in the idle module.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..core.config import BunkerPrices, CharterTerms, DespatchBasis, LaytimeTerms
from ..core.provenance import Provenance, Quantity, Source
from ..core.reference import Port, VesselClass

NM_PER_DEGREE = 60.0


# ---------------------------------------------------------------------------
# distance
# ---------------------------------------------------------------------------

def great_circle_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in nautical miles.

    Deliberately labelled for what it is: a floor, not a route. Real sea
    distances follow traffic separation schemes, avoid land, and for
    Australia-to-East-Coast-India pass through or around the Indonesian
    archipelago. Using great-circle understates the voyage — typically by a few
    percent on this trade, more where a strait forces a detour.

    Any distance produced here is badged SIMULATED so the memo shows it. Replace
    with a published port-to-port distance table before quoting a laycan date to
    anyone; the AIS-derived distances are a week-two upgrade, not a nice-to-have.
    """
    import math

    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    x = math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * math.cos(dl)
    x = max(-1.0, min(1.0, x))
    return math.degrees(math.acos(x)) * NM_PER_DEGREE


def route_distance_nm(
    load_port: Port,
    discharge_port: Port,
    *,
    detour_factor: float = 1.12,
    table_nm: float | None = None,
) -> Quantity:
    """Sea distance, from a published table if we have one, else estimated.

    ``detour_factor`` of 1.12 is a documented allowance for the Australia-India
    trade routing around the archipelago. It is an assumption, it is badged, and
    a real distance table supersedes it.
    """
    if table_nm is not None:
        return Quantity(
            table_nm,
            "nm",
            Provenance.observed(
                Source(name="published distance table", licence="verify"),
                confidence="high",
            ),
            "distance",
        )
    if None in (load_port.lat, load_port.lon, discharge_port.lat, discharge_port.lon):
        raise ValueError(f"coordinates missing for {load_port.name} or {discharge_port.name}")
    gc = great_circle_nm(load_port.lat, load_port.lon, discharge_port.lat, discharge_port.lon)
    return Quantity(
        gc * detour_factor,
        "nm",
        Provenance.simulated(
            f"great_circle x detour_factor({detour_factor})",
            note="replace with published distance table or AIS-derived track",
        ),
        "distance",
    )


# ---------------------------------------------------------------------------
# bunkers
# ---------------------------------------------------------------------------

def consumption_at_speed(ref_mtpd: float, ref_speed_kn: float, speed_kn: float) -> float:
    """Admiralty cube law: FC(v) = FC_ref x (v/v_ref)^3."""
    if ref_speed_kn <= 0:
        raise ValueError("reference speed must be positive")
    return ref_mtpd * (speed_kn / ref_speed_kn) ** 3


@dataclass(frozen=True, slots=True)
class VoyageLegs:
    """Time broken down, because demurrage and hire attach to different pieces."""

    sea_days_laden: Quantity
    sea_days_ballast: Quantity
    port_days_load: Quantity
    port_days_discharge: Quantity
    waiting_days: Quantity

    @property
    def total_days(self) -> Quantity:
        return (
            self.sea_days_laden
            + self.sea_days_ballast
            + self.port_days_load
            + self.port_days_discharge
            + self.waiting_days
        ).relabel("total_days")

    @property
    def sea_days(self) -> Quantity:
        return (self.sea_days_laden + self.sea_days_ballast).relabel("sea_days")

    @property
    def port_days(self) -> Quantity:
        return (self.port_days_load + self.port_days_discharge).relabel("port_days")


def port_days_from_rate(
    intake_t: Quantity,
    port: Port,
    *,
    terms: CharterTerms,
    weather_factor: float = 1.0,
    rate_override: Quantity | None = None,
) -> Quantity:
    """Days alongside, from the port's handling rate.

    Refuses to guess. If ``handling_rate_mtpd`` is unknown and no declared
    assumption is supplied via ``rate_override``, the caller gets a
    MissingDatumError rather than a plausible berth date — an invented handling
    rate produces an invented laycan, which is the kind of error a chartering
    manager spots immediately.

    ``rate_override`` exists so the assumption registry can supply a *declared,
    badged* figure. Its SIMULATED provenance propagates into the result, so the
    memo shows that the berth date rests on an assumption.
    """
    rate = rate_override if rate_override is not None else port.q("handling_rate_mtpd", "t/day")
    days = intake_t.value / rate.value
    if terms.laytime_terms is LaytimeTerms.SHINC:
        note = "SHINC: all days count"
    else:
        # SHEX stretches the calendar: the cargo still takes the same working
        # days, but Sundays and holidays are excepted, so elapsed time is longer.
        days *= 7.0 / 6.0
        note = f"{terms.laytime_terms.value}: excepted days extend elapsed time"
    days *= weather_factor
    return Quantity(
        days,
        "day",
        Provenance.derived(
            f"intake / handling_rate; {note}"
            + (f"; weather_factor={weather_factor}" if weather_factor != 1.0 else ""),
            intake_t.prov,
            rate.prov,
        ),
        f"{port.port_id}.port_days",
    )


def build_legs(
    vessel: VesselClass,
    intake_t: Quantity,
    load_port: Port,
    discharge_port: Port,
    *,
    terms: CharterTerms,
    distance_nm: Quantity | None = None,
    ballast_nm: Quantity | None = None,
    laden_speed_kn: float | None = None,
    waiting_days: float = 0.0,
) -> VoyageLegs:
    dist = distance_nm or route_distance_nm(load_port, discharge_port)
    speed = laden_speed_kn or vessel.speed_laden_kn

    laden = Quantity(
        dist.value / (speed * 24.0),
        "day",
        Provenance.derived(f"distance / (speed {speed:.1f} kn x 24)", dist.prov),
        "sea_days_laden",
    )
    if ballast_nm is not None:
        bal_days = ballast_nm.value / (vessel.speed_ballast_kn * 24.0)
        bal_prov = Provenance.derived("ballast_distance / (ballast_speed x 24)", ballast_nm.prov)
    else:
        # No ballast leg costed: a voyage charter prices the owner's positioning
        # into the freight rate, so the charterer does not pay it separately.
        bal_days, bal_prov = 0.0, Provenance.derived("ballast leg borne by owner in voyage charter")
    ballast = Quantity(bal_days, "day", bal_prov, "sea_days_ballast")

    return VoyageLegs(
        sea_days_laden=laden,
        sea_days_ballast=ballast,
        port_days_load=port_days_from_rate(intake_t, load_port, terms=terms),
        port_days_discharge=port_days_from_rate(intake_t, discharge_port, terms=terms),
        waiting_days=Quantity(
            waiting_days,
            "day",
            Provenance.derived("congestion/waiting estimate"),
            "waiting_days",
        ),
    )


# ---------------------------------------------------------------------------
# laytime, demurrage, despatch
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class LaytimeResult:
    allowed_days: Quantity
    used_days: Quantity
    demurrage_usd: Quantity
    despatch_usd: Quantity

    @property
    def net_usd(self) -> Quantity:
        """Positive is a cost to the charterer; negative is money back."""
        return (self.demurrage_usd - self.despatch_usd).relabel("laytime_net")


def laytime_outcome(
    intake_t: Quantity,
    allowed_rate_mtpd: float,
    used_days: Quantity,
    terms: CharterTerms,
) -> LaytimeResult:
    """Demurrage or despatch, on the agreed laytime.

    Two conventions encoded, both configurable because both are negotiated:

    Once on demurrage, always on demurrage. After laytime expires, excepted
    periods stop being excepted — Sundays, holidays and weather all run. This is
    standard in dry bulk and it means overruns cost more than a naive pro-rata
    calculation suggests.

    Despatch is *not* universally half demurrage. Nil despatch is common in coal
    COAs. ``DespatchBasis`` carries the choice; the default of half demurrage is
    the frequent case, not the only one.
    """
    allowed = (
        Quantity(
            terms.laytime_hours_total / 24.0,
            "day",
            Provenance.observed(Source(name="charterparty laytime clause")),
            "laytime_allowed",
        )
        if terms.laytime_hours_total is not None
        else Quantity(
            intake_t.value / allowed_rate_mtpd,
            "day",
            Provenance.derived(
                f"laytime = intake / agreed_rate({allowed_rate_mtpd:,.0f} t/day)",
                intake_t.prov,
            ),
            "laytime_allowed",
        )
    )

    over = used_days.value - allowed.value

    if over > 0:
        dem = Quantity(
            over * terms.demurrage_usd_per_day,
            "USD",
            Provenance.derived(
                f"demurrage = ({over:.2f} d over) x {terms.demurrage_usd_per_day:,.0f} USD/day"
                + ("; once on demurrage always on demurrage" if terms.once_on_demurrage else ""),
                used_days.prov,
                allowed.prov,
            ),
            "demurrage",
        )
        des = Quantity(0.0, "USD", Provenance.derived("no despatch: laytime exceeded"), "despatch")
    else:
        saved = -over
        if terms.despatch_basis is DespatchBasis.WORKING_TIME_SAVED:
            # Only days the port would have worked earn despatch, so a
            # six-day working week pays on roughly six-sevenths of elapsed saving.
            saved *= 6.0 / 7.0
        rate = terms.despatch_rate()
        des = Quantity(
            saved * rate,
            "USD",
            Provenance.derived(
                f"despatch = {saved:.2f} d saved x {rate:,.0f} USD/day "
                f"(basis: {terms.despatch_basis.value})",
                used_days.prov,
                allowed.prov,
            ),
            "despatch",
        )
        dem = Quantity(0.0, "USD", Provenance.derived("laytime not exceeded"), "demurrage")

    return LaytimeResult(allowed_days=allowed, used_days=used_days, demurrage_usd=dem, despatch_usd=des)


# ---------------------------------------------------------------------------
# the full voyage
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class VoyageResult:
    """Everything a decision needs about one voyage on one vessel class."""

    vessel: VesselClass
    load_port: Port
    discharge_port: Port
    intake_t: Quantity
    legs: VoyageLegs

    freight_rate_usd_per_t: Quantity
    gross_freight_usd: Quantity
    commission_usd: Quantity
    net_revenue_usd: Quantity
    bunker_cost_usd: Quantity
    port_cost_usd: Quantity
    voyage_cost_usd: Quantity
    tce_usd_per_day: Quantity
    delivered_cost_usd_per_t: Quantity
    laytime: LaytimeResult | None = None

    def summary(self) -> str:
        return (
            f"{self.vessel.name}  {self.load_port.name} -> {self.discharge_port.name}\n"
            f"  intake           {self.intake_t.fmt(0)}\n"
            f"  freight          {self.freight_rate_usd_per_t.badged(2)}\n"
            f"  total days       {self.legs.total_days.fmt(1)}\n"
            f"  bunkers          {self.bunker_cost_usd.fmt(0)}\n"
            f"  port costs       {self.port_cost_usd.fmt(0)}\n"
            f"  commission       {self.commission_usd.fmt(0)}\n"
            f"  owner TCE        {self.tce_usd_per_day.badged(0)}\n"
            f"  DELIVERED COST   {self.delivered_cost_usd_per_t.badged(2)}"
        )


def compute_voyage(
    vessel: VesselClass,
    intake_t: Quantity,
    load_port: Port,
    discharge_port: Port,
    freight_rate_usd_per_t: Quantity,
    *,
    terms: CharterTerms,
    bunkers: BunkerPrices,
    legs: VoyageLegs | None = None,
    port_costs_usd: float = 0.0,
    laden_speed_kn: float | None = None,
    waiting_days: float = 0.0,
    agreed_laytime_rate_mtpd: float | None = None,
) -> VoyageResult:
    """Delivered cost per tonne for the charterer, and TCE for the owner."""
    legs = legs or build_legs(
        vessel,
        intake_t,
        load_port,
        discharge_port,
        terms=terms,
        laden_speed_kn=laden_speed_kn,
        waiting_days=waiting_days,
    )

    speed = laden_speed_kn or vessel.speed_laden_kn
    sea_mtpd = consumption_at_speed(vessel.consumption_laden_mtpd, vessel.speed_laden_kn, speed)
    sea_fuel = sea_mtpd * legs.sea_days.value
    port_fuel = vessel.consumption_port_mtpd * (legs.port_days.value + legs.waiting_days.value)

    bunker_cost = Quantity(
        (sea_fuel + port_fuel) * bunkers.vlsfo_usd_per_mt,
        "USD",
        Provenance.derived(
            f"bunkers: sea {sea_mtpd:.1f} mt/day (cube law at {speed:.1f} kn) x sea days "
            f"+ port {vessel.consumption_port_mtpd:.1f} mt/day x port days, "
            f"at {bunkers.vlsfo_usd_per_mt:,.0f} USD/mt VLSFO",
            legs.sea_days.prov,
            legs.port_days.prov,
        ),
        "bunker_cost",
    )

    port_cost = Quantity(
        port_costs_usd,
        "USD",
        Provenance.derived("port disbursements (agency, pilotage, towage, dues)")
        if port_costs_usd
        else Provenance.derived("port disbursements not supplied; treated as zero"),
        "port_cost",
    )

    gross = (freight_rate_usd_per_t * intake_t).relabel("gross_freight")
    c_rate = terms.commission_total()
    commission = Quantity(
        gross.value * c_rate,
        "USD",
        Provenance.derived(
            f"commission = gross_freight x (addr {terms.address_commission:.4f} "
            f"+ brok {terms.brokerage_commission:.4f})",
            gross.prov,
        ),
        "commission",
    )
    net_revenue = Quantity(
        gross.value * (1.0 - c_rate),
        "USD",
        Provenance.derived("net_revenue = gross_freight x (1 - c_addr - c_brok)", gross.prov),
        "net_revenue",
    )

    laytime: LaytimeResult | None = None
    demurrage_net = 0.0
    if agreed_laytime_rate_mtpd is not None:
        laytime = laytime_outcome(
            intake_t,
            agreed_laytime_rate_mtpd,
            legs.port_days,
            terms,
        )
        demurrage_net = laytime.net_usd.value

    voyage_cost = Quantity(
        bunker_cost.value + port_cost.value,
        "USD",
        Provenance.derived("voyage_cost = bunkers + port disbursements", bunker_cost.prov, port_cost.prov),
        "voyage_cost",
    )

    days = legs.total_days
    tce = Quantity(
        (net_revenue.value - voyage_cost.value) / days.value if days.value > 0 else 0.0,
        "USD/day",
        Provenance.derived(
            "TCE = (net_revenue - voyage_cost) / total_days",
            net_revenue.prov,
            voyage_cost.prov,
            days.prov,
        ),
        "tce",
    )

    # The charterer's delivered cost: freight actually paid plus demurrage less
    # despatch, per tonne. Commission is inside the freight the charterer pays,
    # so it is not added again here.
    delivered = Quantity(
        (gross.value + demurrage_net) / intake_t.value,
        "USD/t",
        Provenance.derived(
            "delivered = (gross_freight + demurrage - despatch) / intake",
            gross.prov,
            intake_t.prov,
        ),
        "delivered_cost",
    )

    return VoyageResult(
        vessel=vessel,
        load_port=load_port,
        discharge_port=discharge_port,
        intake_t=intake_t,
        legs=legs,
        freight_rate_usd_per_t=freight_rate_usd_per_t,
        gross_freight_usd=gross,
        commission_usd=commission,
        net_revenue_usd=net_revenue,
        bunker_cost_usd=bunker_cost,
        port_cost_usd=port_cost,
        voyage_cost_usd=voyage_cost,
        tce_usd_per_day=tce,
        delivered_cost_usd_per_t=delivered,
        laytime=laytime,
    )
