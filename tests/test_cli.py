"""Tests for the cronscribe CLI."""

import pytest
from unittest.mock import patch

from cronscribe.cli import run


class TestCLI:
    """Tests for CLI argument handling and output."""

    def test_no_args_prints_help_and_exits_zero(self, capsys):
        exit_code = run([])
        captured = capsys.readouterr()
        assert exit_code == 0
        assert "usage" in captured.out.lower()

    def test_parse_every_minute(self, capsys):
        exit_code = run(["every minute"])
        captured = capsys.readouterr()
        assert exit_code == 0
        assert "* * * * *" in captured.out

    def test_parse_every_day_at_noon(self, capsys):
        exit_code = run(["every day at noon"])
        captured = capsys.readouterr()
        assert exit_code == 0
        assert "0 12 * * *" in captured.out

    def test_parse_with_preview(self, capsys):
        exit_code = run(["every minute", "--preview", "--count", "3"])
        captured = capsys.readouterr()
        assert exit_code == 0
        assert "Next" in captured.out or "execution" in captured.out.lower()

    def test_parse_unknown_description_returns_error(self, capsys):
        exit_code = run(["xyzzy frobulate"])
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Could not parse" in captured.out

    def test_validate_valid_expression(self, capsys):
        exit_code = run(["--validate", "0 12 * * *"])
        captured = capsys.readouterr()
        assert exit_code == 0
        assert "valid" in captured.out.lower()

    def test_validate_invalid_expression(self, capsys):
        exit_code = run(["--validate", "99 99 99 99 99"])
        captured = capsys.readouterr()
        assert exit_code == 1
        assert "Invalid" in captured.out

    def test_validate_with_preview(self, capsys):
        exit_code = run(["--validate", "0 9 * * 1", "--preview", "--count", "2"])
        captured = capsys.readouterr()
        assert exit_code == 0
        assert "valid" in captured.out.lower()

    def test_preview_default_count(self, capsys):
        exit_code = run(["every hour", "--preview"])
        captured = capsys.readouterr()
        assert exit_code == 0
        # Default count is 5; expect at least some lines with datetime-like content
        lines = [l for l in captured.out.splitlines() if l.strip()]
        assert len(lines) >= 2
