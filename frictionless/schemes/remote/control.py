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
    """
    Specifies the time to wait, if the remote server
    does not respond before raising an error. The default
    value is 10.
    """

    http_preload: bool = False
    """
    Preloads data to the memory if set to True. It is set
    to False by default.
    """
