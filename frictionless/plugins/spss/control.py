from ...control import Control


class SpssControl(Control):
    """Spss dialect representation"""

    code = "spss"

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
    }
