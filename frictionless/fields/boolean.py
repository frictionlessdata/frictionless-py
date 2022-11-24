from __future__ import annotations
import attrs
from typing import List
from ..schema import Field
from .. import settings


@attrs.define(kw_only=True)
class BooleanField(Field):
    type = "boolean"
    builtin = True
    supported_constraints = [
        "required",
        "enum",
    ]

    # Properties

    true_values: List[str] = attrs.field(factory=settings.DEFAULT_TRUE_VALUES.copy)
    """
    It defines the values to be read as true values while reading data. The default
    true values are ["true", "True", "TRUE", "1"].
    """

    false_values: List[str] = attrs.field(factory=settings.DEFAULT_FALSE_VALUES.copy)
    """
    It defines the values to be read as false values while reading data. The default
    true values are ["false", "False", "FALSE", "0"].
    """

    # Read

    def create_value_reader(self):

        # Create mapping
        mapping = {}
        for value in self.true_values:
            mapping[value] = True
        for value in self.false_values:
            mapping[value] = False

        # Create reader
        def value_reader(cell):
            if cell is True or cell is False:
                return cell
            if isinstance(cell, str):
                return mapping.get(cell)

        return value_reader

    # Write

    def create_value_writer(self):

        # Create writer
        def value_writer(cell):
            return self.true_values[0] if cell else self.false_values[0]

        return value_writer

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "trueValues": {"type": "array", "items": {"type": "string"}},
            "falseValues": {"type": "array", "items": {"type": "string"}},
        }
    }
