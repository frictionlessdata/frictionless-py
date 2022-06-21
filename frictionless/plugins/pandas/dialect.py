from ...dialect import Dialect


class PandasDialect(Dialect):
    """Pandas dialect representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.pandas import PandasDialect`

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
