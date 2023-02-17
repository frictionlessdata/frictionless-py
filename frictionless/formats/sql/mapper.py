from __future__ import annotations
import json
from datetime import datetime, date, timezone
from typing import TYPE_CHECKING, Dict, Type
from ...platform import platform
from ...schema import Schema, Field
from ...system import Mapper
from . import settings

if TYPE_CHECKING:
    from sqlalchemy import Dialect
    from sqlalchemy.schema import Table, Column
    from sqlalchemy.types import TypeEngine
    from ...table import Row


class SqlMapper(Mapper):
    """Metadata mapper Frictionless from/to SQL

    Partialy based on unmerged @ezwelty's work:
    - https://github.com/frictionlessdata/framework/pull/862

    """

    dialect: Dialect

    def __init__(self, dialect: str):
        self.dialect = platform.sqlalchemy_dialects.registry.load(dialect)()

    # Read

    def read_schema(self, table: Table) -> Schema:
        """Convert sqlalchemy table to frictionless schema"""
        sa = platform.sqlalchemy
        schema = Schema()

        # Fields
        for column in table.columns:
            field = self.read_field(column)
            schema.add_field(field)

        # Primary key
        for constraint in table.constraints:
            if isinstance(constraint, sa.PrimaryKeyConstraint):
                for column in constraint.columns:
                    schema.primary_key.append(str(column.name))

        # Foreign keys
        for constraint in table.constraints:
            if isinstance(constraint, sa.ForeignKeyConstraint):
                resource = ""
                own_fields = []
                foreign_fields = []
                for element in constraint.elements:
                    own_fields.append(str(element.parent.name))
                    if element.column.table.name != table.name:
                        resource = str(element.column.table.name)
                    foreign_fields.append(str(element.column.name))
                ref = {"resource": resource, "fields": foreign_fields}
                schema.foreign_keys.append({"fields": own_fields, "reference": ref})

        return schema

    def read_field(self, column: Column) -> Field:
        """Convert sqlalchemy Column to frictionless Field"""
        sa = platform.sqlalchemy
        sapg = platform.sqlalchemy_dialects_postgresql
        sams = platform.sqlalchemy_dialects_mysql

        # Type mapping
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

        # Create filed
        name = str(column.name)
        type = "string"
        for type_class, value in mapping.items():
            if isinstance(column.type, type_class):
                type = value
        field = Field.from_descriptor(dict(name=name, type=type))
        if isinstance(column.type, (sa.CHAR, sa.VARCHAR)):
            field.constraints["maxLength"] = column.type.length
        if isinstance(column.type, sa.CHAR):
            field.constraints["minLength"] = column.type.length
        if isinstance(column.type, sa.Enum):
            field.constraints["enum"] = column.type.enums
        if not column.nullable:
            field.required = True
        if column.comment:
            field.description = column.comment

        return field

    def read_type(self, column_type: str) -> str:
        """Convert sqlalchemy type to frictionless type"""
        sa = platform.sqlalchemy
        sapg = platform.sqlalchemy_dialects_postgresql
        sams = platform.sqlalchemy_dialects_mysql

        # General mapping
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
        field_type = "string"
        for type_class, value in mapping.items():
            if isinstance(column_type, type_class):
                field_type = value
        return field_type

    # Write

    def write_schema(
        self, schema: Schema, *, table_name: str, with_metadata: bool = False
    ) -> Table:
        """Convert frictionless schema to sqlalchemy table"""
        sa = platform.sqlalchemy
        columns = []
        constraints = []

        # Fields
        if with_metadata:
            columns.append(
                sa.Column(settings.ROW_NUMBER_IDENTIFIER, sa.Integer, primary_key=True)
            )
            columns.append(sa.Column(settings.ROW_VALID_IDENTIFIER, sa.Boolean))
        for field in schema.fields:
            column = self.write_field(field, table_name=table_name)
            columns.append(column)

        # Primary key
        if schema.primary_key:
            Class = sa.UniqueConstraint if with_metadata else sa.PrimaryKeyConstraint
            if not with_metadata:
                constraint = Class(*schema.primary_key)
                constraints.append(constraint)

        # Foreign keys
        for fk in schema.foreign_keys:
            fields = fk["fields"]
            foreign_fields = fk["reference"]["fields"]
            foreign_table_name = fk["reference"]["resource"] or table_name
            composer = lambda field: ".".join([foreign_table_name, field])
            foreign_fields = list(map(composer, foreign_fields))
            constraint = sa.ForeignKeyConstraint(fields, foreign_fields)
            constraints.append(constraint)

        # Table
        table = sa.Table(table_name, sa.MetaData(), *(columns + constraints))
        return table

    def write_field(self, field: Field, *, table_name: str) -> Column:
        """Convert frictionless Field to sqlalchemy Column"""
        sa = platform.sqlalchemy
        quote = self.dialect.identifier_preparer.quote  # type: ignore
        Check = sa.CheckConstraint
        checks = []

        # General properties
        # TODO: why it's not required?
        assert field.name
        quoted_name = quote(field.name)
        column_type = self.write_type(field.type)
        nullable = not field.required

        # Length contraints
        if field.type == "string":
            min_length = field.constraints.get("minLength", None)
            max_length = field.constraints.get("maxLength", None)
            if (
                min_length is not None
                and max_length is not None
                and min_length == max_length
            ):
                column_type = sa.CHAR(max_length)
            if max_length is not None:
                if column_type is sa.Text:
                    column_type = sa.VARCHAR(length=max_length)
                if self.dialect.name == "sqlite":
                    checks.append(Check("LENGTH(%s) <= %s" % (quoted_name, max_length)))
            if min_length is not None:
                if not isinstance(column_type, sa.CHAR) or self.dialect.name == "sqlite":
                    checks.append(Check("LENGTH(%s) >= %s" % (quoted_name, min_length)))

        # Unique contstraint
        unique = field.constraints.get("unique", False)
        if self.dialect.name == "mysql":
            # MySQL requires keys to have an explicit maximum length
            # https://stackoverflow.com/questions/1827063/mysql-error-key-specification-without-a-key-length
            unique = unique and column_type is not sa.Text

        # Others contstraints
        for const, value in field.constraints.items():
            if const == "minimum":
                checks.append(Check("%s >= %s" % (quoted_name, value)))
            elif const == "maximum":
                checks.append(Check("%s <= %s" % (quoted_name, value)))
            elif const == "pattern":
                if self.dialect.name == "postgresql":
                    checks.append(Check("%s ~ '%s'" % (quoted_name, value)))
                else:
                    check = Check("%s REGEXP '%s'" % (quoted_name, value))
                    checks.append(check)
            elif const == "enum":
                # NOTE: https://github.com/frictionlessdata/frictionless-py/issues/778
                if field.type == "string":
                    enum_name = "%s_%s_enum" % (table_name, field.name)
                    column_type = sa.Enum(*value, name=enum_name)

        # Create column
        column_args = [field.name, column_type] + checks
        column_kwargs = {"nullable": nullable, "unique": unique}
        if field.description:
            column_kwargs["comment"] = field.description
        column = sa.Column(*column_args, **column_kwargs)

        return column

    def write_type(self, field_type: str) -> Type[TypeEngine]:
        """Convert frictionless type to sqlalchemy type"""
        sa = platform.sqlalchemy
        sapg = platform.sqlalchemy_dialects_postgresql

        # General mapping
        mapping: Dict[str, Type[TypeEngine]] = {
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

        # Postgres mapping
        if self.dialect.name == "postgresql":
            mapping.update(
                {
                    "array": sapg.JSONB,
                    "geojson": sapg.JSONB,
                    "number": sa.Numeric,
                    "object": sapg.JSONB,
                }
            )

        return mapping.get(field_type, sa.Text)

    def write_row(self, row: Row, *, with_metadata: bool = False) -> Dict:
        """Convert frictionless Row to a sqlalchemy Item for insertion"""
        sa = platform.sqlalchemy
        item = {}
        if with_metadata:
            item["_rowNumber"] = row.row_number
            item["_rowValid"] = row.valid
        for field in row.fields:
            cell = row[field.name]
            if cell is not None:
                column_type = self.write_type(field.type)
                if field.type != "string" and column_type is sa.Text:
                    cell, _ = field.write_cell(cell)
                elif field.type in ["object", "geojson"]:
                    cell = json.dumps(cell)
                elif field.type == "datetime":
                    if cell.tzinfo is not None:
                        dt = cell.astimezone(timezone.utc)
                        cell = dt.replace(tzinfo=None)
                elif field.type == "time":
                    if cell.tzinfo is not None:
                        dt = datetime.combine(date.min, cell)
                        dt = dt.astimezone(timezone.utc)
                        cell = dt.time()
            item[field.name] = cell
        return item
