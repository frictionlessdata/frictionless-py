from ...metadata import Metadata
from ...dialect import Dialect


class HtmlDialect(Dialect):
    """Html dialect representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.html import HtmlDialect`

    Parameters:
        descriptor? (str|dict): descriptor
        selector? (str): HTML selector

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(self, descriptor=None, *, selector=None):
        self.setinitial("selector", selector)
        super().__init__(descriptor)

    @Metadata.property
    def selector(self):
        """
        Returns:
            str: selector
        """
        return self.get("selector", "table")

    # Expand

    def expand(self):
        """Expand metadata"""
        self.setdefault("selector", self.selector)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "selector": {"type": "string"},
        },
    }
