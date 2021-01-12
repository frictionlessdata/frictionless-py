import typing
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

    def create_file(self, file):
        if not file.scheme and not file.format and file.memory:
            types = (list, typing.Iterator, typing.Generator)
            if callable(file.data) or isinstance(file.data, types):
                file.scheme = ""
                file.format = "inline"
                return file

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

    def __init__(self, descriptor=None, *, keys=None, keyed=None):
        self.setinitial("keys", keys)
        self.setinitial("keyed", keyed)
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


# Parser


class InlineParser(Parser):
    """Inline parser implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.inline import InlineParser

    """

    needs_loader = False
    supported_types = [
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
        data = self.resource.data
        if not hasattr(data, "__iter__"):
            data = data()
        data = iter(data)

        # Empty
        try:
            item = next(data)
        except StopIteration:
            yield from []
            return

        # Row
        if hasattr(item, "cells"):
            # Shall we yield field_names or header here?
            yield item.field_names
            yield item.cells
            for item in data:
                yield item.cells

        # Keyed
        elif isinstance(item, dict):
            dialect["keyed"] = True
            headers = dialect.keys or list(item.keys())
            yield headers
            yield [item.get(header) for header in headers]
            for item in data:
                # TODO: measure/optimize
                if not isinstance(item, dict):
                    error = errors.SourceError(note="unsupported inline data")
                    raise FrictionlessException(error)
                yield [item.get(header) for header in headers]

        # General
        elif isinstance(item, (list, tuple)):
            yield item
            for item in data:
                # TODO: measure/optimize
                if not isinstance(item, (list, tuple)):
                    error = errors.SourceError(note="unsupported inline data")
                    raise FrictionlessException(error)
                yield item

        # Unsupported
        else:
            error = errors.SourceError(note="unsupported inline data")
            raise FrictionlessException(error)

    # Write

    def write_row_stream_save(self, read_row_stream):
        data = []
        dialect = self.resource.dialect
        for row in read_row_stream():
            item = row.to_dict() if dialect.keyed else row.to_list()
            if not dialect.keyed and row.row_number == 1:
                self.resource.data.append(row.field_names)
            data.append(item)
        return data
