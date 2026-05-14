"""Tests for cronscribe.snippet_cli module."""

from __future__ import annotations

import argparse
import pytest

import cronscribe.snippet as snippet_mod
from cronscribe.snippet import add_snippet
from cronscribe.snippet_cli import handle_snippet


@pytest.fixture(autouse=True)
def reset_user_snippets(tmp_path, monkeypatch):
    monkeypatch.setattr(snippet_mod, "_USER_SNIPPETS", {})
    monkeypatch.setattr(snippet_mod, "_SNIPPETS_FILE", str(tmp_path / "s.json"))
    yield


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {"snippet_action": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestSnippetCLI:
    def test_list_prints_header(self, capsys):
        handle_snippet(make_args(snippet_action="list"))
        out = capsys.readouterr().out
        assert "Name" in out
        assert "Expression" in out

    def test_list_includes_defaults(self, capsys):
        handle_snippet(make_args(snippet_action="list"))
        out = capsys.readouterr().out
        assert "weekday-morning" in out
        assert "quarterly" in out

    def test_get_known_snippet(self, capsys):
        handle_snippet(make_args(snippet_action="get", name="every-6-hours"))
        out = capsys.readouterr().out
        assert "0 */6 * * *" in out

    def test_get_unknown_snippet(self, capsys):
        handle_snippet(make_args(snippet_action="get", name="no-such-snippet"))
        out = capsys.readouterr().out
        assert "not found" in out.lower()

    def test_add_snippet(self, capsys):
        handle_snippet(
            make_args(
                snippet_action="add",
                name="ci-nightly",
                expression="0 2 * * *",
                description="Nightly CI run",
            )
        )
        out = capsys.readouterr().out
        assert "saved" in out.lower()
        assert snippet_mod.get_snippet("ci-nightly") is not None

    def test_remove_existing_snippet(self, capsys):
        add_snippet("temp-snip", "*/10 * * * *", "")
        handle_snippet(make_args(snippet_action="remove", name="temp-snip"))
        out = capsys.readouterr().out
        assert "removed" in out.lower()

    def test_remove_nonexistent_snippet(self, capsys):
        handle_snippet(make_args(snippet_action="remove", name="ghost"))
        out = capsys.readouterr().out
        assert "not found" in out.lower()

    def test_reverse_lookup_found(self, capsys):
        handle_snippet(
            make_args(snippet_action="reverse", expression="0 8 * * 1-5")
        )
        out = capsys.readouterr().out
        assert "weekday-morning" in out

    def test_reverse_lookup_not_found(self, capsys):
        handle_snippet(
            make_args(snippet_action="reverse", expression="9 9 9 9 9")
        )
        out = capsys.readouterr().out
        assert "no snippets found" in out.lower()

    def test_default_action_lists(self, capsys):
        handle_snippet(make_args(snippet_action=None))
        out = capsys.readouterr().out
        assert "weekday-morning" in out
