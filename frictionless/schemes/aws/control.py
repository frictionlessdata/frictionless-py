import os
import attrs
from ...dialect import Control
from . import settings


@attrs.define
class AwsControl(Control):
    """Aws control representation"""

    type = "aws"

    # State

    s3_endpoint_url: str = (
        os.environ.get("S3_ENDPOINT_URL") or settings.DEFAULT_S3_ENDPOINT_URL
    )

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "name": {"type": "string"},
            "type": {"type": "string"},
            "s3EndpointUrl": {"type": "string"},
        },
    }
