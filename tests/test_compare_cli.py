"""Tests for cronscribe.compare_cli module."""

import argparse
import pytest
from io import StringIO
from unittest.mock import patch

from cronscribe.compare_cli import add_compare_subparser, handle_compare


def make_args(**kwargs):
    defaults = {
        "input_a": "0 9 * * *",
        "input_b": "0 12 * * *",
        "label_a": "A",
        "label_b": "B",
        "no_color": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestAddCompareSubparser:
    def test_registers_compare_command(self):
        parser = argparse.ArgumentParser()
        subs = parser.add_subparsers()
        add_compare_subparser(subs)
        args = parser.parse_args(["compare", "* * * * *", "0 * * * *"])
        assert args.input_a == "* * * * *"
        assert args.input_b == "0 * * * *"

    def test_default_labels(self):
        parser = argparse.ArgumentParser()
        subs = parser.add_subparsers()
        add_compare_subparser(subs)
        args = parser.parse_args(["compare", "* * * * *", "0 * * * *"])
        assert args.label_a == "A"
        assert args.label_b == "B"

    def test_custom_labels(self):
        parser = argparse.ArgumentParser()
        subs = parser.add_subparsers()
        add_compare_subparser(subs)
        args = parser.parse_args(
            ["compare", "* * * * *", "0 * * * *", "--label-a", "old", "--label-b", "new"]
        )
        assert args.label_a == "old"
        assert args.label_b == "new"


class TestHandleCompare:
    def test_returns_zero_for_valid_inputs(self, capsys):
        args = make_args(input_a="0 9 * * *", input_b="0 12 * * *")
        code = handle_compare(args)
        assert code == 0

    def test_returns_one_for_invalid_input(self, capsys):
        args = make_args(input_a="99 99 99 99 99", input_b="0 0 * * *")
        code = handle_compare(args)
        assert code == 1

    def test_prints_expressions(self, capsys):
        args = make_args(input_a="0 9 * * *", input_b="0 9 * * *")
        handle_compare(args)
        out = capsys.readouterr().out
        assert "0 9 * * *" in out

    def test_identical_message(self, capsys):
        args = make_args(input_a="0 9 * * *", input_b="0 9 * * *")
        handle_compare(args)
        out = capsys.readouterr().out
        assert "IDENTICAL" in out

    def test_differ_message(self, capsys):
        args = make_args(input_a="0 9 * * *", input_b="0 12 * * *")
        handle_compare(args)
        out = capsys.readouterr().out
        assert "DIFFER" in out

    def test_error_message_printed_for_invalid(self, capsys):
        args = make_args(input_a="99 99 99 99 99", input_b="0 0 * * *")
        handle_compare(args)
        out = capsys.readouterr().out
        assert "error" in out
