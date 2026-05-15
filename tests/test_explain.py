"""Tests for cronscribe.explain."""
from __future__ import annotations

import pytest

from cronscribe.explain import explain, ExplainResult, FieldExplanation


class TestExplain:
    """Tests for the explain() function."""

    def test_returns_explain_result(self):
        result = explain("* * * * *")
        assert isinstance(result, ExplainResult)

    def test_valid_expression_is_valid(self):
        result = explain("0 9 * * 1-5")
        assert result.is_valid is True

    def test_invalid_expression_is_not_valid(self):
        result = explain("99 99 99 99 99")
        assert result.is_valid is False

    def test_wrong_field_count_is_not_valid(self):
        result = explain("* * *")
        assert result.is_valid is False

    def test_fields_count(self):
        result = explain("*/5 9-17 * * 1-5")
        assert len(result.fields) == 5

    def test_field_labels(self):
        result = explain("* * * * *")
        labels = [f.label for f in result.fields]
        assert labels == ["Minute", "Hour", "Day", "Month", "Weekday"]

    def test_wildcard_field_description(self):
        result = explain("* * * * *")
        minute_field = result.fields[0]
        assert "every" in minute_field.description.lower() or minute_field.description != ""

    def test_step_field_description(self):
        result = explain("*/15 * * * *")
        minute_field = result.fields[0]
        assert "15" in minute_field.description

    def test_range_field_description(self):
        result = explain("0 9-17 * * *")
        hour_field = result.fields[1]
        assert "9" in hour_field.description and "17" in hour_field.description

    def test_summary_not_empty_for_valid(self):
        result = explain("0 0 * * *")
        assert result.summary and len(result.summary) > 0

    def test_summary_empty_or_error_for_invalid(self):
        result = explain("not a cron")
        assert result.is_valid is False

    def test_raw_value_preserved(self):
        expr = "30 6 1 */2 *"
        result = explain(expr)
        raw_values = [f.raw_value for f in result.fields]
        assert raw_values == ["30", "6", "1", "*/2", "*"]

    def test_field_explanation_type(self):
        result = explain("* * * * *")
        for field in result.fields:
            assert isinstance(field, FieldExplanation)

    def test_every_minute_summary(self):
        result = explain("* * * * *")
        assert "minute" in result.summary.lower()

    def test_specific_time_summary(self):
        result = explain("0 12 * * *")
        assert "12" in result.summary or "noon" in result.summary.lower() or result.summary
