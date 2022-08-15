from __future__ import annotations
import attrs
from ...dialect import Control
from . import settings


@attrs.define(kw_only=True)
class RemoteControl(Control):
    """Remote control representation"""

    type = "remote"

    # State

    http_timeout: int = settings.DEFAULT_HTTP_TIMEOUT
    """NOTE: add docs"""

    http_preload: bool = False
    """NOTE: add docs"""
