import re
from functools import partial
from ..metadata import Metadata
from ..dialects import Dialect
from ..resource import Resource
from ..storage import Storage
from ..package import Package
from ..plugin import Plugin
from ..parser import Parser
from ..schema import Schema
from ..field import Field
from .. import exceptions
from .. import helpers
from .. import errors


# Plugin


class SqlPlugin(Plugin):
    """Plugin for SQL

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.sql import SqlPlugin`

    """

    def create_dialect(self, resource, *, descriptor):
        for prefix in SCHEME_PREFIXES:
            if resource.scheme.startswith(prefix):
                return SqlDialect(descriptor)

    def create_parser(self, resource):
        for prefix in SCHEME_PREFIXES:
            if resource.scheme.startswith(prefix):
                return SqlParser(resource)

    def create_storage(self, name, **options):
        if name == "sql":
            return SqlStorage(**options)


# Dialect


class SqlDialect(Dialect):
    """SQL dialect representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.sql import SqlDialect`

    Parameters:
        descriptor? (str|dict): descriptor
        table (str): table
        order_by? (str): order_by

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(
        self,
        descriptor=None,
        *,
        table=None,
        order_by=None,
        namespace=None,
        header=None,
        header_rows=None,
        header_join=None,
        header_case=None,
    ):
        self.setinitial("table", table)
        self.setinitial("order_by", order_by)
        self.setinitial("namespace", namespace)
        super().__init__(
            descriptor=descriptor,
            header=header,
            header_rows=header_rows,
            header_join=header_join,
            header_case=header_case,
        )

    @Metadata.property
    def table(self):
        return self.get("table")

    @Metadata.property
    def order_by(self):
        return self.get("order_by")

    @Metadata.property
    def namespace(self):
        return self.get("namespace")

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["table"],
        "additionalProperties": False,
        "properties": {
            "table": {"type": "string"},
            "order_by": {"type": "string"},
            "namespace": {"type": "string"},
            "header": {"type": "boolean"},
            "headerRows": {"type": "array", "items": {"type": "number"}},
            "headerJoin": {"type": "string"},
            "headerCase": {"type": "boolean"},
        },
    }


# Parser


class SqlParser(Parser):
    """SQL parser implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.sql import SqlParser`

    """

    loading = False

    # Read

    def read_data_stream_create(self):
        sa = helpers.import_from_plugin("sqlalchemy", plugin="sql")
        engine = sa.create_engine(self.resource.source)
        dialect = self.resource.dialect
        storage = SqlStorage(engine=engine, namespace=dialect.namespace)
        resource = storage.read_resource(dialect.table, order_by=dialect.order_by)
        self.resource.schema = resource.schema
        yield resource.schema.field_names
        yield from resource.read_data_stream()

    # Write

    def write(self, read_row_stream):
        sa = helpers.import_from_plugin("sqlalchemy", plugin="sql")
        engine = sa.create_engine(self.resource.source)
        dialect = self.resource.dialect
        schema = self.resource.schema
        storage = SqlStorage(engine=engine, namespace=dialect.namespace)
        resource = Resource(name=dialect.table, data=read_row_stream, schema=schema)
        storage.write_resource(resource)


# Storage


class SqlStorage(Storage):
    """SQL storage implementation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.sql import SqlStorage`

    Parameters:
        engine (object): `sqlalchemy` engine
        prefix (str): prefix for all tables
        namespace (str): SQL scheme

    """

    def __init__(self, *, engine, prefix="", namespace=None):
        sa = helpers.import_from_plugin("sqlalchemy", plugin="sql")

        # Set attributes
        self.__prefix = prefix
        self.__namespace = namespace
        self.__connection = engine.connect()

        # Add regex support
        # It will fail silently if this function already exists
        if self.__connection.engine.dialect.name == "sqlite":
            self.__connection.connection.create_function("REGEXP", 2, regexp)

        # Create metadata and reflect
        self.__metadata = sa.MetaData(bind=self.__connection, schema=self.__namespace)
        self.__metadata.reflect(views=True)

    def __iter__(self):
        names = []
        for sql_table in self.__metadata.sorted_tables:
            name = self.__read_convert_name(sql_table.name)
            if name is not None:
                names.append(name)
        return iter(names)

    @property
    def connection(self):
        return self.__connection

    # Read

    def read_resource(self, name, *, order_by=None):
        sql_table = self.__read_sql_table(name)
        if sql_table is None:
            note = f'Resource "{name}" does not exist'
            raise exceptions.FrictionlessException(errors.StorageError(note=note))
        schema = self.__read_convert_schema(sql_table)
        data = partial(self.__read_convert_data, name, order_by=order_by)
        resource = Resource(name=name, schema=schema, data=data)
        return resource

    def read_package(self):
        package = Package()
        for name in self:
            resource = self.read_resource(name)
            package.resources.append(resource)
        return package

    def __read_convert_name(self, sql_name):
        if sql_name.startswith(self.__prefix):
            return sql_name.replace(self.__prefix, "", 1)
        return None

    def __read_convert_schema(self, sql_table):
        sa = helpers.import_from_plugin("sqlalchemy", plugin="sql")
        schema = Schema()

        # Fields
        for column in sql_table.columns:
            field_type = self.__read_convert_type(column.type)
            field = Field(name=column.name, type=field_type)
            if not column.nullable:
                field.required = True
            schema.fields.append(field)

        # Primary key
        for constraint in sql_table.constraints:
            if isinstance(constraint, sa.PrimaryKeyConstraint):
                for column in constraint.columns:
                    schema.primary_key.append(column.name)

        # Foreign keys
        for constraint in sql_table.constraints:
            if isinstance(constraint, sa.ForeignKeyConstraint):
                resource = ""
                own_fields = []
                foreign_fields = []
                for element in constraint.elements:
                    own_fields.append(element.parent.name)
                    if element.column.table.name != sql_table.name:
                        res_name = element.column.table.name
                        resource = self.__read_convert_name(res_name)
                    foreign_fields.append(element.column.name)
                ref = {"resource": resource, "fields": foreign_fields}
                schema.foreign_keys.append({"fields": own_fields, "reference": ref})

        # Return schema
        return schema

    def __read_convert_data(self, name, *, order_by=None):
        sa = helpers.import_from_plugin("sqlalchemy", plugin="sql")
        sql_table = self.__read_sql_table(name)
        with self.__connection.begin():
            # Streaming could be not working for some backends:
            # http://docs.sqlalchemy.org/en/latest/core/connections.html
            select = sql_table.select().execution_options(stream_results=True)
            if order_by:
                select = select.order_by(sa.sql.text(order_by))
            result = select.execute()
            yield result.keys()
            for item in result:
                cells = list(item)
                yield cells

    def __read_convert_type(self, sql_type=None):
        sa = helpers.import_from_plugin("sqlalchemy", plugin="sql")
        sapg = helpers.import_from_plugin("sqlalchemy.dialects.postgresql", plugin="sql")
        sams = helpers.import_from_plugin("sqlalchemy.dialects.mysql", plugin="sql")

        # Return mapping
        mapping = {
            sapg.ARRAY: "array",
            sams.BIT: "string",
            sa.Boolean: "boolean",
            sa.Date: "date",
            sa.DateTime: "datetime",
            sa.Float: "number",
            sa.Integer: "integer",
            sapg.JSONB: "object",
            sapg.JSON: "object",
            sa.Numeric: "number",
            sa.Text: "string",
            sa.Time: "time",
            sams.VARBINARY: "string",
            sams.VARCHAR: "string",
            sa.VARCHAR: "string",
            sapg.UUID: "string",
        }

        # Return type
        if sql_type:
            for key, value in mapping.items():
                if isinstance(sql_type, key):
                    return value
            return "string"

        # Return mapping
        return mapping

    def __read_sql_table(self, name):
        sql_name = self.__write_convert_name(name)
        if self.__namespace:
            sql_name = ".".join((self.__namespace, sql_name))
        return self.__metadata.tables.get(sql_name)

    # Write

    def write_resource(self, resource, *, force=False):
        package = Package(resources=[resource])
        return self.write_package(package, force=force)

    def write_package(self, package, force=False):
        existent_names = list(self)

        # Check existent
        delete_names = []
        for resource in package.resources:
            if resource.name in existent_names:
                if not force:
                    note = f'Resource "{resource.name}" already exists'
                    raise exceptions.FrictionlessException(errors.StorageError(note=note))
                delete_names.append(resource.name)

        # Wrap into a transaction
        with self.__connection.begin():

            # Create tables
            sql_tables = []
            self.delete_package(delete_names)
            for resource in package.resources:
                if not resource.schema:
                    resource.infer(only_sample=True)
                sql_table = self.__write_convert_schema(resource)
                sql_tables.append(sql_table)
            self.__metadata.create_all(tables=sql_tables)

            # Write data
            for resource in package.resources:
                self.__write_convert_data(resource)

    def __write_convert_name(self, name):
        return self.__prefix + name

    def __write_convert_schema(self, resource):
        sa = helpers.import_from_plugin("sqlalchemy", plugin="sql")

        # Prepare
        columns = []
        constraints = []
        column_mapping = {}
        sql_name = self.__write_convert_name(resource.name)

        # Fields
        Check = sa.CheckConstraint
        for field in resource.schema.fields:
            checks = []
            nullable = not field.required
            column_type = self.__write_convert_type(field.type)
            unique = field.constraints.get("unique", False)
            for const, value in field.constraints.items():
                if const == "minLength":
                    checks.append(Check('LENGTH("%s") >= %s' % (field.name, value)))
                elif const == "maxLength":
                    checks.append(Check('LENGTH("%s") <= %s' % (field.name, value)))
                elif const == "minimum":
                    checks.append(Check('"%s" >= %s' % (field.name, value)))
                elif const == "maximum":
                    checks.append(Check('"%s" <= %s' % (field.name, value)))
                elif const == "pattern":
                    if self.__connection.engine.dialect.name == "postgresql":
                        checks.append(Check("\"%s\" ~ '%s'" % (field.name, value)))
                    else:
                        check = Check("\"%s\" REGEXP '%s'" % (field.name, value))
                        checks.append(check)
                elif const == "enum":
                    enum_name = "%s_%s_enum" % (sql_name, field.name)
                    column_type = sa.Enum(*value, name=enum_name)
            column_args = [field.name, column_type] + checks
            column = sa.Column(*column_args, nullable=nullable, unique=unique)
            columns.append(column)
            column_mapping[field.name] = column

        # Primary key
        if resource.schema.primary_key is not None:
            constraint = sa.PrimaryKeyConstraint(*resource.schema.primary_key)
            constraints.append(constraint)

        # Foreign keys
        for fk in resource.schema.foreign_keys:
            fields = fk["fields"]
            resource = fk["reference"]["resource"]
            foreign_fields = fk["reference"]["fields"]
            table_name = sql_name
            if resource != "":
                table_name = self.__write_convert_name(resource)
            composer = lambda field: ".".join([table_name, field])
            foreign_fields = list(map(composer, foreign_fields))
            constraint = sa.ForeignKeyConstraint(fields, foreign_fields)
            constraints.append(constraint)

        # Create sql table
        sql_table = sa.Table(sql_name, self.__metadata, *(columns + constraints))
        return sql_table

    def __write_convert_data(self, resource):

        # Fallback fields
        fallback_fields = []
        mapping = self.__write_convert_type()
        for field in resource.schema.fields:
            if not mapping.get(field.type):
                fallback_fields.append(field)

        # Write data
        buffer = []
        buffer_size = 1000
        sql_table = self.__read_sql_table(resource.name)
        for row in resource.read_row_stream():
            for field in fallback_fields:
                row[field.name], notes = field.write_cell(row[field.name])
            buffer.append(row)
            if len(buffer) > buffer_size:
                self.__connection.execute(sql_table.insert().values(buffer))
                buffer = []
        if len(buffer):
            self.__connection.execute(sql_table.insert().values(buffer))

    def __write_convert_type(self, type=None):
        sa = helpers.import_from_plugin("sqlalchemy", plugin="sql")
        sapg = helpers.import_from_plugin("sqlalchemy.dialects.postgresql", plugin="sql")

        # Default dialect
        mapping = {
            "any": sa.Text,
            "boolean": sa.Boolean,
            "date": sa.Date,
            "datetime": sa.DateTime,
            "integer": sa.Integer,
            "number": sa.Float,
            "string": sa.Text,
            "time": sa.Time,
            "year": sa.Integer,
        }

        # Postgresql dialect
        if self.__connection.engine.dialect.name == "postgresql":
            mapping.update(
                {
                    "array": sapg.JSONB,
                    "geojson": sapg.JSONB,
                    "number": sa.Numeric,
                    "object": sapg.JSONB,
                }
            )

        # Return type
        if type:
            return mapping.get(type, sa.Text)

        # Return mapping
        return mapping

    # Delete

    def delete_resource(self, name, *, ignore=False):
        return self.delete_package([name], ignore=ignore)

    def delete_package(self, names, *, ignore=False):
        existent_names = list(self)

        # Prepare tables
        sql_tables = []
        for name in names:

            # Check existent
            if name not in existent_names:
                if not ignore:
                    note = f'Resource "{name}" does not exist'
                    raise exceptions.FrictionlessException(errors.StorageError(note=note))
                continue

            # Add table for removal
            sql_table = self.__read_sql_table(name)
            sql_tables.append(sql_table)

        # Wrap into a transaction
        with self.__connection.begin():

            # Drop tables, update metadata
            self.__metadata.drop_all(tables=sql_tables)
            self.__metadata.clear()
            self.__metadata.reflect(views=True)


# Internal

# https://docs.sqlalchemy.org/en/13/core/engines.html
# https://docs.sqlalchemy.org/en/13/dialects/index.html
SCHEME_PREFIXES = [
    "postgresql",
    "mysql",
    "oracle",
    "mssql",
    "sqlite",
    "firebird",
    "sybase",
    "db2",
    "ibm",
]


def regexp(expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None
