from ...dialect import Control


class PandasControl(Control):
    """Pandas dialect representation"""

    code = "pandas"

    # State

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
    }
