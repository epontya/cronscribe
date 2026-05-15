"""Lint cron expressions for common mistakes and style issues."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class LintIssue:
    severity: str  # 'warning' | 'info'
    field: str
    message: str

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.field}: {self.message}"


@dataclass
class LintResult:
    expression: str
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == "warning" for i in self.issues)

    @property
    def is_clean(self) -> bool:
        return len(self.issues) == 0


def _lint_field(name: str, value: str, index: int) -> List[LintIssue]:
    issues: List[LintIssue] = []

    if value != "*" and value.startswith("0") and len(value) > 1 and not value.startswith("0/"):
        issues.append(LintIssue("warning", name, f"Leading zero in '{value}' may be unintended."))

    if "," in value and "/" in value:
        issues.append(LintIssue("warning", name, "Mixing list and step in one field is error-prone."))

    if value == "*/1":
        issues.append(LintIssue("info", name, "'*/1' is equivalent to '*'; prefer '*' for clarity."))

    if "-" in value and not value.startswith("*"):
        parts = value.split("-")
        try:
            lo, hi = int(parts[0]), int(parts[1].split("/")[0])
            if lo > hi:
                issues.append(LintIssue("warning", name, f"Range {lo}-{hi} has start greater than end."))
            if lo == hi:
                issues.append(LintIssue("info", name, f"Range {lo}-{hi} is a single value; use '{lo}' directly."))
        except (ValueError, IndexError):
            pass

    # Day-of-week: 7 is non-standard (some crons treat it as Sunday)
    if index == 4 and value == "7":
        issues.append(LintIssue("info", name, "'7' as Sunday is non-standard; prefer '0'."))

    return issues


def lint(expression: str) -> LintResult:
    """Lint a cron expression and return a LintResult with any issues found."""
    result = LintResult(expression=expression)
    parts = expression.strip().split()
    if len(parts) != 5:
        result.issues.append(LintIssue("warning", "expression", "Expected exactly 5 fields."))
        return result

    names = ["minute", "hour", "day-of-month", "month", "day-of-week"]
    for i, (name, value) in enumerate(zip(names, parts)):
        result.issues.extend(_lint_field(name, value, i))

    # Warn when both day-of-month and day-of-week are specified (non-wildcard)
    if parts[2] != "*" and parts[4] != "*":
        result.issues.append(
            LintIssue(
                "warning",
                "day-of-month/day-of-week",
                "Specifying both day-of-month and day-of-week is ambiguous; most crons use OR semantics.",
            )
        )

    return result
