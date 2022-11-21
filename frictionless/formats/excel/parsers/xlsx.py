from __future__ import annotations
import os
import shutil
import atexit
import hashlib
import tempfile
import warnings
import datetime
from itertools import chain
from ....exception import FrictionlessException
from ....platform import platform
from ..control import ExcelControl
from ....resource import Resource
from ....system import system, Parser
from .... import errors
from .. import settings


class XlsxParser(Parser):
    """XLSX parser implementation."""

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

    def read_loader(self):
        control = ExcelControl.from_dialect(self.resource.dialect)
        loader = system.create_loader(self.resource)
        if not loader.remote:
            return loader.open()

        # Remote
        # Create copy for remote source
        # For remote stream we need local copy (will be deleted on close by Python)
        # https://docs.python.org/3.5/library/tempfile.html#tempfile.TemporaryFile
        if loader.remote:
            path = self.resource.normpath

            # Cached
            if control.workbook_cache is not None and path in control.workbook_cache:
                # TODO: rebase on using resource without system?
                resource = Resource(path, scheme="file", format="xlsx")
                resource.infer(sample=False)
                loader = system.create_loader(resource)
                return loader.open()

            with loader as loader:
                delete = control.workbook_cache is None
                target = tempfile.NamedTemporaryFile(delete=delete)
                shutil.copyfileobj(loader.byte_stream, target)
                target.seek(0)
            if not target.delete:
                control.workbook_cache[path] = target.name  # type: ignore
                atexit.register(os.remove, target.name)
            # TODO: rebase on using resource without system?
            resource = Resource(target, scheme="stream", format="xlsx")
            resource.infer(sample=False)
            loader = system.create_loader(resource)
            return loader.open()

    def read_cell_stream_create(self):
        control = ExcelControl.from_dialect(self.resource.dialect)

        # Get book
        # To fill merged cells we can't use read-only because
        # `sheet.merged_cell_ranges` is not available in this mode
        try:
            warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
            book = platform.openpyxl.load_workbook(
                self.loader.byte_stream,
                read_only=not control.fill_merged_cells,
                data_only=True,
            )
        except Exception as exception:
            error = errors.FormatError(note=f'invalid excel file "{self.resource.path}"')
            raise FrictionlessException(error) from exception

        # Get sheet
        try:
            if isinstance(control.sheet, str):
                sheet = book[control.sheet]
            else:
                sheet = book.worksheets[control.sheet - 1]
        except (KeyError, IndexError):
            note = 'Excel document "%s" does not have a sheet "%s"'
            error = errors.FormatError(
                note=note % (self.resource.normpath, control.sheet)
            )
            raise FrictionlessException(error)

        # Fill merged cells
        if control.fill_merged_cells:
            # NOTE:
            # We can try using an algorithm similiar to what XlsParser has
            # to support mergin cells in the read-only mode (now we need the write mode)
            for merged_cell_range in list(sheet.merged_cells.ranges):
                merged_cell_range = str(merged_cell_range)
                sheet.unmerge_cells(merged_cell_range)
                merged_rows = platform.openpyxl.utils.rows_from_range(merged_cell_range)  # type: ignore
                coordinates = list(chain.from_iterable(merged_rows))
                value = sheet[coordinates[0]].value
                for coordinate in coordinates:
                    cell = sheet[coordinate]
                    cell.value = value

        # Stream data
        for cells in sheet.iter_rows():
            yield extract_row_values(
                cells,
                control.preserve_formatting,
                control.adjust_floating_point_error,
                stringified=control.stringified,
            )

        # Calculate stats
        # TODO: remove when the proper implementation is in-place:
        # https://github.com/frictionlessdata/frictionless-py/issues/438
        if self.resource.scheme == "file":
            stat = os.stat(self.resource.normpath)
            self.resource.stats.bytes = stat.st_size
            md5 = hashlib.new("md5")
            sha256 = hashlib.new("sha256")
            with open(self.resource.normpath, "rb") as file:
                for chunk in iter(lambda: file.read(4096), b""):
                    md5.update(chunk)
                    sha256.update(chunk)
                self.resource.stats.md5 = md5.hexdigest()
                self.resource.stats.sha256 = sha256.hexdigest()

    # Write

    def write_row_stream(self, source):
        control = ExcelControl.from_dialect(self.resource.dialect)
        book = platform.openpyxl.Workbook(write_only=True)
        title = control.sheet
        if isinstance(title, int):
            title = f"Sheet {control.sheet}"
        sheet = book.create_sheet(title)
        with source:
            sheet.append(source.schema.field_names)
            for row in source.row_stream:
                cells = row.to_list(types=self.supported_types)
                sheet.append(cells)
        file = tempfile.NamedTemporaryFile(delete=False)
        file.close()
        book.save(file.name)
        loader = system.create_loader(self.resource)
        loader.write_byte_stream(file.name)


