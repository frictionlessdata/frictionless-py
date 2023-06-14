from __future__ import annotations

# General

BUFFER_SIZE = 1000
ROW_NUMBER_IDENTIFIER = "_rowNumber"
ROW_VALID_IDENTIFIER = "_rowValid"
METADATA_IDENTIFIERS = [ROW_NUMBER_IDENTIFIER, ROW_VALID_IDENTIFIER]

# Prefixes

# https://docs.sqlalchemy.org/en/13/core/engines.html
# https://docs.sqlalchemy.org/en/13/dialects/index.html
SCHEME_PREFIXES = [
    "postgresql",
    "mysql",
    "oracle",
    "mssql",
    "sqlite",
    "duckdb",
    "firebird",
    "sybase",
    "db2",
    "ibm",
]
