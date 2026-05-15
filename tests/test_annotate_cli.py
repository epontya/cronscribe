"""Tests for cronscribe.annotate_cli."""

from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from cronscribe.annotate_cli import add_annotate_subparser, handle_annotate
from cronscribe.annotate import clear_annotations


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {"annotate_cmd": "list", "expression": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestAddAnnotateSubparser:
    def test_registers_annotate_command(self) -> None:
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        add_annotate_subparser(sub)
        args = parser.parse_args(["annotate", "list"])
        assert args.cmd == "annotate"

    def test_add_subcommand_parses_expression_and_note(self) -> None:
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        add_annotate_subparser(sub)
        args = parser.parse_args(["annotate", "add", "0 * * * *", "hourly job"])
        assert args.expression == "0 * * * *"
        assert args.note == "hourly job"

    def test_remove_subcommand_parses_index(self) -> None:
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        add_annotate_subparser(sub)
        args = parser.parse_args(["annotate", "remove", "0 * * * *", "1"])
        assert args.index == 1


class TestHandleAnnotate:
    @pytest.fixture(autouse=True)
    def _patch_path(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        ann_path = tmp_path / "annotations.json"
        monkeypatch.setattr("cronscribe.annotate._DEFAULT_PATH", ann_path)
        monkeypatch.setattr("cronscribe.annotate_cli.add_annotation",
                            lambda expr, note: __import__("cronscribe.annotate", fromlist=["add_annotation"]).add_annotation(expr, note, path=ann_path))
        monkeypatch.setattr("cronscribe.annotate_cli.get_annotations",
                            lambda expr: __import__("cronscribe.annotate", fromlist=["get_annotations"]).get_annotations(expr, path=ann_path))
        monkeypatch.setattr("cronscribe.annotate_cli.remove_annotation",
                            lambda expr, idx: __import__("cronscribe.annotate", fromlist=["remove_annotation"]).remove_annotation(expr, idx, path=ann_path))
        monkeypatch.setattr("cronscribe.annotate_cli.list_annotated",
                            lambda: __import__("cronscribe.annotate", fromlist=["list_annotated"]).list_annotated(path=ann_path))
        monkeypatch.setattr("cronscribe.annotate_cli.clear_annotations",
                            lambda expr=None: __import__("cronscribe.annotate", fromlist=["clear_annotations"]).clear_annotations(expr, path=ann_path))

    def test_add_prints_confirmation(self, capsys: pytest.CaptureFixture) -> None:
        args = make_args(annotate_cmd="add", expression="0 * * * *", note="hourly")
        handle_annotate(args)
        out = capsys.readouterr().out
        assert "added" in out.lower()

    def test_list_no_annotations_message(self, capsys: pytest.CaptureFixture) -> None:
        args = make_args(annotate_cmd="list", expression="0 * * * *")
        handle_annotate(args)
        out = capsys.readouterr().out
        assert "No annotations" in out

    def test_list_all_empty_message(self, capsys: pytest.CaptureFixture) -> None:
        args = make_args(annotate_cmd="list", expression=None)
        handle_annotate(args)
        out = capsys.readouterr().out
        assert "No annotations" in out

    def test_remove_invalid_index_message(self, capsys: pytest.CaptureFixture) -> None:
        args = make_args(annotate_cmd="remove", expression="0 * * * *", index=99)
        handle_annotate(args)
        out = capsys.readouterr().out
        assert "No note" in out

    def test_clear_prints_confirmation(self, capsys: pytest.CaptureFixture) -> None:
        args = make_args(annotate_cmd="clear", expression=None)
        handle_annotate(args)
        out = capsys.readouterr().out
        assert "Cleared" in out
