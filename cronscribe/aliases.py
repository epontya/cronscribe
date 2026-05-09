"""Common cron expression aliases and shortcuts."""

from typing import Optional

# Map human-friendly alias names to cron expressions
ALIAS_MAP: dict[str, str] = {
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@monthly": "0 0 1 * *",
    "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@hourly": "0 * * * *",
    "@every_minute": "* * * * *",
    "@weekdays": "0 9 * * 1-5",
    "@weekends": "0 10 * * 6,0",
    "@noon": "0 12 * * *",
    "@business_hours_start": "0 9 * * 1-5",
    "@business_hours_end": "0 17 * * 1-5",
    "@quarterly": "0 0 1 1,4,7,10 *",
}

# Reverse map: cron expression -> list of alias names
_REVERSE_MAP: dict[str, list[str]] = {}
for _alias, _expr in ALIAS_MAP.items():
    _REVERSE_MAP.setdefault(_expr, []).append(_alias)


def resolve_alias(name: str) -> Optional[str]:
    """Return the cron expression for a given alias, or None if not found."""
    key = name.strip().lower()
    return ALIAS_MAP.get(key)


def get_aliases_for(cron_expr: str) -> list[str]:
    """Return all alias names that map to the given cron expression."""
    return _REVERSE_MAP.get(cron_expr.strip(), [])


def list_aliases() -> list[tuple[str, str]]:
    """Return all (alias, cron_expression) pairs sorted by alias name."""
    return sorted(ALIAS_MAP.items())


def is_alias(name: str) -> bool:
    """Return True if the given string is a known alias."""
    return name.strip().lower() in ALIAS_MAP
