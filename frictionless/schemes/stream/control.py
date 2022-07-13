from __future__ import annotations
import attrs
from ...dialect import Control


@attrs.define(kw_only=True)
class StreamControl(Control):
    """Stream control representation"""

    type = "stream"
