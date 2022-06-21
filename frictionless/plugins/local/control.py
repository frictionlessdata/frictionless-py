from ...control import Control


class LocalControl(Control):
    """Local control representation"""

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
    }
