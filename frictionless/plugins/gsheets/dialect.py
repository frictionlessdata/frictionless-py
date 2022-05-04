from ...dialect import Dialect
from ...metadata import Metadata


class GsheetsDialect(Dialect):
    """Gsheets dialect representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.gsheets import GsheetsDialect`

    Parameters:
        descriptor? (str|dict): descriptor

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(self, descriptor=None, *, credentials=None):
        self.setinitial("credentials", credentials)
        super().__init__(descriptor)

    @Metadata.property
    def credentials(self):
        """
        Returns:
            str: credentials
        """
        return self.get("credentials")

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "credentials": {"type": "string"},
        },
    }
