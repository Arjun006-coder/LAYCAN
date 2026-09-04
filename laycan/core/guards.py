"""Guards — the two structural rules that make LAYCAN auditable.

Rule 1: the language model may not emit a numeral.
Rule 2: no feature may be read from the future.

Both are enforced here and both fail loudly. Neither is a lint warning you can
ignore; they raise, CI runs them, and the build goes red. That is deliberate.
A procurement tool that occasionally invents a confident wrong number is worse
than no tool at all, and a backtest that peeks at the future is worse than no
backtest, because it is confidently wrong.

Do not relax these to make a test pass. If a test fails against these guards,
the test is describing a real defect.
"""

from __future__ import annotations

import re
import unicodedata
from datetime import date, datetime
from typing import Any, Iterable


class NumeralLeakError(AssertionError):
    """An LLM produced a digit. The narration is rejected, not sanitised."""


class LookAheadError(AssertionError):
    """A feature was read whose retrieval time is after the decision time."""


# ---------------------------------------------------------------------------
# Rule 1 — the LLM may not emit a numeral
# ---------------------------------------------------------------------------

# Digits in any script (Devanagari, Arabic-Indic, fullwidth) plus Roman
# numerals, spelled-out numbers, and the sneaky ones: superscripts, fractions,
# and circled digits. A model asked not to write "12" will happily write "twelve"
# or "١٢" or "Ⅻ", and each of those is just as dangerous in a freight quote.
_WORD_NUMBERS = (
    r"zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
    r"thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|"
    r"thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|"
    r"million|billion|crore|lakh|dozen|half|quarter|third"
)

_WORD_NUMBER_RE = re.compile(rf"\b({_WORD_NUMBERS})\b", re.IGNORECASE)
_ROMAN_RE = re.compile(r"\b(?=[MDCLXVI]{2,})M*(?:C[MD]|D?C{0,3})(?:X[CL]|L?X{0,3})(?:I[XV]|V?I{0,3})\b")

# Words we tolerate because they are unavoidable domain vocabulary and carry no
# quantity: "Panamax" contains no digit, but "Capesize 180" does. Kept tiny on
# purpose — every entry here is a hole in the wall.
_ALLOWED_PHRASES = (
    "one-way",
    "one-off",
    "on the one hand",
    "no one",
    "someone",
    "anyone",
    "everyone",
    "one another",
    "first",          # ordinal narrative, not a quantity
    "second",
    "third-party",
)


def _strip_allowed(text: str) -> str:
    out = text
    for phrase in _ALLOWED_PHRASES:
        out = re.sub(re.escape(phrase), " ", out, flags=re.IGNORECASE)
    return out


def find_numerals(text: str) -> list[str]:
    """Return every numeric token found in LLM output. Empty list means clean."""
    if not text:
        return []
    hits: list[str] = []
    scrubbed = _strip_allowed(text)

    for ch in scrubbed:
        # Catches ASCII digits and every Unicode decimal/numeric form:
        # Devanagari ०-९, Arabic-Indic ٠-٩, fullwidth ０-９, ², ½, ①.
        if ch.isdigit() or unicodedata.category(ch) == "No" or unicodedata.numeric(ch, None) is not None:
            hits.append(ch)

    hits.extend(m.group(0) for m in _WORD_NUMBER_RE.finditer(scrubbed))
    hits.extend(m.group(0) for m in _ROMAN_RE.finditer(scrubbed))
    return hits


def assert_no_numerals(text: str, *, where: str = "llm_output", enabled: bool = True) -> str:
    """Gate every LLM string through this before it reaches a human.

    Raises rather than stripping. Stripping would leave a sentence like
    "we recommend fixing at  dollars per tonne", which reads as a rendering bug
    and invites someone to fill the gap by hand. A hard failure sends the
    narration back to the agent with the numbers removed from its remit.
    """
    if not enabled:
        return text
    hits = find_numerals(text)
    if hits:
        preview = ", ".join(repr(h) for h in list(dict.fromkeys(hits))[:8])
        raise NumeralLeakError(
            f"LLM output at {where} contains numeric tokens ({preview}). "
            "Every figure must come from the deterministic core. "
            "Rewrite the narration to reference values by name, not by value."
        )
    return text


def numerals_report(text: str) -> dict[str, Any]:
    """Non-raising variant for the CI report and the /health endpoint."""
    hits = list(dict.fromkeys(find_numerals(text)))
    return {"clean": not hits, "tokens": hits[:20], "count": len(hits)}


# ---------------------------------------------------------------------------
# Rule 2 — no feature may be read from the future
# ---------------------------------------------------------------------------

def _as_dt(v: Any) -> datetime:
    if isinstance(v, datetime):
        return v
    if isinstance(v, date):
        return datetime(v.year, v.month, v.day)
    if isinstance(v, str):
        return datetime.fromisoformat(v.replace("Z", "+00:00"))
    raise TypeError(f"cannot interpret {v!r} as a timestamp")


def _naive(dt: datetime) -> datetime:
    """Compare wall-clock instants without tzinfo mismatches derailing a check."""
    return dt.replace(tzinfo=None) if dt.tzinfo else dt


def assert_point_in_time(
    rows: Iterable[dict[str, Any]],
    as_of: date | datetime,
    *,
    retrieved_key: str = "retrieved_at",
    label: str = "feature query",
    enabled: bool = True,
) -> None:
    """Fail if any row became knowable after the decision was made.

    This is the difference between a backtest and a fantasy. A rate series
    revised last week, replayed into a decision made two years ago, produces a
    beautiful capture ratio and a worthless product. The bitemporal store keeps
    ``valid_at`` (when the fact was true) separate from ``retrieved_at`` (when we
    could first have known it); a decision at time T may only read rows whose
    ``retrieved_at <= T``.
    """
    if not enabled:
        return
    cutoff = _naive(_as_dt(as_of))
    offenders: list[str] = []
    for i, row in enumerate(rows):
        raw = row.get(retrieved_key)
        if raw is None:
            offenders.append(f"row {i}: missing {retrieved_key!r}")
            continue
        if _naive(_as_dt(raw)) > cutoff:
            offenders.append(f"row {i}: {retrieved_key}={raw} > as_of={cutoff.isoformat()}")
        if len(offenders) >= 5:
            break
    if offenders:
        raise LookAheadError(
            f"look-ahead leakage in {label}: " + "; ".join(offenders)
        )


def assert_window_causal(as_of: date, window_start: date, window_end: date) -> None:
    """A laycan window must lie ahead of the decision, and must not be inverted."""
    if window_end < window_start:
        raise ValueError(
            f"laycan window inverted: {window_start.isoformat()} .. {window_end.isoformat()}"
        )
    if window_end < as_of:
        raise LookAheadError(
            f"decision date {as_of.isoformat()} is after the laycan window closed "
            f"({window_end.isoformat()}); there is nothing left to decide"
        )
