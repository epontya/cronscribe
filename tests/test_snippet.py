"""Tests for cronscribe.snippet module."""

from __future__ import annotations

import json
import os
import pytest

import cronscribe.snippet as snippet_mod
from cronscribe.snippet import (
    add_snippet,
    find_snippets_by_expression,
    get_snippet,
    is_snippet,
    list_snippets,
    remove_snippet,
)


@pytest.fixture(autouse=True)
def reset_user_snippets(tmp_path, monkeypatch):
    monkeypatch.setattr(snippet_mod, "_USER_SNIPPETS", {})
    snippets_file = tmp_path / "snippets.json"
    monkeypatch.setattr(snippet_mod, "_SNIPPETS_FILE", str(snippets_file))
    yield


class TestGetSnippet:
    def test_known_snippet_returns_tuple(self):
        result = get_snippet("weekday-morning")
        assert result is not None
        expr, desc = result
        assert expr == "0 8 * * 1-5"
        assert "weekday" in desc.lower()

    def test_case_insensitive(self):
        assert get_snippet("WEEKDAY-MORNING") == get_snippet("weekday-morning")

    def test_whitespace_stripped(self):
        assert get_snippet("  weekend-noon  ") == get_snippet("weekend-noon")

    def test_unknown_returns_none(self):
        assert get_snippet("nonexistent-snippet") is None

    def test_every_6_hours(self):
        result = get_snippet("every-6-hours")
        assert result is not None
        assert result[0] == "0 */6 * * *"


class TestAddRemoveSnippet:
    def test_add_snippet_is_retrievable(self):
        add_snippet("my-custom", "30 9 * * 1", "Monday 9:30 AM")
        result = get_snippet("my-custom")
        assert result == ("30 9 * * 1", "Monday 9:30 AM")

    def test_add_snippet_without_description(self):
        add_snippet("no-desc", "0 0 * * *")
        expr, desc = get_snippet("no-desc")
        assert expr == "0 0 * * *"
        assert desc == ""

    def test_add_snippet_persists_to_file(self, tmp_path):
        add_snippet("persisted", "0 1 * * *", "1 AM daily")
        assert os.path.isfile(snippet_mod._SNIPPETS_FILE)
        with open(snippet_mod._SNIPPETS_FILE) as fh:
            data = json.load(fh)
        assert "persisted" in data

    def test_remove_user_snippet(self):
        add_snippet("temp", "*/5 * * * *", "Every 5 min")
        assert remove_snippet("temp") is True
        assert get_snippet("temp") is None

    def test_remove_nonexistent_returns_false(self):
        assert remove_snippet("does-not-exist") is False

    def test_remove_builtin_returns_false(self):
        assert remove_snippet("quarterly") is False


class TestListSnippets:
    def test_returns_list_of_tuples(self):
        rows = list_snippets()
        assert isinstance(rows, list)
        assert all(len(r) == 3 for r in rows)

    def test_includes_defaults(self):
        names = [r[0] for r in list_snippets()]
        assert "weekday-morning" in names
        assert "quarterly" in names

    def test_user_snippets_included(self):
        add_snippet("user-one", "0 5 * * *", "5 AM")
        names = [r[0] for r in list_snippets()]
        assert "user-one" in names


class TestFindByExpression:
    def test_finds_matching_expression(self):
        matches = find_snippets_by_expression("0 */6 * * *")
        names = [m[0] for m in matches]
        assert "every-6-hours" in names

    def test_no_match_returns_empty(self):
        assert find_snippets_by_expression("1 2 3 4 5") == []


class TestIsSnippet:
    def test_known_is_snippet(self):
        assert is_snippet("end-of-month") is True

    def test_unknown_is_not_snippet(self):
        assert is_snippet("unknown-xyz") is False
