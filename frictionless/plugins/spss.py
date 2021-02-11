import re
import warnings
from ..dialect import Dialect
from ..parser import Parser
from ..plugin import Plugin
from ..schema import Schema
from ..field import Field
from .. import helpers


# Plugin


class SpssPlugin(Plugin):
    """Plugin for SPSS

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.spss import SpssPlugin`
    """

    code = "spss"
    status = "experimental"

    def create_dialect(self, resource, *, descriptor):
        if resource.format in ["sav", "zsav"]:
            return SpssDialect(descriptor)

    def create_parser(self, resource):
        if resource.format in ["sav", "zsav"]:
            return SpssParser(resource)


# Dialect


class SpssDialect(Dialect):
    """Spss dialect representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.spss import SpssDialect`

    Parameters:
        descriptor? (str|dict): descriptor

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
    }


# Parser


class SpssParser(Parser):
    """Spss parser implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.spss import SpssParser`

    """

    supported_types = [
        "string",
    ]

    # Read

    def read_list_stream_create(self):
        sav = helpers.import_from_plugin("savReaderWriter", plugin="spss")
        warnings.filterwarnings("ignore", category=sav.SPSSIOWarning)

        # Schema
        with sav.SavHeaderReader(self.resource.fullpath, ioUtf8=True) as reader:
            spss_schema = reader.all()
        schema = self.__read_convert_schema(spss_schema)
        self.resource.schema = schema

        # Lists
        yield schema.field_names
        with sav.SavReader(self.resource.fullpath, ioUtf8=True) as reader:
            for item in reader:
                cells = []
                for index, field in enumerate(schema.fields):
                    value = item[index]
                    if value is not None:
                        if field.type == "integer":
                            value = int(float(value))
                        elif field.type in ["datetime", "date", "time"]:
                            format = FORMAT_READ[field.type]
                            value = reader.spss2strDate(value, format, None)
                    cells.append(value)
                yield cells

    def __read_convert_schema(self, spss_schema):
        schema = Schema()
        for name in spss_schema.varNames:
            type = self.__read_convert_type(spss_schema.formats[name])
            field = Field(name=name, type=type)
            title = spss_schema.varLabels[name]
            if title:
                field.title = title
            schema.fields.append(field)
        return schema

    def __read_convert_type(self, spss_type=None):

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
        if spss_type:
            for type, pattern in mapping:
                if pattern.match(spss_type):
                    return type
            return "string"

        # Return mapping
        return mapping

    # Write

    def write_row_stream(self, resource):
        sav = helpers.import_from_plugin("savReaderWriter", plugin="spss")
        warnings.filterwarnings("ignore", category=sav.SPSSIOWarning)
        target = self.resource
        source = resource

        # Convert schema
        mapping = self.__write_convert_type()
        spss_schema = self.__write_convert_schema(source)

        # Write rows
        with sav.SavWriter(target.fullpath, ioUtf8=True, **spss_schema) as writer:
            with source:
                for row in source.row_stream:
                    cells = []
                    for field in source.schema.fields:
                        cell = row[field.name]
                        if field.type in ["datetime", "date", "time"]:
                            format = FORMAT_WRITE[field.type]
                            cell = cell.strftime(format).encode()
                            cell = writer.spssDateTime(cell, format)
                        elif field.type not in mapping:
                            cell, notes = field.write_cell(cell)
                            cell = cell.encode("utf-8")
                        cells.append(cell)
                    writer.writerow(cells)

    def __write_convert_schema(self, source):
        spss_schema = {"varNames": [], "varLabels": {}, "varTypes": {}, "formats": {}}
        with source:

            # Add fields
            sizes = {}
            mapping = self.__write_convert_type()
            for field in source.schema.fields:
                spss_schema["varNames"].append(field.name)
                if field.title:
                    spss_schema["varLabels"][field.name] = field.title
                spss_type = mapping.get(field.type)
                if spss_type:
                    spss_schema["varTypes"][field.name] = spss_type[0]
                    spss_schema["formats"][field.name] = spss_type[1]
                else:
                    sizes[field.name] = 0

            # Set string sizes
            for row in source.row_stream:
                for name in sizes.keys():
                    cell = row[name]
                    field = source.schema.get_field(name)
                    cell, notes = field.write_cell(cell)
                    size = len(cell.encode("utf-8"))
                    if size > sizes[name]:
                        sizes[name] = size
            for name, size in sizes.items():
                spss_schema["varTypes"][name] = size

        return spss_schema

    def __write_convert_type(self, type=None):

        # Mapping
        mapping = {
            "integer": [0, "F10"],
            "number": [0, "F10.2"],
            "datetime": [0, "DATETIME20"],
            "date": [0, "DATE10"],
            "time": [0, "TIME8"],
            "year": [0, "F10"],
        }

        # Return type
        if type:
            return mapping.get(type)

        # Return mapping
        return mapping


# Internal

FORMAT_READ = {
    "date": "%Y-%m-%d",
    "datetime": "%Y-%m-%d %H:%M:%S",
    "time": "%H:%M:%S.%f",
}

FORMAT_WRITE = {
    "date": "%Y-%m-%d",
    "datetime": "%Y-%m-%d %H:%M:%S",
    "time": "%H:%M:%S.%f",
}
