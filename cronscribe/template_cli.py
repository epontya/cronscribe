"""CLI handlers for template-related commands."""

from cronscribe.templates import (
    get_template,
    list_templates,
    find_templates_by_expression,
    is_template,
)
from cronscribe.formatter import format_cron_table, _colorize


def handle_list_templates(color: bool = True) -> str:
    """Return a formatted table of all available templates."""
    templates = list_templates()
    lines = []
    header = _colorize("Available Templates:", "bold", color)
    lines.append(header)
    lines.append("")
    col_w = max(len(t["name"]) for t in templates) + 2
    for t in templates:
        name_col = _colorize(t["name"].ljust(col_w), "cyan", color)
        expr_col = _colorize(t["expression"].ljust(16), "yellow", color)
        lines.append(f"  {name_col} {expr_col} {t['description']}")
    return "\n".join(lines)


def handle_template_lookup(name: str, color: bool = True) -> str:
    """Look up a template by name and return its cron expression and description."""
    result = get_template(name)
    if result is None:
        msg = f"Template '{name}' not found."
        return _colorize(msg, "red", color)
    expression, description = result
    lines = [
        _colorize(f"Template: {name}", "bold", color),
        f"  Expression : {_colorize(expression, 'yellow', color)}",
        f"  Description: {description}",
    ]
    return "\n".join(lines)


def handle_reverse_template_lookup(expression: str, color: bool = True) -> str:
    """Find template names matching a given cron expression."""
    names = find_templates_by_expression(expression)
    if not names:
        msg = f"No templates found for expression '{expression}'."
        return _colorize(msg, "yellow", color)
    header = _colorize(f"Templates matching '{expression}':", "bold", color)
    items = "\n".join(f"  - {_colorize(n, 'cyan', color)}" for n in sorted(names))
    return f"{header}\n{items}"
