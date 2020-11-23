from itertools import chain
from ..exception import FrictionlessException
from ..metadata import Metadata
from ..dialect import Dialect
from ..plugin import Plugin
from ..parser import Parser
from .. import errors


# Plugin


class InlinePlugin(Plugin):
    """Plugin for Inline

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.inline import InlinePlugin`

    """

    def create_dialect(self, resource, *, descriptor):
        # TODO: remove this hack; resolve problem with Inline/Pandas/PETL collision
        if resource.format == "inline" and not hasattr(resource.data, "query"):
            return InlineDialect(descriptor)

    def create_parser(self, resource):
        # TODO: remove this hack; resolve problem with Inline/Pandas/PETL collision
        if resource.format == "inline" and not hasattr(resource.data, "query"):
            return InlineParser(resource)


# Dialect


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


# Parser


class InlineParser(Parser):
    """Inline parser implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.inline import InlineParser

    """

    loading = False
    native_types = [
        "array",
        "boolean",
        "date",
        "datetime",
        "duration",
        "geojson",
        "geopoint",
        "integer",
        "number",
        "object",
        "string",
        "time",
        "year",
        "yearmonth",
    ]

    # Read

    def read_data_stream_create(self):
        dialect = self.resource.dialect

        # Iter
        data = self.resource.source
        if not hasattr(data, "__iter__"):
            data = data()
        data = iter(data)

        # Empty
        try:
            cells = next(data)
        except StopIteration:
            yield from []
            return

        # Keyed
        if isinstance(cells, dict):
            dialect["keyed"] = True
            headers = dialect.keys or list(cells.keys())
            yield headers
            for cells in chain([cells], data):
                if not isinstance(cells, dict):
                    error = errors.SourceError(note="all keyed data items must be dicts")
                    raise FrictionlessException(error)
                yield [cells.get(header) for header in headers]
            return

        # General
        for cells in chain([cells], data):
            if not isinstance(cells, (list, tuple)):
                error = errors.SourceError(note="all data items must be lists")
                raise FrictionlessException(error)
            yield cells

    # Write

    def write(self, read_row_stream):
        dialect = self.resource.dialect
        self.resource.data = []
        for row in read_row_stream():
            item = row.to_dict() if dialect.keyed else list(row.values())
            if not dialect.keyed and row.row_number == 1:
                self.resource.data.append(row.schema.field_names)
            self.resource.data.append(item)
