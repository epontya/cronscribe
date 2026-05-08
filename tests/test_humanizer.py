"""Tests for cronscribe.humanizer module."""

import pytest
from cronscribe.humanizer import humanize, _describe_field


class TestDescribeField:
    def test_wildcard(self):
        assert _describe_field("*", "minute") == "every minute"

    def test_step(self):
        assert _describe_field("*/5", "minute") == "every 5 minutes"

    def test_range_no_names(self):
        assert _describe_field("1-5", "day") == "1 through 5"

    def test_range_with_names(self):
        from cronscribe.humanizer import DAY_NAMES
        result = _describe_field("1-5", "weekday", DAY_NAMES)
        assert result == "Monday through Friday"

    def test_list_two(self):
        assert _describe_field("1,3", "day") == "1 and 3"

    def test_list_many(self):
        assert _describe_field("1,3,5", "day") == "1, 3, and 5"

    def test_named_month(self):
        from cronscribe.humanizer import MONTH_NAMES
        assert _describe_field("3", "month", MONTH_NAMES) == "March"


class TestHumanize:
    def test_every_minute(self):
        assert humanize("* * * * *") == "Every minute"

    def test_every_hour(self):
        assert humanize("0 * * * *") == "Every hour at minute 0"

    def test_every_day_midnight(self):
        assert humanize("0 0 * * *") == "Every day at midnight"

    def test_every_day_noon(self):
        assert humanize("0 12 * * *") == "Every day at noon"

    def test_specific_time(self):
        result = humanize("30 9 * * *")
        assert "09:30" in result

    def test_weekday(self):
        result = humanize("0 9 * * 1")
        assert "Monday" in result

    def test_monthly(self):
        result = humanize("0 0 1 * *")
        assert "day 1" in result

    def test_specific_month(self):
        result = humanize("0 0 * 6 *")
        assert "June" in result

    def test_every_5_minutes(self):
        result = humanize("*/5 * * * *")
        assert "5" in result and "minute" in result.lower()

    def test_invalid_expression(self):
        result = humanize("not valid")
        assert "Invalid" in result

    def test_invalid_too_many_parts(self):
        result = humanize("* * * * * *")
        assert "Invalid" in result

    def test_weekday_range(self):
        result = humanize("0 8 * * 1-5")
        assert "Monday" in result
        assert "Friday" in result

    def test_multiple_months(self):
        result = humanize("0 0 * 1,7 *")
        assert "January" in result
        assert "July" in result
