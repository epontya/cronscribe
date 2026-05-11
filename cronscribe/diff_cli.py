"""CLI handler for the diff subcommand."""

import argparse
import sys

from cronscribe.diff import diff_expressions, format_diff
from cronscribe.validator import validate


def add_diff_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "diff",
        help="Compare two cron expressions and show what changed.",
    )
    p.add_argument("expr_a", help="First cron expression (quoted)")
    p.add_argument("expr_b", help="Second cron expression (quoted)")
    p.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI colour output.",
    )


def handle_diff(args: argparse.Namespace) -> int:
    """Handle the diff subcommand. Returns an exit code."""
    for label, expr in (("A", args.expr_a), ("B", args.expr_b)):
        result = validate(expr)
        if not result.valid:
            print(
                f"Error: expression {label} ({expr!r}) is invalid: "
                + "; ".join(result.errors),
                file=sys.stderr,
            )
            return 1

    try:
        diff = diff_expressions(args.expr_a, args.expr_b)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    use_color = not args.no_color
    print(format_diff(diff, use_color=use_color))
    return 0
