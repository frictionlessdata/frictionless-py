from ...dialect import Control


class BufferControl(Control):
    """Buffer control representation"""

    type = "buffer"

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "name": {"type": "string"},
            "type": {"type": "string"},
        },
    }
