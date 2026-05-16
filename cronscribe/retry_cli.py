"""CLI handlers for the retry subcommand."""

from __future__ import annotations

import argparse

from cronscribe.retry import RetryPolicy, build_retry_schedule, format_retry_schedule


def add_retry_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "retry",
        help="Generate retry schedules for a cron expression",
    )
    parser.add_argument("expression", help="Base cron expression")
    parser.add_argument(
        "--attempts",
        type=int,
        default=3,
        metavar="N",
        help="Maximum retry attempts (default: 3)",
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=5,
        metavar="MINUTES",
        help="Delay between retries in minutes (default: 5)",
    )
    parser.add_argument(
        "--jitter",
        type=int,
        default=0,
        metavar="MINUTES",
        help="Additional jitter minutes added per retry (default: 0)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )


def handle_retry(args: argparse.Namespace) -> None:
    policy = RetryPolicy(
        max_attempts=args.attempts,
        delay_minutes=args.delay,
        jitter_minutes=args.jitter,
    )
    schedule = build_retry_schedule(args.expression, policy)

    if getattr(args, "json", False):
        import json
        payload = {
            "base_expression": schedule.base_expression,
            "is_valid": schedule.is_valid,
            "error": schedule.error,
            "policy": {
                "max_attempts": policy.max_attempts,
                "delay_minutes": policy.delay_minutes,
                "jitter_minutes": policy.jitter_minutes,
            },
            "expressions": schedule.expressions,
        }
        print(json.dumps(payload, indent=2))
    else:
        print(format_retry_schedule(schedule))
