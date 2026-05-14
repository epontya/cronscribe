"""Tests for cronscribe.schedule_range."""

import pytest
from datetime import datetime
from cronscribe.schedule_range import expression_for_range, expressions_for_weekday_range


class TestExpressionForRange:
    def _dt(self, hour: int, minute: int = 0) -> datetime:
        return datetime(2024, 1, 1, hour, minute)

    def test_full_day_range(self):
        expr, desc = expression_for_range(self._dt(0), self._dt(23), 60)
        assert expr == "*/60 * * * *"
        assert "all day" in desc

    def test_simple_hour_window(self):
        expr, desc = expression_for_range(self._dt(9), self._dt(17), 30)
        assert expr == "*/30 9-17 * * *"
        assert "09:00" in desc
        assert "17:00" in desc

    def test_single_hour(self):
        expr, desc = expression_for_range(self._dt(12), self._dt(12), 15)
        assert expr == "*/15 12 * * *"

    def test_interval_of_one(self):
        expr, _ = expression_for_range(self._dt(8), self._dt(10), 1)
        assert expr.startswith("* ")

    def test_midnight_spanning_range(self):
        expr, desc = expression_for_range(self._dt(22), self._dt(2), 30)
        # hours should include 22,23,0,1,2
        hour_part = expr.split()[1]
        hours = [int(h) for h in hour_part.split(",")]
        assert 22 in hours
        assert 0 in hours
        assert 2 in hours
        assert "spans midnight" in desc

    def test_invalid_interval_too_small(self):
        with pytest.raises(ValueError, match="interval_minutes"):
            expression_for_range(self._dt(9), self._dt(17), 0)

    def test_invalid_interval_too_large(self):
        with pytest.raises(ValueError, match="interval_minutes"):
            expression_for_range(self._dt(9), self._dt(17), 60)

    def test_returns_five_fields(self):
        expr, _ = expression_for_range(self._dt(6), self._dt(18), 20)
        assert len(expr.split()) == 5


class TestExpressionsForWeekdayRange:
    def test_mon_to_fri(self):
        expr, desc = expressions_for_weekday_range(1, 5, hour=9, minute=0)
        assert expr == "0 9 * * 1-5"
        assert "Mon" in desc
        assert "Fri" in desc

    def test_single_day(self):
        expr, desc = expressions_for_weekday_range(3, 3, hour=14, minute=30)
        assert expr == "30 14 * * 3"

    def test_wraps_weekend(self):
        expr, desc = expressions_for_weekday_range(5, 1, hour=10)
        # Fri=5, Sat=6, Sun=0, Mon=1
        dow_part = expr.split()[4]
        days = [int(d) for d in dow_part.split(",")]
        assert 5 in days
        assert 6 in days
        assert 0 in days
        assert 1 in days

    def test_invalid_dow_low(self):
        with pytest.raises(ValueError, match="Day-of-week"):
            expressions_for_weekday_range(-1, 5)

    def test_invalid_dow_high(self):
        with pytest.raises(ValueError, match="Day-of-week"):
            expressions_for_weekday_range(0, 7)

    def test_hour_and_minute_in_expression(self):
        expr, _ = expressions_for_weekday_range(1, 5, hour=18, minute=45)
        minute_part, hour_part = expr.split()[:2]
        assert minute_part == "45"
        assert hour_part == "18"

    def test_returns_five_fields(self):
        expr, _ = expressions_for_weekday_range(1, 5)
        assert len(expr.split()) == 5
