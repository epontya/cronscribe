"""CLI handlers for the watchlist sub-command."""

from __future__ import annotations

import argparse
from pathlib import Path

from cronscribe.watchlist import add_watch, get_watch, list_watches, remove_watch, clear_watchlist
from cronscribe.preview import get_next_executions


def add_watchlist_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("watch", help="Manage a watchlist of named cron expressions")
    sub = p.add_subparsers(dest="watch_cmd", required=True)

    add_p = sub.add_parser("add", help="Add an expression to the watchlist")
    add_p.add_argument("name", help="Label for the entry")
    add_p.add_argument("expression", help="Cron expression (5 fields)")

    rm_p = sub.add_parser("remove", help="Remove an entry from the watchlist")
    rm_p.add_argument("name", help="Label to remove")

    get_p = sub.add_parser("get", help="Look up a single watchlist entry")
    get_p.add_argument("name")
    get_p.add_argument("--preview", type=int, default=0, metavar="N",
                       help="Show next N execution times")

    sub.add_parser("list", help="List all watchlist entries")
    sub.add_parser("clear", help="Clear the entire watchlist")


def handle_watchlist(args: argparse.Namespace) -> None:
    cmd = args.watch_cmd

    if cmd == "add":
        add_watch(args.name, args.expression)
        print(f"Watching '{args.name}': {args.expression}")

    elif cmd == "remove":
        removed = remove_watch(args.name)
        if removed:
            print(f"Removed '{args.name}' from watchlist.")
        else:
            print(f"'{args.name}' not found in watchlist.")

    elif cmd == "get":
        expr = get_watch(args.name)
        if expr is None:
            print(f"No watchlist entry named '{args.name}'.")
            return
        print(f"{args.name}: {expr}")
        if args.preview > 0:
            times = get_next_executions(expr, count=args.preview)
            for t in times:
                print(f"  -> {t}")

    elif cmd == "list":
        entries = list_watches()
        if not entries:
            print("Watchlist is empty.")
            return
        print(f"{'Name':<20} Expression")
        print("-" * 40)
        for name, expr in entries:
            print(f"{name:<20} {expr}")

    elif cmd == "clear":
        clear_watchlist()
        print("Watchlist cleared.")
