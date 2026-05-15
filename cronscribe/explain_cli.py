"""CLI handlers for the explain feature."""
from __future__ import annotations

import argparse

from cronscribe.explain import explain


def add_explain_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register the 'explain' sub-command."""
    p = subparsers.add_parser(
        "explain",
        help="Show a human-readable breakdown of each cron field.",
    )
    p.add_argument(
        "expression",
        help="A valid 5-field cron expression, e.g. '*/5 9-17 * * 1-5'.",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI colour output.",
    )


def handle_explain(args: argparse.Namespace) -> int:
    """Execute the explain command and print results.

    Returns an exit code (0 = success, 1 = invalid expression).
    """
    result = explain(args.expression)

    if not result.is_valid:
        print(f"Error: '{args.expression}' is not a valid cron expression.")
        return 1

    use_color = not getattr(args, "no_color", False)

    header = "Cron Expression Breakdown"
    sep = "-" * len(header)
    if use_color:
        header = f"\033[1;36m{header}\033[0m"

    print(header)
    print(sep)
    print(f"  Expression : {args.expression}")
    print(f"  Summary    : {result.summary}")
    print()

    field_label_width = max(len(f.label) for f in result.fields)
    for field in result.fields:
        label = field.label.ljust(field_label_width)
        raw = field.raw_value.ljust(10)
        desc = field.description
        if use_color:
            raw = f"\033[33m{raw}\033[0m"
            desc = f"\033[37m{desc}\033[0m"
        print(f"  {label}  {raw}  {desc}")

    return 0
