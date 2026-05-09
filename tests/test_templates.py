"""Tests for cronscribe/templates.py and cronscribe/template_cli.py."""

import pytest
from cronscribe.templates import (
    get_template,
    list_templates,
    find_templates_by_expression,
    add_template,
    is_template,
)
from cronscribe.template_cli import (
    handle_list_templates,
    handle_template_lookup,
    handle_reverse_template_lookup,
)


class TestGetTemplate:
    def test_known_template_returns_tuple(self):
        result = get_template("daily")
        assert result == ("0 0 * * *", "Every day at midnight")

    def test_case_insensitive(self):
        assert get_template("DAILY") == get_template("daily")

    def test_whitespace_stripped(self):
        assert get_template("  hourly  ") == get_template("hourly")

    def test_unknown_returns_none(self):
        assert get_template("nonexistent-template") is None

    def test_minutely(self):
        expr, desc = get_template("minutely")
        assert expr == "* * * * *"

    def test_weekly(self):
        expr, _ = get_template("weekly")
        assert expr == "0 0 * * 0"


class TestListTemplates:
    def test_returns_list_of_dicts(self):
        templates = list_templates()
        assert isinstance(templates, list)
        assert all(isinstance(t, dict) for t in templates)

    def test_each_dict_has_required_keys(self):
        for t in list_templates():
            assert "name" in t
            assert "expression" in t
            assert "description" in t

    def test_sorted_by_name(self):
        names = [t["name"] for t in list_templates()]
        assert names == sorted(names)

    def test_contains_known_templates(self):
        names = {t["name"] for t in list_templates()}
        assert "daily" in names
        assert "hourly" in names
        assert "weekly" in names


class TestFindByExpression:
    def test_finds_matching_template(self):
        names = find_templates_by_expression("0 0 * * *")
        assert "daily" in names

    def test_no_match_returns_empty(self):
        assert find_templates_by_expression("1 2 3 4 5") == []

    def test_strips_whitespace(self):
        names = find_templates_by_expression("  * * * * *  ")
        assert "minutely" in names


class TestAddTemplate:
    def test_add_and_retrieve(self):
        add_template("test-custom", "5 4 * * *", "Custom test template")
        result = get_template("test-custom")
        assert result == ("5 4 * * *", "Custom test template")

    def test_is_template_after_add(self):
        add_template("test-exists", "1 1 1 1 *", "Exists test")
        assert is_template("test-exists") is True


class TestIsTemplate:
    def test_known_is_true(self):
        assert is_template("monthly") is True

    def test_unknown_is_false(self):
        assert is_template("not-a-template") is False


class TestTemplateCLI:
    def test_list_templates_contains_name(self):
        output = handle_list_templates(color=False)
        assert "daily" in output
        assert "0 0 * * *" in output

    def test_lookup_known(self):
        output = handle_template_lookup("hourly", color=False)
        assert "0 * * * *" in output
        assert "hourly" in output

    def test_lookup_unknown(self):
        output = handle_template_lookup("ghost-template", color=False)
        assert "not found" in output.lower()

    def test_reverse_lookup_found(self):
        output = handle_reverse_template_lookup("* * * * *", color=False)
        assert "minutely" in output

    def test_reverse_lookup_not_found(self):
        output = handle_reverse_template_lookup("9 9 9 9 9", color=False)
        assert "no templates" in output.lower()
