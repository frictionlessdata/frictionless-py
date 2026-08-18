from __future__ import annotations

from typing import Any, ClassVar, List

import attrs

from .. import settings
from ..schema import Field

ITEM_TYPES = ["string", "integer", "boolean", "number", "datetime", "date", "time"]


@attrs.define(kw_only=True, repr=False)
class ListField(Field):
    type = "list"
    builtin = True
    supported_constraints = [
        "required",
        "minLength",
        "maxLength",
        "enum",
    ]

    item_types: ClassVar[List[str]] = ITEM_TYPES
    """
    Item types allowed by the standard.
    """

    delimiter: str = settings.DEFAULT_LIST_DELIMITER
    """
    The character sequence that separates the lexically represented items.
    The default value is ",".
    """

    item_type: str = settings.DEFAULT_LIST_ITEM_TYPE
    """
    The type of the list items, given as a Table Schema type. Items are read
    with the default format of that type, as the standard requires.
    The default value is "string".
    """

    # Read

    def create_value_reader(self):
        item_reader = self.__create_item_field().create_value_reader()
        delimiter = self.delimiter

        # Create reader
        def value_reader(cell: Any):
            if isinstance(cell, str):
                cell = cell.split(delimiter)
            elif isinstance(cell, tuple):
                cell = list(cell)  # type: ignore
            elif not isinstance(cell, list):
                return None
            items: List[Any] = []
            for item in cell:  # type: ignore
                item = item_reader(item)
                if item is None:
                    return None
                items.append(item)
            return items

        return value_reader

    # Write

    def create_value_writer(self):
        item_writer = self.__create_item_field().create_value_writer()
        delimiter = self.delimiter

        # Create writer
        def value_writer(cell: Any):
            return delimiter.join(item_writer(item) for item in cell)

        return value_writer

    # Internal

    def __create_item_field(self):
        return Field.from_descriptor({"name": self.name, "type": self.item_type})

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "delimiter": {"type": "string"},
            "itemType": {"type": "string", "enum": ITEM_TYPES},
        }
    }
