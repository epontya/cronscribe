"""Tests for cronscribe.bookmark and cronscribe.bookmark_cli."""

from __future__ import annotations

import argparse
import os
import pytest

from cronscribe.bookmark import (
    add_bookmark,
    get_bookmark,
    is_bookmarked,
    list_bookmarks,
    remove_bookmark,
)
from cronscribe.bookmark_cli import handle_bookmark


@pytest.fixture()
def bm_path(tmp_path):
    return str(tmp_path / "bookmarks.json")


class TestBookmark:
    def test_add_and_get(self, bm_path):
        add_bookmark("daily", "0 0 * * *", path=bm_path)
        assert get_bookmark("daily", path=bm_path) == "0 0 * * *"

    def test_get_unknown_returns_none(self, bm_path):
        assert get_bookmark("nope", path=bm_path) is None

    def test_add_strips_whitespace(self, bm_path):
        add_bookmark("  hourly  ", "  0 * * * *  ", path=bm_path)
        assert get_bookmark("hourly", path=bm_path) == "0 * * * *"

    def test_add_empty_name_raises(self, bm_path):
        with pytest.raises(ValueError):
            add_bookmark("", "* * * * *", path=bm_path)

    def test_overwrite_existing(self, bm_path):
        add_bookmark("job", "0 0 * * *", path=bm_path)
        add_bookmark("job", "0 12 * * *", path=bm_path)
        assert get_bookmark("job", path=bm_path) == "0 12 * * *"

    def test_remove_existing(self, bm_path):
        add_bookmark("tmp", "* * * * *", path=bm_path)
        assert remove_bookmark("tmp", path=bm_path) is True
        assert get_bookmark("tmp", path=bm_path) is None

    def test_remove_nonexistent_returns_false(self, bm_path):
        assert remove_bookmark("ghost", path=bm_path) is False

    def test_list_returns_sorted(self, bm_path):
        add_bookmark("zebra", "0 1 * * *", path=bm_path)
        add_bookmark("alpha", "0 2 * * *", path=bm_path)
        items = list_bookmarks(path=bm_path)
        assert items[0][0] == "alpha"
        assert items[1][0] == "zebra"

    def test_list_empty(self, bm_path):
        assert list_bookmarks(path=bm_path) == []

    def test_is_bookmarked_true(self, bm_path):
        add_bookmark("check", "0 0 * * *", path=bm_path)
        assert is_bookmarked("0 0 * * *", path=bm_path) is True

    def test_is_bookmarked_false(self, bm_path):
        assert is_bookmarked("0 0 * * *", path=bm_path) is False


def _make_args(**kwargs):
    defaults = {"add": None, "get": None, "remove": None, "list": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestBookmarkCLI:
    def test_add_prints_confirmation(self, bm_path, capsys, monkeypatch):
        monkeypatch.setattr(
            "cronscribe.bookmark_cli.add_bookmark",
            lambda n, e: add_bookmark(n, e, path=bm_path),
        )
        args = _make_args(add=["nightly", "0 2 * * *"])
        # Call without monkeypatch path — just verify return code and output
        result = handle_bookmark(args)
        out = capsys.readouterr().out
        assert result == 0
        assert "nightly" in out

    def test_list_no_bookmarks(self, bm_path, capsys, monkeypatch):
        monkeypatch.setattr(
            "cronscribe.bookmark_cli.list_bookmarks",
            lambda: list_bookmarks(path=bm_path),
        )
        args = _make_args(list=True)
        result = handle_bookmark(args)
        assert result == 0
        assert "No bookmarks" in capsys.readouterr().out

    def test_get_missing_returns_1(self, capsys):
        args = _make_args(get="nonexistent_xyz_abc")
        result = handle_bookmark(args)
        assert result == 1

    def test_remove_missing_returns_1(self, capsys):
        args = _make_args(remove="nonexistent_xyz_abc")
        result = handle_bookmark(args)
        assert result == 1
