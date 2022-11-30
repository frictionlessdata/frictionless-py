from __future__ import annotations
import attrs
from typing import Optional
from ...dialect import Control


@attrs.define(kw_only=True)
class CkanControl(Control):
    """Ckan control representation"""

    type = "ckan"

    # State

    baseurl: Optional[str] = None
    """
    Endpoint url for CKAN instance. e.g. https://dados.gov.br
    """

    dataset: Optional[str] = None
    """
    Unique identifier of the dataset to read.
    """

    apikey: Optional[str] = None
    """
    The access token to authenticate to the CKAN instance. It is required 
    to write files to CKAN instance.
    """

    ignore_package_errors: Optional[bool] = False
    """
    Ignore Package errors in a Catalog. If multiple packages are being downloaded
    and one fails with an invalid descriptor, continue downloading the rest.
    """

    ignore_schema: Optional[bool] = False
    """
    Ignore dataset resources schemas
    """

    group_id: Optional[str] = None
    """
    CKAN Group id to get datasets in a Catalog
    """

    organization_name: Optional[str] = None
    """
    CKAN Organization name to get datasets in a Catalog
    """

    search: Optional[dict] = None
    """
    CKAN Search parameters as defined on https://docs.ckan.org/en/2.9/api/#ckan.logic.action.get.package_search
    """

    num_packages: Optional[int] = None
    """
    Maximum number of packages to fetch
    """

    results_offset: Optional[int] = None
    """
    Results page number
    """

    allow_update: Optional[bool] = False
    """
    Update a dataset on publish with an id is provided on the package descriptor
    """

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "baseurl": {"type": "string"},
            "dataset": {"type": "string"},
            "apikey": {"type": "string"},
            "group_id": {"type": "string"},
            "organization_name": {"type": "string"},
            "search": {"type": "object"},
            "ignore_package_errors": {"type": "bool"},
            "ignore_schema": {"type": "bool"},
            "num_packages": {"type": "int"},
            "results_offset": {"type": "int"},
            "allow_update": {"type": "bool"},
        },
    }
