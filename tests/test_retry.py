"""Tests for cronscribe.retry."""

from __future__ import annotations

import pytest

from cronscribe.retry import (
    RetryPolicy,
    RetrySchedule,
    _offset_expression,
    build_retry_schedule,
    format_retry_schedule,
)


class TestOffsetExpression:
    def test_simple_offset(self):
        result = _offset_expression("0 2 * * *", 10)
        assert result == "10 2 * * *"

    def test_offset_crosses_hour(self):
        result = _offset_expression("55 2 * * *", 10)
        assert result == "5 3 * * *"

    def test_offset_crosses_midnight(self):
        result = _offset_expression("50 23 * * *", 15)
        assert result == "5 0 * * *"

    def test_wildcard_minute_returns_none(self):
        assert _offset_expression("* * * * *", 5) is None

    def test_step_minute_returns_none(self):
        assert _offset_expression("*/5 * * * *", 5) is None

    def test_wildcard_hour_small_offset(self):
        result = _offset_expression("10 * * * *", 5)
        assert result == "15 * * * *"

    def test_wildcard_hour_large_offset_returns_none(self):
        assert _offset_expression("10 * * * *", 70) is None

    def test_wrong_field_count_returns_none(self):
        assert _offset_expression("0 2 *", 5) is None


class TestBuildRetrySchedule:
    def test_returns_retry_schedule(self):
        result = build_retry_schedule("0 9 * * 1")
        assert isinstance(result, RetrySchedule)

    def test_valid_expression_is_valid(self):
        result = build_retry_schedule("0 9 * * 1")
        assert result.is_valid is True
        assert result.error is None

    def test_invalid_expression_is_not_valid(self):
        result = build_retry_schedule("99 99 * * *")
        assert result.is_valid is False
        assert result.error is not None

    def test_default_policy_three_attempts(self):
        result = build_retry_schedule("0 6 * * *")
        assert len(result.expressions) == 3

    def test_base_expression_is_first(self):
        result = build_retry_schedule("0 6 * * *")
        assert result.expressions[0] == "0 6 * * *"

    def test_retries_offset_correctly(self):
        policy = RetryPolicy(max_attempts=3, delay_minutes=10)
        result = build_retry_schedule("0 6 * * *", policy)
        assert result.expressions[1] == "10 6 * * *"
        assert result.expressions[2] == "20 6 * * *"

    def test_custom_policy_respected(self):
        policy = RetryPolicy(max_attempts=2, delay_minutes=15)
        result = build_retry_schedule("30 8 * * 1-5", policy)
        assert len(result.expressions) == 2
        assert result.expressions[1] == "45 8 * * 1-5"

    def test_wildcard_minute_stops_early(self):
        result = build_retry_schedule("* * * * *")
        # base is included but retries cannot be computed
        assert result.expressions == ["* * * * *"]


class TestFormatRetrySchedule:
    def test_invalid_shows_error(self):
        schedule = RetrySchedule(
            base_expression="bad",
            policy=RetryPolicy(),
            is_valid=False,
            error="Invalid expression",
        )
        output = format_retry_schedule(schedule)
        assert "Error" in output

    def test_valid_shows_base_and_retries(self):
        policy = RetryPolicy(max_attempts=3, delay_minutes=5)
        result = build_retry_schedule("0 12 * * *", policy)
        output = format_retry_schedule(result)
        assert "Base:" in output
        assert "Retry 1:" in output
        assert "Retry 2:" in output
