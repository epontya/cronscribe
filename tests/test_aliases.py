"""Tests for cronscribe.aliases and cronscribe.alias_cli."""

import pytest
from cronscribe.aliases import (
    resolve_alias,
    get_aliases_for,
    list_aliases,
    is_alias,
    ALIAS_MAP,
)
from cronscribe.alias_cli import (
    handle_alias_lookup,
    handle_list_aliases,
    handle_reverse_lookup,
)


class TestAliases:
    def test_resolve_known_alias(self):
        assert resolve_alias("@daily") == "0 0 * * *"

    def test_resolve_case_insensitive(self):
        assert resolve_alias("@DAILY") == "0 0 * * *"

    def test_resolve_unknown_returns_none(self):
        assert resolve_alias("@unknown") is None

    def test_resolve_with_whitespace(self):
        assert resolve_alias("  @hourly  ") == "0 * * * *"

    def test_is_alias_true(self):
        assert is_alias("@weekly") is True

    def test_is_alias_false(self):
        assert is_alias("@notreal") is False

    def test_get_aliases_for_known_expr(self):
        aliases = get_aliases_for("0 0 1 1 *")
        assert "@yearly" in aliases
        assert "@annually" in aliases

    def test_get_aliases_for_unknown_expr(self):
        assert get_aliases_for("1 2 3 4 5") == []

    def test_list_aliases_returns_all(self):
        pairs = list_aliases()
        assert len(pairs) == len(ALIAS_MAP)
        names = [a for a, _ in pairs]
        assert "@daily" in names
        assert "@monthly" in names

    def test_list_aliases_sorted(self):
        pairs = list_aliases()
        names = [a for a, _ in pairs]
        assert names == sorted(names)

    def test_all_alias_expressions_are_valid(self):
        from cronscribe.validator import validate
        for alias, expr in ALIAS_MAP.items():
            result = validate(expr)
            assert result.valid, f"Alias {alias} -> '{expr}' failed validation: {result.errors}"


class TestAliasCLI:
    def test_handle_alias_lookup_known(self):
        output = handle_alias_lookup("@daily", color=False)
        assert "@daily" in output
        assert "0 0 * * *" in output

    def test_handle_alias_lookup_unknown(self):
        output = handle_alias_lookup("@bogus", color=False)
        assert "Unknown alias" in output
        assert "--list-aliases" in output

    def test_handle_list_aliases_contains_all(self):
        output = handle_list_aliases(color=False)
        for alias in ALIAS_MAP:
            assert alias in output

    def test_handle_list_aliases_has_header(self):
        output = handle_list_aliases(color=False)
        assert "Alias" in output
        assert "Cron Expression" in output

    def test_handle_reverse_lookup_found(self):
        output = handle_reverse_lookup("0 0 * * *")
        assert "@daily" in output or "@midnight" in output

    def test_handle_reverse_lookup_not_found(self):
        output = handle_reverse_lookup("5 4 3 2 1")
        assert "No aliases found" in output
