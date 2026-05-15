"""Tests for cronscribe.annotate."""

from __future__ import annotations

import pytest
from pathlib import Path

from cronscribe.annotate import (
    add_annotation,
    get_annotations,
    remove_annotation,
    list_annotated,
    clear_annotations,
)


@pytest.fixture()
def ann_path(tmp_path: Path) -> Path:
    return tmp_path / "annotations.json"


class TestAddAndGet:
    def test_add_single_note(self, ann_path: Path) -> None:
        add_annotation("0 * * * *", "runs hourly", path=ann_path)
        assert get_annotations("0 * * * *", path=ann_path) == ["runs hourly"]

    def test_add_multiple_notes(self, ann_path: Path) -> None:
        add_annotation("0 0 * * *", "midnight job", path=ann_path)
        add_annotation("0 0 * * *", "daily reset", path=ann_path)
        notes = get_annotations("0 0 * * *", path=ann_path)
        assert notes == ["midnight job", "daily reset"]

    def test_get_unknown_returns_empty(self, ann_path: Path) -> None:
        assert get_annotations("* * * * *", path=ann_path) == []

    def test_add_strips_whitespace(self, ann_path: Path) -> None:
        add_annotation("  0 * * * *  ", "  note  ", path=ann_path)
        assert get_annotations("0 * * * *", path=ann_path) == ["note"]

    def test_add_empty_expression_raises(self, ann_path: Path) -> None:
        with pytest.raises(ValueError):
            add_annotation("", "some note", path=ann_path)

    def test_add_empty_note_raises(self, ann_path: Path) -> None:
        with pytest.raises(ValueError):
            add_annotation("0 * * * *", "", path=ann_path)


class TestRemove:
    def test_remove_existing_note(self, ann_path: Path) -> None:
        add_annotation("0 * * * *", "first", path=ann_path)
        add_annotation("0 * * * *", "second", path=ann_path)
        ok = remove_annotation("0 * * * *", 0, path=ann_path)
        assert ok is True
        assert get_annotations("0 * * * *", path=ann_path) == ["second"]

    def test_remove_last_note_cleans_key(self, ann_path: Path) -> None:
        add_annotation("0 * * * *", "only", path=ann_path)
        remove_annotation("0 * * * *", 0, path=ann_path)
        assert "0 * * * *" not in list_annotated(path=ann_path)

    def test_remove_invalid_index_returns_false(self, ann_path: Path) -> None:
        add_annotation("0 * * * *", "note", path=ann_path)
        assert remove_annotation("0 * * * *", 5, path=ann_path) is False

    def test_remove_from_unknown_expression(self, ann_path: Path) -> None:
        assert remove_annotation("* * * * *", 0, path=ann_path) is False


class TestListAndClear:
    def test_list_annotated_returns_all(self, ann_path: Path) -> None:
        add_annotation("0 * * * *", "hourly", path=ann_path)
        add_annotation("0 0 * * *", "daily", path=ann_path)
        result = list_annotated(path=ann_path)
        assert "0 * * * *" in result
        assert "0 0 * * *" in result

    def test_clear_specific_expression(self, ann_path: Path) -> None:
        add_annotation("0 * * * *", "note", path=ann_path)
        add_annotation("0 0 * * *", "other", path=ann_path)
        clear_annotations("0 * * * *", path=ann_path)
        assert get_annotations("0 * * * *", path=ann_path) == []
        assert get_annotations("0 0 * * *", path=ann_path) == ["other"]

    def test_clear_all(self, ann_path: Path) -> None:
        add_annotation("0 * * * *", "note", path=ann_path)
        clear_annotations(path=ann_path)
        assert list_annotated(path=ann_path) == {}
