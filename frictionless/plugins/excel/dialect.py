from typing import Optional, Union, Any
from dataclasses import dataclass
from ...dialect import Dialect


@dataclass
class ExcelDialect(Dialect):
    """Excel dialect representation"""

    sheet: Union[str, int] = 1
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

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "sheet": {"type": ["number", "string"]},
            "workbookCache": {"type": "object"},
            "fillMergedCells": {"type": "boolean"},
            "preserveFormatting": {"type": "boolean"},
            "adjustFloatingPointError": {"type": "boolean"},
        },
    }
