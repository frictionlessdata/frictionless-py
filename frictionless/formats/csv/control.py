from __future__ import annotations
import csv
import attrs
from typing import Optional
from ...dialect import Control
from . import settings


@attrs.define(kw_only=True)
class CsvControl(Control):
    """Csv dialect representation"""

    type = "csv"

    # State

    delimiter: str = settings.DEFAULT_DELIMITER
    """NOTE: add docs"""

    line_terminator: str = settings.DEFAULT_LINE_TERMINATOR
    """NOTE: add docs"""

    quote_char: str = settings.DEFAULT_QUOTE_CHAR
    """NOTE: add docs"""

    double_quote: bool = settings.DEFAULT_DOUBLE_QUOTE
    """NOTE: add docs"""

    escape_char: Optional[str] = None
    """NOTE: add docs"""

    null_sequence: Optional[str] = None
    """NOTE: add docs"""

    skip_initial_space: bool = False
    """NOTE: add docs"""

    comment_char: Optional[str] = None
    """NOTE: add docs"""

    # Convert

    def to_python(self):
        """Conver to Python's `csv.Dialect`"""
        config = csv.excel()
        config.delimiter = self.delimiter
        config.doublequote = self.double_quote if self.escape_char else True
        config.escapechar = self.escape_char
        config.lineterminator = self.line_terminator
        config.quotechar = self.quote_char
        config.quoting = csv.QUOTE_NONE if self.quote_char == "" else csv.QUOTE_MINIMAL
        config.skipinitialspace = self.skip_initial_space
        return config

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "delimiter": {"type": "string"},
            "lineTerminator": {"type": "string"},
            "quoteChar": {"type": "string"},
            "doubleQuote": {"type": "boolean"},
            "escapeChar": {"type": "string"},
            "nullSequence": {"type": "string"},
            "skipInitialSpace": {"type": "boolean"},
            "commentChar": {"type": "string"},
            "caseSensitiveHeader": {"type": "boolean"},
        },
    }
