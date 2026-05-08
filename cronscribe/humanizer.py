"""Converts cron expressions back into human-readable descriptions."""

from typing import Optional

DAY_NAMES = [
    "Sunday", "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday"
]

MONTH_NAMES = [
    "", "January", "February", "March", "April",
    "May", "June", "July", "August", "September",
    "October", "November", "December"
]


def _describe_field(value: str, unit: str, names: Optional[list] = None) -> str:
    """Describe a single cron field in plain English."""
    if value == "*":
        return f"every {unit}"
    if value.startswith("*/"):
        step = value[2:]
        return f"every {step} {unit}s"
    if "-" in value and "," not in value:
        start, end = value.split("-", 1)
        if names:
            start_name = names[int(start)] if start.isdigit() else start
            end_name = names[int(end)] if end.isdigit() else end
            return f"{start_name} through {end_name}"
        return f"{start} through {end}"
    if "," in value:
        parts = value.split(",")
        if names:
            parts = [names[int(p)] if p.isdigit() else p for p in parts]
        if len(parts) == 2:
            return f"{parts[0]} and {parts[1]}"
        return ", ".join(parts[:-1]) + f", and {parts[-1]}"
    if names and value.isdigit():
        return names[int(value)]
    return value


def humanize(cron_expr: str) -> str:
    """Convert a cron expression to a human-readable description."""
    parts = cron_expr.strip().split()
    if len(parts) != 5:
        return f"Invalid cron expression: '{cron_expr}'"

    minute, hour, dom, month, dow = parts

    # Simple well-known patterns
    if cron_expr == "* * * * *":
        return "Every minute"
    if minute == "0" and hour == "*" and dom == "*" and month == "*" and dow == "*":
        return "Every hour at minute 0"
    if minute == "0" and hour == "0" and dom == "*" and month == "*" and dow == "*":
        return "Every day at midnight"
    if minute == "0" and hour == "12" and dom == "*" and month == "*" and dow == "*":
        return "Every day at noon"

    desc_parts = []

    # Time description
    if minute == "*" and hour == "*":
        desc_parts.append("every minute")
    elif minute.startswith("*/") and hour == "*":
        desc_parts.append(f"every {minute[2:]} minutes")
    elif hour != "*" and minute != "*":
        desc_parts.append(f"at {hour.zfill(2)}:{minute.zfill(2)}")
    elif hour != "*":
        desc_parts.append(f"at hour {_describe_field(hour, 'hour')}")
    else:
        desc_parts.append(f"at minute {_describe_field(minute, 'minute')}")

    if dom != "*":
        desc_parts.append(f"on day {_describe_field(dom, 'day')} of the month")
    if month != "*":
        desc_parts.append(f"in {_describe_field(month, 'month', MONTH_NAMES)}")
    if dow != "*":
        desc_parts.append(f"on {_describe_field(dow, 'weekday', DAY_NAMES)}")

    return ", ".join(desc_parts).capitalize()
