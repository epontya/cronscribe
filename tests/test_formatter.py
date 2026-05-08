"""Tests for cronscribe.formatter module."""

import pytest
from cronscribe.formatter import (
    format_cron_table,
    format_validation_summary,
    format_full_report,
    _colorize,
    ANSI_GREEN,
    ANSI_RESET,
)


class TestColorize:
    def test_with_color(self):
        result = _colorize("hello", ANSI_GREEN, use_color=True)
        assert ANSI_GREEN in result
        assert ANSI_RESET in result
        assert "hello" in result

    def test_without_color(self):
        result = _colorize("hello", ANSI_GREEN, use_color=False)
        assert result == "hello"


class TestFormatCronTable:
    def test_valid_expression(self):
        result = format_cron_table("0 12 * * *", use_color=False)
        assert "Minute" in result
        assert "Hour" in result
        assert "Day(Month)" in result
        assert "Month" in result
        assert "Day(Week)" in result

    def test_values_present(self):
        result = format_cron_table("30 9 1 6 *", use_color=False)
        assert "30" in result
        assert "9" in result
        assert "1" in result
        assert "6" in result

    def test_invalid_expression(self):
        result = format_cron_table("bad expr", use_color=False)
        assert "Invalid" in result


class TestFormatValidationSummary:
    def test_valid_cron(self):
        result = format_validation_summary("* * * * *", use_color=False)
        assert "Valid" in result

    def test_invalid_cron(self):
        result = format_validation_summary("99 * * * *", use_color=False)
        assert "Invalid" in result
        assert "Error" in result


class TestFormatFullReport:
    def test_contains_expression(self):
        result = format_full_report("0 0 * * *", [], use_color=False)
        assert "0 0 * * *" in result

    def test_contains_description(self):
        result = format_full_report("0 0 * * *", [], use_color=False)
        assert "midnight" in result.lower() or "Description" in result

    def test_contains_next_runs(self):
        runs = ["2024-01-01 00:00", "2024-01-02 00:00"]
        result = format_full_report("0 0 * * *", runs, use_color=False)
        assert "2024-01-01 00:00" in result
        assert "Next Executions" in result

    def test_empty_next_runs(self):
        result = format_full_report("0 0 * * *", [], use_color=False)
        assert "Next Executions" not in result

    def test_includes_field_table(self):
        result = format_full_report("*/5 * * * *", [], use_color=False)
        assert "Minute" in result
