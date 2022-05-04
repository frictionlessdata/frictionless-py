from ...metadata import Metadata
from ...dialect import Dialect


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
        where? (str): where statement passed to SQL
        namespace? (str): SQL schema
        basepath? (str): a basepath, for example, for SQLite path

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
        where=None,
        namespace=None,
        basepath=None,
    ):
        self.setinitial("table", table)
        self.setinitial("prefix", prefix)
        self.setinitial("order_by", order_by)
        self.setinitial("where", where)
        self.setinitial("namespace", namespace)
        self.setinitial("basepath", basepath)
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
    def where(self):
        return self.get("where")

    @Metadata.property
    def namespace(self):
        return self.get("namespace")

    @Metadata.property
    def basepath(self):
        return self.get("basepath")

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["table"],
        "additionalProperties": False,
        "properties": {
            "table": {"type": "string"},
            "prefix": {"type": "string"},
            "order_by": {"type": "string"},
            "where": {"type": "string"},
            "namespace": {"type": "string"},
            "basepath": {"type": "string"},
        },
    }
