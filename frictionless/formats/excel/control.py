from __future__ import annotations
import attrs
from typing import Optional, Union, Any
from ...dialect import Control
from . import settings


@attrs.define(kw_only=True)
class ExcelControl(Control):
    """Excel control representation.

    Control class to set params for Excel reader/writer.

    """

    type = "excel"

    # State

    sheet: Union[str, int] = settings.DEFAULT_SHEET
    """
    Name of the sheet from where to read or write data.
    """

    workbook_cache: Optional[Any] = None
    """
    An empty dictionary which is used to handle workbook caching for remote workbooks.
    It stores the path to the temporary file while reading remote workbooks. 
    """

    fill_merged_cells: bool = False
    """
    If True, it will unmerge and fill all merged cells by the visible value.
    Default value is False.
    """

    preserve_formatting: bool = False
    """
    If set to True, it preserves text formatting for numeric and temporal cells. If not set,
    it will return all cell value as string. Default value is False.
    """

    adjust_floating_point_error: bool = False
    """
    If True, it corrects the Excel behavior regarding floating point numbers. 
    For example: 274.65999999999997 -> 274.66 (When True).
    """

    stringified: bool = False
    """
    Stringifies all the cell values. Default value
    is False.
    """

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "sheet": {"type": ["number", "string"]},
            "fillMergedCells": {"type": "boolean"},
            "preserveFormatting": {"type": "boolean"},
            "adjustFloatingPointError": {"type": "boolean"},
        },
    }
