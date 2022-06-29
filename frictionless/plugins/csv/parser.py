# type: ignore
import csv
import tempfile
from itertools import chain
from ...parser import Parser
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

    def read_list_stream_create(self):
        control = self.resource.dialect.get_control("csv", ensure=CsvControl())
        sample = extract_samle(self.loader.text_stream)
        if self.resource.format == "tsv":
            control.delimiter = "\t"
        delimiter = control.get_defined("delimiter", default=",\t;|")
        try:
            config = csv.Sniffer().sniff("".join(sample), delimiter)
        except csv.Error:
            config = csv.excel()
        control.set_not_defined("delimiter", config.delimiter)
        control.set_not_defined("line_terminator", config.lineterminator)
        control.set_not_defined("escape_char", config.escapechar)
        control.set_not_defined("quote_char", config.quotechar)
        control.set_not_defined("skip_initial_space", config.skipinitialspace)
        source = chain(sample, self.loader.text_stream)
        data = csv.reader(source, dialect=control.to_python())
        yield from data

    # Write

    def write_row_stream(self, resource):
        options = {}
        source = resource
        target = self.resource
        control = target.dialect.get_control("csv", ensure=CsvControl())
        for name, value in vars(control.to_python()).items():
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
