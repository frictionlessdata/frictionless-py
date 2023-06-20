from __future__ import annotations

import attrs

from ...dialect import Control
from . import settings


@attrs.define(kw_only=True, repr=False)
class MultipartControl(Control):
    """Multipart control representation"""

    type = "multipart"

    chunk_size: int = settings.DEFAULT_CHUNK_SIZE
    """
    Specifies chunk size for the multipart file.
    """

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "chunkSize": {"type": "integer"},
        },
    }
