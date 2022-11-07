from __future__ import annotations
import attrs
from typing import Optional
from ...dialect import Control


@attrs.define(kw_only=True)
class GsheetsControl(Control):
    """Gsheets control representation.

    Control class to set params for Gsheets api.

    """

    type = "gsheets"

    # State

    credentials: Optional[str] = None
    """
    API key to access google sheets.
    """

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "credentials": {"type": "string"},
        },
    }
