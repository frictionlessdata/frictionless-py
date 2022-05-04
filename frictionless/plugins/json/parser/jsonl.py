import tempfile
from ....plugins.inline import InlineDialect
from ....resource import Resource
from ....parser import Parser
from ....system import system
from .... import helpers


class JsonlParser(Parser):
    """JSONL parser implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.json import JsonlParser

    """

    requires_loader = True
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

    def read_list_stream_create(self):
        jsonlines = helpers.import_from_plugin("jsonlines", plugin="json")
        dialect = self.resource.dialect
        source = iter(jsonlines.Reader(self.loader.text_stream))
        dialect = InlineDialect(keys=dialect.keys)
        resource = Resource(data=source, dialect=dialect)
        with system.create_parser(resource) as parser:
            yield next(parser.list_stream)
            if parser.resource.dialect.keyed:
                dialect["keyed"] = True
            yield from parser.list_stream

    # Write

    def write_row_stream(self, resource):
        jsonlines = helpers.import_from_plugin("jsonlines", plugin="json")
        source = resource
        target = self.resource
        keyed = target.dialect.keyed
        with tempfile.NamedTemporaryFile(delete=False) as file:
            writer = jsonlines.Writer(file)
            with source:
                for row in source.row_stream:
                    cells = row.to_list(json=True)
                    item = dict(zip(row.field_names, cells)) if keyed else cells
                    if not target.dialect.keyed and row.row_number == 1:
                        writer.write(row.field_names)
                    writer.write(item)
        loader = system.create_loader(target)
        loader.write_byte_stream(file.name)
