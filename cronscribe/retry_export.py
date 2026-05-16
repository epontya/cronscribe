"""Export helpers for RetrySchedule objects."""

from __future__ import annotations

import csv
import io
import json
from typing import Literal

from cronscribe.retry import RetrySchedule


def retry_to_json(schedule: RetrySchedule) -> str:
    payload = {
        "base_expression": schedule.base_expression,
        "is_valid": schedule.is_valid,
        "error": schedule.error,
        "policy": {
            "max_attempts": schedule.policy.max_attempts,
            "delay_minutes": schedule.policy.delay_minutes,
            "jitter_minutes": schedule.policy.jitter_minutes,
        },
        "expressions": schedule.expressions,
    }
    return json.dumps(payload, indent=2)


def retry_to_csv(schedule: RetrySchedule) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["attempt", "expression"])
    for i, expr in enumerate(schedule.expressions):
        label = "base" if i == 0 else f"retry_{i}"
        writer.writerow([label, expr])
    return buf.getvalue()


def retry_to_text(schedule: RetrySchedule) -> str:
    lines = [f"Base expression : {schedule.base_expression}"]
    lines.append(
        f"Policy          : {schedule.policy.max_attempts} attempts, "
        f"{schedule.policy.delay_minutes}m delay, "
        f"{schedule.policy.jitter_minutes}m jitter"
    )
    lines.append("")
    for i, expr in enumerate(schedule.expressions):
        label = "Base   " if i == 0 else f"Retry {i}"
        lines.append(f"  {label}: {expr}")
    return "\n".join(lines)


def export_retry(
    schedule: RetrySchedule,
    fmt: Literal["json", "csv", "text"] = "text",
) -> str:
    if fmt == "json":
        return retry_to_json(schedule)
    if fmt == "csv":
        return retry_to_csv(schedule)
    return retry_to_text(schedule)
