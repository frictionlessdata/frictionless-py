from __future__ import annotations
from typing import TYPE_CHECKING
from ...platform import platform

if TYPE_CHECKING:
    from ...schema import Schema, Field
    from sqlalchemy.schema import Table
    from sqlalchemy.engine.base import Engine
    from sqlalchemy.types import TypeEngine


class SqlMapper:
    """Metadata mapper Frictionless from/to SQL"""

    # Import

    def from_schema(self, schema: Schema, *, engine: Engine, table_name: str) -> Table:
        """Convert frictionless schema to sqlalchemy schema items
        as columns and constraints
        """

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
        table = sa.Table(table_name, sa.MetaData(), *(columns + constraints))
        return table

    def from_field(self, field: Field, *, engine: Engine) -> TypeEngine:
        """Convert frictionless field to sqlalchemy type
        as e.g. sa.Text or sa.Integer
        """

        # Prepare
        sa = platform.sqlalchemy
        sapg = platform.sqlalchemy_dialects_postgresql

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
        if engine.dialect.name.startswith("postgresql"):
            mapping.update(
                {
                    "array": sapg.JSONB,
                    "geojson": sapg.JSONB,
                    "number": sa.Numeric,
                    "object": sapg.JSONB,
                }
            )

        return mapping.get(field.type, sa.Text)

    # Export

    def to_schema(self):
        pass

    def to_field(self):
        pass
