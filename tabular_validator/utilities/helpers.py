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
