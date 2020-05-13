from . import validates
from .report import Report


def validate(source, **task):
    return validates.validate_table(source, **task)


# API Helpers


def validate_csv():
    pass


def validate_excel():
    pass


def validate_json():
    pass
