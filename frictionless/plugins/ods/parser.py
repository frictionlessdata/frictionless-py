import io
import tempfile
from datetime import datetime
from ...exception import FrictionlessException
from ...parser import Parser
from ...system import system
from ... import helpers
from ... import errors


class OdsParser(Parser):
    """ODS parser implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.ods import OdsParser`

    """

    requires_loader = True
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

    def read_list_stream_create(self):
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

    def write_row_stream(self, resource):
        ezodf = helpers.import_from_plugin("ezodf", plugin="ods")
        source = resource
        target = self.resource
        file = tempfile.NamedTemporaryFile(delete=False)
        file.close()
        book = ezodf.newdoc(doctype="ods", filename=file.name)
        title = f"Sheet {target.dialect.sheet}"
        book.sheets += ezodf.Sheet(title)
        sheet = book.sheets[title]
        with source:
            for row_index, row in enumerate(source.row_stream):
                if row.row_number == 1:
                    for field_index, name in enumerate(row.field_names):
                        sheet[(0, field_index)].set_value(name)
                cells = row.to_list(types=self.supported_types)
                for field_index, cell in enumerate(cells):
                    sheet[(row_index + 1, field_index)].set_value(cell)
            book.save()
        loader = system.create_loader(target)
        loader.write_byte_stream(file.name)
