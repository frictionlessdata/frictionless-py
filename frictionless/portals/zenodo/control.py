from __future__ import annotations
import attrs
from typing import Optional
from ...dialect import Control


@attrs.define(kw_only=True)
class ZenodoControl(Control):
    """Zenodo control representation"""

    type = "github"

    # State

    record: Optional[str] = None
    """NOTE: add docs"""

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "record": {"type": "string"},
        },
    }
