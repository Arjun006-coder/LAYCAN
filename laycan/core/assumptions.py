"""Assumptions — declared, cited, badged, and never mistaken for facts.

Some numbers the engine needs are not in any free primary source we have yet:
berth handling rates, port disbursement accounts, real sea distances, the
laytime rate a charterparty actually agreed. Without them the engine simply
stops, which is correct behaviour but not a demo.

So assumptions live here, in one file, with three properties that make them
defensible rather than embarrassing:

  * every one carries a written rationale and a named source that would
    supersede it, so "where did this come from" always has an answer
  * every one is badged SIMULATED, which propagates through the arithmetic into
    the memo, so a delivered cost built on an assumed handling rate is visibly
    modelled
  * they are counted and listed in the memo footer, so the reader knows exactly
    how much of the answer rests on assumption

This separation is the whole reason ``reference.py`` is allowed to be strict.
Verified facts and working assumptions live in different files with different
badges, and neither can be mistaken for the other. When the data owner closes a
verification item, the figure moves from this file to the reference CSV and the
badge changes from MODELLED to OBSERVED with no code change.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

from .provenance import Provenance, Quantity, Source, is_unknown

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "reference"


@dataclass(frozen=True, slots=True)
class Assumption:
    """A number we chose, with the reason we chose it and what would replace it."""

    assumption_id: str
    scope: str            # global | port:<id> | route:<load>-<discharge> | class:<id>
    key: str
    value: float
    unit: str
    rationale: str
    supersede_with: str
    owner: str
    status: str

    @property
    def prov(self) -> Provenance:
        return Provenance.simulated(
            f"assumption {self.assumption_id}: {self.rationale}",
            calibrated_against=(
                Source(
                    name=f"supersede with: {self.supersede_with}",
                    licence="pending verification",
                    note=self.rationale,
                ),
            ),
            note=f"owner={self.owner}",
        )

    def q(self, label: str = "") -> Quantity:
        return Quantity(self.value, self.unit, self.prov, label or self.assumption_id)

    def line(self) -> str:
        return (
            f"{self.key} = {self.value:,.4g} {self.unit}  [{self.scope}]\n"
            f"    why:      {self.rationale}\n"
            f"    replace:  {self.supersede_with}"
        )


class AssumptionRegistry:
    """Lookup with a most-specific-wins rule: route beats port beats global."""

    def __init__(self, assumptions: list[Assumption]) -> None:
        self._all = list(assumptions)
        self._by_scope_key: dict[tuple[str, str], Assumption] = {
            (a.scope, a.key): a for a in assumptions
        }

    # ---- construction -------------------------------------------------

    @classmethod
    def load(cls, path: Path | None = None) -> "AssumptionRegistry":
        p = path or DATA_DIR / "assumptions.csv"
        if not p.exists():
            return cls([])
        out: list[Assumption] = []
        with p.open(newline="", encoding="utf-8-sig") as fh:
            for r in csv.DictReader(fh):
                if not r or is_unknown(r.get("assumption_id")):
                    continue
                raw = (r.get("value") or "").strip().replace(",", "")
                try:
                    val = float(raw)
                except ValueError:
                    continue
                out.append(
                    Assumption(
                        assumption_id=(r.get("assumption_id") or "").strip(),
                        scope=(r.get("scope") or "global").strip(),
                        key=(r.get("key") or "").strip(),
                        value=val,
                        unit=(r.get("unit") or "").strip(),
                        rationale=(r.get("rationale") or "").strip(),
                        supersede_with=(r.get("supersede_with") or "").strip(),
                        owner=(r.get("owner") or "").strip(),
                        status=(r.get("status") or "assumed").strip(),
                    )
                )
        return cls(out)

    # ---- lookup -------------------------------------------------------

    def get(
        self,
        key: str,
        *,
        port_id: str | None = None,
        route: tuple[str, str] | None = None,
        class_id: str | None = None,
    ) -> Assumption | None:
        """Most specific scope wins, so a route override beats a global default."""
        candidates: list[str] = []
        if route:
            candidates.append(f"route:{route[0]}-{route[1]}")
        if port_id:
            candidates.append(f"port:{port_id}")
        if class_id:
            candidates.append(f"class:{class_id}")
        candidates.append("global")
        for scope in candidates:
            hit = self._by_scope_key.get((scope, key))
            if hit is not None:
                return hit
        return None

    def value(
        self,
        key: str,
        default: float | None = None,
        **scope: Any,
    ) -> float | None:
        a = self.get(key, **scope)
        return a.value if a is not None else default

    def quantity(self, key: str, **scope: Any) -> Quantity | None:
        a = self.get(key, **scope)
        return a.q() if a is not None else None

    def require(self, key: str, **scope: Any) -> Assumption:
        a = self.get(key, **scope)
        if a is None:
            raise KeyError(
                f"no assumption for {key!r} at scope {scope!r}; add a row to "
                f"data/reference/assumptions.csv with a rationale and a supersede_with"
            )
        return a

    # ---- reporting ----------------------------------------------------

    def __iter__(self) -> Iterator[Assumption]:
        return iter(self._all)

    def __len__(self) -> int:
        return len(self._all)

    def used_report(self, used_ids: set[str]) -> str:
        """The memo footer: exactly which assumptions this answer leans on."""
        used = [a for a in self._all if a.assumption_id in used_ids]
        if not used:
            return "No assumptions were used; every figure traces to an observed source."
        lines = [
            f"This recommendation rests on {len(used)} declared assumption(s). "
            f"Each is modelled, not observed, and each has a named source that supersedes it:",
            "",
        ]
        for a in sorted(used, key=lambda x: x.scope):
            lines.append(a.line())
            lines.append("")
        return "\n".join(lines).rstrip()

    def outstanding(self) -> list[Assumption]:
        return [a for a in self._all if a.status.lower() == "assumed"]
