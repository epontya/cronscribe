"""Detect overlapping cron schedules within a given time window."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Tuple

from cronscribe.preview import get_next_executions
from cronscribe.validator import validate


@dataclass
class OverlapResult:
    expression_a: str
    expression_b: str
    label_a: str
    label_b: str
    overlapping_times: List[datetime] = field(default_factory=list)
    is_valid: bool = True
    error: str = ""

    @property
    def has_overlaps(self) -> bool:
        return len(self.overlapping_times) > 0

    @property
    def overlap_count(self) -> int:
        return len(self.overlapping_times)


def find_overlaps(
    expression_a: str,
    expression_b: str,
    label_a: str = "A",
    label_b: str = "B",
    count: int = 50,
    from_dt: datetime | None = None,
) -> OverlapResult:
    """Find datetime points where both cron expressions fire simultaneously."""
    result = OverlapResult(
        expression_a=expression_a,
        expression_b=expression_b,
        label_a=label_a,
        label_b=label_b,
    )

    val_a = validate(expression_a)
    val_b = validate(expression_b)

    if not val_a.is_valid:
        result.is_valid = False
        result.error = f"Invalid expression '{label_a}': {'; '.join(val_a.errors)}"
        return result

    if not val_b.is_valid:
        result.is_valid = False
        result.error = f"Invalid expression '{label_b}': {'; '.join(val_b.errors)}"
        return result

    base = from_dt or datetime.now().replace(second=0, microsecond=0)

    times_a: set = set(get_next_executions(expression_a, count=count, from_dt=base))
    times_b: set = set(get_next_executions(expression_b, count=count, from_dt=base))

    result.overlapping_times = sorted(times_a & times_b)
    return result


def format_overlap_report(result: OverlapResult, use_color: bool = True) -> str:
    """Format an OverlapResult as a human-readable report string."""
    lines: List[str] = []

    if not result.is_valid:
        return f"Error: {result.error}"

    lines.append(f"Overlap check: [{result.label_a}] {result.expression_a}")
    lines.append(f"           vs: [{result.label_b}] {result.expression_b}")
    lines.append("")

    if not result.has_overlaps:
        lines.append("No overlapping execution times found in the sampled window.")
    else:
        lines.append(f"Found {result.overlap_count} overlapping execution(s):")
        for dt in result.overlapping_times:
            lines.append(f"  • {dt.strftime('%Y-%m-%d %H:%M')}")

    return "\n".join(lines)
