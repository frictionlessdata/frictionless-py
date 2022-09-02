from __future__ import annotations
import attrs
from typing import Optional
from ...dialect import Control


@attrs.define(kw_only=True)
class GsheetsControl(Control):
    """Gsheets control representation"""

    type = "gsheets"

    # State

    credentials: Optional[str] = None
    """NOTE: add docs"""

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "credentials": {"type": "string"},
        },
    }
