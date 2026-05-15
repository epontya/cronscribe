"""Annotation support: attach user notes to cron expressions."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

_DEFAULT_PATH = Path.home() / ".cronscribe" / "annotations.json"


def _load_annotations(path: Path = _DEFAULT_PATH) -> Dict[str, List[str]]:
    if path.exists():
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def _save_annotations(data: Dict[str, List[str]], path: Path = _DEFAULT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def add_annotation(expression: str, note: str, path: Path = _DEFAULT_PATH) -> None:
    """Append *note* to the annotation list for *expression*."""
    expression = expression.strip()
    note = note.strip()
    if not expression or not note:
        raise ValueError("expression and note must be non-empty strings")
    data = _load_annotations(path)
    data.setdefault(expression, []).append(note)
    _save_annotations(data, path)


def get_annotations(expression: str, path: Path = _DEFAULT_PATH) -> List[str]:
    """Return all notes for *expression*, or an empty list."""
    data = _load_annotations(path)
    return list(data.get(expression.strip(), []))


def remove_annotation(expression: str, index: int, path: Path = _DEFAULT_PATH) -> bool:
    """Remove the note at *index* for *expression*. Returns True on success."""
    data = _load_annotations(path)
    key = expression.strip()
    notes = data.get(key, [])
    if index < 0 or index >= len(notes):
        return False
    notes.pop(index)
    if not notes:
        del data[key]
    else:
        data[key] = notes
    _save_annotations(data, path)
    return True


def list_annotated(path: Path = _DEFAULT_PATH) -> Dict[str, List[str]]:
    """Return all annotated expressions and their notes."""
    return dict(_load_annotations(path))


def clear_annotations(expression: Optional[str] = None, path: Path = _DEFAULT_PATH) -> None:
    """Clear notes for *expression*, or wipe everything if *expression* is None."""
    if expression is None:
        _save_annotations({}, path)
        return
    data = _load_annotations(path)
    data.pop(expression.strip(), None)
    _save_annotations(data, path)
