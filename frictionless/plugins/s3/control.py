import os
from ...dialect import Control
from . import settings


class S3Control(Control):
    """S3 control representation"""

    code = "s3"

    # State

    endpoint_url: str = os.environ.get("S3_ENDPOINT_URL") or settings.DEFAULT_ENDPOINT_URL

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "code": {},
            "endpointUrl": {"type": "string"},
        },
    }
