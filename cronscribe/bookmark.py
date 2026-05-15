"""Bookmark module: save and retrieve named cron expressions."""

from __future__ import annotations

import json
import os
from typing import Dict, List, Optional, Tuple

_DEFAULT_BOOKMARK_PATH = os.path.join(
    os.path.expanduser("~"), ".cronscribe", "bookmarks.json"
)


def _load_bookmarks(path: str = _DEFAULT_BOOKMARK_PATH) -> Dict[str, str]:
    """Load bookmarks from disk. Returns empty dict if file missing."""
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        try:
            return json.load(fh)
        except json.JSONDecodeError:
            return {}


def _save_bookmarks(
    bookmarks: Dict[str, str], path: str = _DEFAULT_BOOKMARK_PATH
) -> None:
    """Persist bookmarks to disk."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(bookmarks, fh, indent=2)


def add_bookmark(
    name: str, expression: str, path: str = _DEFAULT_BOOKMARK_PATH
) -> None:
    """Save a named bookmark for a cron expression."""
    name = name.strip()
    if not name:
        raise ValueError("Bookmark name must not be empty.")
    bookmarks = _load_bookmarks(path)
    bookmarks[name] = expression.strip()
    _save_bookmarks(bookmarks, path)


def get_bookmark(
    name: str, path: str = _DEFAULT_BOOKMARK_PATH
) -> Optional[str]:
    """Return the cron expression for *name*, or None if not found."""
    bookmarks = _load_bookmarks(path)
    return bookmarks.get(name.strip())


def remove_bookmark(
    name: str, path: str = _DEFAULT_BOOKMARK_PATH
) -> bool:
    """Remove a bookmark by name. Returns True if it existed."""
    bookmarks = _load_bookmarks(path)
    if name.strip() in bookmarks:
        del bookmarks[name.strip()]
        _save_bookmarks(bookmarks, path)
        return True
    return False


def list_bookmarks(
    path: str = _DEFAULT_BOOKMARK_PATH,
) -> List[Tuple[str, str]]:
    """Return all bookmarks as a sorted list of (name, expression) tuples."""
    bookmarks = _load_bookmarks(path)
    return sorted(bookmarks.items())


def is_bookmarked(
    expression: str, path: str = _DEFAULT_BOOKMARK_PATH
) -> bool:
    """Return True if *expression* is already saved under any name."""
    bookmarks = _load_bookmarks(path)
    return expression.strip() in bookmarks.values()
