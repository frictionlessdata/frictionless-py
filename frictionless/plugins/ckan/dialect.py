from dataclasses import dataclass
from typing import Optional, List
from ...dialect import Dialect


@dataclass
class CkanDialect(Dialect):
    """Ckan dialect representation"""

    # Properties

    resource: str
    """TODO: add docs"""

    dataset: str
    """TODO: add docs"""

    apikey: Optional[str] = None
    """TODO: add docs"""

    fields: Optional[List[str]] = None
    """TODO: add docs"""

    limit: Optional[int] = None
    """TODO: add docs"""

    sort: Optional[str] = None
    """TODO: add docs"""

    filters: Optional[dict] = None
    """TODO: add docs"""

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
