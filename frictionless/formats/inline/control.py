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
    """NOTE: add docs"""

    keyed: bool = False
    """NOTE: add docs"""

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "keys": {"type": "array", "items": {"type": "string"}},
            "keyed": {"type": "boolean"},
        },
    }
