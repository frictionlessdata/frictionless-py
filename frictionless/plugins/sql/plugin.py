from ...plugin import Plugin
from .dialect import SqlDialect
from .parser import SqlParser
from .storage import SqlStorage


# NOTE:
# Can we improve `engline.dialect.name.startswith()` checks?


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
