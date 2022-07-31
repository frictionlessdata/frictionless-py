from __future__ import annotations
import attrs
from typing import Optional, Union, Any
from ...dialect import Control
from . import settings


@attrs.define(kw_only=True)
class ExcelControl(Control):
    """Excel control representation"""

    type = "excel"

    # State

    sheet: Union[str, int] = settings.DEFAULT_SHEET
    """NOTE: add docs"""

    workbook_cache: Optional[Any] = None
    """NOTE: add docs"""

    fill_merged_cells: bool = False
    """NOTE: add docs"""

    preserve_formatting: bool = False
    """NOTE: add docs"""

    adjust_floating_point_error: bool = False
    """NOTE: add docs"""

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "sheet": {"type": ["number", "string"]},
            "fillMergedCells": {"type": "boolean"},
            "preserveFormatting": {"type": "boolean"},
            "adjustFloatingPointError": {"type": "boolean"},
        },
    }
