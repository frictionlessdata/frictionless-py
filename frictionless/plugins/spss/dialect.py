from ...dialect import Dialect


class SpssDialect(Dialect):
    """Spss dialect representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.spss import SpssDialect`

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
