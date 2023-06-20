from __future__ import annotations

from typing import Union

import attrs

from ...dialect import Control
from . import settings


@attrs.define(kw_only=True, repr=False)
class OdsControl(Control):
    """Ods control representation.

    Control class to set params for ODS reader/writer.

    """

    type = "ods"

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
