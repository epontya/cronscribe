"""Tests for cronscribe.macro_cli module."""

import io
import pytest
from types import SimpleNamespace
from cronscribe import macro as macro_mod
from cronscribe.macro_cli import (
    handle_list_macros,
    handle_macro_lookup,
    handle_reverse_macro_lookup,
)


@pytest.fixture(autouse=True)
def reset_user_macros():
    macro_mod._USER_MACROS.clear()
    yield
    macro_mod._USER_MACROS.clear()


def make_args(**kwargs):
    return SimpleNamespace(**kwargs)


class TestHandleListMacros:
    def test_prints_header(self):
        out = io.StringIO()
        handle_list_macros(make_args(), out=out)
        assert "Name" in out.getvalue()

    def test_includes_builtin_macros(self):
        out = io.StringIO()
        handle_list_macros(make_args(), out=out)
        assert "twice_daily" in out.getvalue()

    def test_empty_after_clear(self, monkeypatch):
        monkeypatch.setattr(macro_mod, "_BUILTIN_MACROS", {})
        macro_mod._USER_MACROS.clear()
        out = io.StringIO()
        handle_list_macros(make_args(), out=out)
        assert "No macros" in out.getvalue()


class TestHandleMacroLookup:
    def test_known_macro(self):
        out = io.StringIO()
        handle_macro_lookup(make_args(name="nightly_backup"), out=out)
        result = out.getvalue()
        assert "nightly_backup" in result
        assert "0 2 * * *" in result

    def test_unknown_macro(self):
        out = io.StringIO()
        handle_macro_lookup(make_args(name="ghost_macro"), out=out)
        assert "Unknown macro" in out.getvalue()

    def test_shows_description(self):
        out = io.StringIO()
        handle_macro_lookup(make_args(name="weekly_report"), out=out)
        assert "Description" in out.getvalue()


class TestHandleReverseMacroLookup:
    def test_finds_macro(self):
        out = io.StringIO()
        handle_reverse_macro_lookup(make_args(expression="0 9 * * 1"), out=out)
        assert "weekly_report" in out.getvalue()

    def test_no_match(self):
        out = io.StringIO()
        handle_reverse_macro_lookup(make_args(expression="1 2 3 4 5"), out=out)
        assert "No macros found" in out.getvalue()
