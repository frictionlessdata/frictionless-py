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
    https://cloud.google.com/bigquery/docs/tables#table_naming
    """

    dataset: Optional[str] = None
    """
    Name of the dataset in the project defined by "project"
    field. Dataset names cannot contain spaces or special characters
    such as -, &, @, or %. The naming convention for dataset can be
    found here.
    https://cloud.google.com/bigquery/docs/datasets#dataset-naming
    """

    project: Optional[str] = None
    """

    """

    prefix: Optional[str] = ""
    """
    Unique identifier for the project in Bigquery i.e, project_id.
    Details about project_id can be found here.
    https://cloud.google.com/resource-manager/docs/creating-managing-projects#before_you_begin
    """

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "table": {"type": "string"},
            "dataset": {"type": "string"},
            "project": {"type": "string"},
            "prefix": {"type": "string"},
        },
    }
