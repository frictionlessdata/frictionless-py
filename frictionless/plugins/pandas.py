import isodate
import datetime
from ..dialect import Dialect
from ..plugin import Plugin
from ..parser import Parser
from ..schema import Schema
from ..field import Field
from .. import helpers


# NOTE:
# We need to ensure that the way we detect pandas dataframe is good enough.
# We don't want to be importing pandas and checking the type without a good reason


# Plugin


class PandasPlugin(Plugin):
    """Plugin for Pandas

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.pandas import PandasPlugin`

    """

    code = "pandas"
    status = "experimental"

    def create_file(self, file):
        if not file.scheme and not file.format and file.memory:
            if helpers.is_type(file.data, "DataFrame"):
                file.scheme = ""
                file.format = "pandas"
                return file

    def create_dialect(self, resource, *, descriptor):
        if resource.format == "pandas":
            return PandasDialect(descriptor)

    def create_parser(self, resource):
        if resource.format == "pandas":
            return PandasParser(resource)


# Dialect


class PandasDialect(Dialect):
    """Pandas dialect representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.pandas import PandasDialect`

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


class PandasParser(Parser):
    """Pandas parser implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.pandas import PandasParser`

    """

    supported_types = [
        "string",
    ]

    # Read

    def read_list_stream_create(self):
        np = helpers.import_from_plugin("numpy", plugin="pandas")
        dataframe = self.resource.data

        # Schema
        schema = self.__read_convert_schema()
        if not self.resource.schema:
            self.resource.schema = schema

        # Lists
        yield schema.field_names
        for pk, item in dataframe.iterrows():
            cells = []
            for field in schema.fields:
                if field.name in schema.primary_key:
                    pk = pk if isinstance(pk, tuple) else [pk]
                    value = pk[schema.primary_key.index(field.name)]
                else:
                    value = item[field.name]
                if field.type == "number" and np.isnan(value):
                    value = None
                elif field.type == "datetime":
                    value = value.to_pydatetime()
                cells.append(value)
            yield cells

    def __read_convert_schema(self):
        dataframe = self.resource.data
        schema = Schema()

        # Primary key
        for index, name in enumerate(dataframe.index.names):
            if name is not None:
                dtype = dataframe.index.get_level_values(index).dtype
                type = self.__read_convert_type(dtype)
                field = Field(name=name, type=type)
                field.required = True
                schema.fields.append(field)
                schema.primary_key.append(name)

        # Fields
        for name, dtype in dataframe.dtypes.iteritems():
            sample = dataframe[name].iloc[0] if len(dataframe) else None
            type = self.__read_convert_type(dtype, sample=sample)
            field = Field(name=name, type=type)
            schema.fields.append(field)

        # Return schema
        return schema

    def __read_convert_type(self, dtype, sample=None):
        pdc = helpers.import_from_plugin("pandas.core.dtypes.api", plugin="pandas")

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
            elif isinstance(sample, datetime.date):
                return "date"
            elif isinstance(sample, isodate.Duration):
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

    def write_row_stream(self, resource):
        np = helpers.import_from_plugin("numpy", plugin="pandas")
        pd = helpers.import_from_plugin("pandas", plugin="pandas")
        source = resource
        target = self.resource

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
                    # http://pandas.pydata.org/pandas-docs/stable/gotchas.html#support-for-integer-na
                    if value is None and field.type in ("number", "integer"):
                        fixed_types[field.name] = "number"
                        value = np.NaN
                    if field.type in ["datetime", "time"] and value is not None:
                        value = value.replace(tzinfo=None)
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
        index = None
        if source.schema.primary_key:
            if len(source.schema.primary_key) == 1:
                index_class = pd.Index
                index_field = source.schema.get_field(source.schema.primary_key[0])
                index_dtype = self.__write_convert_type(index_field.type)
                if field.type in ["datetime", "date"]:
                    index_class = pd.DatetimeIndex
                index = index_class(index_rows, name=index_field.name, dtype=index_dtype)
            elif len(source.schema.primary_key) > 1:
                index = pd.MultiIndex.from_tuples(
                    index_rows, names=source.schema.primary_key
                )

        # Create dtypes/columns
        dtypes = []
        columns = []
        for field in source.schema.fields:
            if field.name not in source.schema.primary_key:
                dtype = self.__write_convert_type(fixed_types.get(field.name, field.type))
                dtypes.append((field.name, dtype))
                columns.append(field.name)

        # Create/set dataframe
        array = np.array(data_rows, dtype=dtypes)
        dataframe = pd.DataFrame(array, index=index, columns=columns)
        target.data = dataframe

    def __write_convert_type(self, type=None):
        np = helpers.import_from_plugin("numpy", plugin="pandas")

        # Mapping
        mapping = {
            "array": np.dtype(list),
            "boolean": np.dtype(bool),
            "datetime": np.dtype("datetime64[ns]"),
            "integer": np.dtype(int),
            "number": np.dtype(float),
            "object": np.dtype(dict),
            "year": np.dtype(int),
        }

        # Return type
        if type:
            return mapping.get(type, np.dtype("O"))

        # Return mapping
        return mapping
