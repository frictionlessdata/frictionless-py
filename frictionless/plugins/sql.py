import re
from functools import partial
from ..exception import FrictionlessException
from ..metadata import Metadata
from ..resource import Resource
from ..dialect import Dialect
from ..storage import Storage
from ..package import Package
from ..plugin import Plugin
from ..parser import Parser
from ..schema import Schema
from ..field import Field
from .. import helpers
from .. import errors


# NOTE:
# Can we improve `engline.dialect.name.startswith()` checks?


# Plugin


class SqlPlugin(Plugin):
    """Plugin for SQL

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.sql import SqlPlugin`

    """

    code = "sql"
    status = "experimental"

    def create_file(self, file):
        for prefix in SCHEME_PREFIXES:
            if file.scheme.startswith(prefix):
                file.scheme = ""
                file.format = "sql"
                return file

    def create_dialect(self, resource, *, descriptor):
        if resource.format == "sql":
            return SqlDialect(descriptor)

    def create_parser(self, resource):
        if resource.format == "sql":
            return SqlParser(resource)

    def create_storage(self, name, source, **options):
        if name == "sql":
            return SqlStorage(source, **options)


# Dialect


class SqlDialect(Dialect):
    """SQL dialect representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.sql import SqlDialect`

    Parameters:
        descriptor? (str|dict): descriptor
        table (str): table name
        prefix (str): prefix for all table names
        order_by? (str): order_by statement passed to SQL
        namespace? (str): SQL schema

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(
        self,
        descriptor=None,
        *,
        table=None,
        prefix=None,
        order_by=None,
        namespace=None,
    ):
        self.setinitial("table", table)
        self.setinitial("prefix", prefix)
        self.setinitial("order_by", order_by)
        self.setinitial("namespace", namespace)
        super().__init__(descriptor)

    @Metadata.property
    def table(self):
        return self.get("table")

    @Metadata.property
    def prefix(self):
        return self.get("prefix") or ""

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
            "prefix": {"type": "string"},
            "order_by": {"type": "string"},
            "namespace": {"type": "string"},
        },
    }


# Parser


class SqlParser(Parser):
    """SQL parser implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.sql import SqlParser`

    """

    supported_types = [
        "boolean",
        "date",
        "datetime",
        "integer",
        "number",
        "string",
        "time",
    ]

    # Read

    def read_list_stream_create(self):
        dialect = self.resource.dialect
        storage = SqlStorage(self.resource.fullpath, dialect=dialect)
        resource = storage.read_resource(dialect.table, order_by=dialect.order_by)
        self.resource.schema = resource.schema
        with resource:
            yield from resource.list_stream

    # Write

    # NOTE: this approach is questionable
    def write_row_stream(self, resource):
        source = resource
        target = self.resource
        if not target.dialect.table:
            note = 'Please provide "dialect.table" for writing'
            raise FrictionlessException(errors.StorageError(note=note))
        source.name = target.dialect.table
        storage = SqlStorage(target.fullpath, dialect=target.dialect)
        storage.write_resource(source, force=True)


# Storage


class SqlStorage(Storage):
    """SQL storage implementation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.sql import SqlStorage`

    Parameters:
        url? (string): SQL connection string
        engine? (object): `sqlalchemy` engine
        prefix? (str): prefix for all tables
        namespace? (str): SQL scheme

    """

    def __init__(self, source, *, dialect=None):
        sa = helpers.import_from_plugin("sqlalchemy", plugin="sql")
        engine = sa.create_engine(source) if isinstance(source, str) else source

        # Set attributes
        dialect = dialect or SqlDialect()
        self.__namespace = dialect.namespace
        self.__connection = engine.connect()
        self.__converter = SqlConverter(engine.dialect, dialect)

        # Add regex support
        # It will fail silently if this function already exists
        if self.__connection.engine.dialect.name.startswith("sqlite"):
            self.__connection.connection.create_function("REGEXP", 2, regexp)

        # Create metadata and reflect
        self.__metadata = sa.MetaData(bind=self.__connection, schema=self.__namespace)
        self.__metadata.reflect(views=True)

    def __iter__(self):
        names = []
        for sql_table in self.__metadata.sorted_tables:
            name = self.__converter._read_convert_name(sql_table.name)
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
            raise FrictionlessException(errors.StorageError(note=note))
        resource = self.__converter.sql_table_to_resource(sql_table)
        # TODO: Check if necessary
        resource.name = name
        resource.data = partial(self.__read_convert_data, name, order_by=order_by)
        return resource

    def read_package(self):
        package = Package()
        for name in self:
            resource = self.read_resource(name)
            package.resources.append(resource)
        return package

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
            yield list(result.keys())
            for item in result:
                cells = list(item)
                yield cells

    def __read_sql_table(self, name):
        sql_name = self.__converter._write_convert_name(name)
        if self.__namespace:
            sql_name = ".".join((self.__namespace, sql_name))
        return self.__metadata.tables.get(sql_name)

    # Write

    def write_resource(self, resource, *, force=False):
        package = Package(resources=[resource])
        self.write_package(package, force=force)

    def write_package(self, package, force=False):
        existent_names = list(self)

        # Check existent
        delete_names = []
        for resource in package.resources:
            if resource.name in existent_names:
                if not force:
                    note = f'Resource "{resource.name}" already exists'
                    raise FrictionlessException(errors.StorageError(note=note))
                delete_names.append(resource.name)

        # Wrap into a transaction
        with self.__connection.begin():

            # Create tables
            sql_tables = []
            self.delete_package(delete_names)
            for resource in package.resources:
                if not resource.schema:
                    resource.infer()
                sql_table = self.__converter.resource_to_sql_table(
                    resource, self.__metadata
                )
                sql_tables.append(sql_table)
            self.__metadata.create_all(tables=sql_tables)

            # Write data
            for resource in package.resources:
                self.__write_convert_data(resource)

    def __write_convert_data(self, resource):

        # Fallback fields
        fallback_fields = []
        mapping = self.__converter._write_convert_type()
        for field in resource.schema.fields:
            if not mapping.get(field.type):
                fallback_fields.append(field)

        # Timezone fields
        timezone_fields = []
        for field in resource.schema.fields:
            if field.type in ["datetime", "time"]:
                timezone_fields.append(field)

        # Write data
        buffer = []
        buffer_size = 1000
        sql_table = self.__read_sql_table(resource.name)
        with resource:
            for row in resource.row_stream:
                for field in fallback_fields:
                    row[field.name], notes = field.write_cell(row[field.name])
                for field in timezone_fields:
                    if row[field.name] is not None:
                        row[field.name] = row[field.name].replace(tzinfo=None)
                buffer.append(row)
                if len(buffer) > buffer_size:
                    self.__connection.execute(sql_table.insert().values(buffer))
                    buffer = []
            if len(buffer):
                self.__connection.execute(sql_table.insert().values(buffer))

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
                    raise FrictionlessException(errors.StorageError(note=note))
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


class SqlConverter:
    def __init__(self, sadialect=None, dialect=None):
        sa = helpers.import_from_plugin("sqlalchemy", plugin="sql")
        self.sadialect = sadialect or sa.engine.default.DefaultDialect()
        self.dialect = dialect or SqlDialect()

    # Read

    def _read_convert_name(self, sql_name):
        if sql_name.startswith(self.dialect.prefix):
            return sql_name.replace(self.dialect.prefix, "", 1)
        return None

    def _read_convert_type(self, sql_type=None):
        sa = helpers.import_from_plugin("sqlalchemy", plugin="sql")
        sapg = helpers.import_from_plugin("sqlalchemy.dialects.postgresql", plugin="sql")
        sams = helpers.import_from_plugin("sqlalchemy.dialects.mysql", plugin="sql")

        # Create mapping
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

    def sql_table_to_resource(self, sql_table):
        sa = helpers.import_from_plugin("sqlalchemy", plugin="sql")
        schema = Schema()

        # Fields
        for column in sql_table.columns:
            field_type = self._read_convert_type(column.type)
            field = Field(name=str(column.name), type=field_type)
            if not column.nullable:
                field.required = True
            if column.comment:
                field.description = column.comment
            schema.fields.append(field)

        # Primary key
        for constraint in sql_table.constraints:
            if isinstance(constraint, sa.PrimaryKeyConstraint):
                for column in constraint.columns:
                    schema.primary_key.append(str(column.name))

        # Foreign keys
        for constraint in sql_table.constraints:
            if isinstance(constraint, sa.ForeignKeyConstraint):
                resource = ""
                own_fields = []
                foreign_fields = []
                for element in constraint.elements:
                    own_fields.append(str(element.parent.name))
                    if element.column.table.name != sql_table.name:
                        res_name = element.column.table.name
                        resource = self._read_convert_name(res_name)
                    foreign_fields.append(str(element.column.name))
                ref = {"resource": resource, "fields": foreign_fields}
                schema.foreign_keys.append({"fields": own_fields, "reference": ref})

        # Return resource
        return Resource(name=sql_table.name, schema=schema)

    def sql_metadata_to_package(self, sql_metadata):
        package = Package()
        for sql_table in sql_metadata.tables:
            package.resources.append(self.sql_table_to_resource(sql_table))
        return package

    # Write

    def _write_convert_name(self, name):
        return self.dialect.prefix + name

    def _write_convert_type(self, type=None):
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
        if self.sadialect.name.startswith("postgresql"):
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

    def resource_to_sql_table(self, resource, metadata=None):
        sa = helpers.import_from_plugin("sqlalchemy", plugin="sql")

        # Prepare
        columns = []
        constraints = []
        sql_name = self._write_convert_name(resource.name)

        # Fields
        Check = sa.CheckConstraint
        for field in resource.schema.fields:
            checks = []
            quoted_name = self.sadialect.identifier_preparer.quote(field.name)
            column_type = self._write_convert_type(field.type)
            unique = field.constraints.get("unique", False)
            # https://stackoverflow.com/questions/1827063/mysql-error-key-specification-without-a-key-length
            if self.sadialect.name.startswith("mysql"):
                unique = unique and field.type != "string"
            for const, value in field.constraints.items():
                if const == "minLength":
                    checks.append(Check("LENGTH(%s) >= %s" % (quoted_name, value)))
                elif const == "maxLength":
                    # Some databases don't support TEXT as a Primary Key
                    # https://github.com/frictionlessdata/frictionless-py/issues/777
                    for prefix in ["mysql", "db2", "ibm"]:
                        if self.sadialect.name.startswith(prefix):
                            column_type = sa.VARCHAR(length=value)
                    checks.append(Check("LENGTH(%s) <= %s" % (quoted_name, value)))
                elif const == "minimum":
                    checks.append(Check("%s >= %s" % (quoted_name, value)))
                elif const == "maximum":
                    checks.append(Check("%s <= %s" % (quoted_name, value)))
                elif const == "pattern":
                    if self.sadialect.name.startswith("postgresql"):
                        checks.append(Check("%s ~ '%s'" % (quoted_name, value)))
                    else:
                        check = Check("%s REGEXP '%s'" % (quoted_name, value))
                        checks.append(check)
                elif const == "enum":
                    # NOTE: https://github.com/frictionlessdata/frictionless-py/issues/778
                    if field.type == "string":
                        enum_name = "%s_%s_enum" % (sql_name, field.name)
                        column_type = sa.Enum(*value, name=enum_name)
            column = sa.Column(
                field.name,
                column_type,
                *checks,
                nullable=not field.required,
                unique=unique,
                comment=field.description,
            )
            columns.append(column)

        # Primary key
        if resource.schema.primary_key is not None:
            constraint = sa.PrimaryKeyConstraint(*resource.schema.primary_key)
            constraints.append(constraint)

        # Foreign keys
        for fk in resource.schema.foreign_keys:
            fields = fk["fields"]
            foreign_name = fk["reference"]["resource"]
            foreign_fields = fk["reference"]["fields"]
            table_name = sql_name
            if foreign_name != "":
                table_name = self._write_convert_name(foreign_name)
            composer = lambda field: ".".join([table_name, field])
            foreign_fields = list(map(composer, foreign_fields))
            constraint = sa.ForeignKeyConstraint(fields, foreign_fields)
            constraints.append(constraint)

        # Create sql table
        return sa.Table(
            sql_name,
            metadata or sa.MetaData(schema=self.dialect.namespace),
            *columns,
            *constraints,
            comment=resource.description,
        )

    def package_to_sql_metadata(self, package):
        sa = helpers.import_from_plugin("sqlalchemy", plugin="sql")

        metadata = sa.MetaData(schema=self.dialect.namespace)
        for resource in package.resources:
            _ = self.resource_to_sql_table(resource, metadata=metadata)
        return metadata
