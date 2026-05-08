"""Tests for cronscribe.history module."""

import json
import os
import tempfile

import pytest

from cronscribe.history import (
    clear_history,
    get_history,
    record,
    search_history,
    _load_history,
    _save_history,
)


@pytest.fixture()
def tmp_history(tmp_path):
    return str(tmp_path / "history.json")


class TestHistory:
    def test_record_creates_file(self, tmp_history):
        record("every minute", "* * * * *", path=tmp_history)
        assert os.path.exists(tmp_history)

    def test_record_stores_fields(self, tmp_history):
        record("every hour", "0 * * * *", path=tmp_history)
        entries = _load_history(tmp_history)
        assert len(entries) == 1
        assert entries[0]["description"] == "every hour"
        assert entries[0]["cron"] == "0 * * * *"
        assert "timestamp" in entries[0]

    def test_multiple_records_accumulate(self, tmp_history):
        record("every minute", "* * * * *", path=tmp_history)
        record("every hour", "0 * * * *", path=tmp_history)
        entries = _load_history(tmp_history)
        assert len(entries) == 2

    def test_get_history_newest_first(self, tmp_history):
        record("first", "* * * * *", path=tmp_history)
        record("second", "0 * * * *", path=tmp_history)
        entries = get_history(path=tmp_history)
        assert entries[0]["description"] == "second"
        assert entries[1]["description"] == "first"

    def test_get_history_with_limit(self, tmp_history):
        for i in range(5):
            record(f"desc {i}", f"{i} * * * *", path=tmp_history)
        entries = get_history(limit=3, path=tmp_history)
        assert len(entries) == 3

    def test_clear_history_returns_count(self, tmp_history):
        record("a", "* * * * *", path=tmp_history)
        record("b", "0 * * * *", path=tmp_history)
        removed = clear_history(path=tmp_history)
        assert removed == 2
        assert get_history(path=tmp_history) == []

    def test_search_by_description(self, tmp_history):
        record("every minute", "* * * * *", path=tmp_history)
        record("every day at noon", "0 12 * * *", path=tmp_history)
        results = search_history("noon", path=tmp_history)
        assert len(results) == 1
        assert results[0]["cron"] == "0 12 * * *"

    def test_search_by_cron(self, tmp_history):
        record("every minute", "* * * * *", path=tmp_history)
        record("every hour", "0 * * * *", path=tmp_history)
        results = search_history("0 *", path=tmp_history)
        assert any(r["description"] == "every hour" for r in results)

    def test_load_missing_file_returns_empty(self, tmp_history):
        assert _load_history(tmp_history) == []

    def test_load_corrupt_file_returns_empty(self, tmp_history):
        with open(tmp_history, "w") as f:
            f.write("not valid json{{")
        assert _load_history(tmp_history) == []

    def test_get_history_empty(self, tmp_history):
        assert get_history(path=tmp_history) == []
