"""Diff two cron expressions and describe what changed."""

from typing import Optional

FIELD_NAMES = ["minute", "hour", "day-of-month", "month", "day-of-week"]


def _field_changed(a: str, b: str) -> bool:
    return a.strip() != b.strip()


def diff_expressions(expr_a: str, expr_b: str) -> dict:
    """Compare two cron expressions and return a diff summary.

    Returns a dict with:
      - 'fields': list of per-field dicts with 'name', 'before', 'after', 'changed'
      - 'changed_count': number of fields that differ
      - 'identical': bool
    """
    parts_a = expr_a.strip().split()
    parts_b = expr_b.strip().split()

    if len(parts_a) != 5 or len(parts_b) != 5:
        raise ValueError(
            "Both expressions must have exactly 5 fields. "
            f"Got {len(parts_a)} and {len(parts_b)}."
        )

    fields = []
    changed_count = 0
    for name, val_a, val_b in zip(FIELD_NAMES, parts_a, parts_b):
        changed = _field_changed(val_a, val_b)
        if changed:
            changed_count += 1
        fields.append({"name": name, "before": val_a, "after": val_b, "changed": changed})

    return {
        "fields": fields,
        "changed_count": changed_count,
        "identical": changed_count == 0,
    }


def format_diff(diff: dict, use_color: bool = True) -> str:
    """Format a diff result as a human-readable string."""
    if diff["identical"]:
        return "Expressions are identical."

    lines = [f"Changed fields ({diff['changed_count']}):\n"]
    for field in diff["fields"]:
        if not field["changed"]:
            continue
        name = field["name"]
        before = field["before"]
        after = field["after"]
        if use_color:
            line = f"  {name}: \033[31m{before}\033[0m → \033[32m{after}\033[0m"
        else:
            line = f"  {name}: {before} -> {after}"
        lines.append(line)
    return "\n".join(lines)
