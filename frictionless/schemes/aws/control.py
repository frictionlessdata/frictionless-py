from __future__ import annotations
import os
import attrs
from ...dialect import Control
from . import settings


@attrs.define(kw_only=True)
class AwsControl(Control):
    """Aws control representation"""

    type = "aws"

    # State

    s3_endpoint_url: str = (
        os.environ.get("S3_ENDPOINT_URL") or settings.DEFAULT_S3_ENDPOINT_URL
    )

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "s3EndpointUrl": {"type": "string"},
        },
    }
