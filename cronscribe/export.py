"""Export module — serialise cron results to JSON, CSV, or plain text."""

import csv
import io
import json
from typing import List, Optional


def to_json(
    description: str,
    cron_expr: str,
    next_executions: Optional[List[str]] = None,
    *,
    indent: int = 2,
) -> str:
    """Return a JSON string representing the cron conversion result."""
    payload: dict = {"description": description, "cron": cron_expr}
    if next_executions is not None:
        payload["next_executions"] = next_executions
    return json.dumps(payload, indent=indent)


def to_csv(
    records: List[dict],
    fields: Optional[List[str]] = None,
) -> str:
    """Serialise a list of history/result records to CSV.

    Each record is a dict with at least 'description' and 'cron' keys.
    """
    if not records:
        return ""
    fields = fields or ["description", "cron", "timestamp"]
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf,
        fieldnames=fields,
        extrasaction="ignore",
        lineterminator="\n",
    )
    writer.writeheader()
    for record in records:
        writer.writerow({f: record.get(f, "") for f in fields})
    return buf.getvalue()


def to_text(
    description: str,
    cron_expr: str,
    next_executions: Optional[List[str]] = None,
) -> str:
    """Return a human-readable plain-text summary."""
    lines = [
        f"Description : {description}",
        f"Cron        : {cron_expr}",
    ]
    if next_executions:
        lines.append("Next runs   :")
        for dt in next_executions:
            lines.append(f"  - {dt}")
    return "\n".join(lines)


def export(
    description: str,
    cron_expr: str,
    fmt: str = "text",
    next_executions: Optional[List[str]] = None,
) -> str:
    """Dispatch to the appropriate serialiser based on *fmt*.

    Supported formats: 'json', 'csv', 'text'.
    """
    fmt = fmt.lower()
    if fmt == "json":
        return to_json(description, cron_expr, next_executions)
    if fmt == "csv":
        record = {"description": description, "cron": cron_expr}
        return to_csv([record])
    if fmt == "text":
        return to_text(description, cron_expr, next_executions)
    raise ValueError(f"Unsupported export format: {fmt!r}. Choose json, csv, or text.")
