from __future__ import annotations
import attrs
from typing import Optional
from ...dialect import Control


@attrs.define(kw_only=True)
class BigqueryControl(Control):
    """Bigquery control representation.
    
    Control class to set params for Bigquery api.

    """

    type = "bigquery"

    # State

    table: Optional[str] = None
    """
    Name of the table in Bigquery from where to read the data.
    Table name is unique per dataset. The convention for naming
    a table can be found here.
    """

    dataset: Optional[str] = None
    """NOTE: add docs"""

    project: Optional[str] = None
    """NOTE: add docs"""

    prefix: Optional[str] = ""
    """NOTE: add docs"""

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "table": {"type": "string"},
            "dataset": {"type": "string"},
            "project": {"type": "string"},
            "prefix": {"type": "string"},
        },
    }
