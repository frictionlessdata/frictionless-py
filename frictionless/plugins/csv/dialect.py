import csv
from ...metadata import Metadata
from ...dialect import Dialect


class CsvDialect(Dialect):
    """Csv dialect representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.csv import CsvDialect`

    Parameters:
        descriptor? (str|dict): descriptor
        delimiter? (str): csv delimiter
        line_terminator? (str): csv line terminator
        quote_char? (str): csv quote char
        double_quote? (bool): csv double quote
        escape_char? (str): csv escape char
        null_sequence? (str): csv null sequence
        skip_initial_space? (bool): csv skip initial space
        comment_char? (str): csv comment char

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(
        self,
        descriptor=None,
        *,
        delimiter=None,
        line_terminator=None,
        quote_char=None,
        double_quote=None,
        escape_char=None,
        null_sequence=None,
        skip_initial_space=None,
        comment_char=None,
    ):
        self.setinitial("delimiter", delimiter)
        self.setinitial("lineTerminator", line_terminator)
        self.setinitial("quoteChar", quote_char)
        self.setinitial("doubleQuote", double_quote)
        self.setinitial("escapeChar", escape_char)
        self.setinitial("nullSequence", null_sequence)
        self.setinitial("skipInitialSpace", skip_initial_space)
        self.setinitial("commentChar", comment_char)
        super().__init__(descriptor)

    @Metadata.property
    def delimiter(self):
        """
        Returns:
            str: delimiter
        """
        return self.get("delimiter", ",")

    @Metadata.property
    def line_terminator(self):
        """
        Returns:
            str: line terminator
        """
        return self.get("lineTerminator", "\r\n")

    @Metadata.property
    def quote_char(self):
        """
        Returns:
            str: quote char
        """
        return self.get("quoteChar", '"')

    @Metadata.property
    def double_quote(self):
        """
        Returns:
            bool: double quote
        """
        return self.get("doubleQuote", True)

    @Metadata.property
    def escape_char(self):
        """
        Returns:
            str?: escape char
        """
        return self.get("escapeChar")

    @Metadata.property
    def null_sequence(self):
        """
        Returns:
            str?: null sequence
        """
        return self.get("nullSequence")

    @Metadata.property
    def skip_initial_space(self):
        """
        Returns:
            bool: if skipping initial space
        """
        return self.get("skipInitialSpace", False)

    @Metadata.property
    def comment_char(self):
        """
        Returns:
            str?: comment char
        """
        return self.get("commentChar")

    # Expand

    def expand(self):
        """Expand metadata"""
        self.setdefault("delimiter", self.delimiter)
        self.setdefault("lineTerminator", self.line_terminator)
        self.setdefault("quoteChar", self.quote_char)
        self.setdefault("doubleQuote", self.double_quote)
        self.setdefault("skipInitialSpace", self.skip_initial_space)

    # Import/Export

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
