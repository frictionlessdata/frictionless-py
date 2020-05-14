from . import sources


def validate(source, **options):
    return sources.validate_table(source, **options)
