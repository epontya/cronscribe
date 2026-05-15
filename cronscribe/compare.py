"""Compare two human-readable schedule descriptions or cron expressions."""

from dataclasses import dataclass, field
from typing import List, Optional

from cronscribe.parser import parse
from cronscribe.validator import validate
from cronscribe.humanizer import humanize
from cronscribe.diff import diff_expressions, format_diff


@dataclass
class CompareResult:
    expr_a: str
    expr_b: str
    label_a: str
    label_b: str
    human_a: str
    human_b: str
    are_equal: bool
    diff_lines: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.errors


def compare(
    input_a: str,
    input_b: str,
    label_a: str = "A",
    label_b: str = "B",
) -> CompareResult:
    """Compare two schedule inputs (natural language or cron expressions)."""
    errors: List[str] = []

    expr_a = parse(input_a) or input_a
    expr_b = parse(input_b) or input_b

    val_a = validate(expr_a)
    val_b = validate(expr_b)

    if not val_a.is_valid:
        errors.append(f"{label_a}: {'; '.join(val_a.errors)}")
    if not val_b.is_valid:
        errors.append(f"{label_b}: {'; '.join(val_b.errors)}")

    human_a = humanize(expr_a) if val_a.is_valid else "(invalid)"
    human_b = humanize(expr_b) if val_b.is_valid else "(invalid)"

    are_equal = expr_a.strip() == expr_b.strip()

    diff_lines: List[str] = []
    if val_a.is_valid and val_b.is_valid and not are_equal:
        changes = diff_expressions(expr_a, expr_b)
        diff_lines = format_diff(changes).splitlines()

    return CompareResult(
        expr_a=expr_a,
        expr_b=expr_b,
        label_a=label_a,
        label_b=label_b,
        human_a=human_a,
        human_b=human_b,
        are_equal=are_equal,
        diff_lines=diff_lines,
        errors=errors,
    )
