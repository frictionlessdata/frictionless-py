from ...exception import FrictionlessException
from ...parser import Parser
from ... import errors


class InlineParser(Parser):
    """Inline parser implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.inline import InlineParser

    """

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

    def read_list_stream_create(self):
        dialect = self.resource.dialect

        # Iter
        data = self.resource.data
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
            dialect["keyed"] = True
            headers = dialect.data_keys or list(item.keys())
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

    def write_row_stream(self, resource):
        data = []
        source = resource
        target = self.resource
        with source:
            for row in source.row_stream:
                item = row.to_dict() if target.dialect.keyed else row.to_list()
                if not target.dialect.keyed and row.row_number == 1:
                    data.append(row.field_names)
                data.append(item)
        target.data = data
