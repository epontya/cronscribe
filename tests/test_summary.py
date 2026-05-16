"""Tests for cronscribe.summary and cronscribe.summary_cli."""

import argparse
from unittest.mock import patch

import pytest

from cronscribe.summary import summarize, format_summary, SummaryResult
from cronscribe.summary_cli import add_summary_subparser, handle_summary


class TestSummarize:
    def test_returns_summary_result(self):
        result = summarize("0 * * * *")
        assert isinstance(result, SummaryResult)

    def test_valid_expression_is_valid(self):
        result = summarize("0 * * * *")
        assert result.is_valid is True
        assert result.error is None

    def test_invalid_expression_is_not_valid(self):
        result = summarize("not a cron")
        assert result.is_valid is False
        assert result.error is not None
        assert len(result.error) > 0

    def test_human_description_populated(self):
        result = summarize("0 12 * * *")
        assert result.human_description is not None
        assert len(result.human_description) > 0

    def test_next_runs_count_matches_request(self):
        result = summarize("0 * * * *", run_count=5)
        assert len(result.next_runs) == 5

    def test_next_runs_default_count(self):
        result = summarize("0 * * * *")
        assert len(result.next_runs) == 3

    def test_next_runs_empty_for_invalid(self):
        result = summarize("bad expression")
        assert result.next_runs == []

    def test_next_runs_format(self):
        result = summarize("0 9 * * 1")
        for run in result.next_runs:
            assert len(run) == 16  # YYYY-MM-DD HH:MM

    def test_lint_lists_are_present(self):
        result = summarize("0 * * * *")
        assert isinstance(result.lint_warnings, list)
        assert isinstance(result.lint_infos, list)

    def test_star_slash_one_produces_info(self):
        result = summarize("*/1 * * * *")
        assert any("*/1" in i or "step" in i.lower() for i in result.lint_infos)


class TestFormatSummary:
    def test_includes_expression(self):
        result = summarize("0 * * * *")
        output = format_summary(result)
        assert "0 * * * *" in output

    def test_valid_shows_yes(self):
        result = summarize("0 * * * *")
        output = format_summary(result)
        assert "yes" in output

    def test_invalid_shows_no_and_error(self):
        result = summarize("bad expr")
        output = format_summary(result)
        assert "no" in output
        assert "Error" in output

    def test_next_runs_listed(self):
        result = summarize("0 * * * *")
        output = format_summary(result)
        assert "Next runs" in output

    def test_no_color_flag_accepted(self):
        result = summarize("0 * * * *")
        output = format_summary(result, color=False)
        assert isinstance(output, str)


class TestSummaryCLI:
    def _make_parser(self):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="command")
        add_summary_subparser(sub)
        return parser

    def test_registers_summary_command(self):
        parser = self._make_parser()
        args = parser.parse_args(["summary", "0 * * * *"])
        assert args.command == "summary"

    def test_default_runs(self):
        parser = self._make_parser()
        args = parser.parse_args(["summary", "0 * * * *"])
        assert args.runs == 3

    def test_custom_runs(self):
        parser = self._make_parser()
        args = parser.parse_args(["summary", "0 * * * *", "--runs", "5"])
        assert args.runs == 5

    def test_no_color_defaults_false(self):
        parser = self._make_parser()
        args = parser.parse_args(["summary", "0 * * * *"])
        assert args.no_color is False

    def test_handle_summary_prints_output(self, capsys):
        parser = self._make_parser()
        args = parser.parse_args(["summary", "0 * * * *"])
        handle_summary(args)
        captured = capsys.readouterr()
        assert "0 * * * *" in captured.out
