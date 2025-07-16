from __future__ import annotations

from typing import List

import attrs

from .. import settings
from ..schema import Field


@attrs.define(kw_only=True, repr=False)
class BooleanField(Field):
    type = "boolean"
    builtin = True
    supported_constraints = [
        "required",
        "enum",
    ]

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

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "trueValues": {"type": "array", "items": {"type": "string"}},
            "falseValues": {"type": "array", "items": {"type": "string"}},
        }
    }
