"""Watchlist: persist and manage a set of named cron expressions to monitor."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

_DEFAULT_PATH = Path.home() / ".cronscribe" / "watchlist.json"


def _load_watchlist(path: Path = _DEFAULT_PATH) -> Dict[str, str]:
    if path.exists():
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def _save_watchlist(data: Dict[str, str], path: Path = _DEFAULT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def add_watch(name: str, expression: str, path: Path = _DEFAULT_PATH) -> None:
    """Add or update a named entry in the watchlist."""
    data = _load_watchlist(path)
    data[name.strip()] = expression.strip()
    _save_watchlist(data, path)


def remove_watch(name: str, path: Path = _DEFAULT_PATH) -> bool:
    """Remove a named entry. Returns True if it existed."""
    data = _load_watchlist(path)
    if name.strip() in data:
        del data[name.strip()]
        _save_watchlist(data, path)
        return True
    return False


def get_watch(name: str, path: Path = _DEFAULT_PATH) -> Optional[str]:
    """Return the expression for *name*, or None if not found."""
    return _load_watchlist(path).get(name.strip())


def list_watches(path: Path = _DEFAULT_PATH) -> List[tuple]:
    """Return a sorted list of (name, expression) tuples."""
    return sorted(_load_watchlist(path).items())


def clear_watchlist(path: Path = _DEFAULT_PATH) -> None:
    """Remove all watchlist entries."""
    _save_watchlist({}, path)
