import csv
import tempfile
import stringcase
from itertools import chain
from ...parser import Parser
from ...system import system
from . import settings


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


# System

# https://stackoverflow.com/a/54515177
csv.field_size_limit(settings.FIELD_SIZE_LIMIT)
