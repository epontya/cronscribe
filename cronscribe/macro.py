"""Macro expansion: named multi-step schedule patterns that expand to lists of cron expressions."""

from typing import Dict, List, Optional, Tuple

# Built-in macros: name -> (description, list of cron expressions)
_BUILTIN_MACROS: Dict[str, Tuple[str, List[str]]] = {
    "business_hours": (
        "Every hour during business hours (9-17) on weekdays",
        ["0 9-17 * * 1-5"],
    ),
    "twice_daily": (
        "Twice a day at midnight and noon",
        ["0 0 * * *", "0 12 * * *"],
    ),
    "end_of_month_cleanup": (
        "Last day of common months (28th as safe approximation) at midnight",
        ["0 0 28 * *"],
    ),
    "weekday_digest": (
        "Morning and evening digest on weekdays",
        ["0 8 * * 1-5", "0 18 * * 1-5"],
    ),
    "hourly_office": (
        "Every hour between 8 and 20",
        ["0 8-20 * * *"],
    ),
    "nightly_backup": (
        "Nightly backup at 2 AM every day",
        ["0 2 * * *"],
    ),
    "weekly_report": (
        "Weekly report every Monday at 9 AM",
        ["0 9 * * 1"],
    ),
}

_USER_MACROS: Dict[str, Tuple[str, List[str]]] = {}


def _all_macros() -> Dict[str, Tuple[str, List[str]]]:
    merged = dict(_BUILTIN_MACROS)
    merged.update(_USER_MACROS)
    return merged


def get_macro(name: str) -> Optional[Tuple[str, List[str]]]:
    """Return (description, [cron expressions]) for a macro name, or None."""
    return _all_macros().get(name.strip().lower().replace(" ", "_"))


def list_macros() -> List[Tuple[str, str, List[str]]]:
    """Return list of (name, description, expressions) for all macros."""
    return [
        (name, desc, exprs)
        for name, (desc, exprs) in sorted(_all_macros().items())
    ]


def add_macro(name: str, description: str, expressions: List[str]) -> None:
    """Register a user-defined macro."""
    key = name.strip().lower().replace(" ", "_")
    if not key:
        raise ValueError("Macro name must not be empty.")
    if not expressions:
        raise ValueError("Macro must contain at least one expression.")
    _USER_MACROS[key] = (description, list(expressions))


def is_macro(name: str) -> bool:
    """Return True if the name resolves to a known macro."""
    return get_macro(name) is not None


def find_macros_by_expression(expr: str) -> List[str]:
    """Return macro names whose expression list contains the given cron expression."""
    return [
        name
        for name, (_, exprs) in _all_macros().items()
        if expr.strip() in exprs
    ]
