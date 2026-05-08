"""Tests for the parser and validator modules."""

import pytest
from cronscribe.parser import parse
from cronscribe.validator import validate


class TestParser:
    def test_every_minute(self):
        assert parse("every minute") == "* * * * *"

    def test_every_hour(self):
        assert parse("every hour") == "0 * * * *"

    def test_every_day_midnight(self):
        assert parse("every day at midnight") == "0 0 * * *"

    def test_every_day_noon(self):
        assert parse("every day at noon") == "0 12 * * *"

    def test_every_weekday(self):
        assert parse("every weekday") == "0 0 * * 1-5"

    def test_every_weekend(self):
        assert parse("every weekend") == "0 0 * * 0,6"

    def test_specific_time_am(self):
        assert parse("every day at 9am") == "0 9 * * *"

    def test_specific_time_pm(self):
        assert parse("every day at 3pm") == "0 15 * * *"

    def test_specific_time_with_minutes(self):
        assert parse("every day at 10:30am") == "30 10 * * *"

    def test_interval_minutes(self):
        assert parse("every 15 minutes") == "*/15 * * * *"

    def test_interval_hours(self):
        assert parse("every 6 hours") == "0 */6 * * *"

    def test_unrecognized_returns_none(self):
        assert parse("run on Tuesdays at noon-ish") is None

    def test_case_insensitive(self):
        assert parse("Every Minute") == "* * * * *"


class TestValidator:
    def test_valid_expression(self):
        result = validate("0 9 * * 1-5")
        assert result.valid is True
        assert result.error is None

    def test_invalid_field_count(self):
        result = validate("0 9 * *")
        assert result.valid is False
        assert "5 fields" in result.error

    def test_minute_out_of_range(self):
        result = validate("60 * * * *")
        assert result.valid is False

    def test_hour_out_of_range(self):
        result = validate("0 25 * * *")
        assert result.valid is False

    def test_step_value(self):
        result = validate("*/15 * * * *")
        assert result.valid is True

    def test_list_value(self):
        result = validate("0 0 * * 0,6")
        assert result.valid is True

    def test_range_value(self):
        result = validate("0 0 * * 1-5")
        assert result.valid is True

    def test_parser_output_is_always_valid(self):
        descriptions = [
            "every minute", "every hour", "every day at midnight",
            "every day at 9am", "every 30 minutes", "every 4 hours",
            "every weekday", "every weekend", "every month",
        ]
        for desc in descriptions:
            cron = parse(desc)
            assert cron is not None, f"parse returned None for: {desc}"
            result = validate(cron)
            assert result.valid, f"Invalid cron '{cron}' for: {desc} — {result.error}"
