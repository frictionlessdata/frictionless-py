from __future__ import annotations
import attrs
from ...dialect import Control


@attrs.define(kw_only=True)
class BufferControl(Control):
    """Buffer control representation"""

    type = "buffer"

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "type": {"type": "string"},
            "title": {"type": "string"},
            "description": {"type": "string"},
        },
    }
