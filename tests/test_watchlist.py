"""Tests for cronscribe.watchlist."""

from __future__ import annotations

import pytest
from pathlib import Path

from cronscribe.watchlist import (
    add_watch, get_watch, list_watches, remove_watch, clear_watchlist,
)


@pytest.fixture()
def wl_path(tmp_path: Path) -> Path:
    return tmp_path / "watchlist.json"


class TestWatchlist:
    def test_add_and_get(self, wl_path):
        add_watch("nightly", "0 2 * * *", path=wl_path)
        assert get_watch("nightly", path=wl_path) == "0 2 * * *"

    def test_get_unknown_returns_none(self, wl_path):
        assert get_watch("missing", path=wl_path) is None

    def test_add_strips_whitespace(self, wl_path):
        add_watch("  job  ", "  */5 * * * *  ", path=wl_path)
        assert get_watch("job", path=wl_path) == "*/5 * * * *"

    def test_overwrite_existing(self, wl_path):
        add_watch("job", "0 0 * * *", path=wl_path)
        add_watch("job", "0 1 * * *", path=wl_path)
        assert get_watch("job", path=wl_path) == "0 1 * * *"

    def test_remove_existing(self, wl_path):
        add_watch("job", "0 0 * * *", path=wl_path)
        result = remove_watch("job", path=wl_path)
        assert result is True
        assert get_watch("job", path=wl_path) is None

    def test_remove_missing_returns_false(self, wl_path):
        assert remove_watch("ghost", path=wl_path) is False

    def test_list_returns_sorted(self, wl_path):
        add_watch("zebra", "0 0 * * *", path=wl_path)
        add_watch("alpha", "*/5 * * * *", path=wl_path)
        names = [n for n, _ in list_watches(path=wl_path)]
        assert names == sorted(names)

    def test_list_empty(self, wl_path):
        assert list_watches(path=wl_path) == []

    def test_clear_removes_all(self, wl_path):
        add_watch("a", "* * * * *", path=wl_path)
        add_watch("b", "0 0 * * *", path=wl_path)
        clear_watchlist(path=wl_path)
        assert list_watches(path=wl_path) == []

    def test_file_created_on_add(self, wl_path):
        assert not wl_path.exists()
        add_watch("x", "* * * * *", path=wl_path)
        assert wl_path.exists()
