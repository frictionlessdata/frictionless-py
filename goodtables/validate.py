from . import sources


def validate(source, source_type=None, **options):

    # Detect source type
    if not source_type:
        source_type = 'table'
        if isinstance(source, list):
            if source and isinstance(source[0], dict):
                source_type = 'nested'
        if isinstance(source, dict):
            if source.get('path') is not None:
                source_type = 'resource'
            if source.get('resources') is not None:
                source_type = 'package'
        if isinstance(source, str):
            if source.endswith('.json'):
                source_type = 'resource'
            if source.endswith('datapackage.json'):
                source_type = 'package'

    # Validate source
    validate = getattr(sources, 'validate_%s' % source_type)
    return validate(source, **options)
