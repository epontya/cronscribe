"""Tests for cronscribe.timezone."""

from __future__ import annotations

from datetime import datetime, timezone as dt_timezone

import pytest

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    from backports.zoneinfo import ZoneInfo  # type: ignore

from cronscribe.timezone import (
    TimezoneResult,
    _resolve_zone,
    get_next_runs_in_timezone,
    format_timezone_report,
)

_BASE = datetime(2024, 1, 15, 12, 0, 0, tzinfo=ZoneInfo("UTC"))


class TestResolveZone:
    def test_valid_timezone_returns_zone_info(self):
        zone = _resolve_zone("America/New_York")
        assert zone is not None

    def test_invalid_timezone_returns_none(self):
        zone = _resolve_zone("Galaxy/Andromeda")
        assert zone is None

    def test_utc_resolves(self):
        zone = _resolve_zone("UTC")
        assert zone is not None


class TestGetNextRunsInTimezone:
    def test_returns_timezone_result(self):
        result = get_next_runs_in_timezone("0 * * * *", "UTC", base=_BASE)
        assert isinstance(result, TimezoneResult)

    def test_invalid_timezone_sets_flag(self):
        result = get_next_runs_in_timezone("0 * * * *", "Bad/Zone", base=_BASE)
        assert result.is_valid_tz is False
        assert result.error is not None
        assert "Bad/Zone" in result.error

    def test_valid_timezone_is_valid(self):
        result = get_next_runs_in_timezone("0 * * * *", "UTC", base=_BASE)
        assert result.is_valid_tz is True

    def test_correct_count_returned(self):
        result = get_next_runs_in_timezone("0 * * * *", "UTC", count=3, base=_BASE)
        assert len(result.utc_times) == 3
        assert len(result.local_times) == 3

    def test_default_count_is_five(self):
        result = get_next_runs_in_timezone("0 * * * *", "UTC", base=_BASE)
        assert len(result.utc_times) == 5

    def test_local_times_differ_from_utc_for_offset_zone(self):
        result = get_next_runs_in_timezone(
            "0 * * * *", "America/New_York", count=1, base=_BASE
        )
        assert result.utc_times[0] != result.local_times[0]

    def test_utc_zone_times_equal(self):
        result = get_next_runs_in_timezone(
            "0 * * * *", "UTC", count=1, base=_BASE
        )
        utc = result.utc_times[0].replace(tzinfo=None)
        loc = result.local_times[0].replace(tzinfo=None)
        assert utc == loc

    def test_expression_stored_on_result(self):
        result = get_next_runs_in_timezone("*/5 * * * *", "UTC", base=_BASE)
        assert result.expression == "*/5 * * * *"

    def test_timezone_stored_on_result(self):
        result = get_next_runs_in_timezone("0 * * * *", "Europe/London", base=_BASE)
        assert result.timezone == "Europe/London"


class TestFormatTimezoneReport:
    def test_error_result_shows_error_text(self):
        result = get_next_runs_in_timezone("0 * * * *", "Not/Real", base=_BASE)
        output = format_timezone_report(result)
        assert "Error" in output

    def test_valid_result_contains_expression(self):
        result = get_next_runs_in_timezone("0 * * * *", "UTC", base=_BASE)
        output = format_timezone_report(result)
        assert "0 * * * *" in output

    def test_valid_result_contains_timezone(self):
        result = get_next_runs_in_timezone("0 * * * *", "UTC", base=_BASE)
        output = format_timezone_report(result)
        assert "UTC" in output

    def test_output_has_correct_number_of_rows(self):
        result = get_next_runs_in_timezone("0 * * * *", "UTC", count=4, base=_BASE)
        output = format_timezone_report(result)
        # Each data row contains the year
        assert output.count("2024") >= 4
