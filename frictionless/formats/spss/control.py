from ...dialect import Control


class SpssControl(Control):
    """Spss dialect representation"""

    type = "spss"

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "name": {"type": "string"},
            "type": {"type": "string"},
        },
    }
