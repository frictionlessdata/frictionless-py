from ...dialect import Control


class PandasControl(Control):
    """Pandas dialect representation"""

    type = "pandas"

    # State

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "name": {"type": "string"},
            "type": {"type": "string"},
        },
    }
