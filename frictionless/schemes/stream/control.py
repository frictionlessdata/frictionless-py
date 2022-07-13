from __future__ import annotations
import attrs
from ...dialect import Control


@attrs.define(kw_only=True)
class StreamControl(Control):
    """Stream control representation"""

    type = "stream"

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "name": {"type": "string"},
            "type": {"type": "string"},
        },
    }
