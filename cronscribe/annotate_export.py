"""Export annotation data to JSON, CSV, or plain text."""

from __future__ import annotations

import csv
import io
import json
from typing import Dict, List, Literal

ExportFormat = Literal["json", "csv", "text"]


def annotations_to_json(data: Dict[str, List[str]], indent: int = 2) -> str:
    """Serialise annotation mapping to a JSON string."""
    return json.dumps(data, indent=indent)


def annotations_to_csv(data: Dict[str, List[str]]) -> str:
    """Serialise annotation mapping to CSV (expression, index, note)."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["expression", "index", "note"])
    for expression, notes in sorted(data.items()):
        for idx, note in enumerate(notes):
            writer.writerow([expression, idx, note])
    return buf.getvalue()


def annotations_to_text(data: Dict[str, List[str]]) -> str:
    """Serialise annotation mapping to a human-readable text block."""
    if not data:
        return "No annotations."
    lines: List[str] = []
    for expression in sorted(data):
        notes = data[expression]
        lines.append(f"{expression}")
        for idx, note in enumerate(notes):
            lines.append(f"  [{idx}] {note}")
    return "\n".join(lines)


def export_annotations(
    data: Dict[str, List[str]],
    fmt: ExportFormat = "text",
) -> str:
    """Dispatch to the appropriate serialiser based on *fmt*."""
    if fmt == "json":
        return annotations_to_json(data)
    if fmt == "csv":
        return annotations_to_csv(data)
    if fmt == "text":
        return annotations_to_text(data)
    raise ValueError(f"Unknown export format: {fmt!r}. Choose from json, csv, text.")
