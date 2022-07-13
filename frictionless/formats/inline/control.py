from __future__ import annotations
import attrs
from typing import Optional, List
from ...dialect import Control


@attrs.define(kw_only=True)
class InlineControl(Control):
    """Inline control representation"""

    type = "inline"

    # State

    keys: Optional[List[str]] = None
    """TODO: add docs"""

    keyed: bool = False
    """TODO: add docs"""

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "type": {"type": "string"},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "keys": {"type": "array"},
            "keyed": {"type": "boolean"},
        },
    }
