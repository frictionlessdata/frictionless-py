import sys
import tempfile
from ....exception import FrictionlessException
from ....parser import Parser
from ....system import system
from .... import helpers
from .... import errors


class XlsParser(Parser):
    """XLS parser implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.excel import XlsParser

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
        xlrd = helpers.import_from_plugin("xlrd", plugin="excel")
        dialect = self.resource.dialect

        # Get book
        bytes = self.loader.byte_stream.read()
        try:
            book = xlrd.open_workbook(
                file_contents=bytes,
                encoding_override=self.resource.encoding,
                formatting_info=True,
                logfile=sys.stderr,
            )
        except NotImplementedError:
            book = xlrd.open_workbook(
                file_contents=bytes,
                encoding_override=self.resource.encoding,
                formatting_info=False,
                logfile=sys.stderr,
            )

        # Get sheet
        try:
            if isinstance(dialect.sheet, str):
                sheet = book.sheet_by_name(dialect.sheet)
            else:
                sheet = book.sheet_by_index(dialect.sheet - 1)
        except (xlrd.XLRDError, IndexError):
            note = 'Excel document "%s" does not have a sheet "%s"'
            error = errors.FormatError(
                note=note % (self.resource.fullpath, dialect.sheet)
            )
            raise FrictionlessException(error)

        def type_value(ctype, value):
            """Detects boolean value, int value, datetime"""

            # Boolean
            if ctype == xlrd.XL_CELL_BOOLEAN:
                return bool(value)

            # Excel numbers are only float
            # Float with no decimals can be cast into int
            if ctype == xlrd.XL_CELL_NUMBER and value == value // 1:
                return int(value)

            # Datetime
            if ctype == xlrd.XL_CELL_DATE:
                return xlrd.xldate.xldate_as_datetime(value, book.datemode)

            return value

        # Stream data
        for x in range(0, sheet.nrows):
            cells = []
            for y, value in enumerate(sheet.row_values(x)):
                value = type_value(sheet.cell(x, y).ctype, value)
                if dialect.fill_merged_cells:
                    for xlo, xhi, ylo, yhi in sheet.merged_cells:
                        if x in range(xlo, xhi) and y in range(ylo, yhi):
                            value = type_value(
                                sheet.cell(xlo, ylo).ctype,
                                sheet.cell_value(xlo, ylo),
                            )
                cells.append(value)
            yield cells

    # Write

    def write_row_stream(self, resource):
        xlwt = helpers.import_from_plugin("xlwt", plugin="excel")
        source = resource
        target = self.resource
        book = xlwt.Workbook()
        title = target.dialect.sheet
        if isinstance(title, int):
            title = f"Sheet {target.dialect.sheet}"
        sheet = book.add_sheet(title)
        with source:
            for row_index, row in enumerate(source.row_stream):
                if row.row_number == 1:
                    for field_index, name in enumerate(row.field_names):
                        sheet.write(0, field_index, name)
                cells = row.to_list(types=self.supported_types)
                for field_index, cell in enumerate(cells):
                    sheet.write(row_index + 1, field_index, cell)
        file = tempfile.NamedTemporaryFile(delete=False)
        file.close()
        book.save(file.name)
        loader = system.create_loader(target)
        loader.write_byte_stream(file.name)
