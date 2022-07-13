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
    """TODO: add docs"""

    workbook_cache: Optional[Any] = None
    """TODO: add docs"""

    fill_merged_cells: bool = False
    """TODO: add docs"""

    preserve_formatting: bool = False
    """TODO: add docs"""

    adjust_floating_point_error: bool = False
    """TODO: add docs"""

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "sheet": {"type": ["number", "string"]},
            "workbookCache": {"type": "object"},
            "fillMergedCells": {"type": "boolean"},
            "preserveFormatting": {"type": "boolean"},
            "adjustFloatingPointError": {"type": "boolean"},
        },
    }
