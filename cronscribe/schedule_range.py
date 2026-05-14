"""Generate cron expressions for date/time ranges and bounded schedules."""

from datetime import datetime, timedelta
from typing import Optional, Tuple


def _clamp(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, value))


def expression_for_range(
    start: datetime,
    end: datetime,
    interval_minutes: int = 60,
) -> Tuple[str, str]:
    """Return (cron_expression, description) that runs every *interval_minutes*
    minutes but only within the hour-of-day window defined by *start* and *end*.

    Both *start* and *end* are used only for their time components (hour/minute).
    If the window spans midnight the expression uses a list of hours.

    Returns a tuple of (cron_expr, human_description).
    """
    if interval_minutes < 1 or interval_minutes > 59:
        raise ValueError("interval_minutes must be between 1 and 59")

    start_h = _clamp(start.hour, 0, 23)
    start_m = _clamp(start.minute, 0, 59)
    end_h = _clamp(end.hour, 0, 23)
    end_m = _clamp(end.minute, 0, 59)

    minute_part = f"*/{interval_minutes}" if interval_minutes > 1 else "*"

    if start_h == 0 and end_h == 23:
        hour_part = "*"
        desc = f"Every {interval_minutes} minute(s) all day"
    elif start_h <= end_h:
        if start_h == end_h:
            hour_part = str(start_h)
        else:
            hour_part = f"{start_h}-{end_h}"
        desc = (
            f"Every {interval_minutes} minute(s) from "
            f"{start_h:02d}:{start_m:02d} to {end_h:02d}:{end_m:02d}"
        )
    else:
        # Wraps midnight
        hours = list(range(start_h, 24)) + list(range(0, end_h + 1))
        hour_part = ",".join(str(h) for h in hours)
        desc = (
            f"Every {interval_minutes} minute(s) from "
            f"{start_h:02d}:{start_m:02d} to {end_h:02d}:{end_m:02d} (spans midnight)"
        )

    cron_expr = f"{minute_part} {hour_part} * * *"
    return cron_expr, desc


def expressions_for_weekday_range(
    start_dow: int,
    end_dow: int,
    hour: int = 9,
    minute: int = 0,
) -> Tuple[str, str]:
    """Return (cron_expression, description) for a fixed time across a weekday range.

    *start_dow* and *end_dow* use cron convention: 0=Sunday, 6=Saturday.
    """
    DOW_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    if not (0 <= start_dow <= 6 and 0 <= end_dow <= 6):
        raise ValueError("Day-of-week values must be 0-6")

    hour = _clamp(hour, 0, 23)
    minute = _clamp(minute, 0, 59)

    if start_dow == end_dow:
        dow_part = str(start_dow)
    elif start_dow < end_dow:
        dow_part = f"{start_dow}-{end_dow}"
    else:
        days = list(range(start_dow, 7)) + list(range(0, end_dow + 1))
        dow_part = ",".join(str(d) for d in days)

    cron_expr = f"{minute} {hour} * * {dow_part}"
    desc = (
        f"At {hour:02d}:{minute:02d} on "
        f"{DOW_NAMES[start_dow]} through {DOW_NAMES[end_dow]}"
    )
    return cron_expr, desc
