"""Generate a calendar-style view showing when a cron expression fires."""

from __future__ import annotations

import calendar
from datetime import date, datetime
from typing import List, Optional

from cronscribe.preview import _matches_field


def _fires_on_day(expr: str, day: date) -> bool:
    """Return True if the cron expression fires at least once on the given day."""
    fields = expr.strip().split()
    if len(fields) != 5:
        return False
    _minute, _hour, dom, month, dow = fields
    dt = datetime(day.year, day.month, day.day)
    return (
        _matches_field(month, dt.month)
        and _matches_field(dom, dt.day)
        and _matches_field(dow, dt.weekday() + 1 if dt.weekday() != 6 else 0)
    )


def month_calendar(
    expr: str,
    year: Optional[int] = None,
    month: Optional[int] = None,
) -> List[List[Optional[date]]]:
    """Return a list of weeks; each week is 7 Optional[date] entries (None = padding)."""
    today = date.today()
    y = year if year is not None else today.year
    m = month if month is not None else today.month
    cal = calendar.monthcalendar(y, m)
    weeks: List[List[Optional[date]]] = []
    for week in cal:
        row: List[Optional[date]] = []
        for day_num in week:
            row.append(date(y, m, day_num) if day_num != 0 else None)
        weeks.append(row)
    return weeks


def format_calendar_view(
    expr: str,
    year: Optional[int] = None,
    month: Optional[int] = None,
    color: bool = True,
) -> str:
    """Render a text calendar highlighting days the expression fires."""
    today = date.today()
    y = year if year is not None else today.year
    m = month if month is not None else today.month

    RESET = "\033[0m" if color else ""
    BOLD_GREEN = "\033[1;32m" if color else ""
    DIM = "\033[2m" if color else ""

    header = f"  {calendar.month_name[m]} {y}"
    lines = [header, "  Mo Tu We Th Fr Sa Su"]

    for week in month_calendar(expr, y, m):
        cells = []
        for d in week:
            if d is None:
                cells.append("  ")
            elif _fires_on_day(expr, d):
                label = f"{d.day:2d}"
                cells.append(f"{BOLD_GREEN}{label}{RESET}")
            else:
                label = f"{d.day:2d}"
                cells.append(f"{DIM}{label}{RESET}" if color else label)
        lines.append("  " + " ".join(cells))

    lines.append("")
    if color:
        lines.append(f"  {BOLD_GREEN}■{RESET} = expression fires on this day")
    else:
        lines.append("  [bold] = expression fires on this day")
    return "\n".join(lines)
