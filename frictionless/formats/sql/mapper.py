from __future__ import annotations
import json
from datetime import datetime, date, timezone
from typing import TYPE_CHECKING, Dict, Type, List, Any
from ...platform import platform
from ...schema import Schema, Field
from ...system import Mapper

if TYPE_CHECKING:
    from sqlalchemy.schema import Table
    from sqlalchemy.engine import Engine
    from sqlalchemy.types import TypeEngine
    from ...table import Row


COLUMN_NAME_NUMBER = "_row_number"
COLUMN_NAME_VALID = "_row_valid"


class SqlMapper(Mapper):
    """Metadata mapper Frictionless from/to SQL"""

    # TODO: accept only url/dialect_name not engine (but we need access to dialect quote)?
    def __init__(self, engine: Engine):
        self.engine = engine

    # State

    engine: Engine

    # Read

    def read_schema(self, table: Table) -> Schema:
        """Convert sqlalchemy table to frictionless schema"""

        # Prepare
        sa = platform.sqlalchemy
        schema = Schema()

        # Fields
        for column in table.columns:
            field = self.read_field(column.type, name=str(column.name))
            if not column.nullable:
                field.required = True
            if column.comment:
                field.description = column.comment
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

        # Return schema
        return schema

    def read_field(self, type: TypeEngine, *, name: str) -> Field:
        """Convert sqlalchemy type to frictionless field
        as e.g. sa.Text -> Field(type=string)
        """

        # Prepare
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

        # Get type
        field_type = "string"
        for type_class, value in mapping.items():
            if isinstance(type, type_class):
                field_type = value

        return Field.from_descriptor(dict(name=name, type=field_type))

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
        quote = self.engine.dialect.identifier_preparer.quote  # type: ignore
        if with_metadata:
            columns.append(sa.Column(COLUMN_NAME_NUMBER, sa.Integer, primary_key=True))
            columns.append(sa.Column(COLUMN_NAME_VALID, sa.Boolean))
        for field in schema.fields:
            checks = []
            nullable = not field.required
            quoted_name = quote(field.name)
            column_type = self.write_field(field)
            unique = field.constraints.get("unique", False)
            # https://stackoverflow.com/questions/1827063/mysql-error-key-specification-without-a-key-length
            if self.engine.dialect.name.startswith("mysql"):
                unique = unique and field.type != "string"
            for const, value in field.constraints.items():
                if const == "minLength":
                    checks.append(Check("LENGTH(%s) >= %s" % (quoted_name, value)))
                elif const == "maxLength":
                    # Some databases don't support TEXT as a Primary Key
                    # https://github.com/frictionlessdata/frictionless-py/issues/777
                    for prefix in ["mysql", "db2", "ibm"]:
                        if self.engine.dialect.name.startswith(prefix):
                            column_type = sa.VARCHAR(length=value)
                    checks.append(Check("LENGTH(%s) <= %s" % (quoted_name, value)))
                elif const == "minimum":
                    checks.append(Check("%s >= %s" % (quoted_name, value)))
                elif const == "maximum":
                    checks.append(Check("%s <= %s" % (quoted_name, value)))
                elif const == "pattern":
                    if self.engine.dialect.name.startswith("postgresql"):
                        checks.append(Check("%s ~ '%s'" % (quoted_name, value)))
                    else:
                        check = Check("%s REGEXP '%s'" % (quoted_name, value))
                        checks.append(check)
                elif const == "enum":
                    # NOTE: https://github.com/frictionlessdata/frictionless-py/issues/778
                    if field.type == "string":
                        enum_name = "%s_%s_enum" % (table_name, field.name)
                        column_type = sa.Enum(*value, name=enum_name)
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

        # Prepare
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
        if self.engine.dialect.name.startswith("postgresql"):
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
