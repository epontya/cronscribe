"""Tests for cronscribe.watchlist_cli."""

from __future__ import annotations

import argparse
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from cronscribe.watchlist_cli import add_watchlist_subparser, handle_watchlist
from cronscribe.watchlist import add_watch, clear_watchlist


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {"watch_cmd": "list", "preview": 0}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture(autouse=True)
def reset(tmp_path, monkeypatch):
    wl_path = tmp_path / "wl.json"
    import cronscribe.watchlist as wl_mod
    import cronscribe.watchlist_cli as cli_mod
    monkeypatch.setattr(wl_mod, "_DEFAULT_PATH", wl_path)
    monkeypatch.setattr(cli_mod, "add_watch",
                        lambda n, e: wl_mod.add_watch(n, e, path=wl_path))
    monkeypatch.setattr(cli_mod, "get_watch",
                        lambda n: wl_mod.get_watch(n, path=wl_path))
    monkeypatch.setattr(cli_mod, "list_watches",
                        lambda: wl_mod.list_watches(path=wl_path))
    monkeypatch.setattr(cli_mod, "remove_watch",
                        lambda n: wl_mod.remove_watch(n, path=wl_path))
    monkeypatch.setattr(cli_mod, "clear_watchlist",
                        lambda: wl_mod.clear_watchlist(path=wl_path))
    yield


class TestWatchlistCLI:
    def test_add_subparser_registered(self):
        parser = argparse.ArgumentParser()
        subs = parser.add_subparsers(dest="cmd")
        add_watchlist_subparser(subs)
        args = parser.parse_args(["watch", "list"])
        assert args.cmd == "watch"

    def test_add_prints_confirmation(self, capsys):
        handle_watchlist(make_args(watch_cmd="add", name="nightly", expression="0 2 * * *"))
        out = capsys.readouterr().out
        assert "nightly" in out
        assert "0 2 * * *" in out

    def test_list_empty(self, capsys):
        handle_watchlist(make_args(watch_cmd="list"))
        assert "empty" in capsys.readouterr().out.lower()

    def test_list_shows_entries(self, capsys):
        handle_watchlist(make_args(watch_cmd="add", name="job", expression="*/10 * * * *"))
        capsys.readouterr()
        handle_watchlist(make_args(watch_cmd="list"))
        out = capsys.readouterr().out
        assert "job" in out
        assert "*/10 * * * *" in out

    def test_remove_existing(self, capsys):
        handle_watchlist(make_args(watch_cmd="add", name="tmp", expression="* * * * *"))
        capsys.readouterr()
        handle_watchlist(make_args(watch_cmd="remove", name="tmp"))
        assert "Removed" in capsys.readouterr().out

    def test_remove_missing(self, capsys):
        handle_watchlist(make_args(watch_cmd="remove", name="ghost"))
        assert "not found" in capsys.readouterr().out.lower()

    def test_get_unknown(self, capsys):
        handle_watchlist(make_args(watch_cmd="get", name="nope", preview=0))
        assert "No watchlist" in capsys.readouterr().out

    def test_clear(self, capsys):
        handle_watchlist(make_args(watch_cmd="add", name="a", expression="* * * * *"))
        capsys.readouterr()
        handle_watchlist(make_args(watch_cmd="clear"))
        assert "cleared" in capsys.readouterr().out.lower()
