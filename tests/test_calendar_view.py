"""Tests for cronscribe.calendar_view."""

from __future__ import annotations

from datetime import date

import pytest

from cronscribe.calendar_view import (
    _fires_on_day,
    format_calendar_view,
    month_calendar,
)


class TestFiresOnDay:
    def test_wildcard_fires_every_day(self):
        assert _fires_on_day("* * * * *", date(2024, 6, 15)) is True

    def test_specific_month_match(self):
        # Only fires in June
        assert _fires_on_day("0 9 * 6 *", date(2024, 6, 1)) is True

    def test_specific_month_no_match(self):
        assert _fires_on_day("0 9 * 6 *", date(2024, 7, 1)) is False

    def test_specific_dom_match(self):
        assert _fires_on_day("0 0 15 * *", date(2024, 6, 15)) is True

    def test_specific_dom_no_match(self):
        assert _fires_on_day("0 0 15 * *", date(2024, 6, 14)) is False

    def test_sunday_dow_zero(self):
        # 2024-06-02 is a Sunday; dow=0 in cron
        assert _fires_on_day("0 9 * * 0", date(2024, 6, 2)) is True

    def test_monday_dow_one(self):
        # 2024-06-03 is a Monday
        assert _fires_on_day("0 9 * * 1", date(2024, 6, 3)) is True

    def test_invalid_expression_returns_false(self):
        assert _fires_on_day("not a cron", date(2024, 6, 1)) is False

    def test_wrong_field_count_returns_false(self):
        assert _fires_on_day("* * *", date(2024, 6, 1)) is False


class TestMonthCalendar:
    def test_returns_list_of_weeks(self):
        weeks = month_calendar("* * * * *", 2024, 6)
        assert isinstance(weeks, list)
        assert all(len(w) == 7 for w in weeks)

    def test_first_day_of_june_2024_is_saturday(self):
        # June 2024: first day is Saturday (index 5 in Mo=0 scheme)
        weeks = month_calendar("* * * * *", 2024, 6)
        flat = [d for week in weeks for d in week if d is not None]
        assert flat[0] == date(2024, 6, 1)

    def test_none_padding_present(self):
        weeks = month_calendar("* * * * *", 2024, 6)
        flat_all = [d for week in weeks for d in week]
        assert None in flat_all

    def test_all_days_of_month_present(self):
        weeks = month_calendar("* * * * *", 2024, 2)  # Feb 2024 (leap)
        days = sorted(d.day for week in weeks for d in week if d is not None)
        assert days == list(range(1, 30))


class TestFormatCalendarView:
    def test_returns_string(self):
        result = format_calendar_view("* * * * *", 2024, 6, color=False)
        assert isinstance(result, str)

    def test_contains_month_name(self):
        result = format_calendar_view("0 9 * * 1", 2024, 6, color=False)
        assert "June" in result

    def test_contains_year(self):
        result = format_calendar_view("0 9 * * 1", 2024, 6, color=False)
        assert "2024" in result

    def test_contains_day_numbers(self):
        result = format_calendar_view("* * * * *", 2024, 6, color=False)
        assert " 1" in result
        assert "30" in result

    def test_no_color_flag_omits_ansi(self):
        result = format_calendar_view("* * * * *", 2024, 6, color=False)
        assert "\033[" not in result

    def test_color_flag_includes_ansi(self):
        result = format_calendar_view("* * * * *", 2024, 6, color=True)
        assert "\033[" in result

    def test_legend_present_no_color(self):
        result = format_calendar_view("* * * * *", 2024, 6, color=False)
        assert "expression fires" in result
