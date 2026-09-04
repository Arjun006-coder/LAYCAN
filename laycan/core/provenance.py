"""Provenance — the reason a SAIL auditor can accept a LAYCAN recommendation.

Every number that reaches a human carries a Provenance record saying where it
came from, under what licence, when it was retrieved, and — critically —
whether it was *observed* in the world, *derived* by our own tested code, or
*simulated* by a model.

The three statuses are not decoration. They drive the badge in the UI and they
drive what we are allowed to say on stage:

    observed   a primary source said this. Cite the URL.
    derived    our code computed it from observed inputs. Cite the formula.
    simulated  a model produced it. Never present as observed. Ever.

Design note: this module deliberately depends on nothing outside the standard
library. Provenance has to work in the deterministic core, in the API layer and
in the offline demo snapshot, so it cannot import anything that might be absent
at 9am on stage.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict, replace
from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Iterable, Sequence


class Status(str, Enum):
    """How much weight a number can bear."""

    OBSERVED = "observed"
    DERIVED = "derived"
    SIMULATED = "simulated"

    @property
    def badge(self) -> str:
        """Short label for the interface. Design owns the visual; this is the text."""
        return {"observed": "OBSERVED", "derived": "COMPUTED", "simulated": "MODELLED"}[
            self.value
        ]

    @property
    def rank(self) -> int:
        """Lower is stronger. Used to propagate the weakest link through arithmetic."""
        return {"observed": 0, "derived": 1, "simulated": 2}[self.value]


class ProvenanceError(RuntimeError):
    """Raised when a computation is asked to proceed on a value it cannot defend."""


UNKNOWN_TOKENS = frozenset({"unknown", "", "na", "n/a", "none", "null", "tbd", "?"})


def is_unknown(raw: Any) -> bool:
    """True when a reference-data cell is explicitly not known.

    The project rule is that ``unknown`` is an acceptable answer and a guess is
    not. Reference CSVs carry the literal string ``unknown`` in cells nobody has
    verified yet, and loaders must refuse to coerce those to a number.
    """
    if raw is None:
        return True
    if isinstance(raw, str):
        return raw.strip().lower() in UNKNOWN_TOKENS
    return False


@dataclass(frozen=True, slots=True)
class Source:
    """A citable origin for a value."""

    name: str
    url: str | None = None
    licence: str = "unknown"
    retrieved_at: date | None = None
    note: str = ""

    def cite(self) -> str:
        bits = [self.name]
        if self.url:
            bits.append(self.url)
        if self.retrieved_at:
            bits.append(f"retrieved {self.retrieved_at.isoformat()}")
        if self.licence and self.licence != "unknown":
            bits.append(f"licence: {self.licence}")
        return " — ".join(bits)


@dataclass(frozen=True, slots=True)
class Provenance:
    """Where a number came from and how far you can trust it."""

    status: Status
    sources: tuple[Source, ...] = ()
    formula: str = ""
    code_ref: str = ""
    confidence: str = "unknown"
    computed_at: datetime | None = None
    inputs: tuple[str, ...] = ()

    # ---- constructors -------------------------------------------------

    @classmethod
    def observed(
        cls,
        source: Source | str,
        *,
        confidence: str = "high",
        note: str = "",
    ) -> "Provenance":
        src = Source(name=source, note=note) if isinstance(source, str) else source
        return cls(status=Status.OBSERVED, sources=(src,), confidence=confidence)

    @classmethod
    def derived(
        cls,
        formula: str,
        *parents: "Provenance",
        code_ref: str = "",
        inputs: Sequence[str] = (),
    ) -> "Provenance":
        """A number our own code computed.

        The status is the *weakest* of the parents: derive from a simulated
        input and the result is simulated, no matter how solid the arithmetic.
        That propagation rule is what stops a modelled freight rate from
        laundering itself into an 'observed' delivered cost.
        """
        status = Status.DERIVED
        for p in parents:
            if p.status.rank > status.rank:
                status = p.status
        merged: list[Source] = []
        for p in parents:
            for s in p.sources:
                if s not in merged:
                    merged.append(s)
        conf = _weakest_confidence([p.confidence for p in parents]) if parents else "unknown"
        return cls(
            status=status,
            sources=tuple(merged),
            formula=formula,
            code_ref=code_ref,
            confidence=conf,
            computed_at=datetime.now(timezone.utc),
            inputs=tuple(inputs),
        )

    @classmethod
    def simulated(
        cls,
        model: str,
        *,
        calibrated_against: Iterable[Source] = (),
        note: str = "",
    ) -> "Provenance":
        return cls(
            status=Status.SIMULATED,
            sources=tuple(calibrated_against),
            formula=model,
            confidence="modelled",
            computed_at=datetime.now(timezone.utc),
            inputs=(note,) if note else (),
        )

    # ---- guards -------------------------------------------------------

    def require_defensible(self, what: str) -> None:
        """Refuse to let a simulated number masquerade as fact in a hard constraint.

        Physical feasibility — can this ship berth — must never rest on a
        modelled input. If a port draft is simulated, the honest answer is that
        we do not know, not a confident yes.
        """
        if self.status is Status.SIMULATED:
            raise ProvenanceError(
                f"{what} rests on a simulated value; physical feasibility "
                f"requires observed data. Model: {self.formula!r}"
            )

    def cite(self) -> str:
        if self.sources:
            return "; ".join(s.cite() for s in self.sources)
        if self.formula:
            return f"computed: {self.formula}"
        return "uncited"

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        d["badge"] = self.status.badge
        d["computed_at"] = self.computed_at.isoformat() if self.computed_at else None
        d["sources"] = [
            {
                **{k: v for k, v in asdict(s).items() if k != "retrieved_at"},
                "retrieved_at": s.retrieved_at.isoformat() if s.retrieved_at else None,
            }
            for s in self.sources
        ]
        return d


def _weakest_confidence(levels: Sequence[str]) -> str:
    order = ["high", "medium-high", "medium", "low", "modelled", "unknown"]
    worst = "high"
    for lv in levels:
        lv = (lv or "unknown").strip().lower()
        if lv not in order:
            lv = "unknown"
        if order.index(lv) > order.index(worst):
            worst = lv
    return worst


@dataclass(frozen=True, slots=True)
class Quantity:
    """A number that cannot be separated from its unit or its provenance.

    Arithmetic propagates provenance automatically, so a delivered cost per
    tonne built from a modelled freight rate is still flagged modelled when it
    reaches the memo. That is the whole point: you cannot lose the asterisk by
    doing sums.
    """

    value: float
    unit: str
    prov: Provenance
    label: str = ""

    def __post_init__(self) -> None:
        if isinstance(self.value, bool) or not isinstance(self.value, (int, float)):
            raise TypeError(f"Quantity value must be numeric, got {type(self.value)!r}")

    # ---- arithmetic ---------------------------------------------------

    def _combine(self, other: "Quantity", op: str, unit: str, value: float) -> "Quantity":
        return Quantity(
            value=value,
            unit=unit,
            prov=Provenance.derived(
                f"({self.label or self.unit}) {op} ({other.label or other.unit})",
                self.prov,
                other.prov,
            ),
        )

    def __add__(self, other: "Quantity") -> "Quantity":
        self._assert_same_unit(other, "+")
        return self._combine(other, "+", self.unit, self.value + other.value)

    def __sub__(self, other: "Quantity") -> "Quantity":
        self._assert_same_unit(other, "-")
        return self._combine(other, "-", self.unit, self.value - other.value)

    def __mul__(self, other: "Quantity | float | int") -> "Quantity":
        if isinstance(other, (int, float)):
            return Quantity(self.value * other, self.unit, self.prov, self.label)
        return self._combine(other, "*", f"{self.unit}*{other.unit}", self.value * other.value)

    __rmul__ = __mul__

    def __truediv__(self, other: "Quantity | float | int") -> "Quantity":
        if isinstance(other, (int, float)):
            if other == 0:
                raise ZeroDivisionError("Quantity divided by zero")
            return Quantity(self.value / other, self.unit, self.prov, self.label)
        if other.value == 0:
            raise ZeroDivisionError(f"Quantity {self.label!r} divided by zero {other.label!r}")
        return self._combine(other, "/", f"{self.unit}/{other.unit}", self.value / other.value)

    def _assert_same_unit(self, other: "Quantity", op: str) -> None:
        if self.unit != other.unit:
            raise ValueError(
                f"unit mismatch: cannot {op} {self.unit!r} and {other.unit!r} "
                f"({self.label!r}, {other.label!r})"
            )

    # ---- presentation -------------------------------------------------

    @property
    def status(self) -> Status:
        return self.prov.status

    def fmt(self, dp: int = 2) -> str:
        return f"{self.value:,.{dp}f} {self.unit}"

    def badged(self, dp: int = 2) -> str:
        return f"{self.fmt(dp)} [{self.prov.status.badge}]"

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "value": self.value,
            "unit": self.unit,
            "status": self.prov.status.value,
            "badge": self.prov.status.badge,
            "provenance": self.prov.to_dict(),
        }

    def relabel(self, label: str) -> "Quantity":
        return replace(self, label=label)


def observed_q(value: float, unit: str, source: Source | str, *, label: str = "", confidence: str = "high") -> Quantity:
    return Quantity(value, unit, Provenance.observed(source, confidence=confidence), label)


def derived_q(value: float, unit: str, formula: str, *parents: Provenance, label: str = "") -> Quantity:
    return Quantity(value, unit, Provenance.derived(formula, *parents), label)


def simulated_q(value: float, unit: str, model: str, *, label: str = "") -> Quantity:
    return Quantity(value, unit, Provenance.simulated(model), label)


def worst_status(quantities: Iterable[Quantity]) -> Status:
    """The weakest link in a set of numbers — what the memo header must display."""
    worst = Status.OBSERVED
    for q in quantities:
        if q.status.rank > worst.rank:
            worst = q.status
    return worst


def dumps(obj: Any) -> str:
    """JSON for the audit trail, with Quantity and Provenance made serialisable."""

    def default(o: Any) -> Any:
        if isinstance(o, (Quantity, Provenance)):
            return o.to_dict()
        if isinstance(o, Status):
            return o.value
        if isinstance(o, (date, datetime)):
            return o.isoformat()
        if isinstance(o, Source):
            return o.cite()
        raise TypeError(f"not serialisable: {type(o)!r}")

    return json.dumps(obj, default=default, indent=2, sort_keys=False)
