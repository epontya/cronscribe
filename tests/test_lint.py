"""Tests for cronscribe.lint and cronscribe.lint_cli."""

import io
import types
import pytest

from cronscribe.lint import lint, LintIssue, LintResult
from cronscribe.lint_cli import handle_lint


# ---------------------------------------------------------------------------
# lint() unit tests
# ---------------------------------------------------------------------------


class TestLint:
    def test_clean_expression_returns_no_issues(self):
        result = lint("0 9 * * 1")
        assert result.is_clean
        assert not result.has_warnings

    def test_wrong_field_count(self):
        result = lint("* * *")
        assert not result.is_clean
        assert any("5 fields" in i.message for i in result.issues)

    def test_star_slash_one_is_info(self):
        result = lint("*/1 * * * *")
        issues = [i for i in result.issues if i.field == "minute"]
        assert any("*/1" in i.message for i in issues)
        assert all(i.severity == "info" for i in issues)

    def test_leading_zero_warning(self):
        result = lint("05 * * * *")
        issues = [i for i in result.issues if i.field == "minute"]
        assert any("Leading zero" in i.message for i in issues)
        assert issues[0].severity == "warning"

    def test_inverted_range_warning(self):
        result = lint("50-10 * * * *")
        issues = [i for i in result.issues if i.field == "minute"]
        assert any("start greater than end" in i.message for i in issues)

    def test_single_value_range_info(self):
        result = lint("5-5 * * * *")
        issues = [i for i in result.issues if i.field == "minute"]
        assert any("single value" in i.message for i in issues)

    def test_list_and_step_mixed_warning(self):
        result = lint("1,2/5 * * * *")
        issues = [i for i in result.issues if i.field == "minute"]
        assert any("Mixing list and step" in i.message for i in issues)

    def test_day_of_week_7_info(self):
        result = lint("0 0 * * 7")
        issues = [i for i in result.issues if i.field == "day-of-week"]
        assert any("non-standard" in i.message for i in issues)

    def test_both_dom_and_dow_warning(self):
        result = lint("0 9 15 * 1")
        issues = [i for i in result.issues if "day-of-month" in i.field]
        assert any("ambiguous" in i.message for i in issues)

    def test_wildcard_dom_and_dow_no_ambiguity(self):
        result = lint("0 9 * * 1")
        assert not any("ambiguous" in i.message for i in result.issues)

    def test_lint_result_str(self):
        issue = LintIssue(severity="warning", field="minute", message="Test msg")
        assert "WARNING" in str(issue)
        assert "minute" in str(issue)


# ---------------------------------------------------------------------------
# handle_lint() CLI handler tests
# ---------------------------------------------------------------------------


def _make_args(expression: str, strict: bool = False):
    args = types.SimpleNamespace(expression=expression, strict=strict)
    return args


class TestLintCLI:
    def test_clean_expression_exit_zero(self):
        buf = io.StringIO()
        code = handle_lint(_make_args("0 9 * * 1"), out=buf)
        assert code == 0
        assert "No issues" in buf.getvalue()

    def test_info_only_exit_zero_even_strict(self):
        buf = io.StringIO()
        code = handle_lint(_make_args("*/1 * * * *", strict=True), out=buf)
        assert code == 0

    def test_warning_strict_exit_one(self):
        buf = io.StringIO()
        code = handle_lint(_make_args("05 * * * *", strict=True), out=buf)
        assert code == 1

    def test_warning_not_strict_exit_zero(self):
        buf = io.StringIO()
        code = handle_lint(_make_args("05 * * * *", strict=False), out=buf)
        assert code == 0

    def test_output_contains_expression(self):
        buf = io.StringIO()
        handle_lint(_make_args("50-10 * * * *"), out=buf)
        assert "50-10 * * * *" in buf.getvalue()

    def test_summary_line_present(self):
        buf = io.StringIO()
        handle_lint(_make_args("05 * * * *"), out=buf)
        assert "warning" in buf.getvalue()
