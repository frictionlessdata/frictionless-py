from ...metadata import Metadata
from ...dialect import Dialect


class ExcelDialect(Dialect):
    """Excel dialect representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.excel import ExcelDialect`

    Parameters:
        descriptor? (str|dict): descriptor
        sheet? (int|str): number from 1 or name of an excel sheet
        workbook_cache? (dict): workbook cache
        fill_merged_cells? (bool): whether to fill merged cells
        preserve_formatting? (bool): whither to preserve formatting
        adjust_floating_point_error? (bool): whether to adjust floating point error

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(
        self,
        descriptor=None,
        *,
        sheet=None,
        workbook_cache=None,
        fill_merged_cells=None,
        preserve_formatting=None,
        adjust_floating_point_error=None,
    ):
        self.setinitial("sheet", sheet)
        self.setinitial("workbookCache", workbook_cache)
        self.setinitial("fillMergedCells", fill_merged_cells)
        self.setinitial("preserveFormatting", preserve_formatting)
        self.setinitial("adjustFloatingPointError", adjust_floating_point_error)
        super().__init__(descriptor)

    @Metadata.property
    def sheet(self):
        """
        Returns:
            str|int: sheet
        """
        return self.get("sheet", 1)

    @Metadata.property
    def workbook_cache(self):
        """
        Returns:
            dict: workbook cache
        """
        return self.get("workbookCache")

    @Metadata.property
    def fill_merged_cells(self):
        """
        Returns:
            bool: fill merged cells
        """
        return self.get("fillMergedCells", False)

    @Metadata.property
    def preserve_formatting(self):
        """
        Returns:
            bool: preserve formatting
        """
        return self.get("preserveFormatting", False)

    @Metadata.property
    def adjust_floating_point_error(self):
        """
        Returns:
            bool: adjust floating point error
        """
        return self.get("adjustFloatingPointError", False)

    # Expand

    def expand(self):
        """Expand metadata"""
        self.setdefault("sheet", self.sheet)
        self.setdefault("fillMergedCells", self.fill_merged_cells)
        self.setdefault("preserveFormatting", self.preserve_formatting)
        self.setdefault("adjustFloatingPointError", self.adjust_floating_point_error)

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
