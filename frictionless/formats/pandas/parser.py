from __future__ import annotations
import datetime
import decimal
from ...platform import platform
from ...schema import Schema, Field
from ...system import Parser


class PandasParser(Parser):
    """Pandas parser implementation."""

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
        np = platform.numpy
        pd = platform.pandas
        dataframe = self.resource.normdata

        # Schema
        schema = self.__read_convert_schema()
        if not self.resource.has_schema:
            self.resource.schema = schema

        # Lists
        yield schema.field_names
        for pk, item in dataframe.iterrows():  # type: ignore
            cells = []
            for field in schema.fields:
                if field.name in schema.primary_key:
                    pk = pk if isinstance(pk, tuple) else [pk]
                    value = pk[schema.primary_key.index(field.name)]
                else:
                    value = item[field.name]
                if field.type == "number" and np.isnan(value):  # type: ignore
                    value = None
                elif isinstance(value, pd.Timestamp):
                    value = value.to_pydatetime()  # type: ignore
                cells.append(value)
            yield cells

    def __read_convert_schema(self):
        dataframe = self.resource.normdata
        schema = Schema()

        # Primary key
        for index, name in enumerate(dataframe.index.names):  # type: ignore
            if name is not None:
                dtype = dataframe.index.get_level_values(index).dtype  # type: ignore
                type = self.__read_convert_type(dtype)
                field = Field.from_descriptor({"name": name, "type": type})
                field.required = True
                schema.add_field(field)
                schema.primary_key.append(name)

        # Fields
        for name, dtype in dataframe.dtypes.items():  # type: ignore
            sample = dataframe[name].iloc[0] if len(dataframe) else None  # type: ignore
            type = self.__read_convert_type(dtype, sample=sample)
            field = Field.from_descriptor({"name": name, "type": type})
            schema.add_field(field)

        # Return schema
        return schema

    def __read_convert_type(self, dtype, sample=None):
        pdc = platform.pandas_core_dtypes_api

        # Pandas types
        if pdc.is_bool_dtype(dtype):
            return "boolean"
        elif pdc.is_datetime64_any_dtype(dtype):
            return "datetime"
        elif pdc.is_integer_dtype(dtype):
            return "integer"
        elif pdc.is_numeric_dtype(dtype):
            return "number"

        # Python types
        if sample is not None:
            if isinstance(sample, (list, tuple)):
                return "array"
            elif isinstance(sample, datetime.datetime):
                return "datetime"
            elif isinstance(sample, datetime.date):
                return "date"
            elif isinstance(sample, platform.isodate.Duration):
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

    def write_row_stream(self, source):
        np = platform.numpy
        pd = platform.pandas

        # Get data/index
        data_rows = []
        index_rows = []
        fixed_types = {}
        with source:
            for row in source.row_stream:
                data_values = []
                index_values = []
                for field in source.schema.fields:
                    value = row[field.name]
                    if isinstance(value, float) and np.isnan(value):
                        value = None
                    if isinstance(value, decimal.Decimal):
                        value = float(value)
                    # http://pandas.pydata.org/pandas-docs/stable/gotchas.html#support-for-integer-na
                    if value is None and field.type in ("number", "integer"):
                        fixed_types[field.name] = "number"
                        value = np.NaN
                    if field.name in source.schema.primary_key:
                        index_values.append(value)
                    else:
                        data_values.append(value)

                if len(source.schema.primary_key) == 1:
                    index_rows.append(index_values[0])
                elif len(source.schema.primary_key) > 1:
                    index_rows.append(tuple(index_values))
                data_rows.append(tuple(data_values))

        # Create index
        pd = platform.pandas

        index = None
        if source.schema.primary_key:
            if len(source.schema.primary_key) == 1:
                index_class = pd.Index
                index_field = source.schema.get_field(source.schema.primary_key[0])
                index_dtype = self.__write_convert_type(index_field.type)
                if index_field.type in ["datetime", "date"]:
                    index_class = pd.DatetimeIndex
                    index_rows = pd.to_datetime(index_rows, utc=True)
                index = index_class(index_rows, name=index_field.name, dtype=index_dtype)  # type: ignore

            elif len(source.schema.primary_key) > 1:
                index = pd.MultiIndex.from_tuples(
                    index_rows, names=source.schema.primary_key
                )

        # Create dtypes/columns
        columns = []
        for field in source.schema.fields:
            if field.name not in source.schema.primary_key:
                columns.append(field.name)

        # Create/set dataframe
        dataframe = pd.DataFrame(data_rows, index=index, columns=columns)

        # This step will see if there is any column for which the schema is defined
        # as 'integer' but Pandas inferred it as a float. This can happen if there
        # is an empty value (represented as Not a Number) is the integer column.
        # If the column is of type float instead of integer, convert it to the type
        # Int64 from pandas that supports NaN.
        # Bug: #1109
        # Bug: #1138 create datetime64 for date columns
        for field in source.schema.fields:
            if (
                field.type == "integer"
                and field.name in dataframe.columns
                and str(dataframe.dtypes[field.name]) != "int64"
            ):
                dataframe[field.name] = dataframe[field.name].astype("Int64")

            if (
                field.type == "date"
                and field.name in dataframe.columns
                and str(dataframe.dtypes[field.name]) != "date"
            ):
                dataframe[field.name] = pd.to_datetime(dataframe[field.name])

        self.resource.data = dataframe

    def __write_convert_type(self, type=None):
        np = platform.numpy
        pd = platform.pandas

        # Mapping
        mapping = {
            "array": np.dtype(list),  # type: ignore
            "boolean": np.dtype(bool),
            "datetime": pd.DatetimeTZDtype(tz="UTC"),
            "integer": np.dtype(int),
            "number": np.dtype(float),
            "object": np.dtype(dict),  # type: ignore
            "year": np.dtype(int),
        }

        # Return type
        if type:
            return mapping.get(type, np.dtype("O"))

        # Return mapping
        return mapping
