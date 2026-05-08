"""Validator module for checking cron expression correctness."""

import re
from dataclasses import dataclass
from typing import Optional

CRON_FIELD_RANGES = [
    ("minute", 0, 59),
    ("hour", 0, 23),
    ("day_of_month", 1, 31),
    ("month", 1, 12),
    ("day_of_week", 0, 7),
]


@dataclass
class ValidationResult:
    valid: bool
    error: Optional[str] = None


def _validate_field(value: str, field_name: str, min_val: int, max_val: int) -> Optional[str]:
    """Validate a single cron field value."""
    if value == "*":
        return None

    # Step values: */n or value/n
    step_match = re.fullmatch(r"(\*|\d+)/(\d+)", value)
    if step_match:
        step = int(step_match.group(2))
        if step < 1:
            return f"Invalid step value in {field_name}: '{value}'"
        return None

    # Range: n-m
    range_match = re.fullmatch(r"(\d+)-(\d+)", value)
    if range_match:
        lo, hi = int(range_match.group(1)), int(range_match.group(2))
        if lo < min_val or hi > max_val or lo > hi:
            return f"Range out of bounds in {field_name}: '{value}' (allowed {min_val}-{max_val})"
        return None

    # List: a,b,c
    if "," in value:
        for part in value.split(","):
            err = _validate_field(part.strip(), field_name, min_val, max_val)
            if err:
                return err
        return None

    # Plain integer
    if re.fullmatch(r"\d+", value):
        n = int(value)
        if n < min_val or n > max_val:
            return f"Value out of range in {field_name}: {n} (allowed {min_val}-{max_val})"
        return None

    return f"Invalid value in {field_name}: '{value}'"


def validate(cron_expression: str) -> ValidationResult:
    """Validate a cron expression string.

    Args:
        cron_expression: A standard 5-field cron expression.

    Returns:
        A ValidationResult indicating whether the expression is valid.
    """
    fields = cron_expression.strip().split()
    if len(fields) != 5:
        return ValidationResult(valid=False, error=f"Expected 5 fields, got {len(fields)}")

    for field_value, (field_name, min_val, max_val) in zip(fields, CRON_FIELD_RANGES):
        error = _validate_field(field_value, field_name, min_val, max_val)
        if error:
            return ValidationResult(valid=False, error=error)

    return ValidationResult(valid=True)
