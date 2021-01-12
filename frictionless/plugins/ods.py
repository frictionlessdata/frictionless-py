import io
import tempfile
from datetime import datetime
from ..exception import FrictionlessException
from ..metadata import Metadata
from ..dialect import Dialect
from ..plugin import Plugin
from ..parser import Parser
from ..system import system
from .. import helpers
from .. import errors


# Plugin


class OdsPlugin(Plugin):
    """Plugin for ODS

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.ods import OdsPlugin`

    """

    def create_dialect(self, resource, *, descriptor):
        if resource.format == "ods":
            return OdsDialect(descriptor)

    def create_parser(self, resource):
        if resource.format == "ods":
            return OdsParser(resource)


# Dialect


class OdsDialect(Dialect):
    """Ods dialect representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.ods import OdsDialect`

    Parameters:
        descriptor? (str|dict): descriptor
        sheet? (str): sheet

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(self, descriptor=None, *, sheet=None):
        self.setinitial("sheet", sheet)
        super().__init__(descriptor)

    @Metadata.property
    def sheet(self):
        """
        Returns:
            int|str: sheet
        """
        return self.get("sheet", 1)

    # Expand

    def expand(self):
        """Expand metadata"""
        self.setdefault("sheet", self.sheet)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "sheet": {"type": ["number", "string"]},
        },
    }


# Parser


class OdsParser(Parser):
    """ODS parser implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.ods import OdsParser`

    """

    supported_types = [
        "boolean",
        "date",
        "datetime",
        "integer",
        "number",
        "string",
        "time",
        "year",
    ]

    # Read

    def read_data_stream_create(self):
        ezodf = helpers.import_from_plugin("ezodf", plugin="ods")
        dialect = self.resource.dialect

        # Get book
        book = ezodf.opendoc(io.BytesIO(self.loader.byte_stream.read()))

        # Get sheet
        try:
            if isinstance(dialect.sheet, str):
                sheet = book.sheets[dialect.sheet]
            else:
                sheet = book.sheets[dialect.sheet - 1]
        except (KeyError, IndexError):
            note = 'OpenOffice document "%s" does not have a sheet "%s"'
            note = note % (self.resource.fullpath, dialect.sheet)
            raise FrictionlessException(errors.FormatError(note=note))

        # Type cells
        def type_value(cell):
            """Detects int value, date and datetime"""

            ctype = cell.value_type
            value = cell.value

            # ods numbers are float only
            # float with no decimals can be cast into int
            if isinstance(value, float) and value == value // 1:
                return int(value)

            # Date or datetime
            if ctype == "date":
                if len(value) == 10:
                    return datetime.strptime(value, "%Y-%m-%d").date()
                else:
                    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")

            return value

        # Stream data
        for cells in sheet.rows():
            yield [type_value(cell) for cell in cells]

    # Write

    def write_row_stream_save(self, read_row_stream):
        ezodf = helpers.import_from_plugin("ezodf", plugin="ods")
        dialect = self.resource.dialect
        file = tempfile.NamedTemporaryFile(delete=False)
        book = ezodf.newdoc(doctype="ods", filename=file.name)
        title = f"Sheet {dialect.sheet}"
        book.sheets += ezodf.Sheet(title)
        sheet = book.sheets[title]
        for row_index, row in enumerate(read_row_stream()):
            if row.row_number == 1:
                for field_index, name in enumerate(row.field_names):
                    sheet[(0, field_index)].set_value(name)
            cells = row.to_list(types=self.supported_types)
            for field_index, cell in enumerate(cells):
                sheet[(row_index + 1, field_index)].set_value(cell)
        book.save()
        loader = system.create_loader(self.resource)
        result = loader.write_byte_stream(file.name)
        return result
