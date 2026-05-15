"""Tests for cronscribe.compare module."""

import pytest
from cronscribe.compare import compare, CompareResult


class TestCompare:
    def test_returns_compare_result(self):
        result = compare("* * * * *", "0 * * * *")
        assert isinstance(result, CompareResult)

    def test_identical_expressions_are_equal(self):
        result = compare("0 9 * * *", "0 9 * * *")
        assert result.are_equal is True
        assert result.diff_lines == []

    def test_different_expressions_not_equal(self):
        result = compare("0 9 * * *", "0 12 * * *")
        assert result.are_equal is False

    def test_diff_lines_populated_when_different(self):
        result = compare("0 9 * * *", "0 12 * * *")
        assert len(result.diff_lines) > 0

    def test_human_descriptions_populated(self):
        result = compare("0 0 * * *", "0 12 * * *")
        assert result.human_a != ""
        assert result.human_b != ""
        assert "(invalid)" not in result.human_a
        assert "(invalid)" not in result.human_b

    def test_invalid_expression_sets_error(self):
        result = compare("99 99 99 99 99", "0 0 * * *")
        assert not result.is_valid
        assert len(result.errors) > 0

    def test_invalid_shows_invalid_human(self):
        result = compare("99 99 99 99 99", "0 0 * * *")
        assert result.human_a == "(invalid)"

    def test_custom_labels_stored(self):
        result = compare("* * * * *", "0 * * * *", label_a="old", label_b="new")
        assert result.label_a == "old"
        assert result.label_b == "new"

    def test_natural_language_input(self):
        result = compare("every minute", "every hour")
        assert result.expr_a == "* * * * *"
        assert result.expr_b == "0 * * * *"
        assert result.are_equal is False

    def test_natural_language_same_meaning(self):
        result = compare("every minute", "every minute")
        assert result.are_equal is True

    def test_is_valid_true_for_good_inputs(self):
        result = compare("0 0 * * *", "0 12 * * *")
        assert result.is_valid is True
        assert result.errors == []
