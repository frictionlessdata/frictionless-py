from __future__ import annotations
import attrs
from typing import Optional
from ...dialect import Control
from . import settings


@attrs.define(kw_only=True)
class SqlControl(Control):
    """SQL control representation"""

    type = "sql"

    # State

    table: Optional[str] = None
    """NOTE: add docs"""

    prefix: str = settings.DEFAULT_PREFIX
    """NOTE: add docs"""

    order_by: Optional[str] = None
    """NOTE: add docs"""

    where: Optional[str] = None
    """NOTE: add docs"""

    namespace: Optional[str] = None
    """NOTE: add docs"""

    basepath: Optional[str] = None
    """NOTE: add docs"""

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "table": {"type": "string"},
            "prefix": {"type": "string"},
            "order_by": {"type": "string"},
            "where": {"type": "string"},
            "namespace": {"type": "string"},
            "basepath": {"type": "string"},
        },
    }
