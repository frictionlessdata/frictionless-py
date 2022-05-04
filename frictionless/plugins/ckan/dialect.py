from ...metadata import Metadata
from ...dialect import Dialect


class CkanDialect(Dialect):
    """Ckan dialect representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.ckan import CkanDialect`

    Parameters:
        descriptor? (str|dict): descriptor
        resource? (str): resource
        dataset? (str): dataset
        apikey? (str): apikey
        fields? (array): limit ckan query to certain fields
        limit? (int): limit number of returned entries
        sort? (str): sort returned entries, e.g. by date descending: `date desc`
        filters? (dict): filter data, e.g. field with value: `{ "key": "value" }`

    Raises:
        FrictionlessException: raise any error that occurs during the process
    """

    def __init__(
        self,
        descriptor=None,
        *,
        dataset=None,
        resource=None,
        apikey=None,
        fields=None,
        limit=None,
        sort=None,
        filters=None,
    ):
        self.setinitial("resource", resource)
        self.setinitial("dataset", dataset)
        self.setinitial("apikey", apikey)
        self.setinitial("fields", fields)
        self.setinitial("limit", limit)
        self.setinitial("sort", sort)
        self.setinitial("filters", filters)
        super().__init__(descriptor)

    @Metadata.property
    def resource(self):
        return self.get("resource")

    @Metadata.property
    def dataset(self):
        return self.get("dataset")

    @Metadata.property
    def apikey(self):
        return self.get("apikey")

    @Metadata.property
    def fields(self):
        return self.get("fields")

    @Metadata.property
    def limit(self):
        return self.get("limit")

    @Metadata.property
    def sort(self):
        return self.get("sort")

    @Metadata.property
    def filters(self):
        return self.get("filters")

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["resource", "dataset"],
        "additionalProperties": False,
        "properties": {
            "resource": {"type": "string"},
            "dataset": {"type": "string"},
            "apikey": {"type": "string"},
            "fields": {"type": "array"},
            "limit": {"type": "integer"},
            "sort": {"type": "string"},
            "filters": {"type": "object"},
        },
    }
