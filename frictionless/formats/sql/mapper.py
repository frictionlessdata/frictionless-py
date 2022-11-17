from __future__ import annotations
import json
from datetime import datetime, date, timezone
from typing import TYPE_CHECKING, Dict, Type, List, Any
from ...platform import platform
from ...schema import Schema, Field

if TYPE_CHECKING:
    from sqlalchemy.schema import Table
    from sqlalchemy.engine import Engine
    from sqlalchemy.types import TypeEngine
    from ...table import Row


# TODO: accept engine in constructor?
class SqlMapper:
    """Metadata mapper Frictionless from/to SQL"""

    # Import

    def from_schema(self, schema: Schema, *, engine: Engine, table_name: str) -> Table:
        """Convert frictionless schema to sqlalchemy table"""

        # Prepare
        columns = []
        constraints = []
        sa = platform.sqlalchemy

        # Fields
        Check = sa.CheckConstraint
        quote = engine.dialect.identifier_preparer.quote  # type: ignore
        for field in schema.fields:
            checks = []
            nullable = not field.required
            quoted_name = quote(field.name)
            column_type = self.from_field(field, engine=engine)
            unique = field.constraints.get("unique", False)
            # https://stackoverflow.com/questions/1827063/mysql-error-key-specification-without-a-key-length
            if engine.dialect.name.startswith("mysql"):
                unique = unique and field.type != "string"
            for const, value in field.constraints.items():
                if const == "minLength":
                    checks.append(Check("LENGTH(%s) >= %s" % (quoted_name, value)))
                elif const == "maxLength":
                    # Some databases don't support TEXT as a Primary Key
                    # https://github.com/frictionlessdata/frictionless-py/issues/777
                    for prefix in ["mysql", "db2", "ibm"]:
                        if engine.dialect.name.startswith(prefix):
                            column_type = sa.VARCHAR(length=value)
                    checks.append(Check("LENGTH(%s) <= %s" % (quoted_name, value)))
                elif const == "minimum":
                    checks.append(Check("%s >= %s" % (quoted_name, value)))
                elif const == "maximum":
                    checks.append(Check("%s <= %s" % (quoted_name, value)))
                elif const == "pattern":
                    if engine.dialect.name.startswith("postgresql"):
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
            constraint = sa.PrimaryKeyConstraint(*schema.primary_key)
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
        table = sa.Table(table_name, sa.MetaData(engine), *(columns + constraints))
        return table

    def from_field(self, field: Field, *, engine: Engine) -> Type[TypeEngine]:
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
        if engine.dialect.name.startswith("postgresql"):
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

    def from_row(self, row: Row) -> List[Any]:
        """Convert frictionless row to list of sql cells"""
        cells = []
        for field in row.fields:
            cell = row[field.name]
            if cell is not None:
                if field.type in ["object", "geojson"]:
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

    # Export

    def to_schema(self, table: Table) -> Schema:
        """Convert sqlalchemy table to frictionless schema"""

        # Prepare
        sa = platform.sqlalchemy
        schema = Schema()

        # Fields
        for column in table.columns:
            field = self.to_field(column.type, name=str(column.name))
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
                        resource = element.column.table.name
                    foreign_fields.append(str(element.column.name))
                ref = {"resource": resource, "fields": foreign_fields}
                schema.foreign_keys.append({"fields": own_fields, "reference": ref})

        # Return schema
        return schema

    def to_field(self, type: TypeEngine, *, name: str) -> Field:
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
