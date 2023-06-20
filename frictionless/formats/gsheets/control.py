from __future__ import annotations

from typing import Optional

import attrs

from ...dialect import Control


@attrs.define(kw_only=True, repr=False)
class GsheetsControl(Control):
    """Gsheets control representation.

    Control class to set params for Gsheets api.

    """

    type = "gsheets"

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
