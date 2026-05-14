"""Tests for cronscribe.tag_cli module."""

import pytest
from unittest.mock import patch
import argparse
from cronscribe.tag_cli import add_tag_subparser, handle_tag
from cronscribe.tags import clear_user_tags


@pytest.fixture(autouse=True)
def reset_user_tags():
    yield
    clear_user_tags()


def make_args(**kwargs):
    defaults = {
        "list": False,
        "for_expression": None,
        "for_tag": None,
        "add": None,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestTagCLI:
    def test_list_tags_prints_known_tags(self, capsys):
        args = make_args(list=True)
        handle_tag(args)
        out = capsys.readouterr().out
        assert "daily" in out
        assert "weekly" in out

    def test_for_expression_known(self, capsys):
        args = make_args(for_expression="0 0 * * *")
        handle_tag(args)
        out = capsys.readouterr().out
        assert "daily" in out

    def test_for_expression_unknown(self, capsys):
        args = make_args(for_expression="1 2 3 4 5")
        handle_tag(args)
        out = capsys.readouterr().out
        assert "No tags found" in out

    def test_for_tag_known(self, capsys):
        args = make_args(for_tag="daily")
        handle_tag(args)
        out = capsys.readouterr().out
        assert "0 0 * * *" in out

    def test_for_tag_unknown(self, capsys):
        args = make_args(for_tag="nonexistent")
        handle_tag(args)
        out = capsys.readouterr().out
        assert "No expressions found" in out

    def test_add_tag(self, capsys):
        args = make_args(add=["backup", "0 1 * * *"])
        handle_tag(args)
        out = capsys.readouterr().out
        assert "backup" in out
        assert "0 1 * * *" in out

    def test_add_tag_then_query(self, capsys):
        add_args = make_args(add=["custom", "5 5 5 5 5"])
        handle_tag(add_args)
        query_args = make_args(for_tag="custom")
        handle_tag(query_args)
        out = capsys.readouterr().out
        assert "5 5 5 5 5" in out

    def test_subparser_registration(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        add_tag_subparser(subparsers)
        args = parser.parse_args(["tag", "--list"])
        assert hasattr(args, "func")
        assert args.list is True
