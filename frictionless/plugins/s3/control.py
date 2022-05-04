import os
from ...control import Control
from . import settings


class S3Control(Control):
    """S3 control representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.s3 import S3Control`

    Parameters:
        descriptor? (str|dict): descriptor
        endpoint_url? (string): endpoint url

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(self, descriptor=None, endpoint_url=None):
        self.setinitial("endpointUrl", endpoint_url)
        super().__init__(descriptor)

    @property
    def endpoint_url(self):
        return (
            self.get("endpointUrl")
            or os.environ.get("S3_ENDPOINT_URL")
            or settings.DEFAULT_ENDPOINT_URL
        )

    # Expand

    def expand(self):
        """Expand metadata"""
        self.setdefault("endpointUrl", self.endpoint_url)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "endpointUrl": {"type": "string"},
        },
    }
