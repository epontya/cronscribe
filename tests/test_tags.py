"""Tests for cronscribe.tags module."""

import pytest
from cronscribe.tags import (
    get_tags_for,
    get_expressions_for_tag,
    list_tags,
    add_tag,
    is_tagged,
    clear_user_tags,
)


@pytest.fixture(autouse=True)
def reset_user_tags():
    """Ensure user tags are cleared between tests."""
    yield
    clear_user_tags()


class TestGetTagsFor:
    def test_known_expression_returns_tags(self):
        tags = get_tags_for("* * * * *")
        assert "frequent" in tags

    def test_daily_midnight_tagged_daily(self):
        tags = get_tags_for("0 0 * * *")
        assert "daily" in tags

    def test_unknown_expression_returns_empty(self):
        tags = get_tags_for("1 2 3 4 5")
        assert tags == []

    def test_expression_with_multiple_tags(self):
        # "0 0 * * 1-5" is both daily and business-adjacent; check daily at minimum
        tags = get_tags_for("0 0 * * 1-5")
        assert "daily" in tags

    def test_strips_whitespace(self):
        tags = get_tags_for("  0 0 * * *  ")
        assert "daily" in tags

    def test_result_is_sorted(self):
        tags = get_tags_for("0 0 * * *")
        assert tags == sorted(tags)


class TestGetExpressionsForTag:
    def test_known_tag_returns_list(self):
        exprs = get_expressions_for_tag("daily")
        assert "0 0 * * *" in exprs

    def test_unknown_tag_returns_empty(self):
        exprs = get_expressions_for_tag("nonexistent-tag")
        assert exprs == []

    def test_case_insensitive_lookup(self):
        exprs = get_expressions_for_tag("DAILY")
        assert "0 0 * * *" in exprs

    def test_whitespace_stripped(self):
        exprs = get_expressions_for_tag("  weekly  ")
        assert "0 0 * * 0" in exprs


class TestListTags:
    def test_returns_list_of_strings(self):
        tags = list_tags()
        assert isinstance(tags, list)
        assert all(isinstance(t, str) for t in tags)

    def test_includes_builtin_tags(self):
        tags = list_tags()
        for expected in ["daily", "weekly", "monthly", "hourly"]:
            assert expected in tags

    def test_result_is_sorted(self):
        tags = list_tags()
        assert tags == sorted(tags)


class TestAddTag:
    def test_add_new_tag(self):
        add_tag("backup", "0 1 * * *")
        assert "0 1 * * *" in get_expressions_for_tag("backup")

    def test_add_to_existing_user_tag(self):
        add_tag("backup", "0 1 * * *")
        add_tag("backup", "0 2 * * *")
        exprs = get_expressions_for_tag("backup")
        assert "0 1 * * *" in exprs
        assert "0 2 * * *" in exprs

    def test_duplicate_expression_not_added_twice(self):
        add_tag("backup", "0 1 * * *")
        add_tag("backup", "0 1 * * *")
        exprs = get_expressions_for_tag("backup")
        assert exprs.count("0 1 * * *") == 1

    def test_user_tag_appears_in_list(self):
        add_tag("custom", "5 5 5 5 5")
        assert "custom" in list_tags()


class TestIsTagged:
    def test_tagged_expression_returns_true(self):
        assert is_tagged("0 0 * * *", "daily") is True

    def test_untagged_expression_returns_false(self):
        assert is_tagged("1 2 3 4 5", "daily") is False

    def test_user_added_tag(self):
        add_tag("special", "0 3 * * 2")
        assert is_tagged("0 3 * * 2", "special") is True
