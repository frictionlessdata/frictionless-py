from __future__ import annotations

from typing import Any, Optional, Union

import attrs

from ...dialect import Control
from . import settings


@attrs.define(kw_only=True, repr=False)
class ExcelControl(Control):
    """Excel control representation.

    Control class to set params for Excel reader/writer.

    """

    type = "excel"

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

    Note that a table resource schema will still be applied and types coerced to match the schema
    (either provided or inferred) _after_ the rows are read as strings.

    To return all cells as strings then both set `stringified=True` and specify a 
    schema that defines all fields to be of type string (see #1659).
    """

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "sheet": {"type": ["number", "string"]},
            "fillMergedCells": {"type": "boolean"},
            "preserveFormatting": {"type": "boolean"},
            "adjustFloatingPointError": {"type": "boolean"},
            "stringified": {"type": "boolean"},
        },
    }
