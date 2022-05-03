from ...metadata import Metadata
from ...dialect import Dialect


class BigqueryDialect(Dialect):
    """Bigquery dialect representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.bigquery import BigqueryDialect`

    Parameters:
        descriptor? (str|dict): descriptor
        project (str): project
        dataset? (str): dataset
        table? (str): table

    Raises:
        FrictionlessException: raise any error that occurs during the process
    """

    def __init__(
        self,
        descriptor=None,
        *,
        project=None,
        dataset=None,
        prefix=None,
        table=None,
    ):
        self.setinitial("project", project)
        self.setinitial("dataset", dataset)
        self.setinitial("prefix", prefix)
        self.setinitial("table", table)
        super().__init__(descriptor)

    @Metadata.property
    def project(self):
        return self.get("project")

    @Metadata.property
    def dataset(self):
        return self.get("dataset")

    @Metadata.property
    def prefix(self):
        return self.get("prefix") or ""

    @Metadata.property
    def table(self):
        return self.get("table")

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["table"],
        "additionalProperties": False,
        "properties": {
            "project": {"type": "string"},
            "dataset": {"type": "string"},
            "prefix": {"type": "string"},
            "table": {"type": "string"},
        },
    }
