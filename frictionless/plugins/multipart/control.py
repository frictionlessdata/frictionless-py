from ...control import Control
from . import settings


class MultipartControl(Control):
    """Multipart control representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.multipart import MultipartControl`

    Parameters:
        descriptor? (str|dict): descriptor

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(self, descriptor=None, chunk_size=None):
        self.setinitial("chunkSize", chunk_size)
        super().__init__(descriptor)

    @property
    def chunk_size(self):
        return self.get("chunkSize", settings.DEFAULT_CHUNK_SIZE)

    # Expand

    def expand(self):
        """Expand metadata"""
        self.setdefault("chunkSize", self.chunk_size)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "chunkSize": {"type": "number"},
        },
    }
