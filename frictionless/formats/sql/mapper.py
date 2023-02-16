from __future__ import annotations
import json
from datetime import datetime, date, timezone
from typing import TYPE_CHECKING, Dict, Type, List, Any
from ...platform import platform
from ...schema import Schema, Field
from ...system import Mapper

if TYPE_CHECKING:
    from sqlalchemy import Dialect
    from sqlalchemy.schema import Table, Column
    from sqlalchemy.types import TypeEngine
    from ...table import Row


ROW_NUMBER_IDENTIFIER = "_rowNumber"
ROW_VALID_IDENTIFIER = "_rowValid"


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
        """Convert sqlalchemy type to frictionless field
        as e.g. sa.Text -> Field(type=string)
        """
        sa = platform.sqlalchemy
        sapg = platform.sqlalchemy_dialects_postgresql
        sams = platform.sqlalchemy_dialects_mysql

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

    # Write

    def write_schema(
        self, schema: Schema, *, table_name: str, with_metadata: bool = False
    ) -> Table:
        """Convert frictionless schema to sqlalchemy table"""

        # Prepare
        columns = []
        constraints = []
        sa = platform.sqlalchemy

        # Fields
        Check = sa.CheckConstraint
        quote = self.dialect.identifier_preparer.quote  # type: ignore
        if with_metadata:
            columns.append(sa.Column(ROW_NUMBER_IDENTIFIER, sa.Integer, primary_key=True))
            columns.append(sa.Column(ROW_VALID_IDENTIFIER, sa.Boolean))
        for field in schema.fields:
            checks = []
            nullable = not field.required
            # TODO: why it's not required?
            assert field.name
            quoted_name = quote(field.name)
            column_type = self.write_field(field)

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
                        checks.append(
                            Check("LENGTH(%s) <= %s" % (quoted_name, max_length))
                        )
                if min_length is not None:
                    if (
                        not isinstance(column_type, sa.CHAR)
                        or self.dialect.name == "sqlite"
                    ):
                        checks.append(
                            Check("LENGTH(%s) >= %s" % (quoted_name, min_length))
                        )

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

    def write_field(self, field: Field) -> Type[TypeEngine]:
        """Convert frictionless field to sqlalchemy type
        as e.g. Field(type=string) -> sa.Text
        """
        sa = platform.sqlalchemy
        sapg = platform.sqlalchemy_dialects_postgresql

        # Default dialect
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

        # Postgresql dialect
        if self.dialect.name == "postgresql":
            mapping.update(
                {
                    "array": sapg.JSONB,
                    "geojson": sapg.JSONB,
                    "number": sa.Numeric,
                    "object": sapg.JSONB,
                }
            )

        # Get type
        type = mapping.get(field.type, sa.Text)
        return type

    def write_row(self, row: Row) -> List[Any]:
        """Convert frictionless row to list of sql cells"""
        cells = []
        sa = platform.sqlalchemy
        for field in row.fields:
            cell = row[field.name]
            if cell is not None:
                type = self.write_field(field)
                if field.type != "string" and type is sa.Text:
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
            cells.append(cell)
        return cells
