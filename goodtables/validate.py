from pathlib import Path
from .report import Report
from . import validates
from . import helpers


@Report.catch
def validate(source, source_type=None, **options):

    # Normalize source
    if isinstance(source, Path):
        source = str(source)

    # Detect source type
    if not source_type:
        source_type = helpers.detect_source_type(source)

    # Validate source
    validate = getattr(validates, 'validate_%s' % source_type)
    return validate(source, **options)
