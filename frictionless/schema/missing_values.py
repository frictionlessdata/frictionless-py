from __future__ import annotations

from typing import Any, Iterator, List, Optional, Sequence, Union

import attrs
from pydantic import BaseModel, ConfigDict

from .. import settings

# Descriptor entries are either a plain string or an object with a value/label.
# Per the datapackage spec the array is homogeneous: all strings OR all objects.
IMissingValueEntry = Union[str, dict[str, str]]

# JSON Schema profile shared by Field and Schema. The "anyOf" enforces the
# homogeneity of the array (a mixed string/object array matches neither branch)
# and the uniqueness of the string entries. "anyOf" (rather than "oneOf") is
# required because an empty array matches both branches. The uniqueness of
# object "value" and "label" properties is checked in "metadata_validate".
MISSING_VALUES_PROFILE = {
    "anyOf": [
        {
            "type": "array",
            "items": {"type": "string"},
            "uniqueItems": True,
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


class MissingValue(BaseModel):
    """A single missing value with an optional human-readable label."""

    model_config = ConfigDict(frozen=True)

    value: str
    label: Optional[str] = None

    @classmethod
    def from_descriptor(cls, entry: IMissingValueEntry) -> MissingValue:
        if isinstance(entry, str):
            return cls(value=entry)
        return cls(**entry)


@attrs.frozen(eq=False)
class MissingValues:
    """A collection of missing values

    Supports both the string form (``["", "NA"]``) and the object form
    (``[{"value": "-99", "label": "REFUSED"}]``). Whether the collection
    serializes back as strings or objects is a property of the collection
    (the array is homogeneous), so a single ``as_objects`` flag preserves the
    original form losslessly.

    The collection is list-like over its value strings, so consumers that used
    to read ``missing_values`` as a ``List[str]`` keep working unchanged.
    """

    items: List[MissingValue]
    as_objects: bool = False

    @classmethod
    def from_descriptor(cls, descriptor: Sequence[IMissingValueEntry]) -> MissingValues:
        as_objects = any(isinstance(entry, dict) for entry in descriptor)
        items = [MissingValue.from_descriptor(entry) for entry in descriptor]
        return cls(items=items, as_objects=as_objects)

    def validation_notes(self) -> List[str]:
        """Notes describing why the collection is invalid (empty if valid).

        Per the spec, each object entry must have a unique value and an
        optional unique label. Labels left out do not collide with each other.
        """
        notes: List[str] = []
        values = [item.value for item in self.items]
        for value in _duplicates(values):
            notes.append(f'missing value "{value}" is not unique')
        labels = [item.label for item in self.items if item.label is not None]
        for label in _duplicates(labels):
            notes.append(f'missing value label "{label}" is not unique')
        return notes

    def to_descriptor(self) -> List[IMissingValueEntry]:
        if self.as_objects:
            return [item.model_dump(exclude_none=True) for item in self.items]
        return [item.value for item in self.items]

    def value_strings(self) -> List[str]:
        return [item.value for item in self.items]

    @property
    def representation(self) -> str:
        """The string written to represent a missing cell when serializing.

        Falls back to the spec default missing value ("") when the collection
        is empty.
        """
        if self.items:
            return self.items[0].value
        return settings.DEFAULT_MISSING_VALUES[0]

    # List-like over value strings (backward compatibility)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, MissingValues):
            return (self.items, self.as_objects) == (other.items, other.as_objects)
        return self.value_strings() == other

    def __hash__(self) -> int:
        return hash((tuple(self.items), self.as_objects))

    def __iter__(self) -> Iterator[str]:
        return iter(self.value_strings())

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> str:
        return self.value_strings()[index]

    def __contains__(self, cell: str) -> bool:
        return any(item.value == cell for item in self.items)


def _duplicates(values: List[str]) -> List[str]:
    """Values appearing more than once, each reported once in order."""
    seen: set[str] = set()
    duplicates: List[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return duplicates
