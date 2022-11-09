from __future__ import annotations
import attrs
from ...dialect import Control
from . import settings


@attrs.define(kw_only=True)
class HtmlControl(Control):
    """Html control representation.


    Control class to set params for Html reader/writer.

    """

    type = "html"

    # State

    selector: str = settings.DEFAULT_SELECTOR
    """
    Any valid css selector. Default selector is 'table'.
    For example: "table", "#id", ".meme" etc.
    """

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "selector": {"type": "string"},
        },
    }
