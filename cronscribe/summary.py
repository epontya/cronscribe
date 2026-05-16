"""Generate a human-readable summary report for a cron expression."""

from dataclasses import dataclass, field
from typing import List, Optional

from cronscribe.validator import validate
from cronscribe.humanizer import humanize
from cronscribe.next_run import get_next_runs
from cronscribe.lint import lint


@dataclass
class SummaryResult:
    expression: str
    is_valid: bool
    human_description: Optional[str]
    next_runs: List[str]
    lint_warnings: List[str]
    lint_infos: List[str]
    error: Optional[str] = None

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"SummaryResult(expression={self.expression!r}, "
            f"valid={self.is_valid}, warnings={len(self.lint_warnings)})"
        )


def summarize(expression: str, run_count: int = 3) -> SummaryResult:
    """Build a SummaryResult for the given cron expression."""
    validation = validate(expression)
    if not validation.valid:
        return SummaryResult(
            expression=expression,
            is_valid=False,
            human_description=None,
            next_runs=[],
            lint_warnings=[],
            lint_infos=[],
            error="; ".join(validation.errors),
        )

    description = humanize(expression)
    next_result = get_next_runs(expression, count=run_count)
    next_runs = [
        dt.strftime("%Y-%m-%d %H:%M") for dt in next_result.datetimes
    ] if next_result.valid else []

    lint_result = lint(expression)
    warnings = [str(i) for i in lint_result.issues if i.level == "warning"]
    infos = [str(i) for i in lint_result.issues if i.level == "info"]

    return SummaryResult(
        expression=expression,
        is_valid=True,
        human_description=description,
        next_runs=next_runs,
        lint_warnings=warnings,
        lint_infos=infos,
    )


def format_summary(result: SummaryResult, color: bool = True) -> str:
    """Render a SummaryResult as a printable string."""
    lines: List[str] = []
    lines.append(f"Expression : {result.expression}")
    lines.append(f"Valid      : {'yes' if result.is_valid else 'no'}")

    if not result.is_valid:
        lines.append(f"Error      : {result.error}")
        return "\n".join(lines)

    lines.append(f"Description: {result.human_description}")

    if result.next_runs:
        lines.append("Next runs  :")
        for run in result.next_runs:
            lines.append(f"  - {run}")

    if result.lint_warnings:
        lines.append("Warnings   :")
        for w in result.lint_warnings:
            lines.append(f"  ! {w}")

    if result.lint_infos:
        lines.append("Info       :")
        for i in result.lint_infos:
            lines.append(f"  i {i}")

    return "\n".join(lines)
