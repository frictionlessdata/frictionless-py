import ijson
import tempfile
import jsonlines
import simplejson
from ..file import File
from ..parser import Parser
from ..system import system
from .. import dialects
from .. import helpers


class JsonParser(Parser):
    """JSON parser implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless import parser`

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
        dialect = self.file.dialect
        if dialect.property is not None:
            path = "%s.item" % self.file.dialect.property
        source = ijson.items(self.loader.byte_stream, path)
        file = File(source, dialect=dialects.InlineDialect(keys=dialect.keys))
        with system.create_parser(file) as parser:
            yield next(parser.data_stream)
            if parser.file.dialect.keyed:
                dialect["keyed"] = True
            yield from parser.data_stream

    # Write

    def write(self, row_stream):
        data = []
        dialect = self.file.dialect
        for row in row_stream:
            cells = list(row.values())
            cells, notes = row.schema.write_data(cells, native_types=self.native_types)
            item = dict(zip(row.schema.field_names, cells)) if dialect.keyed else cells
            if not dialect.keyed and row.row_number == 1:
                data.append(row.schema.field_names)
            data.append(item)
        with tempfile.NamedTemporaryFile("wt", delete=False) as file:
            simplejson.dump(data, file, indent=2)
        helpers.move_file(file.name, self.file.source)


class JsonlParser(Parser):
    """JSONL parser implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless import parsers`

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
        dialect = self.file.dialect
        source = iter(jsonlines.Reader(self.loader.text_stream))
        file = File(source, dialect=dialects.InlineDialect(keys=dialect.keys))
        with system.create_parser(file) as parser:
            yield next(parser.data_stream)
            if parser.file.dialect.keyed:
                dialect["keyed"] = True
            yield from parser.data_stream

    # Write

    def write(self, row_stream):
        dialect = self.file.dialect
        with tempfile.NamedTemporaryFile(delete=False) as file:
            writer = jsonlines.Writer(file)
            for row in row_stream:
                schema = row.schema
                cells = list(row.values())
                cells, notes = schema.write_data(cells, native_types=self.native_types)
                item = dict(zip(schema.field_names, cells)) if dialect.keyed else cells
                if not dialect.keyed and row.row_number == 1:
                    writer.write(schema.field_names)
                writer.write(item)
        helpers.move_file(file.name, self.file.source)
