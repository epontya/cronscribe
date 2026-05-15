"""Tests for cronscribe.explain_cli."""
from __future__ import annotations

import argparse
import pytest

from cronscribe.explain_cli import add_explain_subparser, handle_explain


def make_args(expression: str, no_color: bool = True) -> argparse.Namespace:
    return argparse.Namespace(expression=expression, no_color=no_color)


class TestAddExplainSubparser:
    def test_registers_explain_command(self):
        parser = argparse.ArgumentParser()
        subs = parser.add_subparsers(dest="command")
        add_explain_subparser(subs)
        parsed = parser.parse_args(["explain", "* * * * *"])
        assert parsed.expression == "* * * * *"

    def test_no_color_flag_defaults_false(self):
        parser = argparse.ArgumentParser()
        subs = parser.add_subparsers(dest="command")
        add_explain_subparser(subs)
        parsed = parser.parse_args(["explain", "* * * * *"])
        assert parsed.no_color is False

    def test_no_color_flag_can_be_set(self):
        parser = argparse.ArgumentParser()
        subs = parser.add_subparsers(dest="command")
        add_explain_subparser(subs)
        parsed = parser.parse_args(["explain", "--no-color", "* * * * *"])
        assert parsed.no_color is True


class TestHandleExplain:
    def test_valid_expression_returns_zero(self):
        args = make_args("* * * * *")
        assert handle_explain(args) == 0

    def test_invalid_expression_returns_one(self):
        args = make_args("99 99 99 99 99")
        assert handle_explain(args) == 1

    def test_wrong_field_count_returns_one(self):
        args = make_args("* * *")
        assert handle_explain(args) == 1

    def test_output_contains_expression(self, capsys):
        args = make_args("0 9 * * 1-5")
        handle_explain(args)
        captured = capsys.readouterr()
        assert "0 9 * * 1-5" in captured.out

    def test_output_contains_field_labels(self, capsys):
        args = make_args("* * * * *")
        handle_explain(args)
        captured = capsys.readouterr()
        assert "Minute" in captured.out
        assert "Hour" in captured.out

    def test_output_contains_summary(self, capsys):
        args = make_args("* * * * *")
        handle_explain(args)
        captured = capsys.readouterr()
        assert "Summary" in captured.out

    def test_invalid_prints_error_message(self, capsys):
        args = make_args("bad expression")
        handle_explain(args)
        captured = capsys.readouterr()
        assert "Error" in captured.out or "invalid" in captured.out.lower()

    def test_no_ansi_codes_when_no_color(self, capsys):
        args = make_args("*/5 * * * *", no_color=True)
        handle_explain(args)
        captured = capsys.readouterr()
        assert "\033[" not in captured.out
