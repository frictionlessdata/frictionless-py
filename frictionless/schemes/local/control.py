from __future__ import annotations
import attrs
from ...dialect import Control


@attrs.define(kw_only=True)
class LocalControl(Control):
    """Local control representation"""

    type = "local"

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "name": {"type": "string"},
            "type": {"type": "string"},
        },
    }
