from ...dialect import Control


class StreamControl(Control):
    """Stream control representation"""

    type = "stream"

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "type": {},
        },
    }
