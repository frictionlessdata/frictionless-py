from __future__ import annotations

# General

BLOCK_SIZE = 8096
BUFFER_SIZE = 1000
ROW_NUMBER_IDENTIFIER = "_rowNumber"
ROW_VALID_IDENTIFIER = "_rowValid"

# Prefixes

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
