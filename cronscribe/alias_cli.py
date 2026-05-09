"""CLI helpers for alias lookup and listing integrated into cronscribe."""

from __future__ import annotations

from cronscribe.aliases import (
    list_aliases,
    resolve_alias,
    get_aliases_for,
    is_alias,
)
from cronscribe.formatter import format_cron_table
from cronscribe.validator import validate


def handle_alias_lookup(name: str, color: bool = True) -> str:
    """Look up a single alias and return a formatted result string."""
    if not is_alias(name):
        return f"Unknown alias: '{name}'\nRun with --list-aliases to see all available aliases."

    expr = resolve_alias(name)
    result = validate(expr)
    lines = [f"Alias : {name}", f"Cron  : {expr}"]
    if result.valid:
        lines.append(format_cron_table(expr, color=color))
    else:
        lines.append("Validation errors: " + "; ".join(result.errors))
    return "\n".join(lines)


def handle_list_aliases(color: bool = True) -> str:
    """Return a formatted table of all known aliases."""
    pairs = list_aliases()
    col_w = max(len(a) for a, _ in pairs) + 2
    header = f"{'Alias':<{col_w}}  Cron Expression"
    separator = "-" * (col_w + 20)
    rows = [header, separator]
    for alias, expr in pairs:
        rows.append(f"{alias:<{col_w}}  {expr}")
    return "\n".join(rows)


def handle_reverse_lookup(cron_expr: str) -> str:
    """Find aliases that match a given cron expression."""
    aliases = get_aliases_for(cron_expr)
    if not aliases:
        return f"No aliases found for: '{cron_expr}'"
    lines = [f"Aliases for '{cron_expr}':"]
    for a in aliases:
        lines.append(f"  {a}")
    return "\n".join(lines)
