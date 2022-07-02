from typing import Any
from dataclasses import dataclass, field
from ...dialect import Control
from ...system import system
from . import settings


@dataclass
class RemoteControl(Control):
    """Remote control representation"""

    code = "remote"

    # State

    http_session: Any = field(default_factory=system.get_http_session)
    """TODO: add docs"""

    http_timeout: int = settings.DEFAULT_HTTP_TIMEOUT
    """TODO: add docs"""

    http_preload: bool = False
    """TODO: add docs"""

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "code": {},
            "httpSession": {},
            "httpPreload": {"type": "boolean"},
            "httpTimeout": {"type": "number"},
        },
    }
