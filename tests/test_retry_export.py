"""Tests for cronscribe.retry_export."""

from __future__ import annotations

import json

import pytest

from cronscribe.retry import RetryPolicy, build_retry_schedule
from cronscribe.retry_export import (
    export_retry,
    retry_to_csv,
    retry_to_json,
    retry_to_text,
)


@pytest.fixture()
def schedule():
    policy = RetryPolicy(max_attempts=3, delay_minutes=10, jitter_minutes=0)
    return build_retry_schedule("0 8 * * 1-5", policy)


class TestRetryToJson:
    def test_returns_string(self, schedule):
        assert isinstance(retry_to_json(schedule), str)

    def test_valid_json(self, schedule):
        data = json.loads(retry_to_json(schedule))
        assert "base_expression" in data
        assert "expressions" in data

    def test_policy_included(self, schedule):
        data = json.loads(retry_to_json(schedule))
        assert data["policy"]["max_attempts"] == 3
        assert data["policy"]["delay_minutes"] == 10

    def test_expressions_list(self, schedule):
        data = json.loads(retry_to_json(schedule))
        assert isinstance(data["expressions"], list)
        assert data["expressions"][0] == "0 8 * * 1-5"


class TestRetryToCsv:
    def test_returns_string(self, schedule):
        assert isinstance(retry_to_csv(schedule), str)

    def test_has_header(self, schedule):
        csv_text = retry_to_csv(schedule)
        assert csv_text.startswith("attempt,expression")

    def test_base_row_present(self, schedule):
        csv_text = retry_to_csv(schedule)
        assert "base" in csv_text

    def test_retry_rows_present(self, schedule):
        csv_text = retry_to_csv(schedule)
        assert "retry_1" in csv_text
        assert "retry_2" in csv_text


class TestRetryToText:
    def test_returns_string(self, schedule):
        assert isinstance(retry_to_text(schedule), str)

    def test_contains_base_expression(self, schedule):
        text = retry_to_text(schedule)
        assert "0 8 * * 1-5" in text

    def test_contains_policy_info(self, schedule):
        text = retry_to_text(schedule)
        assert "3 attempts" in text


class TestExportRetry:
    def test_default_format_is_text(self, schedule):
        output = export_retry(schedule)
        assert "Base expression" in output

    def test_json_format(self, schedule):
        output = export_retry(schedule, fmt="json")
        data = json.loads(output)
        assert data["is_valid"] is True

    def test_csv_format(self, schedule):
        output = export_retry(schedule, fmt="csv")
        assert "attempt" in output

    def test_text_format(self, schedule):
        output = export_retry(schedule, fmt="text")
        assert "Policy" in output
