import csv
from typing import Optional
from dataclasses import dataclass
from ...dialect import Control
from . import settings


@dataclass
class CsvControl(Control):
    """Csv dialect representation"""

    code = "csv"

    # Properties

    delimiter: str = settings.DEFAULT_DELIMITER
    """TODO: add docs"""

    line_terminator: str = settings.DEFAULT_LINE_TERMINATOR
    """TODO: add docs"""

    quote_char: str = settings.DEFAULT_QUOTE_CHAR
    """TODO: add docs"""

    double_quote: bool = False
    """TODO: add docs"""

    escape_char: Optional[str] = None
    """TODO: add docs"""

    null_sequence: Optional[str] = None
    """TODO: add docs"""

    skip_initial_space: bool = False
    """TODO: add docs"""

    comment_char: Optional[str] = None
    """TODO: add docs"""

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

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
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
