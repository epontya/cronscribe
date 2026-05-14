"""CLI handlers for macro-related subcommands."""

from cronscribe.macro import get_macro, list_macros, find_macros_by_expression


def handle_list_macros(args, out=None) -> None:
    """Print all available macros."""
    import sys
    out = out or sys.stdout
    macros = list_macros()
    if not macros:
        out.write("No macros available.\n")
        return
    out.write(f"{'Name':<25} {'Description':<45} Expressions\n")
    out.write("-" * 90 + "\n")
    for name, desc, exprs in macros:
        expr_str = ", ".join(exprs)
        out.write(f"{name:<25} {desc:<45} {expr_str}\n")


def handle_macro_lookup(args, out=None) -> None:
    """Look up a macro by name and print its expressions."""
    import sys
    out = out or sys.stdout
    result = get_macro(args.name)
    if result is None:
        out.write(f"Unknown macro: '{args.name}'\n")
        return
    desc, exprs = result
    out.write(f"Macro   : {args.name}\n")
    out.write(f"Description: {desc}\n")
    out.write("Expressions:\n")
    for expr in exprs:
        out.write(f"  {expr}\n")


def handle_reverse_macro_lookup(args, out=None) -> None:
    """Find macros that contain a given cron expression."""
    import sys
    out = out or sys.stdout
    matches = find_macros_by_expression(args.expression)
    if not matches:
        out.write(f"No macros found containing expression: '{args.expression}'\n")
        return
    out.write(f"Macros containing '{args.expression}':\n")
    for name in matches:
        out.write(f"  {name}\n")
