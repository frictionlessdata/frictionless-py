from __future__ import annotations
import json
import ijson
import tempfile
from ....exception import FrictionlessException
from ...inline import InlineControl
from ..control import JsonControl
from ....resource import Resource
from ....dialect import Dialect
from ....resource import Parser
from ....system import system
from .... import errors


class JsonParser(Parser):
    """JSON parser implementation."""

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

    def read_cell_stream_create(self):
        path = "item"
        control = JsonControl.from_dialect(self.resource.dialect)
        if control.property is not None:
            path = "%s.item" % control.property
        source = ijson.items(self.loader.byte_stream, path)
        inline_control = InlineControl(keys=control.keys)
        resource = Resource(
            data=source,
            format="inline",
            dialect=Dialect(controls=[inline_control]),
        )
        with system.create_parser(resource) as parser:
            try:
                yield next(parser.cell_stream)  # type: ignore
            except StopIteration:
                note = f'cannot extract JSON tabular data from "{self.resource.fullpath}"'
                raise FrictionlessException(errors.SourceError(note=note))
            parser_control = InlineControl.from_dialect(parser.resource.dialect)
            if parser_control.keyed:
                control.keyed = True
            yield from parser.cell_stream

    # Write

    def write_row_stream(self, source):
        data = []
        control = JsonControl.from_dialect(self.resource.dialect)
        with source:
            if not control.keyed:
                data.append(source.schema.field_names)
            for row in source.row_stream:
                cells = row.to_list(json=True)
                item = dict(zip(row.field_names, cells)) if control.keyed else cells
                data.append(item)
        with tempfile.NamedTemporaryFile("wt", delete=False) as file:
            json.dump(data, file, indent=2)
        loader = system.create_loader(self.resource)
        loader.write_byte_stream(file.name)
