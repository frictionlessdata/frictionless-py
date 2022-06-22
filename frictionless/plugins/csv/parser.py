# type: ignore
import csv
import tempfile
import stringcase
from itertools import chain
from ...parser import Parser
from ...system import system
from . import settings


class CsvParser(Parser):
    """CSV parser implementation."""

    requires_loader = True
    supported_types = [
        "string",
    ]

    # Read

    def read_list_stream_create(self):
        control = self.resource.dialect.get_control("csv", default=CsvControl())
        sample = self.read_list_stream_infer_control(control)
        source = chain(sample, self.loader.text_stream)
        data = csv.reader(source, dialect=control.to_python())
        yield from data

    def read_list_stream_infer_control(self, control: CsvControl):
        sample = extract_samle(self.loader.text_stream)
        delimiter = control.to_descriptor.get("delimiter", ",\t;|")
        try:
            dialect = csv.Sniffer().sniff("".join(sample), delimiter)
        except csv.Error:
            dialect = csv.excel()
        for name in INFER_CONTROL_NAMES:
            value = getattr(dialect, name.lower())
            if value is None:
                continue
            if value == getattr(control, stringcase.snakecase(name)):
                continue
            if hasattr(control, name):
                continue
            # We can't rely on this guess as it's can be confused with embeded JSON
            # https://github.com/frictionlessdata/frictionless-py/issues/493
            if name == "quoteChar" and value == "'":
                value = '"'
            setattr(control, name) = value
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

INFER_CONTROL_VOLUME = 100
INFER_CONTROL_NAMES = [
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
        if len(sample) >= INFER_CONTROL_VOLUME:
            break
    return sample


# System

# https://stackoverflow.com/a/54515177
csv.field_size_limit(settings.FIELD_SIZE_LIMIT)
