"""Export macros to JSON, CSV, or plain text."""

import json
import csv
import io
from typing import List, Optional
from cronscribe.macro import list_macros


def macros_to_json(indent: int = 2) -> str:
    """Serialise all macros to a JSON string."""
    data = [
        {"name": name, "description": desc, "expressions": exprs}
        for name, desc, exprs in list_macros()
    ]
    return json.dumps(data, indent=indent)


def macros_to_csv() -> str:
    """Serialise all macros to CSV (name, description, expressions joined by ';')."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["name", "description", "expressions"])
    for name, desc, exprs in list_macros():
        writer.writerow([name, desc, ";".join(exprs)])
    return buf.getvalue()


def macros_to_text() -> str:
    """Serialise all macros to a human-readable plain text block."""
    lines: List[str] = []
    for name, desc, exprs in list_macros():
        lines.append(f"[{name}]")
        lines.append(f"  Description : {desc}")
        for expr in exprs:
            lines.append(f"  Expression  : {expr}")
        lines.append("")
    return "\n".join(lines)


def export_macros(fmt: str = "text") -> str:
    """Export macros in the requested format ('json', 'csv', or 'text')."""
    fmt = fmt.strip().lower()
    if fmt == "json":
        return macros_to_json()
    if fmt == "csv":
        return macros_to_csv()
    if fmt == "text":
        return macros_to_text()
    raise ValueError(f"Unsupported export format: '{fmt}'. Choose json, csv, or text.")
