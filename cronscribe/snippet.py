"""Snippet management: save and reuse named cron expressions with descriptions."""

from __future__ import annotations

import json
import os
from typing import Dict, List, Optional, Tuple

_DEFAULT_SNIPPETS: Dict[str, Tuple[str, str]] = {
    "weekday-morning": ("0 8 * * 1-5", "Every weekday at 8 AM"),
    "weekend-noon": ("0 12 * * 6,0", "Every weekend at noon"),
    "end-of-month": ("0 23 28-31 * *", "Near end of month at 11 PM"),
    "quarterly": ("0 0 1 1,4,7,10 *", "First day of each quarter at midnight"),
    "every-6-hours": ("0 */6 * * *", "Every 6 hours"),
}

_USER_SNIPPETS: Dict[str, Tuple[str, str]] = {}
_SNIPPETS_FILE = os.path.join(
    os.path.expanduser("~"), ".cronscribe", "snippets.json"
)


def _load_user_snippets() -> None:
    global _USER_SNIPPETS
    if os.path.isfile(_SNIPPETS_FILE):
        try:
            with open(_SNIPPETS_FILE, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            _USER_SNIPPETS = {k: tuple(v) for k, v in data.items()}  # type: ignore
        except (json.JSONDecodeError, ValueError):
            _USER_SNIPPETS = {}


def _save_user_snippets() -> None:
    os.makedirs(os.path.dirname(_SNIPPETS_FILE), exist_ok=True)
    with open(_SNIPPETS_FILE, "w", encoding="utf-8") as fh:
        json.dump({k: list(v) for k, v in _USER_SNIPPETS.items()}, fh, indent=2)


def _all_snippets() -> Dict[str, Tuple[str, str]]:
    _load_user_snippets()
    merged = dict(_DEFAULT_SNIPPETS)
    merged.update(_USER_SNIPPETS)
    return merged


def get_snippet(name: str) -> Optional[Tuple[str, str]]:
    """Return (expression, description) for a snippet name, or None."""
    key = name.strip().lower()
    return _all_snippets().get(key)


def add_snippet(name: str, expression: str, description: str = "") -> None:
    """Save a user-defined snippet."""
    _load_user_snippets()
    _USER_SNIPPETS[name.strip().lower()] = (expression.strip(), description.strip())
    _save_user_snippets()


def remove_snippet(name: str) -> bool:
    """Remove a user snippet by name. Returns True if removed."""
    _load_user_snippets()
    key = name.strip().lower()
    if key in _USER_SNIPPETS:
        del _USER_SNIPPETS[key]
        _save_user_snippets()
        return True
    return False


def list_snippets() -> List[Tuple[str, str, str]]:
    """Return list of (name, expression, description) for all snippets."""
    return [
        (name, expr, desc)
        for name, (expr, desc) in sorted(_all_snippets().items())
    ]


def find_snippets_by_expression(expression: str) -> List[Tuple[str, str]]:
    """Return list of (name, description) whose expression matches."""
    expr = expression.strip()
    return [
        (name, desc)
        for name, (ex, desc) in _all_snippets().items()
        if ex == expr
    ]


def is_snippet(name: str) -> bool:
    """Return True if name is a known snippet."""
    return name.strip().lower() in _all_snippets()
