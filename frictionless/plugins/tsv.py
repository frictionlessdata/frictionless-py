import tempfile
from ..parser import Parser
from ..plugin import Plugin
from ..dialects import Dialect
from .. import helpers


# Plugin


class TsvPlugin(Plugin):
    """Plugin for TSV

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.tsv import TsvPlugin`

    """

    def create_dialect(self, resource, *, descriptor):
        if resource.format == "tsv":
            return TsvDialect(descriptor)

    def create_parser(self, resource):
        if resource.format == "tsv":
            return TsvParser(resource)


# Dialect


class TsvDialect(Dialect):
    """Tsv dialect representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.tsv import TsvDialect`

    Parameters:
        descriptor? (str|dict): descriptor

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    pass


# Parser


class TsvParser(Parser):
    """TSV parser implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.tsv import TsvParser`

    """

    native_types = [
        "string",
    ]

    # Read

    def read_data_stream_create(self):
        tsv = helpers.import_from_plugin("tsv", plugin="tsv")
        data = tsv.reader(self.loader.text_stream)
        yield from data

    # Write

    def write(self, read_row_stream):
        tsv = helpers.import_from_plugin("tsv", plugin="tsv")
        with tempfile.NamedTemporaryFile("wt", delete=False) as file:
            writer = tsv.writer(file)
            for row in read_row_stream():
                schema = row.schema
                if row.row_number == 1:
                    writer.writerow(schema.field_names)
                cells = list(row.values())
                cells, notes = schema.write_data(cells, native_types=self.native_types)
                writer.writerow(cells)
        helpers.move_file(file.name, self.resource.source)
