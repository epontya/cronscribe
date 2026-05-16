"""Retry policy generation for cron expressions.

Given a base cron expression and a retry policy (max attempts, delay in minutes),
produces a list of cron expressions representing the base run plus each retry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from cronscribe.validator import validate


@dataclass
class RetryPolicy:
    max_attempts: int = 3
    delay_minutes: int = 5
    jitter_minutes: int = 0


@dataclass
class RetrySchedule:
    base_expression: str
    policy: RetryPolicy
    expressions: List[str] = field(default_factory=list)
    is_valid: bool = True
    error: Optional[str] = None


def _offset_expression(expression: str, offset_minutes: int) -> Optional[str]:
    """Shift a cron expression by *offset_minutes* (best-effort, minute/hour fields only)."""
    parts = expression.split()
    if len(parts) != 5:
        return None
    minute_field, hour_field, dom, month, dow = parts
    if minute_field == "*" or "/" in minute_field or "," in minute_field or "-" in minute_field:
        return None
    try:
        base_minute = int(minute_field)
        base_hour = int(hour_field) if hour_field != "*" else None
    except ValueError:
        return None

    total_minutes = base_minute + offset_minutes
    new_minute = total_minutes % 60
    extra_hours = total_minutes // 60

    if base_hour is not None:
        new_hour = (base_hour + extra_hours) % 24
        return f"{new_minute} {new_hour} {dom} {month} {dow}"
    else:
        if extra_hours:
            return None  # Cannot safely offset wildcard hour
        return f"{new_minute} {hour_field} {dom} {month} {dow}"


def build_retry_schedule(expression: str, policy: Optional[RetryPolicy] = None) -> RetrySchedule:
    """Return a RetrySchedule for *expression* using *policy*."""
    if policy is None:
        policy = RetryPolicy()

    result = validate(expression)
    if not result.is_valid:
        return RetrySchedule(
            base_expression=expression,
            policy=policy,
            is_valid=False,
            error=result.errors[0] if result.errors else "Invalid expression",
        )

    expressions = [expression]
    for attempt in range(1, policy.max_attempts):
        offset = attempt * (policy.delay_minutes + policy.jitter_minutes)
        shifted = _offset_expression(expression, offset)
        if shifted is None:
            break
        expressions.append(shifted)

    return RetrySchedule(
        base_expression=expression,
        policy=policy,
        expressions=expressions,
        is_valid=True,
    )


def format_retry_schedule(schedule: RetrySchedule) -> str:
    """Return a human-readable summary of a RetrySchedule."""
    if not schedule.is_valid:
        return f"Error: {schedule.error}"
    lines = [f"Base: {schedule.base_expression}"]
    for i, expr in enumerate(schedule.expressions[1:], start=1):
        lines.append(f"Retry {i}: {expr}")
    if len(schedule.expressions) < schedule.policy.max_attempts:
        lines.append("(Some retries could not be computed for this expression pattern)")
    return "\n".join(lines)
