"""Command-line interface for cronscribe."""

import argparse
import sys

from cronscribe.parser import parse
from cronscribe.validator import validate
from cronscribe.preview import format_preview


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="cronscribe",
        description="Convert human-readable schedule descriptions into cron expressions.",
    )
    parser.add_argument(
        "description",
        nargs="?",
        help="Human-readable schedule description (e.g. 'every day at noon')",
    )
    parser.add_argument(
        "--validate",
        metavar="CRON",
        help="Validate an existing cron expression",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Show next execution times for the resulting cron expression",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        metavar="N",
        help="Number of upcoming executions to preview (default: 5)",
    )
    return parser


def _handle_validate_mode(args: argparse.Namespace) -> int:
    """Handle --validate mode. Returns exit code."""
    result = validate(args.validate)
    if result.is_valid:
        print(f"✓ '{args.validate}' is a valid cron expression.")
        if args.preview:
            print(format_preview(args.validate, count=args.count))
        return 0
    else:
        print(f"✗ Invalid cron expression: {args.validate}")
        for error in result.errors:
            print(f"  - {error}")
        return 1


def run(argv: list[str] | None = None) -> int:
    """Main entry point for the CLI. Returns exit code."""
    arg_parser = build_parser()
    args = arg_parser.parse_args(argv)

    # Validate-only mode
    if args.validate:
        return _handle_validate_mode(args)

    if not args.description:
        arg_parser.print_help()
        return 0

    cron_expr = parse(args.description)
    if cron_expr is None:
        print(f"✗ Could not parse description: '{args.description}'")
        return 1

    result = validate(cron_expr)
    if not result.is_valid:
        print(f"✗ Generated invalid cron expression '{cron_expr}':")
        for error in result.errors:
            print(f"  - {error}")
        return 1

    print(f"✓ Cron expression: {cron_expr}")
    if args.preview:
        print(format_preview(cron_expr, count=args.count))
    return 0


def main() -> None:
    """Entry point for console_scripts."""
    sys.exit(run())


if __name__ == "__main__":
    main()
