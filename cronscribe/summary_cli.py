"""CLI integration for the summary feature."""

import argparse

from cronscribe.summary import summarize, format_summary


def add_summary_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the 'summary' subcommand."""
    parser = subparsers.add_parser(
        "summary",
        help="Show a full summary for a cron expression",
    )
    parser.add_argument(
        "expression",
        help="Cron expression to summarise (quote if it contains spaces)",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=3,
        metavar="N",
        help="Number of upcoming runs to include (default: 3)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI colour output",
    )


def handle_summary(args: argparse.Namespace) -> None:
    """Execute the summary subcommand."""
    result = summarize(args.expression, run_count=args.runs)
    output = format_summary(result, color=not args.no_color)
    print(output)
