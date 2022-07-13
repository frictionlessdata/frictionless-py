# type: ignore
from __future__ import annotations
import csv
import tempfile
from itertools import chain
from ...resource import Parser
from ...system import system
from .control import CsvControl
from . import settings


class CsvParser(Parser):
    """CSV parser implementation."""

    requires_loader = True
    supported_types = [
        "string",
    ]

    # Read

    def read_cell_stream_create(self):
        control = CsvControl.from_dialect(self.resource.dialect)
        sample = extract_samle(self.loader.text_stream)
        if self.resource.format == "tsv":
            control.set_not_defined("delimiter", "\t")
        delimiter = control.get_defined("delimiter", default=",\t;|")
        try:
            config = csv.Sniffer().sniff("".join(sample), delimiter)
        except csv.Error:
            config = csv.excel()
        # TODO: set only if it differs from default?
        control.set_not_defined("delimiter", config.delimiter, distinct=True)
        control.set_not_defined("line_terminator", config.lineterminator, distinct=True)
        control.set_not_defined("escape_char", config.escapechar, distinct=True)
        control.set_not_defined("quote_char", config.quotechar, distinct=True)
        control.set_not_defined(
            "skip_initial_space", config.skipinitialspace, distinct=True
        )
        source = chain(sample, self.loader.text_stream)
        data = csv.reader(source, dialect=control.to_python())
        yield from data

    # Write

    def write_row_stream(self, source):
        options = {}
        control = CsvControl.from_dialect(self.resource.dialect)
        if self.resource.format == "tsv":
            control.set_not_defined("delimiter", "\t")
        for name, value in vars(control.to_python()).items():
            if not name.startswith("_") and value is not None:
                options[name] = value
        with tempfile.NamedTemporaryFile(
            "wt", delete=False, encoding=self.resource.encoding, newline=""
        ) as file:
            writer = csv.writer(file, **options)
            with source:
                writer.writerow(source.schema.field_names)
                for row in source.row_stream:
                    writer.writerow(row.to_list(types=self.supported_types))
        loader = system.create_loader(self.resource)
        loader.write_byte_stream(file.name)


# Internal

SAMPLE_SIZE = 100


def extract_samle(text_stream):
    sample = []
    while True:
        try:
            sample.append(next(text_stream))
        except StopIteration:
            break
        if len(sample) >= SAMPLE_SIZE:
            break
    return sample


# System

# https://stackoverflow.com/a/54515177
csv.field_size_limit(settings.FIELD_SIZE_LIMIT)
