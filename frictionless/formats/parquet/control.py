from __future__ import annotations
import attrs
from typing import Optional, List, Any
from ...dialect import Control
from ... import helpers


@attrs.define(kw_only=True)
class ParquetControl(Control):
    """Json control representation"""

    type = "parquet"

    # State

    columns: Optional[List[str]] = None
    """NOTE: add docs"""

    categories: Optional[Any] = None
    """NOTE: add docs"""

    filters: Optional[Any] = False
    """NOTE: add docs"""

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
