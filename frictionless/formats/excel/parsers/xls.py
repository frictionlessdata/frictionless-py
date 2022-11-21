from __future__ import annotations
import sys
import tempfile
from ....platform import platform
from ....exception import FrictionlessException
from ..control import ExcelControl
from ....system import system, Parser
from .... import errors


# TODO: support ExcelControl.stringified


class XlsParser(Parser):
    """XLS parser implementation."""

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
        control = ExcelControl.from_dialect(self.resource.dialect)

        # Get book
        bytes = self.loader.byte_stream.read()
        try:
            book = platform.xlrd.open_workbook(
                file_contents=bytes,
                encoding_override=self.resource.encoding,
                formatting_info=True,
                logfile=sys.stderr,
            )
        except NotImplementedError:
            book = platform.xlrd.open_workbook(
                file_contents=bytes,
                encoding_override=self.resource.encoding,
                formatting_info=False,
                logfile=sys.stderr,
            )

        # Get sheet
        try:
            if isinstance(control.sheet, str):
                sheet = book.sheet_by_name(control.sheet)
            else:
                sheet = book.sheet_by_index(control.sheet - 1)
        except (platform.xlrd.XLRDError, IndexError):
            note = 'Excel document "%s" does not have a sheet "%s"'
            error = errors.FormatError(
                note=note % (self.resource.normpath, control.sheet)
            )
            raise FrictionlessException(error)

        def type_value(ctype, value):
            """Detects boolean value, int value, datetime"""

            # Boolean
            if ctype == platform.xlrd.XL_CELL_BOOLEAN:
                return bool(value)

            # Excel numbers are only float
            # Float with no decimals can be cast into int
            if ctype == platform.xlrd.XL_CELL_NUMBER and value == value // 1:
                return int(value)

            # Datetime
            if ctype == platform.xlrd.XL_CELL_DATE:
                return platform.xlrd.xldate.xldate_as_datetime(value, book.datemode)

            return value

        # Stream data
        for x in range(0, sheet.nrows):
            cells = []
            for y, value in enumerate(sheet.row_values(x)):
                value = type_value(sheet.cell(x, y).ctype, value)
                if control.fill_merged_cells:
                    for xlo, xhi, ylo, yhi in sheet.merged_cells:
                        if x in range(xlo, xhi) and y in range(ylo, yhi):
                            value = type_value(
                                sheet.cell(xlo, ylo).ctype,
                                sheet.cell_value(xlo, ylo),
                            )
                cells.append(value)
            yield cells

    # Write

    def write_row_stream(self, source):
        control = ExcelControl.from_dialect(self.resource.dialect)
        book = platform.xlwt.Workbook()
        title = control.sheet
        if isinstance(title, int):
            title = f"Sheet {control.sheet}"
        sheet = book.add_sheet(title)
        with source:
            for field_index, name in enumerate(source.schema.field_names):
                sheet.write(0, field_index, name)
            for row_index, row in enumerate(source.row_stream):
                cells = row.to_list(types=self.supported_types)
                for field_index, cell in enumerate(cells):
                    sheet.write(row_index + 1, field_index, cell)
        file = tempfile.NamedTemporaryFile(delete=False)
        file.close()
        book.save(file.name)
        loader = system.create_loader(self.resource)
        loader.write_byte_stream(file.name)
