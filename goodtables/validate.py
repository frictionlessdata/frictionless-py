from . import validates


def validate(source, **options):
    return validates.validate_table(source, **options)
