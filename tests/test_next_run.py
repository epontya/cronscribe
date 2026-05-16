"""Tests for cronscribe.next_run."""

from __future__ import annotations

from datetime import datetime

import pytest

from cronscribe.next_run import NextRunResult, format_next_runs, get_next_runs


FIXED = datetime(2024, 1, 15, 12, 0, 0)  # Monday noon


class TestGetNextRuns:
    def test_returns_next_run_result(self):
        result = get_next_runs("* * * * *", count=3, after=FIXED)
        assert isinstance(result, NextRunResult)

    def test_valid_expression_is_valid(self):
        result = get_next_runs("0 9 * * *", count=5, after=FIXED)
        assert result.is_valid is True
        assert result.error is None

    def test_correct_number_of_runs_returned(self):
        result = get_next_runs("* * * * *", count=5, after=FIXED)
        assert len(result.runs) == 5

    def test_custom_count(self):
        result = get_next_runs("* * * * *", count=10, after=FIXED)
        assert len(result.runs) == 10

    def test_runs_are_datetimes(self):
        result = get_next_runs("0 0 * * *", count=3, after=FIXED)
        for dt in result.runs:
            assert isinstance(dt, datetime)

    def test_runs_are_after_base(self):
        result = get_next_runs("* * * * *", count=5, after=FIXED)
        for dt in result.runs:
            assert dt > FIXED

    def test_runs_are_in_order(self):
        result = get_next_runs("* * * * *", count=5, after=FIXED)
        for a, b in zip(result.runs, result.runs[1:]):
            assert a < b

    def test_invalid_expression_returns_invalid_result(self):
        result = get_next_runs("99 99 99 99 99", count=3, after=FIXED)
        assert result.is_valid is False
        assert result.runs == []
        assert result.error is not None

    def test_invalid_expression_preserves_expression(self):
        expr = "99 * * * *"
        result = get_next_runs(expr, after=FIXED)
        assert result.expression == expr

    def test_count_too_low_raises(self):
        with pytest.raises(ValueError):
            get_next_runs("* * * * *", count=0)

    def test_count_too_high_raises(self):
        with pytest.raises(ValueError):
            get_next_runs("* * * * *", count=51)

    def test_defaults_to_now_when_after_is_none(self):
        result = get_next_runs("* * * * *", count=1)
        assert result.is_valid is True
        assert len(result.runs) == 1


class TestFormatNextRuns:
    def test_valid_result_contains_header(self):
        result = get_next_runs("0 9 * * *", count=3, after=FIXED)
        output = format_next_runs(result)
        assert "0 9 * * *" in output
        assert "3 run" in output

    def test_valid_result_lists_each_run(self):
        result = get_next_runs("* * * * *", count=3, after=FIXED)
        output = format_next_runs(result)
        lines = [l for l in output.splitlines() if l.strip().startswith(("1.", "2.", "3."))]
        assert len(lines) == 3

    def test_invalid_result_shows_error(self):
        result = NextRunResult(
            expression="bad expr",
            runs=[],
            is_valid=False,
            error="minute out of range",
        )
        output = format_next_runs(result)
        assert "Invalid" in output
        assert "minute out of range" in output

    def test_custom_format(self):
        result = get_next_runs("0 0 1 * *", count=2, after=FIXED)
        output = format_next_runs(result, fmt="%d/%m/%Y")
        # Should not contain time component
        assert ":" not in output.split("\n", 1)[1]
