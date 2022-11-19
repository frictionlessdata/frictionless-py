from __future__ import annotations
import tempfile
from ....platform import platform
from ...inline import InlineControl
from ....resource import Resource
from ..control import JsonControl
from ....system import system, Parser


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

    def read_cell_stream_create(self):
        control = JsonControl.from_dialect(self.resource.dialect)
        source = iter(platform.jsonlines.Reader(self.loader.text_stream))
        inline_control = InlineControl(keys=control.keys)
        with Resource(data=source, format="inline", control=inline_control) as resource:
            yield next(resource.cell_stream)  # type: ignore
            inline_control = InlineControl.from_dialect(resource.dialect)
            if inline_control.keyed:
                control.keyed = True
            yield from resource.cell_stream

    # Write

    def write_row_stream(self, source):
        control = JsonControl.from_dialect(self.resource.dialect)
        with tempfile.NamedTemporaryFile(delete=False) as file:
            writer = platform.jsonlines.Writer(file)
            with source:
                if not control.keyed:
                    writer.write(source.schema.field_names)
                for row in source.row_stream:
                    cells = row.to_list(json=True)
                    item = dict(zip(row.field_names, cells)) if control.keyed else cells
                    writer.write(item)
        loader = system.create_loader(self.resource)
        loader.write_byte_stream(file.name)
