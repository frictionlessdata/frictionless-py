import csv
import tempfile
import stringcase
from itertools import chain
from ..metadata import Metadata
from ..dialect import Dialect
from ..plugin import Plugin
from ..parser import Parser
from ..system import system


# Plugin


class CsvPlugin(Plugin):
    """Plugin for Pandas

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.csv import CsvPlugin`

    """

    code = "csv"

    def create_dialect(self, resource, *, descriptor):
        if resource.format == "csv":
            return CsvDialect(descriptor)
        elif resource.format == "tsv":
            return CsvDialect(descriptor, delimiter="\t")

    def create_parser(self, resource):
        if resource.format in ["csv", "tsv"]:
            return CsvParser(resource)


# Dialect


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


# Parser


class CsvParser(Parser):
    """CSV parser implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.csv import CsvPlugins

    """

    requires_loader = True
    supported_types = [
        "string",
    ]

    # Read

    def read_list_stream_create(self):
        sample = self.read_list_stream_infer_dialect()
        source = chain(sample, self.loader.text_stream)
        data = csv.reader(source, dialect=self.resource.dialect.to_python())
        yield from data

    def read_list_stream_infer_dialect(self):
        sample = extract_samle(self.loader.text_stream)
        delimiter = self.resource.dialect.get("delimiter", ",\t;|")
        try:
            dialect = csv.Sniffer().sniff("".join(sample), delimiter)
        except csv.Error:
            dialect = csv.excel()
        for name in INFER_DIALECT_NAMES:
            value = getattr(dialect, name.lower())
            if value is None:
                continue
            if value == getattr(self.resource.dialect, stringcase.snakecase(name)):
                continue
            if name in self.resource.dialect:
                continue
            # We can't rely on this guess as it's can be confused with embeded JSON
            # https://github.com/frictionlessdata/frictionless-py/issues/493
            if name == "quoteChar" and value == "'":
                value = '"'
            self.resource.dialect[name] = value
        return sample

    # Write

    def write_row_stream(self, resource):
        options = {}
        source = resource
        target = self.resource
        for name, value in vars(target.dialect.to_python()).items():
            if not name.startswith("_") and value is not None:
                options[name] = value
        with tempfile.NamedTemporaryFile(
            "wt", delete=False, encoding=target.encoding, newline=""
        ) as file:
            writer = csv.writer(file, **options)
            with source:
                for row in source.row_stream:
                    if row.row_number == 1:
                        writer.writerow(row.field_names)
                    writer.writerow(row.to_list(types=self.supported_types))
        loader = system.create_loader(target)
        loader.write_byte_stream(file.name)


# Internal

INFER_DIALECT_VOLUME = 100
INFER_DIALECT_NAMES = [
    "delimiter",
    "lineTerminator",
    "escapeChar",
    "quoteChar",
    "skipInitialSpace",
]


def extract_samle(text_stream):
    sample = []
    while True:
        try:
            sample.append(next(text_stream))
        except StopIteration:
            break
        if len(sample) >= INFER_DIALECT_VOLUME:
            break
    return sample
