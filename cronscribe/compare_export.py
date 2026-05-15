"""Export CompareResult to JSON, CSV, or plain text."""

import csv
import io
import json
from typing import Literal

from cronscribe.compare import CompareResult

ExportFormat = Literal["json", "csv", "text"]


def compare_to_json(result: CompareResult) -> str:
    """Serialise a CompareResult to a JSON string."""
    return json.dumps(
        {
            "label_a": result.label_a,
            "label_b": result.label_b,
            "expr_a": result.expr_a,
            "expr_b": result.expr_b,
            "human_a": result.human_a,
            "human_b": result.human_b,
            "are_equal": result.are_equal,
            "diff": result.diff_lines,
            "errors": result.errors,
        },
        indent=2,
    )


def compare_to_csv(result: CompareResult) -> str:
    """Serialise a CompareResult to CSV text."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["label", "expression", "human", "are_equal"])
    writer.writerow([result.label_a, result.expr_a, result.human_a, result.are_equal])
    writer.writerow([result.label_b, result.expr_b, result.human_b, result.are_equal])
    return buf.getvalue()


def compare_to_text(result: CompareResult) -> str:
    """Serialise a CompareResult to plain text."""
    lines = [
        f"[{result.label_a}] {result.expr_a} => {result.human_a}",
        f"[{result.label_b}] {result.expr_b} => {result.human_b}",
        "",
        "IDENTICAL" if result.are_equal else "DIFFER",
    ]
    if result.diff_lines:
        lines.append("")
        lines.extend(result.diff_lines)
    if result.errors:
        lines.append("")
        lines.extend(f"error: {e}" for e in result.errors)
    return "\n".join(lines)


def export_compare(result: CompareResult, fmt: ExportFormat = "text") -> str:
    """Export a CompareResult in the requested format."""
    if fmt == "json":
        return compare_to_json(result)
    if fmt == "csv":
        return compare_to_csv(result)
    return compare_to_text(result)
