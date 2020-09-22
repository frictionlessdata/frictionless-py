import re
import os
import datetime
from ..resource import Resource
from ..package import Package
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
    """SPSS storage implementation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.spss import SpssStorage`

    Parameters:
        basepath? (str): A path to a dir for reading/writing SAV files.
            Defaults to current dir.

    """

    def __init__(self, *, basepath=None):
        basepath = basepath or os.curdir()
        if not os.path.isdir(basepath):
            note = f'Path "{basepath}" is not a directory, or doesn\'t exist'
            raise exceptions.FrictionlessException(errors.StorageError(note=note))
        self.__basepath = basepath

    def __iter__(self):
        names = []
        for path in os.listdir(self.__basepath):
            name = self.__read_convert_name(path)
            if name is not None:
                names.append(name)
        return iter(names)

    # Read

    def read_resource(self, name):
        sav = helpers.import_from_plugin("savReaderWriter", plugin="spss")
        path = self.__write_convert_name(name)
        with sav.SavHeaderReader(path, ioUtf8=True) as header:
            spss_schema = header.all()
            schema = self.__read_convert_schema(spss_schema)
            data = self.__read_data_stream(name)
            resource = Resource(name=name, schema=schema, data=data)
            return resource

    def read_package(self):
        package = Package()
        for name in self:
            resource = self.read_resource(name)
            package.resources.append(resource)
        return package

    def __read_data_stream(self, name, schema):
        sav = helpers.import_from_plugin("savReaderWriter", plugin="spss")
        path = self.write_convert_name(name)
        with sav.SavReader(path, ioUtf8=False, rawMode=False) as reader:
            for item in reader:
                cells = []
                for index, field in enumerate(schema.fields):
                    value = item[index]
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

    def __read_convert_name(self, path):
        if path.endswith(".sav", ".zsav"):
            return os.path.splitext(path)[0]

    def __read_convert_schema(self, spss_schema):
        schema = Schema()

        # Formats
        date_formats = {
            "time": TIME_FORMAT,
            "date": DATE_FORMAT,
            "datetime": DATETIME_FORMAT,
        }

        # Fields
        for var in spss_schema.varNames:
            type = self.read_table_convert_field_type(spss_schema.formats[var])
            field = Field(name=var, type=type, title=spss_schema.varLabels[var])
            field["spss:format"] = spss_schema.formats[var]
            if type in date_formats.keys():
                field.format = date_formats[type]
            schema.fields.append(field)

        return schema

    def __read_convert_type(self, spss_type):

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
        for type, pattern in mapping:
            if pattern.match(spss_type):
                return type

        # Default
        return "string"

    # Write

    def write_resource(self, resource, *, force=False):
        package = Package(resources=[resource])
        return self.write_package(package, force=force)

    def write_package(self, package, *, force=False):

        # Copy/infer package
        package = Package(package)
        package.infer()

        # Check existence
        for resource in package.resources:
            if resource.name in self:
                if not force:
                    note = f'Resource "{resource.name}" already exists'
                    raise exceptions.FrictionlessException(errors.StorageError(note=note))
                self.delete_resource(resource.name)

        # Save resources
        for resource in package.resources:
            self.__write_row_stream(resource)

    def __write_row_stream(self, resource):
        sav = helpers.import_from_plugin("savReaderWriter", plugin="spss")

        # Prepare SPSS meta
        path = self.write_convert_name(resource.name)
        spss_schema = self.write_convert_schema(resource.schema)

        # Write row stream
        with sav.SavWriter(path, mode=b"ab", ioUtf8=True, **spss_schema) as writer:
            for row in resource.read_rows():
                result = []
                for field in resource.schema.fields:
                    cell = row[field.name]
                    if field.type == "date" and isinstance(cell, datetime.date):
                        cell = cell.strftime(DATE_FORMAT).encode()
                        cell = writer.spssDateTime(cell, DATE_FORMAT)
                    elif field.type == "datetime" and isinstance(cell, datetime.datetime):
                        cell = cell.strftime(DATETIME_FORMAT).encode()
                        cell = writer.spssDateTime(cell, DATETIME_FORMAT)
                    elif field.type == "time" and isinstance(cell, datetime.time):
                        cell = cell.strftime(TIME_FORMAT).encode()
                        cell = writer.spssDateTime(cell, TIME_FORMAT)
                    result.append(cell)
                writer.writerow(result)

    def __write_convert_name(self, name):
        path = os.path.normpath(os.path.join(self.__basepath, f"{name}.sav"))
        if not path.startswith(os.path.normpath(self.__basepath)):
            note = f'Resource name "{name}" is not valid.'
            raise exceptions.FrictionlessException(errors.StorageError(note=note))
        return path

    def __write_convert_schema(self, schema):
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

    # Delete

    def delete_resource(self, name, *, ignore=False):
        return self.delete_package([name], ignore=ignore)

    def delete_package(self, names, *, ignore=False):
        for name in names:

            # Check existent
            if name not in self:
                if not ignore:
                    note = f'Table "{name}" does not exist'
                    raise exceptions.FrictionlessException(errors.StorageError(note=note))
                continue

            # Delete file
            path = self.__write_convert_name(name)
            os.remove(path)


# Internal

DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIME_FORMAT = "%H:%M:%S.%f"
