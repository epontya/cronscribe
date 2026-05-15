"""explain.py — Generates a human-friendly, structured explanation of a cron expression.

Breaks down each field and provides a plain-English summary of when the job runs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .validator import validate

# Field metadata: (index, name, unit, min, max, names)
_FIELD_META = [
    (0, "minute",      "minute",     0,  59, None),
    (1, "hour",        "hour",       0,  23, None),
    (2, "day-of-month","day",        1,  31, None),
    (3, "month",       "month",      1,  12,
     ["January", "February", "March", "April", "May", "June",
      "July", "August", "September", "October", "November", "December"]),
    (4, "day-of-week", "weekday",    0,   7,
     ["Sunday", "Monday", "Tuesday", "Wednesday",
      "Thursday", "Friday", "Saturday", "Sunday"]),
]


@dataclass
class FieldExplanation:
    """Explanation for a single cron field."""
    field_name: str
    raw_value: str
    description: str


@dataclass
class ExplainResult:
    """Full explanation of a cron expression."""
    expression: str
    fields: list[FieldExplanation] = field(default_factory=list)
    summary: str = ""
    error: Optional[str] = None

    @property
    def is_valid(self) -> bool:
        return self.error is None


def _explain_field(value: str, name: str, unit: str,
                   lo: int, hi: int, names: Optional[list[str]]) -> str:
    """Return a plain-English description of a single cron field token."""
    if value == "*":
        return f"every {unit}"

    def _label(n: int) -> str:
        if names and lo <= n <= hi:
            return names[n - lo]
        return str(n)

    # Step: */N or start/N
    if "/" in value:
        base, step = value.split("/", 1)
        step_int = int(step)
        if base == "*" or base == str(lo):
            return f"every {step_int} {unit}s"
        base_int = int(base)
        return f"every {step_int} {unit}s starting at {unit} {_label(base_int)}"

    # List: a,b,c
    if "," in value:
        parts = [_label(int(p)) for p in value.split(",")]
        if len(parts) == 2:
            return f"at {unit}s {parts[0]} and {parts[1]}"
        return f"at {unit}s " + ", ".join(parts[:-1]) + f", and {parts[-1]}"

    # Range: a-b
    if "-" in value:
        start, end = value.split("-", 1)
        return f"from {unit} {_label(int(start))} through {_label(int(end))}"

    # Exact value
    return f"at {unit} {_label(int(value))}"


def explain(expression: str) -> ExplainResult:
    """Explain a cron expression in plain English.

    Args:
        expression: A 5-field cron expression string.

    Returns:
        An ExplainResult with per-field explanations and an overall summary.
    """
    result = ExplainResult(expression=expression)

    validation = validate(expression)
    if not validation.is_valid:
        result.error = "; ".join(validation.errors)
        return result

    parts = expression.split()
    field_explanations: list[FieldExplanation] = []

    for idx, name, unit, lo, hi, names in _FIELD_META:
        raw = parts[idx]
        desc = _explain_field(raw, name, unit, lo, hi, names)
        field_explanations.append(FieldExplanation(
            field_name=name,
            raw_value=raw,
            description=desc,
        ))

    result.fields = field_explanations

    # Build a readable summary sentence
    minute_desc  = field_explanations[0].description
    hour_desc    = field_explanations[1].description
    dom_desc     = field_explanations[2].description
    month_desc   = field_explanations[3].description
    dow_desc     = field_explanations[4].description

    # Simplify common patterns
    if parts[0] == "*" and parts[1] == "*":
        time_part = "every minute"
    elif parts[0] == "*":
        time_part = f"{minute_desc}, {hour_desc}"
    else:
        time_part = f"{minute_desc} past {hour_desc}"

    dom_part   = "" if parts[2] == "*" else f", on {dom_desc}"
    month_part = "" if parts[3] == "*" else f", in {month_desc}"
    dow_part   = "" if parts[4] == "*" else f", on {dow_desc}"

    result.summary = f"Runs {time_part}{dom_part}{month_part}{dow_part}."
    return result


def format_explanation(result: ExplainResult, *, color: bool = True) -> str:
    """Format an ExplainResult as a human-readable string.

    Args:
        result: The ExplainResult to format.
        color:  Whether to include ANSI colour codes.

    Returns:
        A multi-line string ready for printing.
    """
    BOLD  = "\033[1m"  if color else ""
    CYAN  = "\033[36m" if color else ""
    RESET = "\033[0m"  if color else ""
    RED   = "\033[31m" if color else ""

    if not result.is_valid:
        return f"{RED}Error:{RESET} {result.error}"

    lines = [
        f"{BOLD}Expression:{RESET} {CYAN}{result.expression}{RESET}",
        f"{BOLD}Summary:{RESET}    {result.summary}",
        "",
        f"{BOLD}Field breakdown:{RESET}",
    ]
    for fe in result.fields:
        lines.append(f"  {CYAN}{fe.field_name:<14}{RESET} ({fe.raw_value:<10})  {fe.description}")

    return "\n".join(lines)
