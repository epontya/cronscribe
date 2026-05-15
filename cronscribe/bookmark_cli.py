"""CLI handlers for the bookmark sub-command."""

from __future__ import annotations

import argparse
from typing import Optional

from cronscribe.bookmark import (
    add_bookmark,
    get_bookmark,
    list_bookmarks,
    remove_bookmark,
)


def add_bookmark_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the 'bookmark' sub-command."""
    p = subparsers.add_parser("bookmark", help="Manage named cron bookmarks")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--add", nargs=2, metavar=("NAME", "EXPR"),
                       help="Save a cron expression under NAME")
    group.add_argument("--get", metavar="NAME",
                       help="Retrieve the expression for NAME")
    group.add_argument("--remove", metavar="NAME",
                       help="Delete the bookmark named NAME")
    group.add_argument("--list", action="store_true",
                       help="List all saved bookmarks")


def handle_bookmark(args: argparse.Namespace) -> Optional[int]:
    """Dispatch bookmark sub-command actions."""
    if args.add:
        name, expr = args.add
        add_bookmark(name, expr)
        print(f"Bookmark '{name}' saved: {expr}")
        return 0

    if args.get:
        expr = get_bookmark(args.get)
        if expr is None:
            print(f"No bookmark named '{args.get}'.")
            return 1
        print(expr)
        return 0

    if args.remove:
        removed = remove_bookmark(args.remove)
        if removed:
            print(f"Bookmark '{args.remove}' removed.")
            return 0
        print(f"No bookmark named '{args.remove}'.")
        return 1

    if args.list:
        items = list_bookmarks()
        if not items:
            print("No bookmarks saved.")
            return 0
        width = max(len(n) for n, _ in items)
        print(f"{'NAME':<{width}}  EXPRESSION")
        print("-" * (width + 14))
        for name, expr in items:
            print(f"{name:<{width}}  {expr}")
        return 0

    return None
