"""Tests for cronscribe.macro module."""

import pytest
from cronscribe import macro as macro_mod
from cronscribe.macro import (
    get_macro,
    list_macros,
    add_macro,
    is_macro,
    find_macros_by_expression,
)


@pytest.fixture(autouse=True)
def reset_user_macros():
    macro_mod._USER_MACROS.clear()
    yield
    macro_mod._USER_MACROS.clear()


class TestGetMacro:
    def test_known_macro_returns_tuple(self):
        result = get_macro("twice_daily")
        assert result is not None
        desc, exprs = result
        assert isinstance(desc, str)
        assert isinstance(exprs, list)
        assert len(exprs) == 2

    def test_case_insensitive(self):
        assert get_macro("TWICE_DAILY") is not None

    def test_spaces_normalised(self):
        assert get_macro("twice daily") is not None

    def test_unknown_returns_none(self):
        assert get_macro("nonexistent_macro") is None

    def test_business_hours_contains_weekday_range(self):
        _, exprs = get_macro("business_hours")
        assert any("1-5" in e for e in exprs)


class TestListMacros:
    def test_returns_list(self):
        result = list_macros()
        assert isinstance(result, list)

    def test_each_item_is_three_tuple(self):
        for item in list_macros():
            assert len(item) == 3

    def test_builtin_macros_present(self):
        names = [name for name, _, _ in list_macros()]
        assert "twice_daily" in names
        assert "nightly_backup" in names

    def test_sorted_alphabetically(self):
        names = [name for name, _, _ in list_macros()]
        assert names == sorted(names)


class TestAddMacro:
    def test_add_and_retrieve(self):
        add_macro("my_macro", "A custom macro", ["0 6 * * *"])
        result = get_macro("my_macro")
        assert result is not None
        desc, exprs = result
        assert desc == "A custom macro"
        assert exprs == ["0 6 * * *"]

    def test_empty_name_raises(self):
        with pytest.raises(ValueError, match="empty"):
            add_macro("", "desc", ["0 * * * *"])

    def test_empty_expressions_raises(self):
        with pytest.raises(ValueError, match="at least one"):
            add_macro("bad", "desc", [])

    def test_user_macro_appears_in_list(self):
        add_macro("custom_one", "Custom", ["*/5 * * * *"])
        names = [n for n, _, _ in list_macros()]
        assert "custom_one" in names


class TestIsMacro:
    def test_known_is_true(self):
        assert is_macro("weekly_report") is True

    def test_unknown_is_false(self):
        assert is_macro("not_a_macro") is False


class TestFindMacrosByExpression:
    def test_finds_matching_macro(self):
        matches = find_macros_by_expression("0 0 * * *")
        assert "nightly_backup" in matches or "twice_daily" in matches

    def test_no_match_returns_empty(self):
        assert find_macros_by_expression("99 99 99 99 99") == []

    def test_exact_match_required(self):
        # partial string should not match
        matches = find_macros_by_expression("0 0")
        assert matches == []
