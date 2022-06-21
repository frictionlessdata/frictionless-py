from ...dialect import Dialect


class SpssDialect(Dialect):
    """Spss dialect representation"""

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
    }
