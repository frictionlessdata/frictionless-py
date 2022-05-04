from ...control import Control


class LocalControl(Control):
    """Local control representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.local import LocalControl`

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
