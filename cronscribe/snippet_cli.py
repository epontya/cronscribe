"""CLI handlers for snippet subcommands."""

from __future__ import annotations

import argparse
from typing import Any

from cronscribe.snippet import (
    add_snippet,
    find_snippets_by_expression,
    get_snippet,
    list_snippets,
    remove_snippet,
)


def add_snippet_subparser(subparsers: Any) -> None:
    sp = subparsers.add_parser("snippet", help="Manage named cron snippets")
    sub = sp.add_subparsers(dest="snippet_action")

    sub.add_parser("list", help="List all snippets")

    get_p = sub.add_parser("get", help="Look up a snippet by name")
    get_p.add_argument("name", help="Snippet name")

    add_p = sub.add_parser("add", help="Add a new snippet")
    add_p.add_argument("name", help="Snippet name")
    add_p.add_argument("expression", help="Cron expression")
    add_p.add_argument("--description", default="", help="Human-readable description")

    rm_p = sub.add_parser("remove", help="Remove a user snippet")
    rm_p.add_argument("name", help="Snippet name")

    rev_p = sub.add_parser("reverse", help="Find snippets by cron expression")
    rev_p.add_argument("expression", help="Cron expression to look up")


def handle_snippet(args: argparse.Namespace) -> None:
    action = getattr(args, "snippet_action", None)

    if action == "list" or action is None:
        rows = list_snippets()
        if not rows:
            print("No snippets defined.")
            return
        print(f"{'Name':<20} {'Expression':<20} Description")
        print("-" * 60)
        for name, expr, desc in rows:
            print(f"{name:<20} {expr:<20} {desc}")

    elif action == "get":
        result = get_snippet(args.name)
        if result is None:
            print(f"Snippet '{args.name}' not found.")
        else:
            expr, desc = result
            print(f"Expression : {expr}")
            print(f"Description: {desc}")

    elif action == "add":
        add_snippet(args.name, args.expression, args.description)
        print(f"Snippet '{args.name}' saved.")

    elif action == "remove":
        removed = remove_snippet(args.name)
        if removed:
            print(f"Snippet '{args.name}' removed.")
        else:
            print(f"Snippet '{args.name}' not found (or is a built-in).")

    elif action == "reverse":
        matches = find_snippets_by_expression(args.expression)
        if not matches:
            print(f"No snippets found for expression '{args.expression}'.")
        else:
            for name, desc in matches:
                print(f"{name}: {desc}")
