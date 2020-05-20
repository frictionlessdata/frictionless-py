from . import sources


def validate(source, **options):
    if isinstance(source, dict):
        return sources.validate_resource(source, **options)
    return sources.validate_table(source, **options)