# Internal


def extract_row_values(
    row, preserve_formatting=False, adjust_floating_point_error=False, stringified=False
):
    if preserve_formatting:
        values = []
        for cell in row:
            number_format = cell.number_format or ""
            value = cell.value

            if isinstance(cell.value, datetime.datetime) or isinstance(
                cell.value, datetime.time
            ):
                temporal_format = convert_excel_date_format_string(number_format)
                if temporal_format:
                    value = cell.value.strftime(temporal_format)
            elif (
                adjust_floating_point_error
                and isinstance(cell.value, float)
                and number_format == "General"
            ):
                # We have a float with format General
                # Calculate the number of integer digits
                integer_digits = len(str(int(cell.value)))
                # Set the precision to 15 minus the number of integer digits
                precision = 15 - (integer_digits)
                value = round(cell.value, precision)
            elif isinstance(cell.value, (int, float)):
                new_value = convert_excel_number_format_string(number_format, cell.value)
                if new_value:
                    value = new_value
            values.append(value)
        return values
    if stringified:
        return list(
            str(cell.value) if cell.value is not None else cell.value for cell in row
        )
    return list(cell.value for cell in row)


def convert_excel_number_format_string(excel_number, value):
    # A basic attempt to convert excel number_format to a number string
    # The important goal here is to get proper amount of rounding
    percentage = False
    if excel_number.endswith("%"):
        value = value * 100
        excel_number = excel_number[:-1]
        percentage = True
    if excel_number == "General":
        return value
    multi_codes = excel_number.split(";")
    if value < 0 and len(multi_codes) > 1:
        excel_number = multi_codes[1]
    else:
        excel_number = multi_codes[0]

    code = excel_number.split(".")

    if len(code) > 2:
        return None
    if len(code) < 2:
        # No decimals
        new_value = "{0:.0f}".format(value)
    else:
        decimal_section = code[1]
        # Only pay attention to the 0, # and ? characters as they provide precision information
        decimal_section = "".join(d for d in decimal_section if d in ["0", "#", "?"])

        # Count the number of hashes at the end of the decimal_section in order to know how
        # the number should be truncated
        number_hash = 0
        for i in reversed(range(len(decimal_section))):
            if decimal_section[i] == "#":  # type: ignore
                number_hash += 1
            else:
                break
        string_format_code = "{0:." + str(len(decimal_section)) + "f}"
        new_value = string_format_code.format(value)
        if number_hash > 0:
            for i in range(number_hash):
                if new_value.endswith("0"):
                    new_value = new_value[:-1]
    if percentage:
        return new_value + "%"

    return new_value


