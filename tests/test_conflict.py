"""Tests for cronscribe.conflict."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from cronscribe.conflict import ConflictResult, find_conflicts, format_conflict_report


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

EVERY_MINUTE = "* * * * *"
EVERY_HOUR = "0 * * * *"
NOON_DAILY = "0 12 * * *"
MIDNIGHT_DAILY = "0 0 * * *"


class TestFindConflicts:
    def test_returns_conflict_result(self):
        result = find_conflicts([EVERY_MINUTE, EVERY_HOUR])
        assert isinstance(result, ConflictResult)

    def test_single_expression_returns_no_conflicts(self):
        result = find_conflicts([EVERY_MINUTE])
        assert not result.has_conflicts()
        assert result.conflict_count() == 0

    def test_empty_list_returns_no_conflicts(self):
        result = find_conflicts([])
        assert not result.has_conflicts()

    def test_identical_expressions_all_conflict(self):
        result = find_conflicts([EVERY_HOUR, EVERY_HOUR], count=10)
        assert result.has_conflicts()

    def test_non_overlapping_expressions_no_conflict(self):
        # noon vs midnight — never the same minute
        result = find_conflicts([NOON_DAILY, MIDNIGHT_DAILY], count=30)
        assert not result.has_conflicts()

    def test_every_minute_conflicts_with_every_hour(self):
        # every-hour fires at :00, which every-minute also fires at
        result = find_conflicts([EVERY_MINUTE, EVERY_HOUR], count=60)
        assert result.has_conflicts()

    def test_conflict_tuples_have_three_elements(self):
        result = find_conflicts([EVERY_HOUR, EVERY_HOUR], count=5)
        for item in result.conflicts:
            assert len(item) == 3

    def test_expressions_stored_on_result(self):
        exprs = [NOON_DAILY, MIDNIGHT_DAILY]
        result = find_conflicts(exprs)
        assert result.expressions == exprs

    def test_checked_count_positive_for_valid_expressions(self):
        result = find_conflicts([EVERY_HOUR, NOON_DAILY], count=10)
        assert result.checked_count > 0

    def test_bad_expression_does_not_raise(self):
        # An invalid expression should be silently skipped
        result = find_conflicts(["not-valid", EVERY_HOUR], count=5)
        assert isinstance(result, ConflictResult)

    def test_no_duplicate_pairs_checked(self):
        # Three expressions: pairs AB, AC, BC — 3 unique pairs only
        result = find_conflicts([EVERY_HOUR, EVERY_HOUR, NOON_DAILY], count=5)
        pairs = {(a, b) for a, b, _ in result.conflicts}
        # Each pair appears at most once (no (B,A) after (A,B))
        for a, b in pairs:
            assert (b, a) not in pairs


class TestFormatConflictReport:
    def test_returns_string(self):
        result = find_conflicts([NOON_DAILY, MIDNIGHT_DAILY], count=5)
        assert isinstance(format_conflict_report(result), str)

    def test_no_conflict_message_when_clean(self):
        result = find_conflicts([NOON_DAILY, MIDNIGHT_DAILY], count=5)
        report = format_conflict_report(result, use_color=False)
        assert "No scheduling conflicts found" in report

    def test_conflict_count_shown_when_conflicts_exist(self):
        result = find_conflicts([EVERY_HOUR, EVERY_HOUR], count=3)
        report = format_conflict_report(result, use_color=False)
        assert "Conflicts found" in report

    def test_no_color_omits_ansi(self):
        result = find_conflicts([EVERY_HOUR, EVERY_HOUR], count=3)
        report = format_conflict_report(result, use_color=False)
        assert "\033[" not in report

    def test_color_includes_ansi(self):
        result = find_conflicts([EVERY_HOUR, EVERY_HOUR], count=3)
        report = format_conflict_report(result, use_color=True)
        assert "\033[" in report
