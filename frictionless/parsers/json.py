import ijson
import tempfile
import jsonlines
import simplejson
from ..resource import Resource
from ..parser import Parser
from ..system import system
from .. import exceptions
from .. import dialects
from .. import helpers
from .. import errors


class JsonParser(Parser):
    """JSON parser implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless import parsers

    """

    native_types = [
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
        path = "item"
        dialect = self.resource.dialect
        if dialect.property is not None:
            path = "%s.item" % self.resource.dialect.property
        source = ijson.items(self.loader.byte_stream, path)
        inline_dialect = dialects.InlineDialect(keys=dialect.keys)
        resource = Resource.from_source(source, dialect=inline_dialect)
        with system.create_parser(resource) as parser:
            try:
                yield next(parser.data_stream)
            except StopIteration:
                error = errors.SourceError(note="cannot extract tabular data from JSON")
                raise exceptions.FrictionlessException(error)
            if parser.resource.dialect.keyed:
                dialect["keyed"] = True
            yield from parser.data_stream

    # Write

    def write(self, read_row_stream):
        data = []
        dialect = self.resource.dialect
        for row in read_row_stream():
            cells = list(row.values())
            cells, notes = row.schema.write_data(cells, native_types=self.native_types)
            item = dict(zip(row.schema.field_names, cells)) if dialect.keyed else cells
            if not dialect.keyed and row.row_number == 1:
                data.append(row.schema.field_names)
            data.append(item)
        with tempfile.NamedTemporaryFile("wt", delete=False) as file:
            simplejson.dump(data, file, indent=2)
        helpers.move_file(file.name, self.resource.source)


class JsonlParser(Parser):
    """JSONL parser implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless import parsers

    """

    native_types = [
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
        dialect = self.resource.dialect
        source = iter(jsonlines.Reader(self.loader.text_stream))
        dialect = dialects.InlineDialect(keys=dialect.keys)
        resource = Resource.from_source(source, dialect=dialect)
        with system.create_parser(resource) as parser:
            yield next(parser.data_stream)
            if parser.resource.dialect.keyed:
                dialect["keyed"] = True
            yield from parser.data_stream

    # Write

    def write(self, read_row_stream):
        dialect = self.resource.dialect
        with tempfile.NamedTemporaryFile(delete=False) as file:
            writer = jsonlines.Writer(file)
            for row in read_row_stream():
                schema = row.schema
                cells = list(row.values())
                cells, notes = schema.write_data(cells, native_types=self.native_types)
                item = dict(zip(schema.field_names, cells)) if dialect.keyed else cells
                if not dialect.keyed and row.row_number == 1:
                    writer.write(schema.field_names)
                writer.write(item)
        helpers.move_file(file.name, self.resource.source)
