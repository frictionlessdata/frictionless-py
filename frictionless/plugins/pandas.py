import isodate
import datetime
import collections
from functools import partial
from ..dialects import Dialect
from ..resource import Resource
from ..package import Package
from ..storage import Storage
from ..plugin import Plugin
from ..parser import Parser
from ..schema import Schema
from ..field import Field
from .. import exceptions
from .. import helpers
from .. import errors


# Plugin


class PandasPlugin(Plugin):
    """Plugin for Pandas

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.pandas import PandasPlugin`

    """

    def create_dialect(self, resource, *, descriptor):
        try:
            # TODO: cannot be loaded with plugins; improve this solution
            pd = helpers.import_from_plugin("pandas", plugin="pandas")
            if resource.format == "pandas" or isinstance(resource.source, pd.DataFrame):
                return PandasDialect(descriptor)
        except Exception:
            pass

    def create_parser(self, resource):
        try:
            # TODO: cannot be loaded with plugins; improve this solution
            pd = helpers.import_from_plugin("pandas", plugin="pandas")
            if resource.format == "pandas" or isinstance(resource.source, pd.DataFrame):
                return PandasParser(resource)
        except Exception:
            pass

    def create_storage(self, name, **options):
        if name == "pandas":
            return PandasStorage(**options)


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

    pass


# Parser


class PandasParser(Parser):
    """Pandas parser implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.pandas import PandasParser`

    """

    loading = False

    # Read

    def read_data_stream_create(self):
        storage = PandasStorage(dataframes={self.resource.name: self.resource.data})
        resource = storage.read_resource(self.resource.name)
        self.resource.schema = resource.schema
        yield resource.schema.field_names
        yield from resource.read_data_stream()

    # Write

    def write(self, read_row_stream):
        schema = self.resource.schema
        storage = PandasStorage()
        resource = Resource(name=self.resource.name, data=read_row_stream, schema=schema)
        storage.write_resource(resource)
        self.resource.data = storage.dataframe


# Storage


class PandasStorage(Storage):
    """Pandas storage implementation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.pandas import PandasStorage`

    Parameters:
        dataframes? (dict): dictionary of Pandas dataframes

    """

    def __init__(self, *, dataframes=None):
        self.__dataframes = dataframes or collections.OrderedDict()

    def __iter__(self):
        return iter(sorted(self.__dataframes.keys()))

    @property
    def dataframes(self):
        return self.__dataframes

    @property
    def dataframe(self):
        if len(self.__dataframes) != 1:
            note = 'The "storage.dataframe" is available for single dataframe storages'
            raise exceptions.FrictionlessException(errors.StorageError(note=note))
        return list(self.__dataframes.values())[0]

    # Read

    def read_resource(self, name):
        dataframe = self.__read_pandas_dataframe(name)
        if dataframe is None:
            note = f'Resource "{name}" does not exist'
            raise exceptions.FrictionlessException(errors.StorageError(note=note))
        schema = self.__read_convert_schema(dataframe)
        data = partial(self.__read_convert_data, name, schema)
        resource = Resource(name=name, schema=schema, data=data)
        return resource

    def read_package(self):
        package = Package()
        for name in self:
            resource = self.read_resource(name)
            package.resources.append(resource)
        return package

    def __read_convert_schema(self, dataframe):
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

    def __read_convert_data(self, name, schema):
        np = helpers.import_from_plugin("numpy", plugin="pandas")
        dataframe = self.__read_pandas_dataframe(name)
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

    def __read_pandas_dataframe(self, name):
        return self.__dataframes.get(name)

    # Write

    def write_resource(self, resource, *, force=False):
        package = Package(resources=[resource])
        return self.write_package(package, force=force)

    def write_package(self, package, *, force=False):
        existent_names = list(self)

        # Check existent
        for resource in package.resources:
            if resource.name in existent_names:
                if not force:
                    note = f'Table "{resource.name}" already exists'
                    raise exceptions.FrictionlessException(errors.StorageError(note=note))
                self.delete_resource(resource.name)

        # Write resources
        for resource in package.resources:
            if not resource.schema:
                resource.infer(only_sample=True)
            self.__dataframes[resource.name] = self.__write_convert_resource(resource)

    def __write_convert_resource(self, resource):
        np = helpers.import_from_plugin("numpy", plugin="pandas")
        pd = helpers.import_from_plugin("pandas", plugin="pandas")

        # Get data/index
        data_rows = []
        index_rows = []
        fixed_types = {}
        for row in resource.read_row_stream():
            data_values = []
            index_values = []
            for field in resource.schema.fields:
                value = row[field.name]
                if isinstance(value, float) and np.isnan(value):
                    value = None
                # http://pandas.pydata.org/pandas-docs/stable/gotchas.html#support-for-integer-na
                if value is None and field.type in ("number", "integer"):
                    fixed_types[field.name] = "number"
                    value = np.NaN
                if field.name in resource.schema.primary_key:
                    index_values.append(value)
                else:
                    data_values.append(value)
            if len(resource.schema.primary_key) == 1:
                index_rows.append(index_values[0])
            elif len(resource.schema.primary_key) > 1:
                index_rows.append(tuple(index_values))
            data_rows.append(tuple(data_values))

        # Create index
        index = None
        if resource.schema.primary_key:
            if len(resource.schema.primary_key) == 1:
                index_class = pd.Index
                index_field = resource.schema.get_field(resource.schema.primary_key[0])
                index_dtype = self.__write_convert_type(index_field.type)
                if field.type in ["datetime", "date"]:
                    index_class = pd.DatetimeIndex
                index = index_class(index_rows, name=index_field.name, dtype=index_dtype)
            elif len(resource.schema.primary_key) > 1:
                index = pd.MultiIndex.from_tuples(
                    index_rows, names=resource.schema.primary_key
                )

        # Create dtypes/columns
        dtypes = []
        columns = []
        for field in resource.schema.fields:
            if field.name not in resource.schema.primary_key:
                dtype = self.__write_convert_type(fixed_types.get(field.name, field.type))
                dtypes.append((field.name, dtype))
                columns.append(field.name)

        # Create dataframe
        array = np.array(data_rows, dtype=dtypes)
        dataframe = pd.DataFrame(array, index=index, columns=columns)

        return dataframe

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

    # Delete

    def delete_resource(self, name, *, ignore=False):
        return self.delete_package([name], ignore=ignore)

    def delete_package(self, names, *, ignore=False):
        existent_names = list(self)

        # Remove dataframes
        for name in names:

            # Check existent
            if name not in existent_names:
                if not ignore:
                    note = f'Resource "{name}" does not exist'
                    raise exceptions.FrictionlessException(errors.StorageError(note=note))
                return

            # Remove resource
            self.__dataframes.pop(name)
