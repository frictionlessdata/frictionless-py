from __future__ import annotations
import attrs
from typing import Optional, List, Any
from ...dialect import Control
from ... import helpers


@attrs.define(kw_only=True)
class ParquetControl(Control):
    """Parquet control representation.

    Control class to set params for Parquet read/write class.

    """

    type = "parquet"

    # State

    columns: Optional[List[str]] = None
    """
    A list of columns to load. By selecting columns, we can only access
    parts of file that we are interested in and skip columns that are
    not of interest. Default value is None.
    """

    categories: Optional[Any] = None
    """
    List of columns that should be returned as Pandas Category-type column.
    The second example specifies the number of expected labels for that column.
    For example: categories=['col1'] or categories={'col1': 12}
    """

    filters: Optional[Any] = False
    """
    Specifies the condition to filter data(row-groups).
    For example: [('col3', 'in', [1, 2, 3, 4])])
    """

    # Convert

    def to_python(self):
        """Convert to options"""
        return helpers.cleaned_dict(
            columns=self.columns,
            categories=self.categories,
            filters=self.filters,
        )

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "columns": {"type": "array", "items": {"type": "string"}},
            "categories": {},
            "filters": {},
        },
    }
