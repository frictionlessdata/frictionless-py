from __future__ import annotations

import attrs

from ...dialect import Control


@attrs.define(kw_only=True, repr=False)
class PolarsControl(Control):
    """Polars dialect representation"""

    type = "polars"
