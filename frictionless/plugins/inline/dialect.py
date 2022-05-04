from ...metadata import Metadata
from ...dialect import Dialect


# NOTE:
# Consider renaming keys/data_keys to labels due to dict.keys conflict


class InlineDialect(Dialect):
    """Inline dialect representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.inline import InlineDialect`

    Parameters:
        descriptor? (str|dict): descriptor
        keys? (str[]): a list of strings to use as data keys
        keyed? (bool): whether data rows are keyed

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(self, descriptor=None, *, keys=None, keyed=None):
        self.setinitial("keys", keys)
        self.setinitial("keyed", keyed)
        super().__init__(descriptor)

    @Metadata.property
    def data_keys(self):
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
        },
    }
