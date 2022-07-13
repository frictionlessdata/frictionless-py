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

    metadata_profile_patch = {
        "properties": {
            "keys": {"type": "array"},
            "keyed": {"type": "boolean"},
        },
    }
