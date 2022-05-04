from ...metadata import Metadata
from ...dialect import Dialect


class JsonDialect(Dialect):
    """Json dialect representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.json import JsonDialect`

    Parameters:
        descriptor? (str|dict): descriptor
        keys? (str[]): a list of strings to use as data keys
        keyed? (bool): whether data rows are keyed
        property? (str): a path within JSON to the data

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(
        self,
        descriptor=None,
        *,
        keys=None,
        keyed=None,
        property=None,
    ):
        self.setinitial("keys", keys)
        self.setinitial("keyed", keyed)
        self.setinitial("property", property)
        super().__init__(descriptor)

    @Metadata.property
    def keys(self):
        """
        Returns:
            str[]?: keys
        """
        return self.get("keys")

    @Metadata.property
    def keyed(self):
        """
        Returns:
            bool: keyed
        """
        return self.get("keyed", False)

    @Metadata.property
    def property(self):
        """
        Returns:
            str?: property
        """
        return self.get("property")

    # Expand

    def expand(self):
        """Expand metadata"""
        self.setdefault("keyed", self.keyed)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "keys": {"type": "array"},
            "keyed": {"type": "boolean"},
            "property": {"type": "string"},
        },
    }
