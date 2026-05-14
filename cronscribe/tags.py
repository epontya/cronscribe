"""Tag-based categorization and filtering of cron expressions."""

from typing import Optional

_BUILTIN_TAGS: dict[str, list[str]] = {
    "frequent": [
        "* * * * *",
        "*/5 * * * *",
        "*/10 * * * *",
        "*/15 * * * *",
        "*/30 * * * *",
    ],
    "hourly": [
        "0 * * * *",
        "0 */2 * * *",
        "0 */4 * * *",
        "0 */6 * * *",
        "0 */12 * * *",
    ],
    "daily": [
        "0 0 * * *",
        "0 6 * * *",
        "0 12 * * *",
        "0 18 * * *",
        "0 0 * * 1-5",
    ],
    "weekly": [
        "0 0 * * 0",
        "0 0 * * 1",
        "0 0 * * 5",
        "0 0 * * 6",
    ],
    "monthly": [
        "0 0 1 * *",
        "0 0 15 * *",
        "0 0 L * *",
    ],
    "yearly": [
        "0 0 1 1 *",
        "0 0 1 6 *",
        "0 0 1 12 *",
    ],
    "business-hours": [
        "0 9 * * 1-5",
        "0 17 * * 1-5",
        "0 9-17 * * 1-5",
        "*/30 9-17 * * 1-5",
    ],
    "maintenance": [
        "0 2 * * 0",
        "0 3 * * *",
        "0 4 1 * *",
    ],
}

_user_tags: dict[str, list[str]] = {}


def get_tags_for(expression: str) -> list[str]:
    """Return all tags associated with the given cron expression."""
    expression = expression.strip()
    matched: list[str] = []
    combined = {**_BUILTIN_TAGS, **_user_tags}
    for tag, expressions in combined.items():
        if expression in expressions:
            matched.append(tag)
    return sorted(matched)


def get_expressions_for_tag(tag: str) -> list[str]:
    """Return all cron expressions associated with a given tag."""
    tag = tag.strip().lower()
    combined = {**_BUILTIN_TAGS, **_user_tags}
    return list(combined.get(tag, []))


def list_tags() -> list[str]:
    """Return all known tag names."""
    combined = {**_BUILTIN_TAGS, **_user_tags}
    return sorted(combined.keys())


def add_tag(tag: str, expression: str) -> None:
    """Associate a cron expression with a user-defined tag."""
    tag = tag.strip().lower()
    expression = expression.strip()
    if tag not in _user_tags:
        _user_tags[tag] = []
    if expression not in _user_tags[tag]:
        _user_tags[tag].append(expression)


def is_tagged(expression: str, tag: str) -> bool:
    """Check whether a cron expression has a specific tag."""
    return tag.strip().lower() in get_tags_for(expression.strip())


def clear_user_tags() -> None:
    """Remove all user-defined tags (used in testing)."""
    _user_tags.clear()
