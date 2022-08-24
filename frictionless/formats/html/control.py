from __future__ import annotations
import attrs
from ...dialect import Control
from . import settings


@attrs.define(kw_only=True)
class HtmlControl(Control):
    """Html control representation"""

    type = "html"

    # State

    selector: str = settings.DEFAULT_SELECTOR
    """NOTE: add docs"""

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "selector": {"type": "string"},
        },
    }
