from ...control import Control


class LocalControl(Control):
    """Local control representation"""

    code = "local"

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
    }
