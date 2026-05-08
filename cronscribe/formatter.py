"""Formats cron expressions and related data for display."""

from typing import List
from cronscribe.humanizer import humanize
from cronscribe.validator import validate


ANSI_GREEN = "\033[92m"
ANSI_RED = "\033[91m"
ANSI_YELLOW = "\033[93m"
ANSI_CYAN = "\033[96m"
ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"


def _colorize(text: str, color: str, use_color: bool = True) -> str:
    if not use_color:
        return text
    return f"{color}{text}{ANSI_RESET}"


def format_cron_table(cron_expr: str, use_color: bool = True) -> str:
    """Format a cron expression as a labeled field table."""
    parts = cron_expr.strip().split()
    if len(parts) != 5:
        return _colorize(f"Invalid expression: '{cron_expr}'", ANSI_RED, use_color)

    labels = ["Minute", "Hour", "Day(Month)", "Month", "Day(Week)"]
    lines = [_colorize("Cron Field Breakdown:", ANSI_BOLD, use_color)]
    for label, value in zip(labels, parts):
        lines.append(f"  {_colorize(label + ':', ANSI_CYAN, use_color):<20} {value}")
    return "\n".join(lines)


def format_validation_summary(cron_expr: str, use_color: bool = True) -> str:
    """Format a validation summary for the given cron expression."""
    result = validate(cron_expr)
    lines = []
    if result.is_valid:
        status = _colorize("✓ Valid", ANSI_GREEN, use_color)
    else:
        status = _colorize("✗ Invalid", ANSI_RED, use_color)
    lines.append(f"Status: {status}")
    if result.errors:
        lines.append(_colorize("Errors:", ANSI_RED, use_color))
        for err in result.errors:
            lines.append(f"  - {err}")
    if result.warnings:
        lines.append(_colorize("Warnings:", ANSI_YELLOW, use_color))
        for warn in result.warnings:
            lines.append(f"  - {warn}")
    return "\n".join(lines)


def format_full_report(
    cron_expr: str,
    next_runs: List[str],
    use_color: bool = True
) -> str:
    """Produce a full formatted report for a cron expression."""
    sections = []

    header = _colorize(f"Cron Expression: {cron_expr}", ANSI_BOLD, use_color)
    sections.append(header)

    description = humanize(cron_expr)
    sections.append(f"Description: {_colorize(description, ANSI_CYAN, use_color)}")

    sections.append(format_validation_summary(cron_expr, use_color))
    sections.append(format_cron_table(cron_expr, use_color))

    if next_runs:
        sections.append(_colorize("Next Executions:", ANSI_BOLD, use_color))
        for run in next_runs:
            sections.append(f"  {run}")

    return "\n".join(sections)
