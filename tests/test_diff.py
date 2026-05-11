"""Tests for cronscribe.diff module."""

import pytest

from cronscribe.diff import diff_expressions, format_diff


class TestDiffExpressions:
    def test_identical_expressions(self):
        result = diff_expressions("* * * * *", "* * * * *")
        assert result["identical"] is True
        assert result["changed_count"] == 0

    def test_single_field_changed(self):
        result = diff_expressions("0 * * * *", "30 * * * *")
        assert result["identical"] is False
        assert result["changed_count"] == 1
        minute_field = result["fields"][0]
        assert minute_field["name"] == "minute"
        assert minute_field["before"] == "0"
        assert minute_field["after"] == "30"
        assert minute_field["changed"] is True

    def test_multiple_fields_changed(self):
        result = diff_expressions("0 9 * * 1", "0 17 * * 5")
        assert result["changed_count"] == 2
        changed = [f for f in result["fields"] if f["changed"]]
        names = [f["name"] for f in changed]
        assert "hour" in names
        assert "day-of-week" in names

    def test_all_fields_changed(self):
        result = diff_expressions("0 0 1 1 0", "59 23 31 12 6")
        assert result["changed_count"] == 5

    def test_unchanged_fields_marked_correctly(self):
        result = diff_expressions("0 12 * * *", "0 12 1 * *")
        unchanged = [f for f in result["fields"] if not f["changed"]]
        unchanged_names = [f["name"] for f in unchanged]
        assert "minute" in unchanged_names
        assert "hour" in unchanged_names

    def test_invalid_field_count_raises(self):
        with pytest.raises(ValueError, match="exactly 5 fields"):
            diff_expressions("* * *", "* * * * *")

    def test_whitespace_tolerance(self):
        result = diff_expressions("0  *  *  *  *", "0 * * * *")
        assert result["identical"] is True


class TestFormatDiff:
    def test_identical_message(self):
        diff = diff_expressions("* * * * *", "* * * * *")
        output = format_diff(diff, use_color=False)
        assert "identical" in output.lower()

    def test_changed_fields_shown(self):
        diff = diff_expressions("0 9 * * *", "0 17 * * *")
        output = format_diff(diff, use_color=False)
        assert "hour" in output
        assert "9" in output
        assert "17" in output

    def test_no_color_uses_arrow(self):
        diff = diff_expressions("0 9 * * *", "0 17 * * *")
        output = format_diff(diff, use_color=False)
        assert "->" in output
        assert "\033[" not in output

    def test_color_uses_ansi(self):
        diff = diff_expressions("0 9 * * *", "0 17 * * *")
        output = format_diff(diff, use_color=True)
        assert "\033[" in output

    def test_unchanged_fields_not_shown(self):
        diff = diff_expressions("0 9 * * *", "0 17 * * *")
        output = format_diff(diff, use_color=False)
        assert "minute" not in output
