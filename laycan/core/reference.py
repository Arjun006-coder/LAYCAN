"""Typed loaders for the reference data, with unknowns kept as unknown.

Three CSVs describe the physical world: ports, vessel classes, cargo types.
Every numeric cell arrives as either a real figure with a citation, or the
literal string ``unknown``. This module keeps that distinction alive all the way
into the solvers.

The rule that matters: a loader never substitutes a plausible default for a
missing figure. If ``handling_rate_mtpd`` is unknown for Paradip, the laytime
calculation raises and the memo says the data is missing. A silent default of
"25,000 tonnes a day, that's about right" is how a tool produces a confident
wrong berth date, and one of those is enough to lose a customer.

Two domain subtleties are encoded here rather than left to the caller:

Visakhapatnam is two ports wearing one name. The Outer Harbour takes about
18.1 m and Capesize vessels; the Inner Harbour takes about 14.5 m and caps near
260 m LOA. They are separate rows (``INVTZ-OH``, ``INVTZ-IH``) and any code that
collapses them to "Vizag" is wrong half the time.

Paradip is not one draft either. Coal berths run near 16.0 m while thermal coal
and inner berths are shallower, so ``max_draft_m`` on the port row is the coal
berth figure and the notes carry the rest.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Iterator, Mapping

from .provenance import (
    Provenance,
    ProvenanceError,
    Quantity,
    Source,
    Status,
    is_unknown,
)

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "reference"


class MissingDatumError(ProvenanceError):
    """A required physical figure is unknown, so the computation must stop."""


def _f(raw: Any) -> float | None:
    """Parse a float, mapping every unknown token to None. Never guesses."""
    if is_unknown(raw):
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    txt = str(raw).strip().replace(",", "")
    if txt.lower() == "dynamic":
        # Hay Point's draft is tidal and genuinely has no single value. Treating
        # 'dynamic' as unknown is correct: it forces the caller to supply a
        # tidal window rather than pretend a constant exists.
        return None
    try:
        return float(txt)
    except ValueError:
        return None


def _i(raw: Any) -> int | None:
    v = _f(raw)
    return int(v) if v is not None else None


def _s(raw: Any) -> str:
    return "" if raw is None else str(raw).strip()


def _bool(raw: Any) -> bool | None:
    txt = _s(raw).lower()
    if txt in {"yes", "true", "y", "1"}:
        return True
    if txt in {"no", "false", "n", "0"}:
        return False
    return None


def _parse_date(raw: Any) -> date | None:
    txt = _s(raw)
    if not txt or is_unknown(txt):
        return None
    try:
        return date.fromisoformat(txt[:10])
    except ValueError:
        return None


@dataclass(frozen=True, slots=True)
class Port:
    """A discharge or load point, with its physical limits."""

    port_id: str
    unlocode: str
    name: str
    country: str
    lat: float | None
    lon: float | None
    port_type: str                    # discharge | load | anchorage
    max_draft_m: float | None
    max_loa_m: float | None
    max_beam_m: float | None
    max_dwt: float | None
    dry_bulk_berths: int | None
    handling_rate_mtpd: float | None
    gear_required: bool | None
    tidal_window_hrs: float | None
    lightering_available: bool
    water_density: float | None
    load_line_zone: str
    notes: str
    source: Source
    confidence: str

    # ---- provenance ---------------------------------------------------

    def prov(self, field_name: str) -> Provenance:
        """Port physical limits are observed facts or they are nothing.

        Deliberately never SIMULATED: a modelled port draft has no business
        inside a feasibility check, and ``require_defensible`` downstream relies
        on that guarantee.
        """
        return Provenance.observed(self.source, confidence=self.confidence, note=field_name)

    def q(self, field_name: str, unit: str) -> Quantity:
        """A required figure as a Quantity, or a hard failure naming the gap."""
        val = getattr(self, field_name)
        if val is None:
            raise MissingDatumError(
                f"{self.name} ({self.port_id}): {field_name} is unknown. "
                f"Verify from a primary source and record the URL — see docs/VERIFY-FIRST.md. "
                f"LAYCAN will not substitute an estimate."
            )
        return Quantity(float(val), unit, self.prov(field_name), f"{self.name}.{field_name}")

    def has(self, field_name: str) -> bool:
        return getattr(self, field_name) is not None

    # ---- domain -------------------------------------------------------

    @property
    def is_tidal(self) -> bool:
        return bool(self.tidal_window_hrs)

    @property
    def is_brackish(self) -> bool:
        """Brackish water sinks a ship deeper, so FWA/DWA correction is mandatory.

        Haldia sits up the Hooghly at roughly 1010 kg/m3. Ignore that and your
        arrival draft is optimistic by a margin that grounds ships.
        """
        return self.water_density is not None and self.water_density < 1024.0

    def __str__(self) -> str:
        return f"{self.name} [{self.port_id}]"


@dataclass(frozen=True, slots=True)
class VesselClass:
    """A size band, not a specific ship. Specific ships come from AIS/fixtures."""

    class_id: str
    name: str
    dwt_min: float
    dwt_max: float
    dwt_typical: float
    loa_m: float
    beam_m: float
    summer_draft_m: float
    tpc: float | None
    grain_capacity_m3: float | None
    holds: int | None
    geared: bool | None
    speed_ballast_kn: float
    speed_laden_kn: float
    consumption_ballast_mtpd: float
    consumption_laden_mtpd: float
    consumption_port_mtpd: float
    constants_mt: float
    source_ref: str
    confidence: str

    @property
    def source(self) -> Source:
        return Source(
            name=self.source_ref,
            licence="unknown",
            note="vessel class band; verify against EU MRV/THETIS observed data",
        )

    def prov(self, field_name: str) -> Provenance:
        return Provenance.observed(self.source, confidence=self.confidence, note=field_name)

    def q(self, field_name: str, unit: str) -> Quantity:
        val = getattr(self, field_name)
        if val is None:
            raise MissingDatumError(
                f"{self.name} ({self.class_id}): {field_name} is unknown. "
                f"EU MRV/THETIS carries observed values for ~13,000 real ships — "
                f"use those rather than a cube-law guess."
            )
        return Quantity(float(val), unit, self.prov(field_name), f"{self.class_id}.{field_name}")

    def estimated_tpc(self) -> Quantity:
        """Tonnes per centimetre immersion, estimated when not tabulated.

        TPC = A_wp * rho / 100 with the waterplane area approximated as
        LOA * beam * Cwp. A block-ish bulk carrier runs Cwp around 0.85-0.90;
        0.87 is used here. This is an *estimate* and is badged SIMULATED, which
        means the intake calculation that consumes it inherits that badge and the
        memo shows it. Replace with the ship's real hydrostatic table the moment
        a specific vessel is nominated — every ship carries one.
        """
        if self.tpc is not None:
            return self.q("tpc", "t/cm")
        cwp = 0.87
        rho = 1.025
        tpc = self.loa_m * self.beam_m * cwp * rho / 100.0
        return Quantity(
            tpc,
            "t/cm",
            Provenance.simulated(
                f"TPC ~= LOA*beam*Cwp*rho/100 with Cwp={cwp}, rho={rho} t/m3",
                note="waterplane approximation; supersede with vessel hydrostatics",
            ),
            f"{self.class_id}.tpc_estimated",
        )

    def __str__(self) -> str:
        return f"{self.name} [{self.class_id}]"


@dataclass(frozen=True, slots=True)
class CargoType:
    """What we are shipping, and whether the hold fills up before the deadweight."""

    cargo_id: str
    name: str
    sf_min: float
    sf_max: float
    sf_typical: float
    weight_or_volume_limited: str
    imsbc_group: str
    hazards: str
    notes: str
    source_ref: str
    confidence: str

    @property
    def source(self) -> Source:
        return Source(name=self.source_ref, note="IMSBC stowage factor band")

    def prov(self, field_name: str = "stowage_factor") -> Provenance:
        return Provenance.observed(self.source, confidence=self.confidence, note=field_name)

    def sf(self, *, conservative: bool = True) -> Quantity:
        """Stowage factor in m3 per tonne.

        Conservative means the *high* end of the band, because a bulkier cargo
        fills the hold sooner and reduces the intake. For a feasibility promise
        you want the answer that cannot embarrass you.
        """
        v = self.sf_max if conservative else self.sf_typical
        which = "sf_max (conservative)" if conservative else "sf_typical"
        return Quantity(v, "m3/t", self.prov(which), f"{self.cargo_id}.{which}")

    @property
    def liquefaction_risk(self) -> bool:
        return "liquefaction" in self.hazards.lower()

    def __str__(self) -> str:
        return f"{self.name} [{self.cargo_id}]"


# ---------------------------------------------------------------------------
# loading
# ---------------------------------------------------------------------------

def _rows(path: Path) -> Iterator[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            if row and any((v or "").strip() for v in row.values()):
                yield row


def load_ports(path: Path | None = None) -> dict[str, Port]:
    p = path or DATA_DIR / "ports.csv"
    out: dict[str, Port] = {}
    for r in _rows(p):
        pid = _s(r.get("port_id"))
        if not pid:
            continue
        out[pid] = Port(
            port_id=pid,
            unlocode=_s(r.get("unlocode")),
            name=_s(r.get("name")),
            country=_s(r.get("country")),
            lat=_f(r.get("lat")),
            lon=_f(r.get("lon")),
            port_type=_s(r.get("port_type")) or "discharge",
            max_draft_m=_f(r.get("max_draft_m")),
            max_loa_m=_f(r.get("max_loa_m")),
            max_beam_m=_f(r.get("max_beam_m")),
            max_dwt=_f(r.get("max_dwt")),
            dry_bulk_berths=_i(r.get("dry_bulk_berths")),
            handling_rate_mtpd=_f(r.get("handling_rate_mtpd")),
            gear_required=_bool(r.get("gear_required")),
            tidal_window_hrs=_f(r.get("tidal_window_hrs")),
            lightering_available=bool(_bool(r.get("lightering_available"))),
            water_density=_f(r.get("water_density")),
            load_line_zone=_s(r.get("load_line_zone")),
            notes=_s(r.get("notes")),
            source=Source(
                name=_s(r.get("source_ref")) or "unknown",
                url=(_s(r.get("source_ref")) if _s(r.get("source_ref")).startswith("http") else None),
                licence="public web, verify terms",
                retrieved_at=_parse_date(r.get("retrieved_at")),
            ),
            confidence=_s(r.get("confidence")) or "unknown",
        )
    if not out:
        raise MissingDatumError(f"no ports loaded from {p}")
    return out


def load_vessel_classes(path: Path | None = None) -> dict[str, VesselClass]:
    p = path or DATA_DIR / "vessel_classes.csv"
    out: dict[str, VesselClass] = {}
    for r in _rows(p):
        cid = _s(r.get("class_id"))
        if not cid:
            continue
        out[cid] = VesselClass(
            class_id=cid,
            name=_s(r.get("name")),
            dwt_min=_f(r.get("dwt_min")) or 0.0,
            dwt_max=_f(r.get("dwt_max")) or 0.0,
            dwt_typical=_f(r.get("dwt_typical")) or 0.0,
            loa_m=_f(r.get("loa_m")) or 0.0,
            beam_m=_f(r.get("beam_m")) or 0.0,
            summer_draft_m=_f(r.get("summer_draft_m")) or 0.0,
            tpc=_f(r.get("tpc")),
            grain_capacity_m3=_f(r.get("grain_capacity_m3")),
            holds=_i(r.get("holds")),
            geared=_bool(r.get("geared")),
            speed_ballast_kn=_f(r.get("speed_ballast_kn")) or 0.0,
            speed_laden_kn=_f(r.get("speed_laden_kn")) or 0.0,
            consumption_ballast_mtpd=_f(r.get("consumption_ballast_mtpd")) or 0.0,
            consumption_laden_mtpd=_f(r.get("consumption_laden_mtpd")) or 0.0,
            consumption_port_mtpd=_f(r.get("consumption_port_mtpd")) or 0.0,
            constants_mt=_f(r.get("constants_mt")) or 0.0,
            source_ref=_s(r.get("source_ref")) or "unknown",
            confidence=_s(r.get("confidence")) or "unknown",
        )
    if not out:
        raise MissingDatumError(f"no vessel classes loaded from {p}")
    return out


def load_cargo_types(path: Path | None = None) -> dict[str, CargoType]:
    p = path or DATA_DIR / "cargo_types.csv"
    out: dict[str, CargoType] = {}
    for r in _rows(p):
        cid = _s(r.get("cargo_id"))
        if not cid:
            continue
        out[cid] = CargoType(
            cargo_id=cid,
            name=_s(r.get("name")),
            sf_min=_f(r.get("stowage_factor_m3_mt_min")) or 0.0,
            sf_max=_f(r.get("stowage_factor_m3_mt_max")) or 0.0,
            sf_typical=_f(r.get("stowage_factor_typical")) or 0.0,
            weight_or_volume_limited=_s(r.get("weight_or_volume_limited")),
            imsbc_group=_s(r.get("imsbc_group")),
            hazards=_s(r.get("hazards")),
            notes=_s(r.get("notes")),
            source_ref=_s(r.get("source_ref")) or "unknown",
            confidence=_s(r.get("confidence")) or "unknown",
        )
    if not out:
        raise MissingDatumError(f"no cargo types loaded from {p}")
    return out


@dataclass(frozen=True, slots=True)
class ReferenceData:
    """Everything physical, loaded once, immutable thereafter."""

    ports: Mapping[str, Port]
    vessels: Mapping[str, VesselClass]
    cargoes: Mapping[str, CargoType]

    @classmethod
    def load(cls, data_dir: Path | None = None) -> "ReferenceData":
        d = data_dir or DATA_DIR
        return cls(
            ports=load_ports(d / "ports.csv"),
            vessels=load_vessel_classes(d / "vessel_classes.csv"),
            cargoes=load_cargo_types(d / "cargo_types.csv"),
        )

    def port(self, pid: str) -> Port:
        try:
            return self.ports[pid]
        except KeyError:
            raise MissingDatumError(
                f"unknown port {pid!r}; known: {', '.join(sorted(self.ports))}"
            ) from None

    def vessel(self, cid: str) -> VesselClass:
        try:
            return self.vessels[cid]
        except KeyError:
            raise MissingDatumError(
                f"unknown vessel class {cid!r}; known: {', '.join(sorted(self.vessels))}"
            ) from None

    def cargo(self, cid: str) -> CargoType:
        try:
            return self.cargoes[cid]
        except KeyError:
            raise MissingDatumError(
                f"unknown cargo {cid!r}; known: {', '.join(sorted(self.cargoes))}"
            ) from None

    def discharge_ports(self) -> list[Port]:
        return [p for p in self.ports.values() if p.port_type == "discharge"]

    def load_ports(self) -> list[Port]:
        return [p for p in self.ports.values() if p.port_type == "load"]

    def anchorages(self) -> list[Port]:
        return [p for p in self.ports.values() if p.port_type == "anchorage"]

    def data_gaps(self) -> list[str]:
        """Every unknown that will stop a calculation. Shown in the memo footer.

        Being able to print this list is a feature: it is the honest answer to
        "what don't you know", and it is what a procurement reviewer checks.
        """
        gaps: list[str] = []
        for p in self.ports.values():
            for f in ("max_draft_m", "handling_rate_mtpd", "max_loa_m", "max_dwt"):
                if not p.has(f) and p.port_type != "anchorage":
                    gaps.append(f"port {p.port_id} ({p.name}): {f}")
        for v in self.vessels.values():
            if v.tpc is None:
                gaps.append(f"vessel {v.class_id}: tpc (estimated from waterplane)")
            if v.grain_capacity_m3 is None:
                gaps.append(f"vessel {v.class_id}: grain_capacity_m3 (volume limit unavailable)")
        return gaps
