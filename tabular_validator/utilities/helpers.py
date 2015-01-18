"""Helper functions and variables."""


def builtin_validators():
    """Return dict of public builtin validators. Avoids circular import."""
    from .. import validators
    return {
        'spec': validators.SpecValidator,
        'structure': validators.StructureValidator,
        'schema': validators.SchemaValidator
    }


DEFAULT_PIPELINE = ('structure',)


# a schema for the reporter.Report() instances used by validators
report_schema = {
    'name': {'type': str},
    'category': {'type': str},
    'level': {'type': str},
    'position': {'type': int},
    'message': {'type': str}
}
