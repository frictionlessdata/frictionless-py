"""Helpers for the `missingValues` property, shared by Schema and Field.

Datapackage v2 allows object entries `{value, label?}` alongside plain
strings. The canonical in-memory model keeps `missing_values` as a list of
strings plus a side-car mapping of labels: the split (import) is shape-driven,
never version-driven, and the export emits object entries if and only if at
least one current value has a label.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Union

IEntries = List[Union[str, Dict[str, str]]]

PROFILE: Dict[str, Any] = {
    "anyOf": [
        {
            "type": "array",
            "items": {"type": "string"},
        },
        {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["value"],
                "properties": {
                    "value": {"type": "string"},
                    "label": {"type": "string"},
                },
            },
        },
    ],
}


def split(entries: IEntries) -> Tuple[List[str], Dict[str, str]]:
    """Split entries into plain string values and a label mapping"""
    labels = {
        entry["value"]: entry["label"]
        for entry in entries
        if isinstance(entry, dict) and entry.get("label") is not None
    }
    values = [entry["value"] if isinstance(entry, dict) else entry for entry in entries]
    return values, labels


def validation_notes(entries: IEntries) -> List[str]:
    """Uniqueness notes for object entries (empty if valid)

    Object entries must have a unique value and an optional unique label;
    absent labels do not collide with each other. Plain string entries keep
    the lax v1 behavior (duplicates allowed).
    """
    notes: List[str] = []
    if not any(isinstance(entry, dict) for entry in entries):
        return notes
    values = [entry["value"] if isinstance(entry, dict) else entry for entry in entries]
    for value in _duplicates(values):
        notes.append(f'missing value "{value}" is not unique')
    labels = [
        entry["label"]
        for entry in entries
        if isinstance(entry, dict) and entry.get("label") is not None
    ]
    for label in _duplicates(labels):
        notes.append(f'missing value label "{label}" is not unique')
    return notes


def version_gate_notes(entries: IEntries, version: Optional[str]) -> List[str]:
    """Notes when object entries appear under an explicitly declared v1 schema

    The object form `{value, label?}` is a datapackage v2 addition. It is
    rejected only when the version is explicitly resolved to v1; an undeclared
    version (`None`) stays lenient and accepts the v1 union v2 superset.
    """
    if version != "v1":
        return []
    if not any(isinstance(entry, dict) for entry in entries):
        return []
    return ["missing values in object form require datapackage v2"]


def export(
    values: List[str], labels: Dict[str, str]
) -> Union[List[str], List[Dict[str, str]]]:
    """Render the canonical descriptor form (objects iff at least one label)"""
    if not any(value in labels for value in values):
        return values
    return [
        (
            {"value": value, "label": labels[value]}
            if value in labels
            else {"value": value}
        )
        for value in values
    ]


def _duplicates(values: List[str]) -> List[str]:
    """Values appearing more than once, each reported once in order"""
    seen: set[str] = set()
    duplicates: List[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return duplicates
