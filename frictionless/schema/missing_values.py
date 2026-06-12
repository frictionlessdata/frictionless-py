"""Helpers for the `missingValues` property, shared by Schema and Field.

Datapackage v2 allows object entries `{value, label?}` alongside plain
strings. The canonical in-memory model keeps `missing_values` as a list of
strings plus a side-car mapping of labels: the split (import) is shape-driven,
never version-driven, and the export emits object entries if and only if at
least one current value has a label.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple, Union

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
