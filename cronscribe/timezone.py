"""Timezone-aware next-run utilities for cron expressions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError  # Python 3.9+
except ImportError:  # pragma: no cover
    from backports.zoneinfo import ZoneInfo, ZoneInfoNotFoundError  # type: ignore

from cronscribe.preview import get_next_executions


@dataclass
class TimezoneResult:
    expression: str
    timezone: str
    is_valid_tz: bool
    utc_times: List[datetime] = field(default_factory=list)
    local_times: List[datetime] = field(default_factory=list)
    error: Optional[str] = None

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"TimezoneResult(expression={self.expression!r}, "
            f"timezone={self.timezone!r}, is_valid_tz={self.is_valid_tz})"
        )


def _resolve_zone(tz_name: str) -> Optional[ZoneInfo]:
    """Return a ZoneInfo object or None if the timezone name is invalid."""
    try:
        return ZoneInfo(tz_name)
    except (ZoneInfoNotFoundError, KeyError):
        return None


def get_next_runs_in_timezone(
    expression: str,
    timezone: str,
    count: int = 5,
    base: Optional[datetime] = None,
) -> TimezoneResult:
    """Return the next *count* executions of *expression* expressed in *timezone*.

    UTC times are computed first (from *base* which defaults to ``datetime.utcnow()``),
    then converted to the requested timezone.
    """
    zone = _resolve_zone(timezone)
    if zone is None:
        return TimezoneResult(
            expression=expression,
            timezone=timezone,
            is_valid_tz=False,
            error=f"Unknown timezone: {timezone!r}",
        )

    base_utc = (base or datetime.utcnow()).replace(tzinfo=ZoneInfo("UTC"))
    utc_times = get_next_executions(expression, count=count, base=base_utc)

    if not utc_times:
        return TimezoneResult(
            expression=expression,
            timezone=timezone,
            is_valid_tz=True,
            error="Could not compute next executions — expression may be invalid.",
        )

    local_times = [dt.astimezone(zone) for dt in utc_times]

    return TimezoneResult(
        expression=expression,
        timezone=timezone,
        is_valid_tz=True,
        utc_times=utc_times,
        local_times=local_times,
    )


def format_timezone_report(result: TimezoneResult, use_color: bool = True) -> str:
    """Render a human-readable side-by-side UTC / local-time report."""
    if not result.is_valid_tz or result.error:
        msg = result.error or "Unknown error."
        return f"[timezone] Error: {msg}\n"

    header = f"Next runs for '{result.expression}' in {result.timezone}:\n"
    header += f"  {'UTC':<26}  {'Local':<26}\n"
    header += "  " + "-" * 54 + "\n"
    rows = ""
    for utc, loc in zip(result.utc_times, result.local_times):
        rows += f"  {utc.strftime('%Y-%m-%d %H:%M:%S %Z'):<26}  {loc.strftime('%Y-%m-%d %H:%M:%S %Z'):<26}\n"
    return header + rows
