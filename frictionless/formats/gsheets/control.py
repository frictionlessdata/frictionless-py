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
    """TODO: add docs"""

    # Metadata

    metadata_profile = Control.metadata_merge(
        {
            "properties": {
                "credentials": {"type": "string"},
            },
        }
    )
