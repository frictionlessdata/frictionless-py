import json
import tempfile
from ....exception import FrictionlessException
from ....plugins.inline import InlineDialect
from ....resource import Resource
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
        dialect = self.resource.dialect
        if dialect.property is not None:
            path = "%s.item" % self.resource.dialect.property
        source = ijson.items(self.loader.byte_stream, path)
        inline_dialect = InlineDialect(keys=dialect.keys)
        resource = Resource(data=source, dialect=inline_dialect)
        with system.create_parser(resource) as parser:
            try:
                yield next(parser.list_stream)
            except StopIteration:
                note = f'cannot extract JSON tabular data from "{self.resource.fullpath}"'
                raise FrictionlessException(errors.SourceError(note=note))
            if parser.resource.dialect.keyed:
                dialect["keyed"] = True
            yield from parser.list_stream

    # Write

    def write_row_stream(self, resource):
        data = []
        source = resource
        target = self.resource
        keyed = target.dialect.keyed
        with source:
            for row in source.row_stream:
                cells = row.to_list(json=True)
                item = dict(zip(row.field_names, cells)) if keyed else cells
                if not target.dialect.keyed and row.row_number == 1:
                    data.append(row.field_names)
                data.append(item)
        with tempfile.NamedTemporaryFile("wt", delete=False) as file:
            json.dump(data, file, indent=2)
        loader = system.create_loader(target)
        loader.write_byte_stream(file.name)
