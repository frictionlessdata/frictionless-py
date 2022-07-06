import os
from ...dialect import Control
from . import settings


class AwsControl(Control):
    """Aws control representation"""

    code = "aws"

    # State

    s3_endpoint_url: str = (
        os.environ.get("S3_ENDPOINT_URL") or settings.DEFAULT_S3_ENDPOINT_URL
    )

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "code": {},
            "s3EndpointUrl": {"type": "string"},
        },
    }
