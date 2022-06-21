from ...control import Control


class BufferControl(Control):
    """Buffer control representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.buffer import BufferControl`

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
