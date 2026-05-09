"""Named cron templates for common scheduling patterns."""

from typing import Optional

# Template registry: name -> (cron_expression, description)
_TEMPLATES: dict[str, tuple[str, str]] = {
    "minutely": ("* * * * *", "Every minute"),
    "hourly": ("0 * * * *", "Every hour at minute 0"),
    "daily": ("0 0 * * *", "Every day at midnight"),
    "daily-noon": ("0 12 * * *", "Every day at noon"),
    "weekly": ("0 0 * * 0", "Every Sunday at midnight"),
    "weekly-monday": ("0 0 * * 1", "Every Monday at midnight"),
    "monthly": ("0 0 1 * *", "First day of every month at midnight"),
    "monthly-end": ("0 0 28 * *", "28th of every month at midnight"),
    "yearly": ("0 0 1 1 *", "Every January 1st at midnight"),
    "weekdays": ("0 9 * * 1-5", "Weekdays at 9am"),
    "weekends": ("0 10 * * 6,0", "Weekends at 10am"),
    "every-6h": ("0 */6 * * *", "Every 6 hours"),
    "every-12h": ("0 */12 * * *", "Every 12 hours"),
    "every-15m": ("*/15 * * * *", "Every 15 minutes"),
    "every-30m": ("*/30 * * * *", "Every 30 minutes"),
    "business-hours": ("0 9-17 * * 1-5", "Every hour during business hours on weekdays"),
    "nightly": ("0 2 * * *", "Every night at 2am"),
    "twice-daily": ("0 8,20 * * *", "Twice daily at 8am and 8pm"),
}


def get_template(name: str) -> Optional[tuple[str, str]]:
    """Return (cron_expression, description) for a template name, or None."""
    return _TEMPLATES.get(name.lower().strip())


def list_templates() -> list[dict]:
    """Return all templates as a list of dicts with name, expression, description."""
    return [
        {"name": name, "expression": expr, "description": desc}
        for name, (expr, desc) in sorted(_TEMPLATES.items())
    ]


def find_templates_by_expression(expression: str) -> list[str]:
    """Return template names whose cron expression matches the given expression."""
    expr = expression.strip()
    return [name for name, (e, _) in _TEMPLATES.items() if e == expr]


def add_template(name: str, expression: str, description: str) -> None:
    """Register a custom template at runtime."""
    _TEMPLATES[name.lower().strip()] = (expression, description)


def is_template(name: str) -> bool:
    """Return True if the given name is a registered template."""
    return name.lower().strip() in _TEMPLATES
