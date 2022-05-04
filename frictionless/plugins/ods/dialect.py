from ...metadata import Metadata
from ...dialect import Dialect


class OdsDialect(Dialect):
    """Ods dialect representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.ods import OdsDialect`

    Parameters:
        descriptor? (str|dict): descriptor
        sheet? (str): sheet

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(self, descriptor=None, *, sheet=None):
        self.setinitial("sheet", sheet)
        super().__init__(descriptor)

    @Metadata.property
    def sheet(self):
        """
        Returns:
            int|str: sheet
        """
        return self.get("sheet", 1)

    # Expand

    def expand(self):
        """Expand metadata"""
        self.setdefault("sheet", self.sheet)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "sheet": {"type": ["number", "string"]},
        },
    }
