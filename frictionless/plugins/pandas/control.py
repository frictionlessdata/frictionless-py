from ...control import Control


class PandasControl(Control):
    """Pandas dialect representation"""

    code = "pandas"

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
    }
