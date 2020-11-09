import csv
from .metadata import Metadata
from . import errors
from . import config


class Dialect(Metadata):
    """Dialect representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import dialects`

    Parameters:
        descriptor? (str|dict): descriptor
        header? (bool): whether there is a header row
        headerRows? (int[]): row numbers of header rows
        headerJoin? (str): a multiline header joiner
        headerCase? (bool): case sensitive header

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(
        self,
        descriptor=None,
        header=None,
        header_rows=None,
        header_join=None,
        header_case=None,
    ):
        self.setinitial("header", header)
        self.setinitial("headerRows", header_rows)
        self.setinitial("headerJoin", header_join)
        self.setinitial("headerCase", header_case)
        super().__init__(descriptor)

    @Metadata.property
    def header(self):
        """
        Returns:
            bool: if there is a header row
        """
        return self.get("header", config.DEFAULT_HEADER)

    @Metadata.property
    def header_rows(self):
        """
        Returns:
            int[]: header rows
        """
        return self.get("headerRows", config.DEFAULT_HEADER_ROWS)

    @Metadata.property
    def header_join(self):
        """
        Returns:
            str: header joiner
        """
        return self.get("headerJoin", config.DEFAULT_HEADER_JOIN)

    @Metadata.property
    def header_case(self):
        """
        Returns:
            str: header case sensitive
        """
        return self.get("headerCase", config.DEFAULT_HEADER_CASE)

    # Expand

    def expand(self):
        """Expand metadata"""
        self.setdefault("header", self.header)
        self.setdefault("headerRows", self.header_rows)
        self.setdefault("headerJoin", self.header_join)
        self.setdefault("headerCase", self.header_case)

    # Metadata

    metadata_Error = errors.DialectError
    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "header": {"type": "boolean"},
            "headerRows": {"type": "array", "items": {"type": "number"}},
            "headerJoin": {"type": "string"},
            "headerCase": {"type": "boolean"},
        },
    }


class CsvDialect(Dialect):
    """Csv dialect representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import dialects`

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
        header=None,
        header_rows=None,
        header_join=None,
        header_case=None,
    ):
        self.setinitial("delimiter", delimiter)
        self.setinitial("lineTerminator", line_terminator)
        self.setinitial("quoteChar", quote_char)
        self.setinitial("doubleQuote", double_quote)
        self.setinitial("escapeChar", escape_char)
        self.setinitial("nullSequence", null_sequence)
        self.setinitial("skipInitialSpace", skip_initial_space)
        self.setinitial("commentChar", comment_char)
        super().__init__(
            descriptor=descriptor,
            header=header,
            header_rows=header_rows,
            header_join=header_join,
            header_case=header_case,
        )

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
        super().expand()
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
            "header": {"type": "boolean"},
            "headerRows": {"type": "array", "items": {"type": "number"}},
            "headerJoin": {"type": "string"},
            "headerCase": {"type": "boolean"},
        },
    }


class ExcelDialect(Dialect):
    """Excel dialect representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import dialects`

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
        header=None,
        header_rows=None,
        header_join=None,
        header_case=None,
    ):
        self.setinitial("sheet", sheet)
        self.setinitial("workbookCache", workbook_cache)
        self.setinitial("fillMergedCells", fill_merged_cells)
        self.setinitial("preserveFormatting", preserve_formatting)
        self.setinitial("adjustFloatingPointError", adjust_floating_point_error)
        super().__init__(
            descriptor=descriptor,
            header=header,
            header_rows=header_rows,
            header_join=header_join,
            header_case=header_case,
        )

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
        super().expand()
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
            "header": {"type": "boolean"},
            "headerRows": {"type": "array", "items": {"type": "number"}},
            "headerJoin": {"type": "string"},
            "headerCase": {"type": "boolean"},
        },
    }


class InlineDialect(Dialect):
    """Inline dialect representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import dialects`

    Parameters:
        descriptor? (str|dict): descriptor
        keys? (str[]): a list of strings to use as data keys
        keyed? (bool): whether data rows are keyed

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(
        self,
        descriptor=None,
        *,
        keys=None,
        keyed=None,
        header=None,
        header_rows=None,
        header_join=None,
        header_case=None,
    ):
        self.setinitial("keys", keys)
        self.setinitial("keyed", keyed)
        super().__init__(
            descriptor=descriptor,
            header=header,
            header_rows=header_rows,
            header_join=header_join,
            header_case=header_case,
        )

    @Metadata.property
    def keys(self):
        """
        Returns:
            str[]?: keys
        """
        return self.get("keys")

    @Metadata.property
    def keyed(self):
        """
        Returns:
            bool: keyed
        """
        return self.get("keyed", False)

    # Expand

    def expand(self):
        """Expand metadata"""
        self.setdefault("keyed", self.keyed)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "keys": {"type": "array"},
            "keyed": {"type": "boolean"},
            "header": {"type": "boolean"},
            "headerRows": {"type": "array", "items": {"type": "number"}},
            "headerJoin": {"type": "string"},
            "headerCase": {"type": "boolean"},
        },
    }


class JsonDialect(Dialect):
    """Json dialect representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import dialects`

    Parameters:
        descriptor? (str|dict): descriptor
        keys? (str[]): a list of strings to use as data keys
        keyed? (bool): whether data rows are keyed
        property? (str): a path within JSON to the data

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(
        self,
        descriptor=None,
        *,
        keys=None,
        keyed=None,
        property=None,
        header=None,
        header_rows=None,
        header_join=None,
        header_case=None,
    ):
        self.setinitial("keys", keys)
        self.setinitial("keyed", keyed)
        self.setinitial("property", property)
        super().__init__(
            descriptor=descriptor,
            header=header,
            header_rows=header_rows,
            header_join=header_join,
            header_case=header_case,
        )

    @Metadata.property
    def keys(self):
        """
        Returns:
            str[]?: keys
        """
        return self.get("keys")

    @Metadata.property
    def keyed(self):
        """
        Returns:
            bool: keyed
        """
        return self.get("keyed", False)

    @Metadata.property
    def property(self):
        """
        Returns:
            str?: property
        """
        return self.get("property")

    # Expand

    def expand(self):
        """Expand metadata"""
        super().expand()
        self.setdefault("keyed", self.keyed)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "keys": {"type": "array"},
            "keyed": {"type": "boolean"},
            "property": {"type": "string"},
            "header": {"type": "boolean"},
            "headerRows": {"type": "array", "items": {"type": "number"}},
            "headerJoin": {"type": "string"},
            "headerCase": {"type": "boolean"},
        },
    }
