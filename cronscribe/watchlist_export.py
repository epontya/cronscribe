"""Export watchlist entries to various formats."""

from __future__ import annotations

import csv
import io
import json
from typing import List, Tuple

from cronscribe.watchlist import list_watches


def watchlist_to_json() -> str:
    entries = list_watches()
    payload = [{"name": name, "expression": expr} for name, expr in entries]
    return json.dumps(payload, indent=2)


def watchlist_to_csv() -> str:
    entries = list_watches()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["name", "expression"])
    writer.writerows(entries)
    return buf.getvalue()


def watchlist_to_text() -> str:
    entries = list_watches()
    if not entries:
        return "Watchlist is empty."
    lines = [f"{name}: {expr}" for name, expr in entries]
    return "\n".join(lines)


def export_watchlist(fmt: str = "text") -> str:
    """Return the watchlist serialised as *fmt* ('json', 'csv', or 'text')."""
    fmt = fmt.lower().strip()
    if fmt == "json":
        return watchlist_to_json()
    if fmt == "csv":
        return watchlist_to_csv()
    return watchlist_to_text()
