"""Suggests cron expression corrections and alternatives."""

from typing import List
from cronscribe.validator import validate

COMMON_PATTERNS = [
    ("* * * * *", "every minute"),
    ("0 * * * *", "every hour"),
    ("0 0 * * *", "every day at midnight"),
    ("0 12 * * *", "every day at noon"),
    ("0 0 * * 0", "every Sunday at midnight"),
    ("0 0 1 * *", "first day of every month"),
    ("0 0 1 1 *", "once a year on January 1st"),
    ("*/5 * * * *", "every 5 minutes"),
    ("*/15 * * * *", "every 15 minutes"),
    ("*/30 * * * *", "every 30 minutes"),
    ("0 9-17 * * 1-5", "every hour 9am-5pm on weekdays"),
    ("0 0 * * 1-5", "every weekday at midnight"),
]


def suggest_similar(cron_expr: str, max_results: int = 3) -> List[tuple]:
    """Suggest similar valid cron patterns based on a given expression."""
    parts = cron_expr.strip().split()
    if len(parts) != 5:
        return COMMON_PATTERNS[:max_results]

    scored: List[tuple] = []
    for pattern, description in COMMON_PATTERNS:
        pattern_parts = pattern.split()
        score = sum(1 for a, b in zip(parts, pattern_parts) if a == b)
        scored.append((score, pattern, description))

    scored.sort(key=lambda x: -x[0])
    return [(p, d) for _, p, d in scored[:max_results]]


def suggest_fixes(cron_expr: str) -> List[str]:
    """Suggest possible fixes for an invalid cron expression."""
    result = validate(cron_expr)
    if result.is_valid:
        return []

    parts = cron_expr.strip().split()
    if len(parts) != 5:
        return ["Expression must have exactly 5 fields: minute hour day month weekday"]

    suggestions = []
    field_ranges = [
        ("minute", 0, 59),
        ("hour", 0, 23),
        ("day of month", 1, 31),
        ("month", 1, 12),
        ("day of week", 0, 7),
    ]

    for (name, low, high), part in zip(field_ranges, parts):
        if part == "*" or part.startswith("*/"):
            continue
        if part.isdigit():
            val = int(part)
            if not (low <= val <= high):
                suggestions.append(
                    f"Field '{name}' value {val} is out of range [{low}-{high}]."
                    f" Try a value between {low} and {high}."
                )
        elif "-" in part:
            bounds = part.split("-", 1)
            if all(b.isdigit() for b in bounds):
                start, end = int(bounds[0]), int(bounds[1])
                if start > end:
                    suggestions.append(
                        f"Field '{name}' range {part} is inverted. Try {end}-{start}."
                    )

    if not suggestions:
        suggestions.append("Check each field is within its valid range and uses valid syntax.")

    return suggestions
