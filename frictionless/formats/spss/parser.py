from __future__ import annotations
import re
import warnings
from ...platform import platform
from ...system import Parser
from ...schema import Schema, Field
from . import settings


class SpssParser(Parser):
    """Spss parser implementation."""

    supported_types = [
        "string",
    ]

    # Read

    def read_cell_stream_create(self):
        sav = platform.sav_reader_writer
        warnings.filterwarnings("ignore", category=sav.SPSSIOWarning)  # type: ignore

        # Schema
        with sav.SavHeaderReader(self.resource.normpath, ioUtf8=True) as reader:  # type: ignore
            spss_schema = reader.all()
        schema = self.__read_convert_schema(spss_schema)
        self.resource.schema = schema

        # Lists
        yield schema.field_names
        with sav.SavReader(self.resource.normpath, ioUtf8=True) as reader:  # type: ignore
            for item in reader:
                cells = []
                for index, field in enumerate(schema.fields):
                    value = item[index]
                    if value is not None:
                        if field.type == "integer":
                            value = int(float(value))
                        elif field.type in ["datetime", "date", "time"]:
                            format = settings.FORMAT_READ[field.type]
                            value = reader.spss2strDate(value, format, None)
                    cells.append(value)
                yield cells

    def __read_convert_schema(self, spss_schema):
        schema = Schema()
        for name in spss_schema.varNames:
            type = self.__read_convert_type(spss_schema.formats[name])
            field = Field.from_descriptor({"name": name, "type": type})
            title = spss_schema.varLabels[name]
            if title:
                field.title = title
            schema.add_field(field)
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

    def write_row_stream(self, source):
        sav = platform.sav_reader_writer
        warnings.filterwarnings("ignore", category=sav.SPSSIOWarning)  # type: ignore

        # Convert schema
        mapping = self.__write_convert_type()
        spss_schema = self.__write_convert_schema(source)

        # Write rows
        with sav.SavWriter(self.resource.normpath, ioUtf8=True, **spss_schema) as writer:  # type: ignore
            with source:
                for row in source.row_stream:  # type: ignore
                    cells = []
                    for field in source.schema.fields:  # type: ignore
                        cell = row[field.name]
                        if field.type in ["datetime", "date", "time"]:
                            format = settings.FORMAT_WRITE[field.type]
                            cell = cell.strftime(format).encode()
                            cell = writer.spssDateTime(cell, format)
                        elif field.type not in mapping:  # type: ignore
                            cell, _ = field.write_cell(cell)
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
                spss_type = mapping.get(field.type)  # type: ignore
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
                    cell, _ = field.write_cell(cell)
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
