from __future__ import annotations
import attrs
from typing import Optional, List
from ...dialect import Control


@attrs.define(kw_only=True)
class JsonControl(Control):
    """Json control representation"""

    type = "json"

    # State

    keys: Optional[List[str]] = None
    """NOTE: add docs"""

    keyed: bool = False
    """NOTE: add docs"""

    property: Optional[str] = None
    """NOTE: add docs"""

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "keys": {"type": "array", "items": {"type": "string"}},
            "keyed": {"type": "boolean"},
            "property": {"type": "string"},
        },
    }
