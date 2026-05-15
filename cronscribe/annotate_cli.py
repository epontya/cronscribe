"""CLI handlers for the 'annotate' sub-command."""

from __future__ import annotations

import argparse

from cronscribe.annotate import (
    add_annotation,
    get_annotations,
    remove_annotation,
    list_annotated,
    clear_annotations,
)


def add_annotate_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("annotate", help="Manage notes attached to cron expressions")
    sub = p.add_subparsers(dest="annotate_cmd", required=True)

    # add
    pa = sub.add_parser("add", help="Add a note to an expression")
    pa.add_argument("expression", help="Cron expression")
    pa.add_argument("note", help="Note text")

    # list
    pl = sub.add_parser("list", help="List notes for an expression (or all)")
    pl.add_argument("expression", nargs="?", default=None, help="Cron expression (omit for all)")

    # remove
    pr = sub.add_parser("remove", help="Remove a note by index")
    pr.add_argument("expression", help="Cron expression")
    pr.add_argument("index", type=int, help="Zero-based index of the note to remove")

    # clear
    pc = sub.add_parser("clear", help="Clear all notes for an expression")
    pc.add_argument("expression", nargs="?", default=None, help="Cron expression (omit for all)")


def handle_annotate(args: argparse.Namespace) -> None:
    cmd = args.annotate_cmd

    if cmd == "add":
        add_annotation(args.expression, args.note)
        print(f"Note added to '{args.expression}'.")

    elif cmd == "list":
        if args.expression:
            notes = get_annotations(args.expression)
            if not notes:
                print(f"No annotations for '{args.expression}'.")
            else:
                for i, note in enumerate(notes):
                    print(f"  [{i}] {note}")
        else:
            all_ann = list_annotated()
            if not all_ann:
                print("No annotations stored.")
            else:
                for expr, notes in all_ann.items():
                    print(f"{expr}")
                    for i, note in enumerate(notes):
                        print(f"  [{i}] {note}")

    elif cmd == "remove":
        ok = remove_annotation(args.expression, args.index)
        if ok:
            print(f"Removed note [{args.index}] from '{args.expression}'.")
        else:
            print(f"No note at index {args.index} for '{args.expression}'.")

    elif cmd == "clear":
        clear_annotations(args.expression or None)
        target = f"'{args.expression}'" if args.expression else "all expressions"
        print(f"Cleared annotations for {target}.")
