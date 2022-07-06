import tempfile
from ...inline import InlineControl
from ....resource import Resource
from ..control import JsonControl
from ....dialect import Dialect
from ....resource import Parser
from ....system import system
from .... import helpers


class JsonlParser(Parser):
    """JSONL parser implementation."""

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
        control = self.resource.dialect.get_control("json", ensure=JsonControl())
        source = iter(jsonlines.Reader(self.loader.text_stream))
        inline_control = InlineControl(keys=control.keys)
        resource = Resource(
            data=source,
            format="inline",
            dialect=Dialect(controls=[control]),
        )
        with system.create_parser(resource) as parser:
            yield next(parser.list_stream)
            parser_control = parser.resource.dialect.get_control("inline")
            if parser_control.keyed:
                control.keyed = True
            yield from parser.list_stream

    # Write

    def write_row_stream(self, resource):
        jsonlines = helpers.import_from_plugin("jsonlines", plugin="json")
        source = resource
        target = self.resource
        control = target.dialect.get_control("json", ensure=JsonControl())
        with tempfile.NamedTemporaryFile(delete=False) as file:
            writer = jsonlines.Writer(file)
            with source:
                if not control.keyed:
                    writer.write(source.schema.field_names)
                for row in source.row_stream:
                    cells = row.to_list(json=True)
                    item = dict(zip(row.field_names, cells)) if control.keyed else cells
                    writer.write(item)
        loader = system.create_loader(target)
        loader.write_byte_stream(file.name)
