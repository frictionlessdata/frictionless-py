import json
import tempfile
from ....exception import FrictionlessException
from ....plugins.inline import InlineControl
from ....resource import Resource
from ..control import JsonControl
from ....dialect import Dialect
from ....parser import Parser
from ....system import system
from .... import errors
from .... import helpers


class JsonParser(Parser):
    """JSON parser implementation.
    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.json import JsonParser
    """

    requires_loader = True
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

    def read_list_stream_create(self):
        ijson = helpers.import_from_plugin("ijson", plugin="json")
        path = "item"
        control = self.resource.dialect.get_control("json", ensure=JsonControl())
        if control.property is not None:
            path = "%s.item" % control.property
        source = ijson.items(self.loader.byte_stream, path)
        inline_control = InlineControl(keys=control.keys)
        resource = Resource(data=source, dialect=Dialect(controls=[inline_control]))
        with system.create_parser(resource) as parser:
            try:
                yield next(parser.list_stream)
            except StopIteration:
                note = f'cannot extract JSON tabular data from "{self.resource.fullpath}"'
                raise FrictionlessException(errors.SourceError(note=note))
            parser_control = parser.resource.dialect.get_control("inline")
            if parser_control.keyed:
                control.keyed = True
            yield from parser.list_stream

    # Write

    def write_row_stream(self, resource):
        data = []
        source = resource
        target = self.resource
        control = target.dialect.get_control("json", ensure=JsonControl())
        with source:
            for row in source.row_stream:
                cells = row.to_list(json=True)
                item = dict(zip(row.field_names, cells)) if control.keyed else cells
                if not control.keyed and row.row_number == 1:
                    data.append(row.field_names)
                data.append(item)
        with tempfile.NamedTemporaryFile("wt", delete=False) as file:
            json.dump(data, file, indent=2)
        loader = system.create_loader(target)
        loader.write_byte_stream(file.name)
