"""Tests for cronscribe.overlap."""

from __future__ import annotations

from datetime import datetime

import pytest

from cronscribe.overlap import find_overlaps, format_overlap_report, OverlapResult


FIXED_BASE = datetime(2024, 1, 1, 0, 0, 0)


class TestFindOverlaps:
    def test_returns_overlap_result(self):
        result = find_overlaps("* * * * *", "* * * * *", from_dt=FIXED_BASE)
        assert isinstance(result, OverlapResult)

    def test_identical_expressions_all_overlap(self):
        result = find_overlaps("* * * * *", "* * * * *", count=10, from_dt=FIXED_BASE)
        assert result.is_valid
        assert result.overlap_count == 10

    def test_non_overlapping_expressions(self):
        # One fires at minute 0, the other at minute 30 each hour
        result = find_overlaps("0 * * * *", "30 * * * *", count=50, from_dt=FIXED_BASE)
        assert result.is_valid
        assert result.overlap_count == 0

    def test_partial_overlap(self):
        # Every hour vs every 2 hours — overlaps at every 2-hour mark
        result = find_overlaps("0 * * * *", "0 */2 * * *", count=48, from_dt=FIXED_BASE)
        assert result.is_valid
        assert result.has_overlaps
        # Every 2-hour expression fires fewer times, all should be subset
        for dt in result.overlapping_times:
            assert dt.minute == 0
            assert dt.hour % 2 == 0

    def test_invalid_expression_a_sets_error(self):
        result = find_overlaps("invalid", "* * * * *", from_dt=FIXED_BASE)
        assert not result.is_valid
        assert "A" in result.error
        assert result.overlap_count == 0

    def test_invalid_expression_b_sets_error(self):
        result = find_overlaps("* * * * *", "99 * * * *", from_dt=FIXED_BASE)
        assert not result.is_valid
        assert "B" in result.error

    def test_custom_labels_appear_in_result(self):
        result = find_overlaps(
            "* * * * *", "* * * * *",
            label_a="job1", label_b="job2",
            from_dt=FIXED_BASE,
        )
        assert result.label_a == "job1"
        assert result.label_b == "job2"

    def test_overlapping_times_are_sorted(self):
        result = find_overlaps("* * * * *", "* * * * *", count=20, from_dt=FIXED_BASE)
        assert result.overlapping_times == sorted(result.overlapping_times)


class TestFormatOverlapReport:
    def test_no_overlap_message(self):
        result = find_overlaps("0 * * * *", "30 * * * *", count=50, from_dt=FIXED_BASE)
        report = format_overlap_report(result)
        assert "No overlapping" in report

    def test_overlap_count_shown(self):
        result = find_overlaps("* * * * *", "* * * * *", count=5, from_dt=FIXED_BASE)
        report = format_overlap_report(result)
        assert "5" in report

    def test_expressions_shown_in_report(self):
        result = find_overlaps("0 9 * * 1", "0 9 * * 1", count=5, from_dt=FIXED_BASE)
        report = format_overlap_report(result)
        assert "0 9 * * 1" in report

    def test_error_report_on_invalid(self):
        result = find_overlaps("bad expr", "* * * * *", from_dt=FIXED_BASE)
        report = format_overlap_report(result)
        assert "Error" in report

    def test_datetime_format_in_report(self):
        result = find_overlaps("0 9 * * *", "0 9 * * *", count=3, from_dt=FIXED_BASE)
        report = format_overlap_report(result)
        # Should contain formatted datetimes like 2024-01-01 09:00
        assert "09:00" in report
