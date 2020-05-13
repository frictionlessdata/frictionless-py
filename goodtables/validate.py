from . import validates
from .report import Report


def validate(source, **task):
    table = validates.validate_table(source, **task)
    return Report(time=table['time'], warnings=[], tables=[table])


# API Helpers


def validate_csv():
    pass


def validate_excel():
    pass


def validate_json():
    pass
