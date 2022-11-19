from __future__ import annotations
import io
import tempfile
from datetime import datetime
from ...exception import FrictionlessException
from ...platform import platform
from .control import OdsControl
from ...system import system, Parser
from ... import errors


class OdsParser(Parser):
    """ODS parser implementation."""

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

    def read_cell_stream_create(self):
        control = OdsControl.from_dialect(self.resource.dialect)

        # Get book
        book = platform.ezodf.opendoc(io.BytesIO(self.loader.byte_stream.read()))

        # Get sheet
        try:
            if isinstance(control.sheet, str):
                sheet = book.sheets[control.sheet]
            else:
                sheet = book.sheets[control.sheet - 1]
        except (KeyError, IndexError):
            note = 'OpenOffice document "%s" does not have a sheet "%s"'
            note = note % (self.resource.normpath, control.sheet)
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
                if len(value) == 10:  # type: ignore
                    return datetime.strptime(value, "%Y-%m-%d").date()  # type: ignore
                else:
                    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")  # type: ignore

            return value

        # Stream data
        for cells in sheet.rows():
            yield [type_value(cell) for cell in cells]

    # Write

    def write_row_stream(self, source):
        control = OdsControl.from_dialect(self.resource.dialect)
        file = tempfile.NamedTemporaryFile(delete=False)
        file.close()
        book = platform.ezodf.newdoc(doctype="ods", filename=file.name)
        title = f"Sheet {control.sheet}"
        book.sheets += platform.ezodf.Sheet(title)
        sheet = book.sheets[title]
        with source:
            for field_index, name in enumerate(source.schema.field_names):
                sheet[(0, field_index)].set_value(name)
            for row_index, row in enumerate(source.row_stream):
                cells = row.to_list(types=self.supported_types)
                for field_index, cell in enumerate(cells):
                    sheet[(row_index + 1, field_index)].set_value(cell)
            book.save()
        loader = system.create_loader(self.resource)
        loader.write_byte_stream(file.name)
