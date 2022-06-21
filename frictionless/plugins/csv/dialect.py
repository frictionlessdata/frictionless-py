import csv
from typing import Optional
from dataclasses import dataclass
from ...dialect import Dialect


@dataclass
class CsvDialect(Dialect):
    """Csv dialect representation"""

    delimiter: str = ","
    """TODO: add docs"""

    line_terminator: str = "\r\n"
    """TODO: add docs"""

    quote_char: str = '"'
    """TODO: add docs"""

    double_quote: bool = True
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
        dialect = csv.excel()
        dialect.delimiter = self.delimiter
        dialect.doublequote = self.double_quote if self.escape_char else True
        dialect.escapechar = self.escape_char
        dialect.lineterminator = self.line_terminator
        dialect.quotechar = self.quote_char
        dialect.quoting = csv.QUOTE_NONE if self.quote_char == "" else csv.QUOTE_MINIMAL
        dialect.skipinitialspace = self.skip_initial_space
        return dialect

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
