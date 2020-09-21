import csv
import tempfile
import stringcase
import unicodecsv
from itertools import chain
from ..parser import Parser
from .. import helpers


class CsvParser(Parser):
    """CSV parser implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless import parsers`

    """

    newline = ""
    native_types = [
        "string",
    ]

    # Read

    def read_data_stream_create(self):
        sample = self.read_data_stream_infer_dialect()
        source = chain(sample, self.loader.text_stream)
        data = csv.reader(source, dialect=self.file.dialect.to_python())
        yield from data

    def read_data_stream_infer_dialect(self):
        sample = extract_samle(self.loader.text_stream)
        delimiter = self.file.dialect.get("delimiter", ",\t;|")
        try:
            dialect = csv.Sniffer().sniff("".join(sample), delimiter)
        except csv.Error:
            dialect = csv.excel()
        for name in INFER_DIALECT_NAMES:
            value = getattr(dialect, name.lower())
            if value is None:
                continue
            if value == getattr(self.file.dialect, stringcase.snakecase(name)):
                continue
            if name in self.file.dialect:
                continue
            self.file.dialect[name] = value
        return sample

    # Write

    def write(self, row_stream):
        options = {}
        for name in vars(self.file.dialect.to_python()):
            value = getattr(self.file.dialect, name, None)
            if value is not None:
                options[name] = value
        with tempfile.NamedTemporaryFile(delete=False) as file:
            writer = unicodecsv.writer(file, encoding=self.file.encoding, **options)
            for row in row_stream:
                schema = row.schema
                if row.row_number == 1:
                    writer.writerow(schema.field_names)
                # NOTE: move this logic to Row?
                cells = list(row.values())
                cells, notes = schema.write_data(cells, native_types=self.native_types)
                writer.writerow(cells)
        helpers.move_file(file.name, self.file.source)


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
