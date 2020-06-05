from pathlib import Path
from .report import Report
from . import sources


@Report.catch
def validate(source, source_type=None, **options):

    # Normalize source
    if isinstance(source, Path):
        source = str(source)

    # Detect source type
    if not source_type:
        source_type = 'table'
        if isinstance(source, dict):
            if source.get('sources') is not None:
                source_type = 'inquiry'
            if source.get('path') is not None:
                source_type = 'resource'
            if source.get('resources') is not None:
                source_type = 'package'
        if isinstance(source, str):
            if source.endswith('inquiry.json'):
                source_type = 'inquiry'
            if source.endswith('.json'):
                source_type = 'resource'
            if source.endswith('datapackage.json'):
                source_type = 'package'

    # Validate source
    validate = getattr(sources, 'validate_%s' % source_type)
    return validate(source, **options)
