from .metadata import Metadata
from . import errors
from . import config


class Dialect(Metadata):
    """Dialect representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import dialects`

    Parameters:
        descriptor? (str|dict): descriptor
        header? (bool): whether there is a header row
        headerRows? (int[]): row numbers of header rows
        headerJoin? (str): a multiline header joiner
        headerCase? (bool): case sensitive header

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(
        self,
        descriptor=None,
        header=None,
        header_rows=None,
        header_join=None,
        header_case=None,
    ):
        self.setinitial("header", header)
        self.setinitial("headerRows", header_rows)
        self.setinitial("headerJoin", header_join)
        self.setinitial("headerCase", header_case)
        super().__init__(descriptor)

    @Metadata.property
    def header(self):
        """
        Returns:
            bool: if there is a header row
        """
        return self.get("header", config.DEFAULT_HEADER)

    @Metadata.property
    def header_rows(self):
        """
        Returns:
            int[]: header rows
        """
        return self.get("headerRows", config.DEFAULT_HEADER_ROWS)

    @Metadata.property
    def header_join(self):
        """
        Returns:
            str: header joiner
        """
        return self.get("headerJoin", config.DEFAULT_HEADER_JOIN)

    @Metadata.property
    def header_case(self):
        """
        Returns:
            str: header case sensitive
        """
        return self.get("headerCase", config.DEFAULT_HEADER_CASE)

    # Expand

    def expand(self):
        """Expand metadata"""
        self.setdefault("header", self.header)
        self.setdefault("headerRows", self.header_rows)
        self.setdefault("headerJoin", self.header_join)
        self.setdefault("headerCase", self.header_case)

    # Metadata

    metadata_Error = errors.DialectError
    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "header": {"type": "boolean"},
            "headerRows": {"type": "array", "items": {"type": "number"}},
            "headerJoin": {"type": "string"},
            "headerCase": {"type": "boolean"},
        },
    }


class InlineDialect(Dialect):
    """Inline dialect representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import dialects`

    Parameters:
        descriptor? (str|dict): descriptor
        keys? (str[]): a list of strings to use as data keys
        keyed? (bool): whether data rows are keyed

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(
        self,
        descriptor=None,
        *,
        keys=None,
        keyed=None,
        header=None,
        header_rows=None,
        header_join=None,
        header_case=None,
    ):
        self.setinitial("keys", keys)
        self.setinitial("keyed", keyed)
        super().__init__(
            descriptor=descriptor,
            header=header,
            header_rows=header_rows,
            header_join=header_join,
            header_case=header_case,
        )

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
            "header": {"type": "boolean"},
            "headerRows": {"type": "array", "items": {"type": "number"}},
            "headerJoin": {"type": "string"},
            "headerCase": {"type": "boolean"},
        },
    }


class JsonDialect(Dialect):
    """Json dialect representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import dialects`

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
        header=None,
        header_rows=None,
        header_join=None,
        header_case=None,
    ):
        self.setinitial("keys", keys)
        self.setinitial("keyed", keyed)
        self.setinitial("property", property)
        super().__init__(
            descriptor=descriptor,
            header=header,
            header_rows=header_rows,
            header_join=header_join,
            header_case=header_case,
        )

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
        super().expand()
        self.setdefault("keyed", self.keyed)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "keys": {"type": "array"},
            "keyed": {"type": "boolean"},
            "property": {"type": "string"},
            "header": {"type": "boolean"},
            "headerRows": {"type": "array", "items": {"type": "number"}},
            "headerJoin": {"type": "string"},
            "headerCase": {"type": "boolean"},
        },
    }
