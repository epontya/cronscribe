"""CLI integration for the conflict-detection feature."""

from __future__ import annotations

import argparse
from typing import List

from cronscribe.conflict import find_conflicts, format_conflict_report


def add_conflict_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "conflict",
        help="Detect scheduling conflicts between cron expressions",
    )
    p.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPR",
        help="Two or more cron expressions to compare",
    )
    p.add_argument(
        "--count",
        type=int,
        default=50,
        metavar="N",
        help="Number of upcoming executions to sample per expression (default: 50)",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI colour output",
    )


def handle_conflict(args: argparse.Namespace) -> None:
    expressions: List[str] = args.expressions
    count: int = args.count
    use_color: bool = not args.no_color

    if len(expressions) < 2:
        print("Error: at least two expressions are required.")
        return

    result = find_conflicts(expressions, count=count)
    print(format_conflict_report(result, use_color=use_color))
