from __future__ import annotations
import attrs
from typing import Optional, List
from ...dialect import Control


@attrs.define(kw_only=True)
class CkanControl(Control):
    """Ckan control representation"""

    type = "ckan"

    # State

    baseurl: Optional[str] = None
    """
    Endpoint url for CKAN instance.
    """

    dataset: Optional[str] = None
    """
    Unique identifier of the dataset to read.
    """

    resource: Optional[str] = None
    """NOTE: add docs"""

    apikey: Optional[str] = None
    """
    The access token to authenticate to the CKAN instance. It is required 
    to write files to CKAN instance.
    """

    fields: Optional[List[str]] = None
    """
    Specify the number of fields to read. Other fields
    will not be read.
    """

    limit: Optional[int] = None
    """
    Limit the number of records to read.
    """

    sort: Optional[str] = None
    """
    Field by which to sort the data before reading the data.
    """

    filters: Optional[dict] = None
    """
    Params as a list of dict to filter the data while reading.
    """

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "baseurl": {"type": "string"},
            "dataset": {"type": "string"},
            "resource": {"type": "string"},
            "apikey": {"type": "string"},
            "fields": {"type": "array", "items": {"type": "string"}},
            "limit": {"type": "integer"},
            "sort": {"type": "string"},
            "filters": {"type": "object"},
        },
    }
