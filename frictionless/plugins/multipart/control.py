from dataclasses import dataclass
from ...dialect import Control
from . import settings


@dataclass
class MultipartControl(Control):
    """Multipart control representation"""

    code = "multipart"

    # Properties

    chunk_size: int = settings.DEFAULT_CHUNK_SIZE
    """TODO: add docs"""

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "chunkSize": {"type": "number"},
        },
    }
