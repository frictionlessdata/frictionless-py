from __future__ import annotations

import datetime
import decimal
from typing import TYPE_CHECKING, Any, List, Optional, Tuple

from dateutil.tz import tzoffset

from ... import types
from ...platform import platform
from ...schema import Field, Schema
from ...system import Parser

if TYPE_CHECKING:
    from ...resources import TableResource


class PolarsParser(Parser):
    """Polars parser implementation."""

    supported_types = [
        "array",
        "boolean",
        "datetime",
        "date",
        "duration",
        "integer",
        "number",
        "object",
        "string",
        "time",
    ]

    # Read

    def read_cell_stream_create(self):
        pl = platform.polars
        assert isinstance(self.resource.data, pl.DataFrame)
        dataframe = self.resource.data

        # Schema
        schema = self.__read_convert_schema()
        if not self.resource.schema:
            self.resource.schema = schema

        # Lists
        yield schema.field_names
        for row in dataframe.iter_rows():  # type: ignore
            cells: List[Any] = [v if v is not pl.Null else None for v in row]
            yield cells

    def __read_convert_schema(self):
        pl = platform.polars
        dataframe = self.resource.data
        schema = Schema()

        # Fields
        for name, dtype in zip(dataframe.columns, dataframe.dtypes):  # type: ignore
            sample = dataframe.select(pl.first(name)).item() if len(dataframe) else None  # type: ignore
            type = self.__read_convert_type(dtype, sample=sample)  # type: ignore
            field = Field.from_descriptor({"name": name, "type": type})
            schema.add_field(field)

        # Return schema
        return schema

    def __read_convert_type(self, _: Any, sample: Optional[types.ISample] = None):
        pl = platform.polars
        # Python types
        if sample is not None:
            if isinstance(sample, bool):  # type: ignore
                return "boolean"
            elif isinstance(sample, int):  # type: ignore
                return "integer"
            elif isinstance(sample, float):  # type: ignore
                return "number"
            if isinstance(sample, (list, tuple, pl.Series)):  # type: ignore
                return "array"
            elif isinstance(sample, datetime.datetime):
                return "datetime"
            elif isinstance(sample, datetime.date):
                return "date"
            elif isinstance(sample, platform.isodate.Duration):  # type: ignore
                return "duration"
            elif isinstance(sample, dict):
                return "object"
            elif isinstance(sample, str):
                return "string"
            elif isinstance(sample, datetime.time):
                return "time"

        # Default
        return "string"

    # Write

    def write_row_stream(self, source: TableResource):
        pl = platform.polars
        data_rows: List[Tuple[Any]] = []
        fixed_types = {}
        with source:
            for row in source.row_stream:
                data_values: List[Any] = []
                for field in source.schema.fields:
                    value = row[field.name]
                    if isinstance(value, dict):
                        value = str(value)  # type: ignore
                    if isinstance(value, decimal.Decimal):
                        value = float(value)
                    if isinstance(value, datetime.datetime) and value.tzinfo:
                        value = value.astimezone(datetime.timezone.utc)
                    if isinstance(value, datetime.time) and value.tzinfo:
                        value = value.replace(
                            tzinfo=tzoffset(
                                datetime.timezone.utc,
                                value.utcoffset().total_seconds(),  # type: ignore
                            )
                        )
                    if value is None and field.type in ("number", "integer"):
                        fixed_types[field.name] = "number"
                        value = None
                    data_values.append(value)
                data_rows.append(tuple(data_values))
        # Create dtypes/columns
        columns: List[str] = []
        for field in source.schema.fields:
            if field.name not in source.schema.primary_key:
                columns.append(field.name)

        # Create/set dataframe
        dataframe = pl.DataFrame(data_rows, orient="row")
        dataframe.columns = columns

        for field in source.schema.fields:
            if (
                field.type == "integer"
                and field.name in dataframe.columns
                and str(dataframe.select(field.name).dtypes[0]) != "int"
            ):
                dataframe = dataframe.with_columns(pl.col(field.name).cast(int))

        self.resource.data = dataframe
