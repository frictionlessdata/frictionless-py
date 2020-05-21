from . import sources


def validate(source, source_type=None, **options):
    if isinstance(source, dict):
        return sources.validate_resource(source, **options)
    if isinstance(source, str) and source.endswith('.json'):
        return sources.validate_resource(source, **options)
    return sources.validate_table(source, **options)
