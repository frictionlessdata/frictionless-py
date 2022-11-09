from __future__ import annotations
import attrs
from typing import Union
from ...dialect import Control
from . import settings


@attrs.define(kw_only=True)
class OdsControl(Control):
    """Ods control representation.

    Control class to set params for ODS reader/writer.

    """

    type = "ods"

    # State

    sheet: Union[str, int] = settings.DEFAULT_SHEET
    """
    Name or index of the sheet to read/write.
    """

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "sheet": {"type": ["number", "string"]},
        },
    }
