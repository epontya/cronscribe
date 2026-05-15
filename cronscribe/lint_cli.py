"""CLI handler for the lint subcommand."""

from cronscribe.lint import lint


def add_lint_subparser(subparsers) -> None:
    """Register the 'lint' subcommand on an argparse subparsers object."""
    p = subparsers.add_parser(
        "lint",
        help="Lint a cron expression for common issues.",
    )
    p.add_argument("expression", help="Cron expression to lint (quote it).")
    p.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if any warnings are found.",
    )


def handle_lint(args, out=None) -> int:
    """Handle the lint subcommand.  Returns an exit code."""
    import sys

    out = out or sys.stdout

    result = lint(args.expression)

    if result.is_clean:
        out.write(f"✓ No issues found in: {args.expression}\n")
        return 0

    out.write(f"Lint results for: {args.expression}\n")
    for issue in result.issues:
        icon = "⚠" if issue.severity == "warning" else "ℹ"
        out.write(f"  {icon} {issue}\n")

    warnings = sum(1 for i in result.issues if i.severity == "warning")
    infos = sum(1 for i in result.issues if i.severity == "info")
    out.write(f"\n{warnings} warning(s), {infos} info(s).\n")

    if args.strict and result.has_warnings:
        return 1
    return 0
