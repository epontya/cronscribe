"""Preview module for cronscribe — generates human-readable next execution times for cron expressions."""

from datetime import datetime, timedelta
from typing import List


def _matches_field(value: int, field: str) -> bool:
    """Check if a value matches a cron field expression."""
    if field == "*":
        return True

    if "/" in field:
        parts = field.split("/")
        step = int(parts[1])
        start = 0 if parts[0] == "*" else int(parts[0])
        return value >= start and (value - start) % step == 0

    if "," in field:
        return value in [int(v) for v in field.split(",")]

    if "-" in field:
        start, end = field.split("-")
        return int(start) <= value <= int(end)

    return value == int(field)


def _next_datetime(cron_expr: str, after: datetime) -> datetime:
    """Find the next datetime matching the cron expression after a given datetime."""
    parts = cron_expr.strip().split()
    if len(parts) != 5:
        raise ValueError(f"Invalid cron expression: {cron_expr}")

    minute_f, hour_f, dom_f, month_f, dow_f = parts

    dt = after.replace(second=0, microsecond=0) + timedelta(minutes=1)

    for _ in range(527040):  # max iterations: 1 year in minutes
        if (
            _matches_field(dt.month, month_f)
            and _matches_field(dt.day, dom_f)
            and _matches_field(dt.weekday(), dow_f.replace("7", "0"))
            and _matches_field(dt.hour, hour_f)
            and _matches_field(dt.minute, minute_f)
        ):
            return dt
        dt += timedelta(minutes=1)

    raise RuntimeError("Could not find next execution time within one year.")


def get_next_executions(cron_expr: str, count: int = 5, start: datetime = None) -> List[datetime]:
    """Return the next `count` execution datetimes for a cron expression.

    Args:
        cron_expr: A valid 5-field cron expression.
        count: Number of upcoming execution times to return.
        start: Datetime to start from (defaults to now).

    Returns:
        A list of upcoming datetime objects.
    """
    if count < 1 or count > 20:
        raise ValueError("count must be between 1 and 20")

    current = start or datetime.now()
    results: List[datetime] = []

    for _ in range(count):
        current = _next_datetime(cron_expr, current)
        results.append(current)

    return results


def format_preview(cron_expr: str, count: int = 5, start: datetime = None) -> str:
    """Return a formatted string preview of the next executions."""
    executions = get_next_executions(cron_expr, count=count, start=start)
    lines = [f"Next {count} executions for '{cron_expr}':"]
    for i, dt in enumerate(executions, 1):
        lines.append(f"  {i}. {dt.strftime('%Y-%m-%d %H:%M')}")
    return "\n".join(lines)
