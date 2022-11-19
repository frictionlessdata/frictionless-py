from __future__ import annotations
from ...exception import FrictionlessException
from ...system import Parser
from ... import errors
from .control import InlineControl


class InlineParser(Parser):
    """Inline parser implementation."""

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

    def read_cell_stream_create(self):
        control = InlineControl.from_dialect(self.resource.dialect)

        # Iter
        data = self.resource.normdata
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
            control.keyed = True
            headers = control.keys or list(item.keys())
            yield headers
            yield [item.get(header) for header in headers]
            for item in data:
                if not isinstance(item, dict):
                    error = errors.SourceError(note="unsupported inline data")
                    raise FrictionlessException(error)
                yield [item.get(header) for header in headers]

        # General
        elif isinstance(item, (list, tuple)):
            yield item
            for item in data:
                if not isinstance(item, (list, tuple)):
                    error = errors.SourceError(note="unsupported inline data")
                    raise FrictionlessException(error)
                yield item

        # Unsupported
        else:
            error = errors.SourceError(note="unsupported inline data")
            raise FrictionlessException(error)

    # Write

    def write_row_stream(self, source):
        data = []
        control = InlineControl.from_dialect(self.resource.dialect)
        with source:
            if not control.keyed:
                data.append(source.schema.field_names)
            for row in source.row_stream:
                item = row.to_dict() if control.keyed else row.to_list()
                data.append(item)
        self.resource.data = data
