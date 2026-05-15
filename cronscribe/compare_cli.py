"""CLI handler for the compare subcommand."""

import argparse
from cronscribe.compare import compare


def add_compare_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'compare' subcommand."""
    p = subparsers.add_parser(
        "compare",
        help="Compare two cron expressions or schedule descriptions",
    )
    p.add_argument("input_a", help="First schedule description or cron expression")
    p.add_argument("input_b", help="Second schedule description or cron expression")
    p.add_argument("--label-a", default="A", help="Label for the first expression")
    p.add_argument("--label-b", default="B", help="Label for the second expression")
    p.add_argument("--no-color", action="store_true", default=False)


def handle_compare(args: argparse.Namespace) -> int:
    """Handle the compare subcommand and return an exit code."""
    result = compare(
        args.input_a,
        args.input_b,
        label_a=args.label_a,
        label_b=args.label_b,
    )

    if not result.is_valid:
        for err in result.errors:
            print(f"[error] {err}")
        return 1

    print(f"[{result.label_a}] {result.expr_a}")
    print(f"      => {result.human_a}")
    print(f"[{result.label_b}] {result.expr_b}")
    print(f"      => {result.human_b}")
    print()

    if result.are_equal:
        print("Result: expressions are IDENTICAL.")
    else:
        print("Result: expressions DIFFER.")
        if result.diff_lines:
            print()
            print("Field-level diff:")
            for line in result.diff_lines:
                print(f"  {line}")

    return 0
