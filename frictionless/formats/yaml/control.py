from __future__ import annotations
import attrs
from typing import Optional, List
from ...dialect import Control


@attrs.define(kw_only=True)
class YamlControl(Control):
    """Yaml control representation."""

    type = "yaml"

    # State

    keys: Optional[List[str]] = None
    """
    Specifies the keys/columns to read from the resource.
    For example: keys=["id","name"].
    """

    keyed: bool = False
    """
    If set to True, It returns the data as key:value pair. Default value is False.
    """

    property: Optional[str] = None
    """
    This property specifies the path to the attribute in a json file, it it has
    nested fields.
    """

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "keys": {"type": "array", "items": {"type": "string"}},
            "keyed": {"type": "boolean"},
            "property": {"type": "string"},
        },
    }