def convert_excel_date_format_string(excel_date):
    # Created using documentation here:
    # https://support.office.com/en-us/article/review-guidelines-for-customizing-a-number-format-c0a1d1fa-d3f4-4018-96b7-9c9354dd99f5

    # The python date string that is being built
    python_date = ""
    # The excel code currently being parsed
    excel_code = ""
    prev_code = ""
    # If the previous character was the escape character
    char_escaped = False
    # If we are in a quotation block (surrounded by "")
    quotation_block = False
    # Variables used for checking if a code should be a minute or a month
    checking_minute_or_month = False
    minute_or_month_buffer = ""

    for c in excel_date:
        ec = excel_code.lower()
        # The previous character was an escape, the next character should be added normally
        if char_escaped:
            if checking_minute_or_month:
                minute_or_month_buffer += c
            else:
                python_date += c
            char_escaped = False
            continue
        # Inside a quotation block
        if quotation_block:
            if c == '"':
                # Quotation block should now end
                quotation_block = False
            elif checking_minute_or_month:
                minute_or_month_buffer += c
            else:
                python_date += c
            continue
        # The start of a quotation block
        if c == '"':
            quotation_block = True
            continue
        if c == settings.EXCEL_SECTION_DIVIDER:
            # We ignore excel sections for datetimes
            break

        is_escape_char = c == settings.EXCEL_ESCAPE_CHAR
        # The am/pm and a/p code add some complications, need to make sure we are not that code
        is_misc_char = c in settings.EXCEL_MISC_CHARS and (
            c != "/" or (ec != "am" and ec != "a")
        )
        new_excel_code = False

        # Handle a new code without a different characeter in between
        if (
            ec
            and not is_escape_char
            and not is_misc_char
            # If the code does not start with c, we are in a new code
            and not ec.startswith(c.lower())
            # other than the case where we are building up
            # am/pm (minus the case where it is fully built), we are in a new code
            and (not ec.startswith("a") or ec == "am/pm")
        ):
            new_excel_code = True

        # Code is finished, check if it is a proper code
        if (is_escape_char or is_misc_char or new_excel_code) and ec:
            # Checking if the previous code should have been minute or month
            if checking_minute_or_month:
                if ec == "ss" or ec == "s":
                    # It should be a minute!
                    minute_or_month_buffer = (
                        settings.EXCEL_MINUTE_CODES[prev_code] + minute_or_month_buffer
                    )
                else:
                    # It should be a months!
                    minute_or_month_buffer = (
                        settings.EXCEL_MONTH_CODES[prev_code] + minute_or_month_buffer
                    )
                python_date += minute_or_month_buffer
                checking_minute_or_month = False
                minute_or_month_buffer = ""

            if ec in settings.EXCEL_CODES:
                python_date += settings.EXCEL_CODES[ec]
            # Handle months/minutes differently
            elif ec in settings.EXCEL_MINUTE_CODES:
                # If preceded by hours, we know this is referring to minutes
                if prev_code == "h" or prev_code == "hh":
                    python_date += settings.EXCEL_MINUTE_CODES[ec]
                else:
                    # Have to check if the next code is ss or s
                    checking_minute_or_month = True
                    minute_or_month_buffer = ""
            else:
                # Have to abandon this attempt to convert because the code is not recognized
                return None
            prev_code = ec
            excel_code = ""
        if is_escape_char:
            char_escaped = True
        elif is_misc_char:
            # Add the misc char
            if checking_minute_or_month:
                minute_or_month_buffer += c
            else:
                python_date += c
        else:
            # Just add to the code
            excel_code += c

    # Complete, check if there is still a buffer
    if checking_minute_or_month:
        # We know it's a month because there were no more codes after
        minute_or_month_buffer = (
            settings.EXCEL_MONTH_CODES[prev_code] + minute_or_month_buffer
        )
        python_date += minute_or_month_buffer
    if excel_code:
        ec = excel_code.lower()
        if ec in settings.EXCEL_CODES:
            python_date += settings.EXCEL_CODES[ec]
        elif ec in settings.EXCEL_MINUTE_CODES:
            if prev_code == "h" or prev_code == "hh":
                python_date += settings.EXCEL_MINUTE_CODES[ec]
            else:
                python_date += settings.EXCEL_MONTH_CODES[ec]
        else:
            return None
    return python_date
