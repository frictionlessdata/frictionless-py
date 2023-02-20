from __future__ import annotations
import attrs
from typing import Optional
from ...dialect import Control


@attrs.define(kw_only=True)
class SqlControl(Control):
    """SQL control representation.

    Control class to set params for Sql read/write class.

    """

    type = "sql"

    table: Optional[str] = None
    """
    Table name from which to read the data.
    """

    order_by: Optional[str] = None
    """
    It specifies the ORDER BY keyword for SQL queries to sort the
    results that are being read. The default value is None.
    """

    where: Optional[str] = None
    """
    It specifies the WHERE clause to filter the records in SQL
    queries. The default value is None.
    """

    namespace: Optional[str] = None
    """
    To refer to table using schema or namespace or database such as
    `FOO`.`TABLEFOO1` we can specify namespace. For example:
    control = formats.SqlControl(table="test_table", namespace="FOO")
    """

    basepath: Optional[str] = None
    """
    It specifies the base path for the database. The basepath will
    be appended to the db path. The default value is None. For example:
    formats.SqlControl(table="test_table", basepath="data")
    """

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "table": {"type": "string"},
            "prefix": {"type": "string"},
            "order_by": {"type": "string"},
            "where": {"type": "string"},
            "namespace": {"type": "string"},
            "basepath": {"type": "string"},
        },
    }
