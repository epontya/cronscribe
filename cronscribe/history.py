"""History module for tracking and replaying past cron conversions."""

import json
import os
from datetime import datetime
from typing import List, Optional

DEFAULT_HISTORY_FILE = os.path.expanduser("~/.cronscribe_history.json")
MAX_HISTORY_ENTRIES = 100


def _load_history(path: str = DEFAULT_HISTORY_FILE) -> List[dict]:
    """Load history entries from a JSON file."""
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _save_history(entries: List[dict], path: str = DEFAULT_HISTORY_FILE) -> None:
    """Persist history entries to a JSON file."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(entries[-MAX_HISTORY_ENTRIES:], f, indent=2)
    except OSError:
        pass


def record(description: str, cron_expr: str, path: str = DEFAULT_HISTORY_FILE) -> None:
    """Append a new conversion record to history."""
    entries = _load_history(path)
    entries.append({
        "description": description,
        "cron": cron_expr,
        "timestamp": datetime.utcnow().isoformat(),
    })
    _save_history(entries, path)


def get_history(limit: Optional[int] = None, path: str = DEFAULT_HISTORY_FILE) -> List[dict]:
    """Return history entries, newest first, optionally limited."""
    entries = _load_history(path)
    entries = list(reversed(entries))
    if limit is not None:
        entries = entries[:limit]
    return entries


def clear_history(path: str = DEFAULT_HISTORY_FILE) -> int:
    """Delete all history entries. Returns number of removed entries."""
    entries = _load_history(path)
    count = len(entries)
    _save_history([], path)
    return count


def search_history(query: str, path: str = DEFAULT_HISTORY_FILE) -> List[dict]:
    """Return entries whose description or cron expression contains query."""
    query_lower = query.lower()
    return [
        e for e in _load_history(path)
        if query_lower in e.get("description", "").lower()
        or query_lower in e.get("cron", "").lower()
    ]
