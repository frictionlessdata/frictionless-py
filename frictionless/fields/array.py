from __future__ import annotations

import json
from typing import Any, Dict, Optional

import attrs

from ..schema import Field


@attrs.define(kw_only=True, repr=False)
class ArrayField(Field):
    type = "array"
    builtin = True
    supported_constraints = [
        "required",
        "minLength",
        "maxLength",
        "enum",
    ]

    array_item: Optional[Dict[str, Any]] = attrs.field(factory=dict)
    """
    A dictionary that specifies the type and other constraints for the
    data that will be read in this data type field.
    """

    # Read

    def create_cell_reader(self):
        default_reader = super().create_cell_reader()

        # Create field
        field_reader = None
        if self.array_item:
            descriptor = self.array_item.copy()
            descriptor.pop("arrayItem", None)
            descriptor.setdefault("name", self.name)
            descriptor.setdefault("type", "any")
            field = Field.from_descriptor(descriptor)
            field_reader = field.create_cell_reader()

        # Create reader
        def cell_reader(cell: Any):
            cell, notes = default_reader(cell)
            if cell is not None and not notes and field_reader:
                for index, item in enumerate(cell):
                    item_cell, item_notes = field_reader(item)
                    if item_notes:
                        notes = notes or {}
                        for name, note in item_notes.items():
                            notes[name] = f"array item {note}"
                    cell[index] = item_cell
            return cell, notes

        return cell_reader

    def create_value_reader(self):
        # Create reader
        def value_reader(cell: Any):  # type: ignore
            if not isinstance(cell, list):
                if isinstance(cell, str):
                    try:
                        cell = json.loads(cell)
                    except Exception:
                        return None
                    if not isinstance(cell, list):
                        return None
                elif isinstance(cell, tuple):
                    cell = list(cell)  # type: ignore
                else:
                    return None
            return cell  # type: ignore

        return value_reader

    # Write

    def create_value_writer(self):
        # Create writer
        def value_writer(cell: Any):
            return json.dumps(cell)

        return value_writer

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "arrayItem": {"type": "object"},
        }
    }
