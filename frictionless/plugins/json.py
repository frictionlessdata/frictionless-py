import json
import tempfile
from ..plugins.inline import InlineDialect
from ..exception import FrictionlessException
from ..metadata import Metadata
from ..resource import Resource
from ..dialect import Dialect
from ..plugin import Plugin
from ..parser import Parser
from ..system import system
from .. import helpers
from .. import errors


# Plugin


class JsonPlugin(Plugin):
    """Plugin for Json

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.json import JsonPlugin`

    """

    def create_dialect(self, resource, *, descriptor):
        if resource.format in ["json", "jsonl", "ndjson"]:
            return JsonDialect(descriptor)

    def create_parser(self, resource):
        if resource.format == "json":
            return JsonParser(resource)
        elif resource.format in ["jsonl", "ndjson"]:
            return JsonlParser(resource)


# Dialect


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


# Parser


class JsonParser(Parser):
    """JSON parser implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.json import JsonParser

    """

    supported_types = [
        "array",
        "boolean",
        "geojson",
        "integer",
        "object",
        "string",
        "year",
    ]

    # Read

    def read_data_stream_create(self, dialect=None):
        ijson = helpers.import_from_plugin("ijson", plugin="json")
        path = "item"
        dialect = self.resource.dialect
        if dialect.property is not None:
            path = "%s.item" % self.resource.dialect.property
        source = ijson.items(self.loader.byte_stream, path)
        inline_dialect = InlineDialect(keys=dialect.keys)
        resource = Resource(data=source, dialect=inline_dialect)
        with system.create_parser(resource) as parser:
            try:
                yield next(parser.data_stream)
            except StopIteration:
                note = f'cannot extract JSON tabular data from "{self.resource.fullpath}"'
                raise FrictionlessException(errors.SourceError(note=note))
            if parser.resource.dialect.keyed:
                dialect["keyed"] = True
            yield from parser.data_stream

    # Write

    def write_row_stream_save(self, read_row_stream):
        data = []
        dialect = self.resource.dialect
        for row in read_row_stream():
            cells = row.to_list(json=True)
            item = dict(zip(row.field_names, cells)) if dialect.keyed else cells
            if not dialect.keyed and row.row_number == 1:
                data.append(row.field_names)
            data.append(item)
        with tempfile.NamedTemporaryFile("wt", delete=False) as file:
            json.dump(data, file, indent=2)
        loader = system.create_loader(self.resource)
        result = loader.write_byte_stream(file.name)
        return result


class JsonlParser(Parser):
    """JSONL parser implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.json import JsonlParser

    """

    supported_types = [
        "array",
        "boolean",
        "geojson",
        "integer",
        "number",
        "object",
        "string",
        "year",
    ]

    # Read

    def read_data_stream_create(self, dialect=None):
        jsonlines = helpers.import_from_plugin("jsonlines", plugin="json")
        dialect = self.resource.dialect
        source = iter(jsonlines.Reader(self.loader.text_stream))
        dialect = InlineDialect(keys=dialect.keys)
        resource = Resource(data=source, dialect=dialect)
        with system.create_parser(resource) as parser:
            yield next(parser.data_stream)
            if parser.resource.dialect.keyed:
                dialect["keyed"] = True
            yield from parser.data_stream

    # Write

    def write_row_stream_save(self, read_row_stream):
        jsonlines = helpers.import_from_plugin("jsonlines", plugin="json")
        dialect = self.resource.dialect
        with tempfile.NamedTemporaryFile(delete=False) as file:
            writer = jsonlines.Writer(file)
            for row in read_row_stream():
                cells = row.to_list(json=True)
                item = dict(zip(row.field_names, cells)) if dialect.keyed else cells
                if not dialect.keyed and row.row_number == 1:
                    writer.write(row.field_names)
                writer.write(item)
        loader = system.create_loader(self.resource)
        result = loader.write_byte_stream(file.name)
        return result
