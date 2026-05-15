"""Tests for the cronscribe preview module."""

import pytest
from datetime import datetime
from cronscribe.preview import get_next_executions, format_preview, _matches_field


FIXED_START = datetime(2024, 1, 15, 12, 0, 0)  # Monday noon


class TestMatchesField:
    def test_wildcard(self):
        assert _matches_field(5, "*") is True

    def test_exact_match(self):
        assert _matches_field(5, "5") is True
        assert _matches_field(5, "3") is False

    def test_range(self):
        assert _matches_field(5, "3-7") is True
        assert _matches_field(2, "3-7") is False

    def test_list(self):
        assert _matches_field(5, "1,3,5") is True
        assert _matches_field(4, "1,3,5") is False

    def test_step(self):
        assert _matches_field(0, "*/15") is True
        assert _matches_field(15, "*/15") is True
        assert _matches_field(30, "*/15") is True
        assert _matches_field(7, "*/15") is False


class TestGetNextExecutions:
    def test_every_minute_returns_correct_count(self):
        results = get_next_executions("* * * * *", count=5, start=FIXED_START)
        assert len(results) == 5

    def test_every_minute_increments_by_one(self):
        results = get_next_executions("* * * * *", count=3, start=FIXED_START)
        assert results[0] == datetime(2024, 1, 15, 12, 1)
        assert results[1] == datetime(2024, 1, 15, 12, 2)
        assert results[2] == datetime(2024, 1, 15, 12, 3)

    def test_hourly_cron(self):
        results = get_next_executions("0 * * * *", count=3, start=FIXED_START)
        assert results[0] == datetime(2024, 1, 15, 13, 0)
        assert results[1] == datetime(2024, 1, 15, 14, 0)
        assert results[2] == datetime(2024, 1, 15, 15, 0)

    def test_daily_midnight(self):
        results = get_next_executions("0 0 * * *", count=2, start=FIXED_START)
        assert results[0] == datetime(2024, 1, 16, 0, 0)
        assert results[1] == datetime(2024, 1, 17, 0, 0)

    def test_every_15_minutes(self):
        results = get_next_executions("*/15 * * * *", count=4, start=FIXED_START)
        assert results[0] == datetime(2024, 1, 15, 12, 15)
        assert results[1] == datetime(2024, 1, 15, 12, 30)
        assert results[2] == datetime(2024, 1, 15, 12, 45)
        assert results[3] == datetime(2024, 1, 15, 13, 0)

    def test_weekly_cron(self):
        # Every Monday at 9:00 AM; FIXED_START is Monday 2024-01-15 at noon,
        # so the next occurrence should be the following Monday.
        results = get_next_executions("0 9 * * 1", count=2, start=FIXED_START)
        assert results[0] == datetime(2024, 1, 22, 9, 0)
        assert results[1] == datetime(2024, 1, 29, 9, 0)

    def test_invalid_count_too_low(self):
        with pytest.raises(ValueError, match="count must be between"):
            get_next_executions("* * * * *", count=0)

    def test_invalid_count_too_high(self):
        with pytest.raises(ValueError, match="count must be between"):
            get_next_executions("* * * * *", count=21)

    def test_invalid_cron_expression(self):
        with pytest.raises(ValueError, match="Invalid cron expression"):
            get_next_executions("* * * *", count=1)


class TestFormatPreview:
    def test_format_preview_contains_expression(self):
        output = format_preview("0 0 * * *", count=3, start=FIXED_START)
        assert "0 0 * * *" in output
