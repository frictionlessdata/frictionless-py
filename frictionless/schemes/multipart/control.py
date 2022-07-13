from __future__ import annotations
import attrs
from ...dialect import Control
from . import settings


@attrs.define(kw_only=True)
class MultipartControl(Control):
    """Multipart control representation"""

    type = "multipart"

    # State

    chunk_size: int = settings.DEFAULT_CHUNK_SIZE
    """TODO: add docs"""

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "type": {"type": "string"},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "chunkSize": {"type": "number"},
        },
    }
