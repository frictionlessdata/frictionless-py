from __future__ import annotations
import attrs
from typing import Any
from ...dialect import Control
from ...system import system
from . import settings


@attrs.define(kw_only=True)
class RemoteControl(Control):
    """Remote control representation"""

    type = "remote"

    # State

    http_session: Any = attrs.field(factory=system.get_http_session)
    """TODO: add docs"""

    http_timeout: int = settings.DEFAULT_HTTP_TIMEOUT
    """TODO: add docs"""

    http_preload: bool = False
    """TODO: add docs"""
