from ...control import Control


class StreamControl(Control):
    """Stream control representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.stream import StreamControl`

    Parameters:
        descriptor? (str|dict): descriptor

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
    }
