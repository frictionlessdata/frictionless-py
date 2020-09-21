import re
import os
import datetime
from ..resource import Resource
from ..storage import Storage
from ..plugin import Plugin
from ..schema import Schema
from ..field import Field
from .. import exceptions
from .. import helpers
from .. import errors


# Plugin


class SpssPlugin(Plugin):
    """Plugin for SPSS

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.spss import SpssPlugin`

    """

    def create_storage(self, name, **options):
        pass


# Storage


class SpssStorage(Storage):
    """SPSS storage implementation"""

    def __init__(self, *, basepath):
        self.__tables = {}
        self.__basepath = basepath
        if not os.path.isdir(basepath):
            note = f'"{basepath}" is not a directory, or doesn\'t exist'
            raise exceptions.FrictionlessException(errors.StorageError(note=note))

    def __repr__(self):
        template = "Storage <{basepath}>"
        text = template.format(basepath=self.__basepath)
        return text

    # Read

    @property
    def read_table_names(self):
        names = []
        for name in os.listdir(self.__basepath):
            if name.endswith(".sav", ".zsav"):
                name = self.read_table_convert_name(name)
                names.append(name)
        return name

    def reat_table_list(self):
        tables = []
        for name in self.read_table_names():
            table = self.read_table(name)
            tables.append(table)
        return tables

    def read_table(self, name):
        sav = helpers.import_from_plugin("savReaderWriter", plugin="spss")
        table = self.__tables.get(name)
        if table is None:
            path = self.read_table_convert_name(name)
            with sav.SavHeaderReader(path, ioUtf8=True) as header:
                table = self.read_table_convert_table(header.all())
        return table

    def read_table_convert_name(self, name):
        if not name.endswith((".sav", ".zsav")):
            name = "{}.sav".format(name)
        path = os.path.join(self.__basepath, name)
        path = os.path.normpath(path)
        if not path.startswith(os.path.normpath(self.__basepath)):
            note = f'Bucket name "{name}" is not valid.'
            raise exceptions.FrictionlessException(errors.StorageError(note=note))
        return path

    def read_table_convert_table(self, name, header):
        schema = Schema()
        date_formats = {
            "time": self.TIME_FORMAT,
            "date": self.DATE_FORMAT,
            "datetime": self.DATETIME_FORMAT,
        }

        # Fields
        for var in header.varNames:
            type = self.read_table_convert_field_type(header.formats[var])
            field = Field(name=var, type=type, title=header.varLabels[var])
            field["spss:format"] = header.formats[var]
            if type in date_formats.keys():
                field.format = date_formats[type]
            schema.fields.append(field)

        # Table
        table = Resource(name=name, schema=schema)
        return table

    def read_table_convert_field_type(self, type):

        # Mapping
        mapping = [
            ("string", re.compile(r"\bA\d+")),
            ("number", re.compile(r"\bF\d+\.\d+")),  # Basic decimal number
            ("number", re.compile(r"\b[E|N]\d+\.?\d*")),  # Exponent or N format number
            (
                "integer",
                re.compile(r"\bF\d+"),
            ),  # Integer (must come after Basic decimal in list)
            ("date", re.compile(r"\b[A|E|J|S]?DATE\d+")),  # Various date formats
            ("datetime", re.compile(r"\bDATETIME\d+")),
            ("time", re.compile(r"\bTIME\d+")),
            ("number", re.compile(r"\bDOLLAR\d+")),
            ("number", re.compile(r"\bPCT\d+")),  # Percentage format
        ]

        # Return type
        for ts_type, pattern in mapping:
            if pattern.match(format):
                return ts_type

        # Default
        return "string"

    def read_table_stream_data(self, name):
        sav = helpers.import_from_plugin("savReaderWriter", plugin="spss")
        table = self.read_table(name)
        path = self.read_table_convert_name(name)
        with sav.SavReader(path, ioUtf8=False, rawMode=False) as reader:
            for r in reader:
                cells = []
                for i, field in enumerate(table.schema.fields):
                    value = r[i]
                    # Fix decimals that should be integers
                    if field.type == "integer" and value is not None:
                        value = int(float(value))
                    # We need to decode bytes to strings
                    if isinstance(value, bytes):
                        value = value.decode(reader.fileEncoding)
                    # Time values need a decimal, add one if missing.
                    if field.type == "time" and not re.search(r"\.\d*", value):
                        value = "{}.0".format(value)
                    cells.append(value)
                yield cells

    # Write

    def write_table(self, *tables, force=False):
        sav = helpers.import_from_plugin("savReaderWriter", plugin="spss")

        # Check existence
        for table in tables:
            if table.name in self.read_table_names():
                if not force:
                    note = f'Table "{table.name}" already exists'
                    raise exceptions.FrictionlessException(errors.StorageError(note=note))
                self.write_table_remove(table.name)

        # Define buckets
        for table in tables:
            self.__tables[table.name] = table
            path = self.read_table_convert_name(table.name)
            # map descriptor to sav header format so we can use the method below.
            kwargs = self.write_table_convert_table(table)
            writer = sav.SavWriter(path, ioUtf8=True, **kwargs)
            writer.close()

    def write_table_remove(self, *tables, ignore=False):
        for table in tables:

            # Check existent
            if table.name not in self.read_table_names():
                if not ignore:
                    note = f'Table "{table.name}" does not exist'
                    raise exceptions.FrictionlessException(errors.StorageError(note=note))
                continue

            # Remove from tables
            self.__tables.pop(table.name, None)
            path = self.write_table_convert_name(table.name)
            os.remove(path)

    def write_table_convert_name(self, name):
        if not name.endswith((".sav", ".zsav")):
            name = "{}.sav".format(name)
        path = os.path.join(self.__basepath, name)
        path = os.path.normpath(path)
        if not path.startswith(os.path.normpath(self.__basepath)):
            note = f'Bucket name "{name}" is not valid.'
            raise exceptions.FrictionlessException(errors.StorageError(note=note))
        return path

    def write_table_convert_table(self, table):
        schema = table.schema

        def get_format_for_name(name):
            return schema.get_field(name).descriptor.get("spss:format")

        def get_spss_type_for_name(name):
            """Return spss number type for `name`.

            First we try to get the spss format (A10, F8.2, etc), and derive the spss type
            from that.

            If there's not spss format defined, we see if the type is a number and return the
            appropriate type.

            All else fails, we return a string type of width 1 (the default string format is
            A1).
            """
            spss_format = get_format_for_name(name)
            if spss_format:
                string_pattern = re.compile(
                    r"(?P<printFormat>A(HEX)?)(?P<printWid>\d+)", re.IGNORECASE
                )
                is_string = string_pattern.match(spss_format)
                if is_string:
                    # Return the 'width' discovered from the passed `format`.
                    return int(is_string.group("printWid"))
                else:
                    return 0
            else:
                descriptor_type = schema.get_field(name).type
                if descriptor_type == "integer" or descriptor_type == "number":
                    return 0

            note = f'Field "{name}" requires a "spss:format" property.'
            raise exceptions.FrictionlessException(errors.StorageError(note=note))

        var_names = [field.name for field in schema.fields]
        var_types = {n: get_spss_type_for_name(n) for n in var_names}
        formats = {n: get_format_for_name(n) for n in var_names if get_format_for_name(n)}
        return {"varNames": var_names, "varTypes": var_types, "formats": formats}

    def write_table_row_stream(self, name, row_stream):
        sav = helpers.import_from_plugin("savReaderWriter", plugin="spss")
        path = self.read_table_convert_name(name)
        table = self.read_table(name)
        kwargs = self.write_table_convert_table(table)
        schema = table.schema
        with sav.SavWriter(path, mode=b"ab", ioUtf8=True, **kwargs) as writer:
            for r in row_stream:
                row = []
                for i, field in enumerate(schema.fields):
                    value = r[i]
                    if field.type == "date" and isinstance(value, datetime.date):
                        value = writer.spssDateTime(
                            value.strftime(self.__mapper.DATE_FORMAT).encode(),
                            self.__mapper.DATE_FORMAT,
                        )
                    elif field.type == "datetime" and isinstance(
                        value, datetime.datetime
                    ):
                        value = writer.spssDateTime(
                            value.strftime(self.__mapper.DATETIME_FORMAT).encode(),
                            self.__mapper.DATETIME_FORMAT,
                        )
                    elif field.type == "time" and isinstance(value, datetime.time):
                        value = writer.spssDateTime(
                            value.strftime(self.__mapper.TIME_FORMAT).encode(),
                            self.__mapper.TIME_FORMAT,
                        )
                    row.append(value)
                writer.writerow(row)
