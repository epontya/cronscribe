"""CLI handlers for tag-based cron expression queries."""

import argparse
from cronscribe.tags import (
    get_tags_for,
    get_expressions_for_tag,
    list_tags,
    add_tag,
    is_tagged,
)


def add_tag_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'tag' subcommand."""
    p = subparsers.add_parser("tag", help="Tag-based cron expression queries")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--list", action="store_true", help="List all available tags"
    )
    group.add_argument(
        "--for-expression",
        metavar="EXPR",
        help="Show tags for a cron expression",
    )
    group.add_argument(
        "--for-tag",
        metavar="TAG",
        help="Show expressions associated with a tag",
    )
    group.add_argument(
        "--add",
        nargs=2,
        metavar=("TAG", "EXPR"),
        help="Associate EXPR with TAG",
    )
    p.set_defaults(func=handle_tag)


def handle_tag(args: argparse.Namespace) -> None:
    """Dispatch tag subcommand actions."""
    if args.list:
        tags = list_tags()
        if not tags:
            print("No tags defined.")
        else:
            print("Available tags:")
            for tag in tags:
                print(f"  {tag}")

    elif args.for_expression:
        expr = args.for_expression
        tags = get_tags_for(expr)
        if not tags:
            print(f"No tags found for: {expr}")
        else:
            print(f"Tags for '{expr}':")
            for tag in tags:
                print(f"  {tag}")

    elif args.for_tag:
        tag = args.for_tag
        expressions = get_expressions_for_tag(tag)
        if not expressions:
            print(f"No expressions found for tag: {tag}")
        else:
            print(f"Expressions tagged '{tag}':")
            for expr in expressions:
                print(f"  {expr}")

    elif args.add:
        tag, expr = args.add
        add_tag(tag, expr)
        print(f"Tagged '{expr}' as '{tag}'.")
