from . import validates


def validate(source, **task):
    return validates.validate_table(source, **task)


def validate_csv():
    pass


def validate_excel():
    pass


def validate_json():
    pass
