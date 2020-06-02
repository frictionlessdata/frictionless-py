from pathlib import Path
from .task import task
from . import sources


@task
def validate(source, source_type=None, **options):

    # Normalize source
    if isinstance(source, Path):
        source = str(source)

    # Detect source type
    if not source_type:
        source_type = 'table'
        if isinstance(source, dict):
            if source.get('path') is not None:
                source_type = 'resource'
            if source.get('resources') is not None:
                source_type = 'package'
            if source.get('tasks') is not None:
                source_type = 'job'
        if isinstance(source, str):
            if source.endswith('.json'):
                source_type = 'resource'
            if source.endswith('datapackage.json'):
                source_type = 'package'
            if source.endswith('job.json'):
                source_type = 'job'

    # Validate source
    validate = getattr(sources, 'validate_%s' % source_type)
    return validate(source, **options)
