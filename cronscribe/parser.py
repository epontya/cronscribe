"""Parser module for converting human-readable schedule descriptions to cron expressions."""

import re
from typing import Optional

# Mapping of common human-readable patterns to cron expressions
PATTERN_MAP = [
    (r"every minute", "* * * * *"),
    (r"every hour", "0 * * * *"),
    (r"every day at midnight", "0 0 * * *"),
    (r"every day at noon", "0 12 * * *"),
    (r"every sunday", "0 0 * * 0"),
    (r"every monday", "0 0 * * 1"),
    (r"every tuesday", "0 0 * * 2"),
    (r"every wednesday", "0 0 * * 3"),
    (r"every thursday", "0 0 * * 4"),
    (r"every friday", "0 0 * * 5"),
    (r"every saturday", "0 0 * * 6"),
    (r"every weekday", "0 0 * * 1-5"),
    (r"every weekend", "0 0 * * 0,6"),
    (r"every month", "0 0 1 * *"),
    (r"every year", "0 0 1 1 *"),
]

TIME_PATTERN = re.compile(
    r"every day at (\d{1,2})(?::(\d{2}))?\s*(am|pm)?", re.IGNORECASE
)
INTERVAL_MINUTE_PATTERN = re.compile(r"every (\d+) minutes?", re.IGNORECASE)
INTERVAL_HOUR_PATTERN = re.compile(r"every (\d+) hours?", re.IGNORECASE)


def parse(description: str) -> Optional[str]:
    """Parse a human-readable schedule description and return a cron expression.

    Args:
        description: Human-readable schedule string (e.g. 'every day at 9am')

    Returns:
        A valid cron expression string, or None if the description cannot be parsed.
    """
    normalized = description.strip().lower()

    for pattern, cron in PATTERN_MAP:
        if re.fullmatch(pattern, normalized):
            return cron

    match = TIME_PATTERN.fullmatch(normalized)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        meridiem = match.group(3)
        if meridiem == "pm" and hour != 12:
            hour += 12
        elif meridiem == "am" and hour == 12:
            hour = 0
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return f"{minute} {hour} * * *"

    match = INTERVAL_MINUTE_PATTERN.fullmatch(normalized)
    if match:
        n = int(match.group(1))
        if 1 <= n <= 59:
            return f"*/{n} * * * *"

    match = INTERVAL_HOUR_PATTERN.fullmatch(normalized)
    if match:
        n = int(match.group(1))
        if 1 <= n <= 23:
            return f"0 */{n} * * *"

    return None
