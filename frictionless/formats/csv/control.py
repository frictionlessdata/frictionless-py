from __future__ import annotations
import csv
import attrs
from typing import Optional
from ...dialect import Control
from . import settings


@attrs.define(kw_only=True)
class CsvControl(Control):
    """Csv dialect representation.

    Control class to set params for CSV reader/writer.

    """

    type = "csv"

    # State

    delimiter: str = settings.DEFAULT_DELIMITER
    """
    Specify the delimiter used to separate text strings while
    reading from or writing to the csv file. Default value is ",".
    For example: delimiter=";"
    """

    line_terminator: str = settings.DEFAULT_LINE_TERMINATOR
    """
    Specify the line terminator for the csv file while reading/writing.
    For example: line_terminator="\n". Default line_terminator is "\r\n".
    """

    quote_char: str = settings.DEFAULT_QUOTE_CHAR
    """
    Specify the quote char for fields that contains a special character
    such as comma, CR, LF or double quote. Default value is '"'.
    For example: quotechar='|'
    """

    double_quote: bool = settings.DEFAULT_DOUBLE_QUOTE
    """
    It controls how 'quote_char' appearing inside a field should themselves be
    quoted. When set to True, the 'quote_char' is doubled else escape char is
    used. Default value is True.
    """

    escape_char: Optional[str] = None
    """
    A one-character string used by the csv writer to escape. Default is None, which disables
    escaping. It uses 'quote_char', if double_quote is False.
    """

    null_sequence: Optional[str] = None
    """
    Specify the null sequence and not set by default.
    For example: \\N
    """

    skip_initial_space: bool = False
    """
    Ignores spaces following the comma if set to True.
    For example space in header(in csv file): "Name", "Team"
    """

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
        },
    }
