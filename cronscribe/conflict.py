"""Detect scheduling conflicts between multiple cron expressions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from cronscribe.preview import get_next_executions


@dataclass
class ConflictResult:
    expressions: List[str]
    conflicts: List[Tuple[str, str, str]]  # (expr_a, expr_b, timestamp)
    checked_count: int

    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0

    def conflict_count(self) -> int:
        return len(self.conflicts)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"ConflictResult(expressions={self.expressions!r}, "
            f"conflicts={len(self.conflicts)}, checked={self.checked_count})"
        )


def find_conflicts(
    expressions: List[str],
    count: int = 50,
) -> ConflictResult:
    """Find scheduling conflicts (same fire time) across a list of cron expressions."""
    if len(expressions) < 2:
        return ConflictResult(expressions=expressions, conflicts=[], checked_count=0)

    schedules: dict[str, set[str]] = {}
    for expr in expressions:
        try:
            runs = get_next_executions(expr, n=count)
            schedules[expr] = set(runs)
        except Exception:
            schedules[expr] = set()

    conflicts: List[Tuple[str, str, str]] = []
    seen_pairs: set[frozenset] = set()

    for i, expr_a in enumerate(expressions):
        for j, expr_b in enumerate(expressions):
            if j <= i:
                continue
            pair_key: frozenset = frozenset({expr_a, expr_b})
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)
            shared = schedules.get(expr_a, set()) & schedules.get(expr_b, set())
            for ts in sorted(shared):
                conflicts.append((expr_a, expr_b, ts))

    total_checked = sum(len(v) for v in schedules.values())
    return ConflictResult(
        expressions=expressions,
        conflicts=conflicts,
        checked_count=total_checked,
    )


def format_conflict_report(result: ConflictResult, use_color: bool = True) -> str:
    """Format a human-readable conflict report."""
    RED = "\033[31m" if use_color else ""
    GREEN = "\033[32m" if use_color else ""
    BOLD = "\033[1m" if use_color else ""
    RESET = "\033[0m" if use_color else ""

    lines = [f"{BOLD}Conflict Report{RESET}"]
    lines.append(f"Expressions checked : {len(result.expressions)}")
    lines.append(f"Timestamps sampled  : {result.checked_count}")

    if not result.has_conflicts():
        lines.append(f"{GREEN}No scheduling conflicts found.{RESET}")
        return "\n".join(lines)

    lines.append(f"{RED}Conflicts found: {result.conflict_count()}{RESET}")
    for expr_a, expr_b, ts in result.conflicts:
        lines.append(f"  {ts}  |  {expr_a!r}  vs  {expr_b!r}")

    return "\n".join(lines)
