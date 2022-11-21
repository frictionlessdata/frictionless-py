from __future__ import annotations
import attrs
from typing import Optional, List
from ...dialect import Control


@attrs.define(kw_only=True)
class InlineControl(Control):
    """Inline control representation.

    Control class to set params for Inline reader/writer.

    """

    type = "inline"

    # State

    keys: Optional[List[str]] = None
    """
    Specify the keys/columns to read from the resource.
    For example: keys=["id","name"].
    """

    keyed: bool = False
    """
    If set to True, It returns the data as key:value pair.
    """

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "keys": {"type": "array", "items": {"type": "string"}},
            "keyed": {"type": "boolean"},
        },
    }
