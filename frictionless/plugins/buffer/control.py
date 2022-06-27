from ...dialect import Control


class BufferControl(Control):
    """Buffer control representation"""

    code = "buffer"

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
    }
